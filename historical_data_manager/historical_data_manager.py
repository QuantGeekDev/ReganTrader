import pandas as pd
import logging
from datetime import datetime, timedelta

FRESHNESS_THRESHOLD_MINUTES = 59  # Change this value as required

class HistoricalDataManager:
    def __init__(self, data_provider):
        self.data_provider = data_provider
        self.freshness_threshold = timedelta(minutes=FRESHNESS_THRESHOLD_MINUTES)
        self.data_frame = pd.DataFrame()  # Initialize an empty DataFrame

    def get_historical_data(self, symbol, timeframe, start=None, end=None):
        logging.info("historical_data_manager.py - Attempting to get historical data")
        if not self.data_frame.empty and start is None and end is None:
            last_data_timestamp = self.data_frame.index.get_level_values('timestamp')[-1]
            if self._is_fresh(last_data_timestamp):
                logging.info(f"Returning historical data for {symbol} from DataFrame.")
                return self.data_frame.loc[symbol]

        logging.info(f"Fetching historical data for {symbol} from data provider.")
        try:
            new_data_frame = self.data_provider.get_data('bars', symbol, start=start, end=end, timeframe=timeframe)
            self.data_frame = pd.concat([self.data_frame, new_data_frame]).sort_index().reset_index().drop_duplicates().set_index(['symbol', 'timestamp'])
            return self.data_frame.loc[symbol]
        except Exception as e:
            logging.error(f"Error fetching historical data for {symbol}: {e}")
            raise

    def _is_fresh(self, timestamp):
        current_time = datetime.now()
        data_time = datetime.fromtimestamp(timestamp)

        if (current_time - data_time) < self.freshness_threshold:
            return True
        return False