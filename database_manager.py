#!/usr/bin/env python3
"""
Менеджер базы данных - создает базу данных при первом запуске
"""

import asyncio
import asyncpg
import os

class DatabaseManager:
    def __init__(self, host=None, port=None, user=None, password=None):
        self.host = host or os.environ.get("DB_HOST", "localhost")
        self.port = port or int(os.environ.get("DB_PORT", "5432"))
        self.user = user or os.environ.get("DB_USER", "postgres")
        self.password = password or os.environ.get("DB_PASSWORD", "password")
        self.db_name = os.environ.get("DB_NAME", "moex_data")
        self.connection = None
        
    async def create_database(self):
        """Создает базу данных и таблицы"""
        try:
            print("Подключение к PostgreSQL...")
            
            # Подключаемся к системной базе postgres
            postgres_conn = await asyncpg.connect(
                user=self.user,
                password=self.password,
                host=self.host,
                port=self.port,
                database="postgres"
            )
            
            print("Создаем базу данных...")
            await postgres_conn.execute(f"""
                CREATE DATABASE {self.db_name} 
                WITH 
                TEMPLATE = template0
                OWNER = {self.user}
                ENCODING = 'UTF8'
                LC_COLLATE = 'en_US.utf8'
                LC_CTYPE = 'en_US.utf8'
                TABLESPACE = pg_default
                CONNECTION LIMIT = -1;
            """)
            print(f"База данных '{self.db_name}' создана!")
            await postgres_conn.close()
            
            # Создаем таблицы
            await self.create_tables()
            
        except asyncpg.exceptions.DuplicateDatabaseError:
            print(f"База данных '{self.db_name}' уже существует")
            await self.create_tables()
        except Exception as e:
            print(f"Ошибка при создании базы данных: {e}")
            raise
    
    async def create_tables(self):
        """Создает таблицы в базе данных"""
        try:
            print("Создаем таблицы...")
            
            # Подключаемся к нашей базе данных
            self.connection = await asyncpg.connect(
                user=self.user,
                password=self.password,
                host=self.host,
                port=self.port,
                database=self.db_name
            )
            
            print("Подключены к базе данных")
            
            # Создаем таблицу stock_data
            await self.connection.execute("""
                CREATE TABLE IF NOT EXISTS stock_data (
                    id SERIAL PRIMARY KEY,
                    ticker VARCHAR(20) NOT NULL,
                    date DATE NOT NULL,
                    price FLOAT NOT NULL,
                    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
                    updated_at TIMESTAMP WITH TIME ZONE
                );
            """)
            print("Таблица 'stock_data' создана!")
            
            # Создаем индексы
            await self.connection.execute("""
                CREATE INDEX IF NOT EXISTS ix_stock_data_id 
                ON stock_data (id);
            """)
            
            await self.connection.execute("""
                CREATE INDEX IF NOT EXISTS ix_stock_data_ticker 
                ON stock_data (ticker);
            """)
            
            await self.connection.execute("""
                CREATE UNIQUE INDEX IF NOT EXISTS idx_ticker_date 
                ON stock_data (ticker, date);
            """)
            
            print("Все индексы созданы!")
            
        except Exception as e:
            print(f"Ошибка при создании таблиц: {e}")
            raise

async def setup_database():
    """Настройка базы данных при запуске приложения"""
    db_manager = DatabaseManager()
    await db_manager.create_database()
    print("База данных готова к работе!")

if __name__ == "__main__":
    async def main():
        try:
            await setup_database()
            print("База данных успешно создана!")
        except Exception as e:
            print(f"Ошибка: {e}")
    
    asyncio.run(main())
