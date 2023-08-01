# historical_data_manager.py

import logging
import pickle
from database_manager.database_manager import DatabaseManager

class HistoricalDataManager:
    def __init__(self, data_provider, db_manager):
        self.data_provider = data_provider
        self.db_manager = db_manager

    def get_historical_data(self, symbol, timeframe, start=None, end=None):
        """
        Get historical data for a given symbol and timeframe. If the data is available in the cache,
        it is returned from there. Otherwise, it is fetched from the data provider and
        then stored in the cache.
        """
        table_name = f"{symbol}_{timeframe}"

        # Create the table if it doesn't already exist
        self.db_manager.create_table(table_name)

        rows = self.db_manager.select_data(table_name, start, end)

        if rows and start is None and end is None:
            logging.info(f"Returning historical data for {symbol} from cache.")
            return [pickle.loads(row[0]) for row in rows]

        logging.info(f"Fetching historical data for {symbol} from data provider.")
        try:
            data = self.data_provider.get_crypto_bars(symbol, start=start, end=end, timeframe=timeframe)
            self.db_manager.insert_data(table_name, [(d.timestamp, pickle.dumps(d)) for d in data])
            return data
        except Exception as e:
            logging.error(f"Error fetching historical data for {symbol}: {e}")
            raise
