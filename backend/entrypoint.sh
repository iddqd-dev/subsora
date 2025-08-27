#!/bin/sh
set -e

echo "Waiting for postgres at $DB_HOST:$DB_PORT..."
while ! nc -z "$DB_HOST" "$DB_PORT"; do
  sleep 0.1
done
echo "PostgreSQL started"

# Применяем миграции Alembic
echo "Running Alembic migrations..."
alembic -c /app/backend/alembic.ini upgrade head

# Запускаем приложение
echo "Starting Uvicorn..."
exec uvicorn main:app --host 0.0.0.0 --port 8000