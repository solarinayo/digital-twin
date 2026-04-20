FROM python:3.12-slim

WORKDIR /app

ENV PYTHONUNBUFFERED=1
ENV PORT=8080
ENV PYTHONPATH=/app

COPY requirements.txt .
COPY backend/requirements.txt backend/requirements.txt
RUN pip install --no-cache-dir -r requirements.txt

COPY backend ./backend
COPY frontend ./frontend
COPY public ./public/

EXPOSE 8080

CMD exec uvicorn backend.app.main:app --host 0.0.0.0 --port "${PORT:-8080}"
