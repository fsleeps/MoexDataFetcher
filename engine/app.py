import logging
from fastapi import FastAPI, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from typing import Dict
import asyncio
from database.database import get_db
from engine.data_service import DataService
from models.pydantic_models import StockRequest, ApiResponse
from database_manager import setup_database

# Настройка логирования
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

app = FastAPI(title="MOEX Data Fetcher", version="1.0.0")

@app.on_event("startup")
async def startup_event():
    """Событие запуска приложения - создаем базу данных если не существует"""
    await setup_database()

@app.get("/", response_model=ApiResponse)
async def root():
    """Информация о приложении"""
    return ApiResponse(
        success=True,
        data={"message": "MOEX Data Fetcher API", "version": "1.0.0"}
    )

@app.post("/fetch-stock-data", response_model=ApiResponse)
async def fetch_stock_data(
    request: StockRequest,
    db: AsyncSession = Depends(get_db)
):
    """
    Получает данные по акциям с Московской биржи
    """
    try:
        data_service = DataService(db)
        result = await data_service.get_stock_data(
            tickers=request.tickers,
            start_date=request.start_date,
            end_date=request.end_date
        )
        return ApiResponse(success=True, data=result)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        logging.error(f"Ошибка при получении данных: {e}")
        raise HTTPException(status_code=500, detail="Внутренняя ошибка сервера")