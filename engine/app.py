import logging
from fastapi import FastAPI, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from typing import Dict
import asyncio

from database.database import get_db
from engine.data_service import DataService
from models.pydantic_models import StockRequest
from database_manager import setup_database, cleanup_database

# Настройка логирования
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

app = FastAPI(title="MOEX Data Fetcher", version="1.0.0")

@app.on_event("startup")
async def startup_event():
    """Событие запуска приложения - создаем базу данных"""
    await setup_database()

@app.on_event("shutdown")
async def shutdown_event():
    """Событие завершения приложения - удаляем базу данных"""
    await cleanup_database()

@app.get("/")
async def root():
    return {"message": "MOEX Data Fetcher API"}

@app.post("/fetch-stock-data", response_model=Dict[str, Dict[str, float]])
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
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))