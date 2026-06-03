# atc-mail

Microservicio independiente que responde automáticamente consultas de **timbrado de CTO** por correo.

- Buzón: `sebastian.apestey@americantower.com` (Outlook / Microsoft 365)
- Entrada: IMAP · Salida: SMTP (sin Azure AD)
- Datos: Postgres (`cm.inventory_fat_occupation`), misma base que `atc-noc-suite`

## Formato de mail (TASA / remitentes)

Asunto **exacto** (mayúsculas/minúsculas indistinto; admite prefijo `Re:`):

```text
TIMBRADO CTO ES01-FATC-8-105270
timbrado cto es01-fatc-8-105270
```

El bot responde con tabla OUT (1–8), AID, STATUS (`FREE`, `RESERVED`, `IN SERVICE`) y operador.

La respuesta se envía al **remitente (From)** y a todas las direcciones en **Cc** (excepto el buzón del bot).

## Prueba con otro proveedor (Gmail, etc.)

El **remitente** de las respuestas es siempre `MAIL_USER`. Para probar sin M365, configurá **el mismo buzón** en IMAP y SMTP (solo cambiá `.env`).

**Gmail (recomendado para prueba):**

1. Activar IMAP en Gmail.
2. Crear una [contraseña de aplicación](https://myaccount.google.com/apppasswords).
3. En `.env`:

```env
MAIL_IMAP_HOST=imap.gmail.com
MAIL_IMAP_PORT=993
MAIL_SMTP_HOST=smtp.gmail.com
MAIL_SMTP_PORT=587
MAIL_USER=tu@gmail.com
MAIL_PASSWORD=<contraseña de aplicación de 16 caracteres>
```

Enviá el mail de prueba **a esa casilla Gmail** con asunto `TIMBRADO CTO ES01-FATC-8-105270`.

**Proton (`@proton.me`):** no expone IMAP público; hace falta [Proton Mail Bridge](https://proton.me/mail/bridge) corriendo en local (`127.0.0.1:1143` / `1025`). Ver comentarios en `.env.example`.

## Configuración del buzón (sin IT)

1. Outlook web → **Configuración → Correo → Sincronizar correo** → activar **IMAP**.
2. Si hay MFA: perfil Microsoft → **Seguridad** → **Contraseña de aplicación** (si el tenant lo permite).
3. Usar esa contraseña en `MAIL_PASSWORD` del `.env`.

## Instalación local

```bash
cd /home/sdapestey/Documents/devops/atc-mail
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
cp .env.example .env
# Editar .env: DB_* y MAIL_PASSWORD
```

Variables DB iguales que `atc-noc-suite` (`DATABASE_URL` o `DB_HOST` / `DB_USER` / …).

## Prueba en dry-run

No envía mails ni marca procesados en SQLite:

```bash
export DRY_RUN=1
python scripts/run_once.py
```

Enviá un mail de prueba con asunto `TIMBRADO CTO <FATC>` a tu buzón y ejecutá `run_once.py`. La respuesta aparece en logs.

## Producción (Docker)

```bash
docker compose up -d --build
docker compose logs -f atc-mail
```

El worker corre en loop (`POLL_INTERVAL_SECONDS`, default 60 s). Estado idempotente en volumen `atc-mail-data`.

## Variables de entorno

| Variable | Descripción |
|----------|-------------|
| `DATABASE_URL` | Postgres (alternativa a `DB_*`) |
| `MAIL_USER` / `MAIL_PASSWORD` | Buzón IMAP/SMTP (timbrado) |
| `MAIL_ALLOWED_SENDER_DOMAINS` | Vacío = todos; ej. `tmoviles.com` |
| `DRY_RUN` | `1` = solo log, sin SMTP |
| `PROCESSED_DB_PATH` | SQLite de message-id procesados |

## Tests

```bash
pytest
```

## Estructura

```text
atc_mail/
  worker.py          # loop IMAP → Postgres → SMTP
  cto_inventory.py   # query + formato tabla
  mail_imap.py       # lectura UNSEEN
  mail_smtp.py       # reply en hilo
  parser.py          # TIMBRADO CTO <FATC>
  security.py        # whitelist / anti-loop
  processed.py       # idempotencia SQLite
```
