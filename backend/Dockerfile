# Multi-stage build для оптимизации размера образа
FROM python:3.11-slim as builder

WORKDIR /app

# Установка зависимостей для сборки
RUN apt-get update && apt-get install -y --no-install-recommends \
    gcc \
    postgresql-client \
    && rm -rf /var/lib/apt/lists/*

# Копирование requirements
COPY requirements.txt .

# Установка Python зависимостей
RUN pip install --no-cache-dir --user -r requirements.txt

# Финальный образ
FROM python:3.11-slim

WORKDIR /app

# Копирование установленных зависимостей из builder
COPY --from=builder /root/.local /root/.local

# Копирование исходного кода
COPY . .

# Установка PATH для Python пакетов
ENV PATH=/root/.local/bin:$PATH

# Создание директории для логов
RUN mkdir -p logs

# Открытие порта
EXPOSE 8000

# Запуск приложения
CMD ["uvicorn", "src.api.main:app", "--host", "0.0.0.0", "--port", "8000"]
