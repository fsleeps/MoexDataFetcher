from sqlalchemy import Column, Integer, String, Date, Float, DateTime, Index
from sqlalchemy.sql import func
from database.database import Base

class StockData(Base):
    __tablename__ = "stock_data"
    
    id = Column(Integer, primary_key=True, index=True)
    ticker = Column(String(20), nullable=False, index=True)
    date = Column(Date, nullable=False, index=True)
    price = Column(Float, nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    # Создаем составной индекс для быстрого поиска по тикеру и дате
    __table_args__ = (
        Index('idx_ticker_date', 'ticker', 'date', unique=True),
    )
    
    def __repr__(self):
        return f"<StockData(ticker='{self.ticker}', date='{self.date}', price={self.price})>" 