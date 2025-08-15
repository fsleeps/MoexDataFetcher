import aiohttp
import logging
from typing import List, Dict, Optional
from datetime import date, datetime

logger = logging.getLogger(__name__)

class MoexClient:
    """Асинхронный клиент для работы с API Московской биржи"""
    
    def __init__(self):
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
            url = f"https://iss.moex.com/iss/engines/stock/markets/shares/securities/{ticker}/candles.json"
            
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
            
            if 'candles' not in data:
                logger.warning(f"Нет данных для тикера {ticker}")
                return []
            
            # Обрабатываем полученные данные
            candles_data = data['candles']['data']
            logger.info(f"Получено {len(candles_data)} свечей для {ticker}")
            

            
            result = []
            
            for candle in candles_data:
                # Структура данных: [open, close, high, low, value, volume, begin, end]
                begin_date_str = candle[6]  # "2025-08-01 00:00:00"
                candle_date = datetime.strptime(begin_date_str, '%Y-%m-%d %H:%M:%S').date()
                close_price = float(candle[1])  # Цена закрытия находится на позиции 1
                
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
    
 