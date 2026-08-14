FROM python:3.11-slim

WORKDIR /app

RUN apt-get update && apt-get install -y \
    ffmpeg \
    libreoffice \
    tesseract-ocr \
    ghostscript \
    curl \
    && rm -rf /var/lib/apt/lists/*

COPY backend/requirements.txt /tmp/backend-requirements.txt
COPY worker/requirements.txt /tmp/worker-requirements.txt
RUN pip install --no-cache-dir -r /tmp/backend-requirements.txt -r /tmp/worker-requirements.txt

COPY backend /backend

COPY worker/app ./app

ENV PYTHONPATH=/backend
ENV BACKEND_PATH=/backend

CMD ["celery", "-A", "app.worker", "worker", "--loglevel=info", "--beat", "--concurrency=1"]