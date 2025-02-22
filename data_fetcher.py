# data_fetcher.py
import ccxt
import pandas as pd
import datetime
import time
import os
import logging
from typing import Optional

logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.INFO)

class DataFetcher:
    """
    Fetches historical and live OHLCV data from an exchange.
    """
    def __init__(self, exchange_id: str = 'binance', max_retries: int = 5, backoff_factor: float = 1.5):
        self.exchange_id = exchange_id
        self.max_retries = max_retries
        self.backoff_factor = backoff_factor
        self.exchange = self.initialize_exchange()
        self.cache = {}

    def initialize_exchange(self) -> ccxt.Exchange:
        if self.exchange_id == 'binance':
            api_key = os.getenv("BINANCE_API_KEY")
            secret = os.getenv("BINANCE_API_SECRET")
            exchange = ccxt.binance({
                'enableRateLimit': True,
                'apiKey': api_key,
                'secret': secret,
            })
            logger.info("Initialized Binance exchange with rate limit: %s ms", exchange.rateLimit)
            return exchange
        else:
            raise ValueError(f"Exchange {self.exchange_id} is not supported yet.")

    def fetch_historical_data(self, symbol: str = "BTC/USDT", timeframe: str = "1h",
                                since: Optional[int] = None, limit: int = 500, use_cache: bool = True) -> pd.DataFrame:
        """
        Fetch historical OHLCV data and return it as a pandas DataFrame.
        """
        cache_key = (symbol, timeframe, since, limit)
        if use_cache and cache_key in self.cache:
            logger.info("Using cached data for %s", cache_key)
            return self.cache[cache_key]
        
        if since is None:
            since = self.exchange.parse8601('2023-01-01T00:00:00Z')
        try:
            since_readable = datetime.datetime.fromtimestamp(since / 1000).strftime('%Y-%m-%d %H:%M:%S')
            logger.info("Fetching historical data for %s since %s", symbol, since_readable)
        except Exception:
            logger.warning("Error converting 'since' to a readable format.")

        attempt = 0
        delay = 1  # initial delay (seconds)
        while attempt < self.max_retries:
            try:
                ohlcv = self.exchange.fetch_ohlcv(symbol, timeframe=timeframe, since=since, limit=limit)
                if not ohlcv:
                    raise ValueError("Empty data returned")
                df = pd.DataFrame(ohlcv, columns=['Timestamp', 'Open', 'High', 'Low', 'Close', 'Volume'])
                df['Timestamp'] = pd.to_datetime(df['Timestamp'], unit='ms')
                df.set_index('Timestamp', inplace=True)
                df.dropna(inplace=True)
                if df.empty:
                    raise ValueError("DataFrame empty after cleaning")
                self.cache[cache_key] = df
                logger.info("Fetched %d rows of data for %s.", len(df), symbol)
                return df
            except Exception as e:
                attempt += 1
                logger.error("Attempt %d: Error fetching historical data for %s: %s", attempt, symbol, e)
                if attempt >= self.max_retries:
                    logger.error("Max retries reached for %s. Returning empty DataFrame.", symbol)
                    return pd.DataFrame()
                time.sleep(delay)
                delay *= self.backoff_factor

    def fetch_live_data(self, symbol: str = "BTC/USDT", timeframe: str = "1m") -> dict:
        """
        Fetch the latest OHLCV data for the given symbol.
        """
        attempt = 0
        delay = 1
        while attempt < self.max_retries:
            try:
                logger.info("Fetching live data for %s", symbol)
                ohlcv = self.exchange.fetch_ohlcv(symbol, timeframe=timeframe, limit=1)
                if not ohlcv:
                    raise ValueError("Empty live data returned")
                latest = ohlcv[-1]
                data = {
                    'Timestamp': pd.to_datetime(latest[0], unit='ms'),
                    'Open': latest[1],
                    'High': latest[2],
                    'Low': latest[3],
                    'Close': latest[4],
                    'Volume': latest[5]
                }
                if any(val is None for val in data.values()):
                    raise ValueError("Live data contains None values")
                logger.info("Fetched live data: %s", data)
                return data
            except Exception as e:
                attempt += 1
                logger.error("Attempt %d: Error fetching live data for %s: %s", attempt, symbol, e)
                if attempt >= self.max_retries:
                    logger.error("Max retries reached for live data for %s.", symbol)
                    return {}
                time.sleep(delay)
                delay *= self.backoff_factor
