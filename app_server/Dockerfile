# Dockerfile for App Server (Backend)
FROM python:3.10-slim

WORKDIR /app

COPY requirements.txt .
RUN apt-get update && \
    apt-get install -y default-libmysqlclient-dev build-essential pkg-config && \
    pip install --no-cache-dir -r requirements.txt && \
    pip install --no-cache-dir mysqlclient && \
    apt-get clean && rm -rf /var/lib/apt/lists/*

COPY . .

EXPOSE 5001

CMD ["python3", "app.py"]