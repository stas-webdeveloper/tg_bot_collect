FROM python:3.11-slim

# Устанавливаем системные зависимости
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    libpq-dev \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

# Копируем requirements и устанавливаем зависимости
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Копируем содержимое папки app в текущую директорию (/app)
COPY ./app .

# Создаём директорию для данных (внутри /app)
RUN mkdir -p /app/data

VOLUME ["/app/data"]

# Запускаем main.py напрямую или как модуль
CMD ["python", "main.py"]
