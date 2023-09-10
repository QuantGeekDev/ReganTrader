from abc import ABC, abstractmethod
from retry import retry
import logging
from configuration_manager.configuration_manager import ConfigurationManager

#TODO: Should the DataProviderInterface connect to config manager or should we have this work in a different way?

class DataProviderInterface(ABC):
    def __init__(self, connector, config_manager: ConfigurationManager):
        self.connector = connector
        self.config_manager = config_manager

    @abstractmethod
    def retry_request(self, fn, *args, **kwargs):
        @retry(Exception, tries=3, delay=2)
        def wrapper():
            return fn(*args, **kwargs)

        return wrapper()

    def get_data(self, method, symbol_or_symbols, start=None, end=None, limit=None, feed=None, timeframe=None):
        # Retrieve optional parameters from ConfigurationManager using get_strategy_setting
        start = start or self.config_manager.get_strategy_setting("start")
        end = end or self.config_manager.get_strategy_setting("end")
        limit = limit or self.config_manager.get_strategy_setting("limit")
        feed = feed or self.config_manager.get_strategy_setting("feed")
        timeframe = timeframe or self.config_manager.get_strategy_setting("timeframe")

        try:
            return self.retry_request(self.connector.get_data, method, symbol_or_symbols, start, end, limit, feed,
                                      timeframe)
        except Exception as e:
            logging.error(f"Error fetching {method} for {symbol_or_symbols}: {e}")
            raise
