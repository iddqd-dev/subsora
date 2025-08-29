FROM python:3.11-slim
WORKDIR /app
ENV PYTHONPATH=/app

# Устанавливаем netcat для проверки готовности БД
RUN apt-get update && apt-get install -y netcat-traditional && rm -rf /var/lib/apt/lists/*

COPY requirements.txt /app/backend/requirements.txt
RUN pip install --no-cache-dir --upgrade pip && \
    pip install --no-cache-dir -r /app/backend/requirements.txt
COPY . /app/backend/
EXPOSE 8000

# Команда по умолчанию (может быть переопределена в docker-compose)
CMD ["sh", "-c", "alembic -c /app/backend/alembic.ini upgrade head && uvicorn main:app --host 0.0.0.0 --port 8000"]
