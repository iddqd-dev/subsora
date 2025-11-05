FROM python:3.10-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt && apt-get -y update && apt-get -y install curl

COPY . .

CMD ["python", "-u", "main.py"]