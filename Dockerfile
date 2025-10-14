# Используем официальный Python образ
FROM python:3.11-slim

# Устанавливаем минимальные системные зависимости
RUN apt-get update && apt-get install -y \
    gcc \
    g++ \
    && rm -rf /var/lib/apt/lists/*

# Устанавливаем рабочую директорию
WORKDIR /app

# Устанавливаем переменные окружения
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    DJANGO_SETTINGS_MODULE=config.settings

# Копируем файлы зависимостей
COPY requirements.txt .

# Устанавливаем Python зависимости
RUN pip install --no-cache-dir -r requirements.txt

# Добавляем gunicorn в PATH
ENV PATH="/app/.venv/bin:$PATH"

# Копируем код приложения
COPY . .

# Делаем entrypoint скрипт исполняемым
RUN chmod +x entrypoint.sh

# Создаем пользователя для безопасности
RUN adduser --disabled-password --gecos '' appuser && \
    chown -R appuser:appuser /app
USER appuser

# Открываем порт
EXPOSE 8000

# Используем entrypoint скрипт
ENTRYPOINT ["./entrypoint.sh"]
