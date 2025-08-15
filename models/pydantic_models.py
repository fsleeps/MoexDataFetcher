from pydantic import BaseModel, Field, validator
from typing import List
from datetime import date

class StockRequest(BaseModel):
    """Модель для запроса данных по акциям"""
    
    tickers: List[str] = Field(..., min_items=1, max_items=10, description="Список тикеров акций")
    start_date: date = Field(..., description="Дата начала периода")
    end_date: date = Field(..., description="Дата окончания периода")
    
    @validator('tickers')
    def validate_tickers(cls, v):
        """Валидация тикеров"""
        for ticker in v:
            if not ticker or len(ticker) > 20:
                raise ValueError(f"Некорректный тикер: {ticker}")
            # Приводим к верхнему регистру
            ticker = ticker.upper()
        return [ticker.upper() for ticker in v]
    
    @validator('end_date')
    def validate_dates(cls, v, values):
        """Валидация дат"""
        if 'start_date' in values and v < values['start_date']:
            raise ValueError("Дата окончания не может быть раньше даты начала")
        return v
    
    @validator('start_date')
    def validate_start_date(cls, v):
        """Валидация даты начала"""
        if v > date.today():
            raise ValueError("Дата начала не может быть в будущем")
        return v

class StockResponse(BaseModel):
    """Модель для ответа с данными по акциям"""
    
    ticker: str = Field(..., description="Тикер акции")
    data: dict = Field(..., description="Словарь с данными в формате {дата: цена}")

class ErrorResponse(BaseModel):
    """Модель для ответа с ошибкой"""
    
    detail: str = Field(..., description="Описание ошибки")
    error_code: str = Field(..., description="Код ошибки") 