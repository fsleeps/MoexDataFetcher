from pydantic import BaseModel, Field, field_validator, model_validator, ConfigDict
from typing import List, Dict, Optional
from datetime import date, datetime

class StockRequest(BaseModel):
    """Модель для запроса данных по акциям"""
    
    model_config = ConfigDict(str_strip_whitespace=True, extra='forbid')
    
    tickers: List[str] = Field(..., min_items=1, max_items=10, description="Список тикеров акций")
    start_date: date = Field(..., description="Дата начала периода")
    end_date: date = Field(..., description="Дата окончания периода")
    
    @field_validator('tickers')
    @classmethod
    def validate_tickers(cls, v):
        """Валидация тикеров"""
        return [ticker.upper() for ticker in v if ticker and len(ticker) <= 20]
    
    @field_validator('start_date')
    @classmethod
    def validate_start_date(cls, v):
        """Валидация даты начала"""
        if v > date.today():
            raise ValueError("Дата начала не может быть в будущем")
        return v
    
    @model_validator(mode='after')
    def validate_dates(self):
        """Валидация дат (проверка что end_date >= start_date)"""
        if self.end_date < self.start_date:
            raise ValueError("Дата окончания не может быть раньше даты начала")
        return self

class StockResponse(BaseModel):
    """Модель для ответа с данными по акциям"""
    
    ticker: str = Field(..., description="Тикер акции")
    data: Dict[str, float] = Field(..., description="Словарь с данными в формате {дата: цена}")

class ErrorResponse(BaseModel):
    """Модель для ответа с ошибкой"""
    
    detail: str = Field(..., description="Описание ошибки")
    error_code: str = Field(..., description="Код ошибки")
    timestamp: datetime = Field(default_factory=datetime.now, description="Время возникновения ошибки")

class ApiResponse(BaseModel):
    """Общая модель для API ответов"""
    
    success: bool = Field(..., description="Статус выполнения запроса")
    data: Optional[Dict] = Field(None, description="Данные ответа")
    error: Optional[str] = Field(None, description="Описание ошибки")
    timestamp: datetime = Field(default_factory=datetime.now, description="Время ответа") 