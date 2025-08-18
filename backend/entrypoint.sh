#!/bin/sh
set -e

echo "Waiting for postgres at $DB_HOST:$DB_PORT..."
while ! nc -z "$DB_HOST" "$DB_PORT"; do
  sleep 0.1
done
echo "PostgreSQL started"

# 👇 ИСПРАВЛЕНИЕ: Указываем правильный путь к конфигу alembic
echo "Running database migrations..."
alembic -c /app/backend/alembic.ini upgrade head

echo "Starting FastAPI server..."
exec "$@"