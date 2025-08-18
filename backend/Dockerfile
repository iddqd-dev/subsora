WORKDIR /app

# Устанавливаем netcat
RUN apt-get update && apt-get install -y netcat-openbsd && rm -rf /var/lib/apt/lists/*

# 2. 👇 КЛЮЧЕВОЕ ИЗМЕНЕНИЕ: Говорим Python, что корень для импортов - это /app.
# Когда он увидит `from backend.app...`, он будет искать папку /app/backend/app.
ENV PYTHONPATH=/app

# 3. Создаем папку `backend` внутри контейнера
RUN mkdir /app/backend

# 4. Копируем ТОЛЬКО requirements.txt в /app/backend
COPY requirements.txt /app/backend/requirements.txt

# 5. Устанавливаем зависимости
RUN pip install --no-cache-dir -r /app/backend/requirements.txt

# 6. Копируем ВЕСЬ текущий контекст (содержимое папки subsora/backend)
# в папку /app/backend/ внутри контейнера.
COPY . /app/backend/

# 7. Копируем entrypoint и делаем его исполняемым
COPY entrypoint.sh /app/entrypoint.sh
RUN chmod +x /app/entrypoint.sh

ENTRYPOINT ["/app/entrypoint.sh"]

# 8. Указываем uvicorn, где найти main.py, используя полный путь
CMD ["uvicorn", "backend.main:app", "--host", "0.0.0.0", "--port", "8000"]