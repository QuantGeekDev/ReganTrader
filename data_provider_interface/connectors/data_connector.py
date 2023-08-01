from abc import ABC, abstractmethod


class DataConnector(ABC):
    @abstractmethod
    def get_data(self, method, symbol_or_symbols, start=None, end=None, limit=None, feed=None, timeframe=None):
        pass
