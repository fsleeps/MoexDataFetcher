#!/usr/bin/env python3
"""
Скрипт для запуска приложения MOEX Data Fetcher
"""

import uvicorn
import os
from dotenv import load_dotenv

# Загружаем переменные окружения
load_dotenv()

def main():
    # Получаем настройки из переменных окружения
    host = os.getenv("HOST", "0.0.0.0")
    port = int(os.getenv("PORT", "8000"))
    debug = os.getenv("DEBUG", "False").lower() == "true"
    
    print(f"Запуск MOEX Data Fetcher на {host}:{port}")
    print(f"Режим отладки: {debug}")
    
    uvicorn.run(
        "engine.app:app",
        host=host,
        port=port,
        reload=debug,
        log_level="info"
    )

if __name__ == "__main__":
    main() 