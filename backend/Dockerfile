FROM python:3.11-slim
RUN mkdir /app/backend
COPY requirements.txt /app/backend/requirements.txt
RUN pip install --no-cache-dir --upgrade pip && \
    pip install --no-cache-dir -r /app/backend/requirements.txt
COPY . /app/backend/
EXPOSE 8000
CMD ["sh", "-c", "alembic -c /app/backend/alembic.ini upgrade head && uvicorn main:app --host 0.0.0.0 --port 8000"]
