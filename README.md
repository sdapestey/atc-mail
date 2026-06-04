# atc-mail

Microservicio que responde automáticamente consultas de **timbrado CTO** por correo (IMAP → Postgres → SMTP).

## Qué hace

1. Lee el buzón configurado (`MAIL_USER`) buscando mails con asunto `TIMBRADO CTO <FATC>`.
2. Consulta inventario en Postgres (misma base que `atc-noc-suite`).
3. Responde al **remitente (Para)** y pone en **Cc** a Lucas/Facundo (siempre) más otros contactos del Cc entrante en dominios permitidos.

## Remitentes permitidos (From)

Solo se procesan mails cuyo **From** pertenece a:

| Dominio |
|---------|
| `tmoviles.com.ar` |
| `retesar.com` |
| `americantower.com` |

Cualquier otro dominio se ignora (se registra en log). El propio buzón del bot nunca se procesa (anti-loop).

`MAIL_ALLOWED_SENDER_DOMAINS` — si está vacío, se usan los tres dominios de la tabla.

## Destinatarios de la respuesta

| Campo | Quién |
|-------|--------|
| **Para (To)** | Remitente del timbrado |
| **Cc** | Siempre `lucas.gimenez@americantower.com` y `facundo.vergara@americantower.com`, más cualquier Cc entrante en dominio permitido (sin duplicar) |

`MAIL_ALWAYS_CC` — lista fija (coma-separados). Los externos en Cc del mail entrante (ej. Gmail) no se copian.

## Formato del mail entrante

Asunto (mayúsculas/minúsculas indistinto; admite prefijo `Re:`):

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
# Editar .env: DB_*, MAIL_USER, MAIL_PASSWORD
```

## Variables de entorno

| Variable | Descripción |
|----------|-------------|
| `DB_HOST`, `DB_PORT`, `DB_NAME`, `DB_USER`, `DB_PASSWORD` | Postgres (o usar `DATABASE_URL`) |
| `MAIL_USER` / `MAIL_PASSWORD` | Buzón IMAP/SMTP del bot |
| `MAIL_IMAP_HOST` / `MAIL_SMTP_HOST` | Servidores (ver `.env.example`) |
| `MAIL_ALLOWED_SENDER_DOMAINS` | Default: `tmoviles.com.ar,retesar.com,americantower.com` |
| `MAIL_ALWAYS_CC` | Default: Lucas + Facundo (siempre en Cc de la respuesta) |
| `DRY_RUN` | `1` = simular sin enviar mail |
| `POLL_INTERVAL_SECONDS` | Intervalo del worker (default 60) |
| `PROCESSED_DB_PATH` | SQLite de idempotencia |

Ver `.env.example` para firma, Gmail de prueba y opciones de mail.

## Prueba local (dry-run)

No envía SMTP ni marca procesados:

```bash
export DRY_RUN=1
python scripts/run_once.py
```

Enviá un mail de prueba desde `@tmoviles.com.ar` o `@americantower.com` al buzón configurado.

## Producción (Docker)

```bash
docker compose up -d --build
docker compose logs -f atc-mail
```

Estado persistente en volumen `atc-mail-data` (`processed.db`).

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
