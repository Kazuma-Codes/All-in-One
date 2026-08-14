FROM python:3.11-slim

WORKDIR /app

RUN apt-get update && apt-get install -y \
    ffmpeg \
    libreoffice \
    tesseract-ocr \
    curl \
    && rm -rf /var/lib/apt/lists/*

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

ENV PYTHONPATH=/backend
ENV BACKEND_PATH=/backend

CMD ["celery", "-A", "app.worker", "worker", "--loglevel=info", "--beat", "--concurrency=1"]