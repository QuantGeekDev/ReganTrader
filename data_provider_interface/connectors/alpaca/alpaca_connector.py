import pandas as pd
import logging
from alpaca.data import timeframe
from alpaca.data.historical.crypto import CryptoHistoricalDataClient
from alpaca.data.requests import (CryptoBarsRequest, CryptoTradesRequest,
                                  CryptoLatestQuoteRequest, CryptoLatestTradeRequest,
                                  CryptoLatestBarRequest, CryptoSnapshotRequest,
                                  CryptoLatestOrderbookRequest)
from ..data_connector import DataConnector

class AlpacaConnector(DataConnector):

    def __init__(self, api_key: str, secret_key: str):
        try:
            self.client = CryptoHistoricalDataClient(api_key, secret_key)
            logging.info('Alpaca - CryptoHistoricalDataClient Initialized')
        except Exception as e:
            logging.error(f"Error initializing CryptoHistoricalDataClient: {e}")
            raise

    def to_dataframe(self, data, symbol):
        # Assuming data is a list of objects that can be converted to dictionary
        df = pd.DataFrame([item.__dict__ for item in data])
        df['symbol'] = symbol
        df.set_index(['symbol', 'timestamp'], inplace=True)
        return df

    def get_data(self, method, symbol_or_symbols, start=None, end=None, limit=None, feed=None, timeframe=None):
        data = None
        request_params = {
            'symbol_or_symbols': symbol_or_symbols,
            'start': start,
            'end': end,
            'limit': limit,
            'timeframe': timeframe
        }
        try:
            if method == 'bars':
                data = self.client.get_crypto_bars(CryptoBarsRequest(**request_params))
            elif method == 'trades':
                data = self.client.get_crypto_trades(CryptoTradesRequest(**request_params))
            elif method == 'latest_quote':
                data = self.client.get_crypto_latest_quote(CryptoLatestQuoteRequest(symbol_or_symbols=symbol_or_symbols))
            elif method == 'latest_trade':
                data = self.client.get_crypto_latest_trade(CryptoLatestTradeRequest(symbol_or_symbols=symbol_or_symbols))
            elif method == 'latest_bar':
                data = self.client.get_crypto_latest_bar(CryptoLatestBarRequest(symbol_or_symbols=symbol_or_symbols))
            elif method == 'snapshot':
                data = self.client.get_crypto_snapshot(CryptoSnapshotRequest(symbol_or_symbols=symbol_or_symbols))
            elif method == 'latest_orderbook':
                data = self.client.get_crypto_latest_orderbook(CryptoLatestOrderbookRequest(symbol_or_symbols=symbol_or_symbols))

            if data:
                # Assume that data is a BarSet object and access its 'data' attribute
                barset_data = data.data if hasattr(data, 'data') else data
                return pd.concat([self.to_dataframe(data_chunk, symbol) for symbol, data_chunk in barset_data.items()])
            else:
                return None
        except Exception as e:
            logging.error(f"Error fetching data using method {method}: {e}")
            raise
