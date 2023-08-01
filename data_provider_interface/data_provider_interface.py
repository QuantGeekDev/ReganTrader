from alpaca.data import timeframe
from alpaca.data.historical.crypto import CryptoHistoricalDataClient
from alpaca.data.requests import CryptoBarsRequest, CryptoTradesRequest, CryptoLatestQuoteRequest, \
    CryptoLatestTradeRequest, CryptoLatestBarRequest, CryptoSnapshotRequest
from retry import retry
import logging



class DataProviderInterface:
    def __init__(self, api_key: str, secret_key: str):
        try:
            self.client = CryptoHistoricalDataClient(api_key, secret_key)
        except Exception as e:
            logging.error(f"Error initializing CryptoHistoricalDataClient: {e}")
            raise

    def retry_request(self, fn, *args, **kwargs):
        @retry(Exception, tries=3, delay=2)
        def wrapper():
            return fn(*args, **kwargs)

        return wrapper()

    def get_crypto_bars(self, symbol_or_symbols, start=None, end=None, limit=None, feed=None, timeframe=None):
        try:
            request_params = CryptoBarsRequest(symbol_or_symbols=symbol_or_symbols, start=start, end=end, limit=limit,
                                               timeframe=timeframe)
            return self.retry_request(self.client.get_crypto_bars, request_params)
        except Exception as e:
            logging.error(f"Error fetching historical bars for {symbol_or_symbols}: {e}")
            raise

    def get_crypto_trades(self, symbol_or_symbols, start=None, end=None, limit=None,timeframe=None, feed=None):
        try:
            request_params = CryptoTradesRequest(symbol_or_symbols=symbol_or_symbols, start=start, end=end, limit=limit,
                                                 timeframe=timeframe)
            return self.retry_request(self.client.get_crypto_trades, request_params)
        except Exception as e:
            logging.error(f"Error fetching trades for {symbol_or_symbols}: {e}")
            raise

    def get_crypto_latest_quote(self, symbol_or_symbols, feed='us'):
        try:
            request_params = CryptoLatestQuoteRequest(symbol_or_symbols=symbol_or_symbols)
            return self.retry_request(self.client.get_crypto_latest_quote, request_params)
        except Exception as e:
            logging.error(f"Error fetching latest quote for {symbol_or_symbols}: {e}")
            raise

    def get_crypto_latest_trade(self, symbol_or_symbols, feed='us'):
        try:
            request_params = CryptoLatestTradeRequest(symbol_or_symbols=symbol_or_symbols)
            return self.retry_request(self.client.get_crypto_latest_trade, request_params)
        except Exception as e:
            logging.error(f"Error fetching latest trade for {symbol_or_symbols}: {e}")
            raise

    def get_crypto_latest_bar(self, symbol_or_symbols, feed='us'):
        try:
            request_params = CryptoLatestBarRequest(symbol_or_symbols=symbol_or_symbols)
            return self.retry_request(self.client.get_crypto_latest_bar, request_params)
        except Exception as e:
            logging.error(f"Error fetching latest bar for {symbol_or_symbols}: {e}")
            raise

    def get_crypto_snapshot(self, symbol_or_symbols, feed='us'):
        try:
            request_params = CryptoSnapshotRequest(symbol_or_symbols=symbol_or_symbols)
            return self.retry_request(self.client.get_crypto_snapshot, request_params)
        except Exception as e:
            logging.error(f"Error fetching snapshot for {symbol_or_symbols}: {e}")
            raise
