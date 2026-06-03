FROM python:3.12-slim

WORKDIR /app

ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY atc_mail/ ./atc_mail/
COPY scripts/ ./scripts/

RUN mkdir -p /app/data

CMD ["python", "-m", "atc_mail.worker"]
