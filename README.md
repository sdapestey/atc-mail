# atc-mail

Microservicio que responde automáticamente consultas de **timbrado CTO** por correo (IMAP → Postgres → SMTP).

## Qué hace

1. Lee el buzón configurado (`MAIL_USER`) buscando mails con asunto `TIMBRADO CTO <FATC>`.
2. Consulta inventario en Postgres (misma base que `atc-noc-suite`).
3. Responde al **remitente (Para)** y pone en **Cc** a Lucas/Facundo/`noc_atc` (según `MAIL_ALWAYS_CC`) más otros contactos del Cc entrante en dominios permitidos.

## Remitentes permitidos (From)

Solo se procesan mails cuyo **From** pertenece a un dominio de `MAIL_ALLOWED_SENDER_DOMAINS`. En producción típica:

| Dominio |
|---------|
| `tmoviles.com.ar` |
| `retesar.com` |
| `americantower.com` |
| `digitsa.com.ar` |
| `rowing.com.ar` |
| `comfica.com` |

Cualquier otro dominio se ignora (se registra en log). El propio buzón del bot nunca se procesa (anti-loop).

Si `MAIL_ALLOWED_SENDER_DOMAINS` está vacío, el código usa el default: `tmoviles.com.ar`, `retesar.com`, `americantower.com`. Completá la lista en `.env` para sumar operadores.

## Destinatarios de la respuesta

| Campo | Quién |
|-------|--------|
| **Para (To)** | Remitente del timbrado |
| **Cc** | Siempre los de `MAIL_ALWAYS_CC` (Lucas, Facundo y `noc_atc@americantower.com`), más cualquier Cc entrante en dominio permitido (sin duplicar) |

Los externos en Cc del mail entrante (ej. Gmail) no se copian.

## Formato del mail entrante

Asunto (mayúsculas/minúsculas indistinto). Las consultas nuevas **no** deben llevar prefijo `Re:` / `Fw:` (eso se usa para ignorar reacciones/reply de Outlook):

```text
TIMBRADO CTO ES01-FATC-8-105270
```

Ejemplo válido en minúsculas: `timbrado cto si01-fatc-8-101093`.

## Respuesta

Incluye:

- Identificador CTO, fuente de inventario, dirección postal, enlace a Maps y coordenadas.
- Tabla HTML: OUT, AID, STATUS (`FREE`, `RESERVED`, `IN SERVICE`), operador.
- Firma **NOC Bot** / American Tower Corporation.

## Requisitos

- Python 3.12+
- Postgres con esquemas `cm` / `aux` (como `atc-noc-suite`)
- Buzón con IMAP y SMTP habilitados (Gmail con contraseña de aplicación, M365 según política del tenant)

## Instalación

```bash
git clone https://github.com/sdapestey/atc-mail.git
cd atc-mail
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
cp .env.example .env
# Editar .env: DB_*, MAIL_USER, MAIL_PASSWORD, MAIL_ALLOWED_SENDER_DOMAINS
```

## Variables de entorno

| Variable | Descripción |
|----------|-------------|
| `DB_HOST`, `DB_PORT`, `DB_NAME`, `DB_USER`, `DB_PASSWORD` | Postgres (o usar `DATABASE_URL`) |
| `MAIL_USER` / `MAIL_PASSWORD` | Buzón IMAP/SMTP del bot |
| `MAIL_IMAP_HOST` / `MAIL_SMTP_HOST` | Servidores (ver `.env.example`) |
| `MAIL_ALLOWED_SENDER_DOMAINS` | Dominios From permitidos (ver tabla arriba) |
| `MAIL_ALWAYS_CC` | Siempre en Cc de la respuesta |
| `DRY_RUN` | `1` = simular sin enviar mail |
| `POLL_INTERVAL_SECONDS` | Intervalo del worker (default 60) |
| `PROCESSED_DB_PATH` | SQLite de idempotencia |
| `TIMBRADO_HISTORICO_CSV_PATH` | CSV de historial (default: `data/timbrado_historico.csv` junto a processed.db) |

Ver `.env.example` para firma, Gmail y opciones de mail.

## Prueba local (dry-run)

No envía SMTP ni marca procesados:

```bash
export DRY_RUN=1
python scripts/run_once.py
```

Enviá un mail de prueba desde un dominio permitido (ej. `@americantower.com`) al buzón configurado.

## Producción (Docker)

```bash
docker compose up -d --build
docker compose logs -f atc-mail
```

Estado persistente en volumen `atc-mail-data` (`processed.db` y `timbrado_historico.csv`).

## Historial de consultas (CSV)

Cada respuesta enviada con éxito agrega una línea a **`timbrado_historico.csv`** (mismo directorio que `processed.db`, o la ruta de `TIMBRADO_HISTORICO_CSV_PATH`).

En Docker el archivo está en: `/app/data/timbrado_historico.csv`.

### Columnas

| Columna | Contenido |
|--------|-----------|
| `consulted_at` | Fecha/hora de Buenos Aires (ISO 8601 con offset, ej. `2026-07-14T23:00:00-03:00`) |
| `sender_email` | Mail de quien consultó |
| `sender_name` | Nombre del remitente (si venía en el From) |
| `cto` | Identificador CTO |
| `site` | Partido/sitio desde el prefijo (ej. `SI01` → San Isidro) |
| `reply_to` | Destinatarios To de la respuesta |
| `reply_cc` | Destinatarios Cc de la respuesta |
| `message_id` | Message-ID del mail entrante |
| `status` | `sent` cuando la respuesta se envió OK |

### Descargar el CSV (servidor Docker)

En el servidor del bot:

```bash
cd ~/devops/atc-mail   # o la ruta donde esté el clone

# Ver si existe
docker compose exec atc-mail ls -la /app/data/

# Copiar al directorio del proyecto en el servidor
docker cp atc-mail:/app/data/timbrado_historico.csv ./timbrado_historico.csv
```

Desde tu PC (reemplazá usuario y host):

```bash
scp usuario@servidor:~/devops/atc-mail/timbrado_historico.csv .
```

También podés bajarlo con WinSCP / FileZilla desde el servidor, o verlo en el acto:

```bash
docker compose exec atc-mail cat /app/data/timbrado_historico.csv
```

Abrí el archivo en Excel / LibreOffice para estadísticas.

> El CSV se crea en la **primera** respuesta exitosa. Si cambió el formato/nombre, borrá o renombrá el archivo viejo en `/app/data/` antes de continuar.

## Tests

```bash
pytest
```

## Estructura

```text
atc_mail/
  worker.py          # loop principal
  mail_imap.py       # lectura IMAP
  mail_smtp.py       # envío reply + logo embebido
  cto_inventory.py   # query + formato respuesta
  parser.py          # asunto TIMBRADO CTO
  security.py        # whitelist dominios
  recipients.py      # From + Cc
  signature.py       # firma HTML
  processed.py       # idempotencia SQLite
  query_log.py       # historial CSV de consultas
  sites.py           # site/partido desde prefijo CTO
scripts/
  run_once.py        # una pasada manual
  build_signature_logo.py
```

## Seguridad

- No commitear `.env` (credenciales).
- Repo recomendado: **privado**.
- Rotar contraseñas de aplicación si se expusieron.

## Licencia

Uso interno American Tower / operadores autorizados.
