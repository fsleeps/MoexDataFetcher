import aiohttp
import logging
from typing import List, Dict, Optional
from datetime import date, datetime
import asyncio

logger = logging.getLogger(__name__)

class MoexClient:
    """Асинхронный клиент для работы с API Московской биржи"""
    
    def __init__(self):
        self.base_url = "https://iss.moex.com/iss"
        self.timeout = aiohttp.ClientTimeout(total=30)
        self.headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        }
    
    async def get_stock_data(self, ticker: str, start_date: date, end_date: date) -> List[Dict]:
        """
        Асинхронно получает данные по акции за указанный период
        
        Args:
            ticker: Тикер акции (например, 'SBER')
            start_date: Дата начала периода
            end_date: Дата окончания периода
            
        Returns:
            Список словарей с данными о ценах
        """
        try:
            # Формируем URL для запроса
            url = f"{self.base_url}/engines/stock/markets/shares/securities/{ticker}/candles.json"
            
            params = {
                'from': start_date.strftime('%Y-%m-%d'),
                'till': end_date.strftime('%Y-%m-%d'),
                'interval': 24,  # Дневные свечи
                'iss.meta': 'off',
                'iss.only': 'candles'
            }
            
            logger.info(f"Запрос данных для {ticker} с {start_date} по {end_date}")
            
            async with aiohttp.ClientSession(timeout=self.timeout, headers=self.headers) as session:
                async with session.get(url, params=params) as response:
                    response.raise_for_status()
                    data = await response.json()
            
            if 'candles' not in data or 'data' not in data['candles']:
                logger.warning(f"Нет данных для тикера {ticker}")
                return []
            
            # Обрабатываем полученные данные
            candles_data = data['candles']['data']
            result = []
            
            for candle in candles_data:
                # Структура данных: [begin, open, close, high, low, value, volume]
                candle_date = datetime.strptime(candle[0], '%Y-%m-%d').date()
                close_price = float(candle[2])  # Цена закрытия
                
                result.append({
                    'date': candle_date,
                    'price': close_price
                })
            
            logger.info(f"Получено {len(result)} записей для {ticker}")
            return result
            
        except aiohttp.ClientError as e:
            logger.error(f"Ошибка при запросе к MOEX API для {ticker}: {e}")
            raise
        except Exception as e:
            logger.error(f"Неожиданная ошибка при получении данных для {ticker}: {e}")
            raise
    
    async def get_multiple_stocks_data(self, tickers: List[str], start_date: date, end_date: date) -> Dict[str, List[Dict]]:
        """
        Асинхронно получает данные по нескольким акциям
        
        Args:
            tickers: Список тикеров
            start_date: Дата начала периода
            end_date: Дата окончания периода
            
        Returns:
            Словарь с данными по каждому тикеру
        """
        # Создаем задачи для всех тикеров
        tasks = []
        for ticker in tickers:
            task = self.get_stock_data(ticker, start_date, end_date)
            tasks.append((ticker, task))
        
        # Выполняем все задачи параллельно
        result = {}
        for ticker, task in tasks:
            try:
                result[ticker] = await task
            except Exception as e:
                logger.error(f"Ошибка при получении данных для {ticker}: {e}")
                result[ticker] = []
        
        return result 