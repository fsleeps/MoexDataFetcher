from fastapi import FastAPI, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from typing import List, Dict
from datetime import date

from database.database import get_db
from models.stock_data import StockData
from engine.moex_client import MoexClient
from engine.data_service import DataService
from models.pydantic_models import StockRequest, StockResponse

app = FastAPI(title="MOEX Data Fetcher", version="1.0.0")

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

@app.get("/health")
async def health_check():
    return {"status": "healthy"} 