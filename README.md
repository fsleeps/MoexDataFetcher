# MOEX Data Fetcher

Асинхронное приложение для получения данных о ценах акций с Московской биржи с кэшированием в PostgreSQL.

## Возможности

- Асинхронное получение данных о ценах акций за указанный период
- Кэширование данных в PostgreSQL для ускорения повторных запросов
- Поддержка множественных тикеров в одном запросе
- Параллельная обработка запросов к API
- Валидация входных данных с помощью Pydantic
- REST API на FastAPI
- Умное кэширование: запрашиваются только недостающие данные
- Логгирование

## Технологии

- Python 3.11
- FastAPI (асинхронный)
- PostgreSQL
- SQLAlchemy (асинхронный)
- Pydantic
- aiohttp (асинхронные HTTP запросы)
- asyncpg (асинхронный драйвер PostgreSQL)

- Poetry (управление зависимостями)

## Установка

1. Клонируйте репозиторий:
```bash
git clone <repository-url>
cd moex_fetch
```

2. Установите Poetry (если не установлен):
```bash
pip install poetry
```

3. Установите зависимости:
```bash
poetry install
```

4. Создайте файл `.env` с настройками подключения к базе данных:
```env
DATABASE_URL=postgresql+asyncpg://username:password@localhost:5432/moex_data
HOST=0.0.0.0
PORT=8000
DEBUG=True
```

5. Создайте базу данных PostgreSQL:
```sql
CREATE DATABASE moex_data;
```

6. Создайте таблицы в базе данных:
```bash
poetry run python create_tables.py
```

## Запуск

```bash
# Способ 1: Через run.py (с настройками из .env)
poetry run python run.py

# Способ 2: Через uvicorn напрямую
poetry run uvicorn engine.app:app --reload
```

Приложение будет доступно по адресу: http://localhost:8000

## API Endpoints

### POST /fetch-stock-data

Получение данных о ценах акций.

**Параметры запроса:**
```json
{
  "tickers": ["SBER", "GAZP"],
  "start_date": "2024-01-01",
  "end_date": "2024-01-31"
}
```

**Ответ:**
```json
{
  "SBER": {
    "2024-01-01": 250.5,
    "2024-01-02": 251.2,
    "2024-01-03": 249.8
  },
  "GAZP": {
    "2024-01-01": 150.1,
    "2024-01-02": 151.3,
    "2024-01-03": 149.9
  }
}
```

### GET /

Информация о приложении.

## Структура проекта

```
moex_fetch/
├── run.py                    # Скрипт запуска приложения
├── database/                 # Подключение к базе данных
│   ├── __init__.py
│   └── database.py          # Асинхронное подключение к БД
├── models/                   # Модели SQLAlchemy и Pydantic
│   ├── __init__.py
│   ├── stock_data.py        # Модель данных акций
│   └── pydantic_models.py   # Pydantic модели
├── engine/                   # Бизнес-логика и приложение
│   ├── __init__.py
│   ├── app.py               # Основное FastAPI приложение
│   ├── moex_client.py       # Асинхронный клиент MOEX API
│   └── data_service.py      # Асинхронный сервис работы с данными
├── alembic/                  # Миграции базы данных
│   ├── env.py
│   ├── script.py.mako
│   └── versions/
├── pyproject.toml           # Конфигурация Poetry
├── alembic.ini              # Конфигурация Alembic
└── README.md                # Документация
```

## Архитектура приложения

### MoexClient
- Асинхронный клиент для работы с API Московской биржи
- Делает HTTP запросы к `https://iss.moex.com/iss/`
- Обрабатывает ответы API и извлекает данные о ценах

### DataService
- Оркестрирует получение данных с учетом кэширования
- Проверяет наличие данных в базе данных
- Определяет недостающие даты и запрашивает их с MOEX API
- Параллельно обрабатывает несколько тикеров

### Кэширование
- Данные сохраняются в PostgreSQL
- При повторных запросах используются кэшированные данные
- Автоматически дополняются недостающие данные

## Использование

1. Запустите приложение
2. Отправьте POST запрос на `/fetch-stock-data` с JSON телом
3. Получите данные о ценах акций в формате словаря



## Разработка

### Создание таблиц:
```bash
poetry run python create_tables.py
```

### Запуск тестов:
```bash
poetry run pytest
```

### Форматирование кода:
```bash
poetry run black .
```