#!/usr/bin/env python3
"""
Менеджер базы данных - создает и удаляет базу данных автоматически
"""

import asyncio
import asyncpg
import signal
import sys
from contextlib import asynccontextmanager

class DatabaseManager:
    def __init__(self, host="localhost", port=5432, user="postgres", password="password"):
        self.host = host
        self.port = port
        self.user = user
        self.password = password
        self.db_name = "moex_data"
        self.connection = None
        
    async def create_database(self):
        """Создает базу данных и таблицы"""
        try:
            print("🔍 Подключение к PostgreSQL...")
            
            # Подключаемся к системной базе postgres
            postgres_conn = await asyncpg.connect(
                user=self.user,
                password=self.password,
                host=self.host,
                port=self.port,
                database="postgres"
            )
            
            print("📋 Создаем базу данных...")
            await postgres_conn.execute(f"""
                CREATE DATABASE {self.db_name} 
                WITH 
                OWNER = {self.user}
                ENCODING = 'UTF8'
                LC_COLLATE = 'Russian_Russia.utf8'
                LC_CTYPE = 'Russian_Russia.utf8'
                TABLESPACE = pg_default
                CONNECTION LIMIT = -1;
            """)
            print(f"✅ База данных '{self.db_name}' создана!")
            await postgres_conn.close()
            
            # Создаем таблицы
            await self.create_tables()
            
        except asyncpg.exceptions.DuplicateDatabaseError:
            print(f"ℹ️ База данных '{self.db_name}' уже существует")
            await self.create_tables()
        except Exception as e:
            print(f"❌ Ошибка при создании базы данных: {e}")
            raise
    
    async def create_tables(self):
        """Создает таблицы в базе данных"""
        try:
            print("📋 Создаем таблицы...")
            
            # Подключаемся к нашей базе данных
            self.connection = await asyncpg.connect(
                user=self.user,
                password=self.password,
                host=self.host,
                port=self.port,
                database=self.db_name
            )
            
            print("✅ Подключены к базе данных")
            
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
            print("✅ Таблица 'stock_data' создана!")
            
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
            
            print("✅ Все индексы созданы!")
            
        except Exception as e:
            print(f"❌ Ошибка при создании таблиц: {e}")
            raise
    
    async def drop_database(self):
        """Удаляет базу данных"""
        try:
            if self.connection:
                await self.connection.close()
                print("🔌 Соединение с базой данных закрыто")
            
            print("🗑️ Удаляем базу данных...")
            
            # Подключаемся к системной базе postgres
            postgres_conn = await asyncpg.connect(
                user=self.user,
                password=self.password,
                host=self.host,
                port=self.port,
                database="postgres"
            )
            
            # Принудительно закрываем все соединения к базе
            await postgres_conn.execute(f"""
                SELECT pg_terminate_backend(pid)
                FROM pg_stat_activity
                WHERE datname = '{self.db_name}' AND pid <> pg_backend_pid();
            """)
            
            # Удаляем базу данных
            await postgres_conn.execute(f"DROP DATABASE IF EXISTS {self.db_name};")
            print(f"✅ База данных '{self.db_name}' удалена!")
            
            await postgres_conn.close()
            
        except Exception as e:
            print(f"❌ Ошибка при удалении базы данных: {e}")
    
    async def cleanup(self):
        """Очистка при завершении работы"""
        await self.drop_database()

# Глобальный экземпляр менеджера
db_manager = None

async def setup_database():
    """Настройка базы данных при запуске приложения"""
    global db_manager
    db_manager = DatabaseManager()
    await db_manager.create_database()
    print("🚀 База данных готова к работе!")

async def cleanup_database():
    """Очистка базы данных при завершении приложения"""
    global db_manager
    if db_manager:
        await db_manager.cleanup()
        print("🧹 База данных очищена!")

def signal_handler(signum, frame):
    """Обработчик сигналов для корректного завершения"""
    print(f"\n📡 Получен сигнал {signum}, завершаем работу...")
    asyncio.create_task(cleanup_database())
    sys.exit(0)

# Регистрируем обработчики сигналов
signal.signal(signal.SIGINT, signal_handler)
signal.signal(signal.SIGTERM, signal_handler)

if __name__ == "__main__":
    async def main():
        try:
            await setup_database()
            print("⏳ База данных создана. Нажмите Ctrl+C для удаления...")
            
            # Ждем сигнала завершения
            while True:
                await asyncio.sleep(1)
                
        except KeyboardInterrupt:
            print("\n📡 Получен сигнал завершения...")
        finally:
            await cleanup_database()
    
    asyncio.run(main())
