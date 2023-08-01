from alpaca.data import timeframe
from alpaca.data.historical.crypto import CryptoHistoricalDataClient
from alpaca.data.requests import (CryptoBarsRequest, CryptoTradesRequest,
                                  CryptoLatestQuoteRequest, CryptoLatestTradeRequest,
                                  CryptoLatestBarRequest, CryptoSnapshotRequest,
                                  CryptoLatestOrderbookRequest)
import logging
from ..data_connector import DataConnector


class AlpacaConnector(DataConnector):
    def __init__(self, api_key: str, secret_key: str):
        try:
            self.client = CryptoHistoricalDataClient(api_key, secret_key)
        except Exception as e:
            logging.error(f"Error initializing CryptoHistoricalDataClient: {e}")
            raise

    def get_data(self, method, symbol_or_symbols, start=None, end=None, limit=None, feed=None, timeframe=None):
        if method == 'bars':
            request_params = CryptoBarsRequest(symbol_or_symbols=symbol_or_symbols, start=start, end=end, limit=limit,
                                               timeframe=timeframe)
            return self.client.get_crypto_bars(request_params)
        elif method == 'trades':
            request_params = CryptoTradesRequest(symbol_or_symbols=symbol_or_symbols, start=start, end=end, limit=limit,
                                                 timeframe=timeframe)
            return self.client.get_crypto_trades(request_params)
        elif method == 'latest_quote':
            request_params = CryptoLatestQuoteRequest(symbol_or_symbols=symbol_or_symbols)
            return self.client.get_crypto_latest_quote(request_params)
        elif method == 'latest_trade':
            request_params = CryptoLatestTradeRequest(symbol_or_symbols=symbol_or_symbols)
            return self.client.get_crypto_latest_trade(request_params)
        elif method == 'latest_bar':
            request_params = CryptoLatestBarRequest(symbol_or_symbols=symbol_or_symbols)
            return self.client.get_crypto_latest_bar(request_params)
        elif method == 'snapshot':
            request_params = CryptoSnapshotRequest(symbol_or_symbols=symbol_or_symbols)
            return self.client.get_crypto_snapshot(request_params)
        elif method == 'latest_orderbook':
            request_params = CryptoLatestOrderbookRequest(symbol_or_symbols=symbol_or_symbols)
            return self.client.get_crypto_latest_orderbook(request_params)
