import logging
from typing import List, Dict, Optional
from datetime import date, timedelta
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import and_, select
from models.stock_data import StockData
from .moex_client import MoexClient

logger = logging.getLogger(__name__)

class DataService:
    """Асинхронный сервис для работы с данными акций"""
    
    def __init__(self, db: AsyncSession):
        self.db = db
        self.moex_client = MoexClient()
    
    async def get_cached_data(self, ticker: str, start_date: date, end_date: date) -> List[Dict]:
        """
        Асинхронно получает данные из кэша (базы данных)
        
        Args:
            ticker: Тикер акции
            start_date: Дата начала периода
            end_date: Дата окончания периода
            
        Returns:
            Список словарей с данными о ценах
        """
        try:
            query = select(StockData).where(
                and_(
                    StockData.ticker == ticker,
                    StockData.date >= start_date,
                    StockData.date <= end_date
                )
            ).order_by(StockData.date)
            
            result = await self.db.execute(query)
            cached_data = result.scalars().all()
            
            data_list = []
            for record in cached_data:
                data_list.append({
                    'date': record.date,
                    'price': record.price
                })
            
            logger.info(f"Найдено {len(data_list)} записей в кэше для {ticker}")
            return data_list
            
        except Exception as e:
            logger.error(f"Ошибка при получении данных из кэша для {ticker}: {e}")
            return []
    
    async def save_data_to_cache(self, ticker: str, data: List[Dict]) -> None:
        """
        Асинхронно сохраняет данные в кэш (базу данных)
        
        Args:
            ticker: Тикер акции
            data: Список словарей с данными о ценах
        """
        try:
            for item in data:
                # Проверяем, существует ли уже запись
                query = select(StockData).where(
                    and_(
                        StockData.ticker == ticker,
                        StockData.date == item['date']
                    )
                )
                result = await self.db.execute(query)
                existing_record = result.scalar_one_or_none()
                
                if existing_record:
                    # Обновляем существующую запись
                    existing_record.price = item['price']
                else:
                    # Создаем новую запись
                    new_record = StockData(
                        ticker=ticker,
                        date=item['date'],
                        price=item['price']
                    )
                    self.db.add(new_record)
            
            await self.db.commit()
            logger.info(f"Сохранено {len(data)} записей в кэш для {ticker}")
            
        except Exception as e:
            await self.db.rollback()
            logger.error(f"Ошибка при сохранении данных в кэш для {ticker}: {e}")
            raise
    
    def get_missing_dates(self, cached_data: List[Dict], start_date: date, end_date: date) -> List[date]:
        """
        Определяет даты, для которых нет данных в кэше
        
        Args:
            cached_data: Данные из кэша
            start_date: Дата начала периода
            end_date: Дата окончания периода
            
        Returns:
            Список дат, для которых нужно получить данные
        """
        cached_dates = {item['date'] for item in cached_data}
        missing_dates = []
        
        current_date = start_date
        while current_date <= end_date:
            if current_date not in cached_dates:
                missing_dates.append(current_date)
            current_date += timedelta(days=1)
        
        return missing_dates
    
    async def get_stock_data(self, tickers: List[str], start_date: date, end_date: date) -> Dict[str, Dict[str, float]]:
        """
        Асинхронно получает данные по акциям с учетом кэширования
        
        Args:
            tickers: Список тикеров
            start_date: Дата начала периода
            end_date: Дата окончания периода
            
        Returns:
            Словарь в формате {ticker: {date: price}}
        """
        result = {}
        
        # Создаем задачи для обработки всех тикеров
        tasks = []
        for ticker in tickers:
            task = self._process_ticker(ticker, start_date, end_date)
            tasks.append((ticker, task))
        
        # Выполняем все задачи параллельно
        for ticker, task in tasks:
            try:
                ticker_result = await task
                result[ticker] = ticker_result
            except Exception as e:
                logger.error(f"Ошибка при получении данных для {ticker}: {e}")
                result[ticker] = {}
        
        return result
    
    async def _process_ticker(self, ticker: str, start_date: date, end_date: date) -> Dict[str, float]:
        """
        Обрабатывает один тикер: получает данные из кэша и дополняет недостающие
        
        Args:
            ticker: Тикер акции
            start_date: Дата начала периода
            end_date: Дата окончания периода
            
        Returns:
            Словарь с данными в формате {date: price}
        """
        # Получаем данные из кэша
        cached_data = await self.get_cached_data(ticker, start_date, end_date)
        
        # Определяем недостающие даты
        missing_dates = self.get_missing_dates(cached_data, start_date, end_date)
        
        if missing_dates:
            logger.info(f"Для {ticker} отсутствуют данные за {len(missing_dates)} дней")
            
            # Получаем недостающие данные с MOEX
            min_missing_date = min(missing_dates)
            max_missing_date = max(missing_dates)
            
            new_data = await self.moex_client.get_stock_data(
                ticker, min_missing_date, max_missing_date
            )
            
            if new_data:
                # Сохраняем новые данные в кэш
                await self.save_data_to_cache(ticker, new_data)
                
                # Добавляем новые данные к кэшированным
                cached_data.extend(new_data)
        
        # Формируем результат в нужном формате
        ticker_result = {}
        for item in cached_data:
            ticker_result[item['date'].strftime('%Y-%m-%d')] = item['price']
        
        return ticker_result 