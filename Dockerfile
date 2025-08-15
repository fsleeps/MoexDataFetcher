FROM python:3.11-slim

# Устанавливаем системные зависимости
RUN apt-get update && apt-get install -y \
    gcc \
    && rm -rf /var/lib/apt/lists/*

# Устанавливаем зависимости напрямую
RUN pip install fastapi uvicorn[standard] sqlalchemy asyncpg aiohttp pydantic python-dotenv psycopg2-binary

# Копируем код приложения
COPY . .

# Создаем пользователя для безопасности
RUN useradd --create-home --shell /bin/bash app
USER app

# Рабочая директория
WORKDIR /app

# Команда запуска
CMD ["uvicorn", "engine.app:app", "--host", "0.0.0.0", "--port", "8000"]
