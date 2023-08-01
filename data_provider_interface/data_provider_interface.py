from abc import ABC, abstractmethod
from retry import retry
import logging


class DataProviderInterface(ABC,):
    def __init__(self, connector):
        self.connector = connector

    @abstractmethod
    def retry_request(self, fn, *args, **kwargs):
        @retry(Exception, tries=3, delay=2)
        def wrapper():
            return fn(*args, **kwargs)

        return wrapper()

    def get_data(self, method, symbol_or_symbols, start=None, end=None, limit=None, feed=None, timeframe=None):
        try:
            return self.retry_request(self.connector.get_data, method, symbol_or_symbols, start, end, limit, feed,
                                      timeframe)
        except Exception as e:
            logging.error(f"Error fetching {method} for {symbol_or_symbols}: {e}")
            raise

