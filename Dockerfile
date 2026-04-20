FROM python:3.12-slim

WORKDIR /app

ENV PYTHONUNBUFFERED=1
ENV PORT=8080

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY api/ ./api/
COPY public/ ./public/

EXPOSE 8080

CMD exec uvicorn api.index:app --host 0.0.0.0 --port "${PORT:-8080}"
