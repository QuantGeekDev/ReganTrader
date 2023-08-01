# account_manager.py

import logging
from typing import List
from alpaca.trading.client import TradingClient
from alpaca.trading.requests import GetOrdersRequest
from alpaca.trading.enums import QueryOrderStatus
from alpaca.trading.models import Order, Position


class AccountManager:

    def __init__(self, api_key: str, secret_key: str, paper: bool = True):
        self.trading_client = TradingClient(api_key=api_key, secret_key=secret_key, paper=paper)

    def get_orders(self, status: QueryOrderStatus = QueryOrderStatus.OPEN) -> List[Order]:
        try:
            request_params = GetOrdersRequest(status=status)
            return self.trading_client.get_orders(filter=request_params)
        except Exception as e:
            logging.error(f"Error retrieving orders: {e}")
            return []

    def get_all_positions(self) -> List[Position]:
        try:
            return self.trading_client.get_all_positions()
        except Exception as e:
            logging.error(f"Error retrieving positions: {e}")
            return []

    def get_order_by_id(self, order_id: str) -> Order:
        try:
            return self.trading_client.get_order_by_id(order_id)
        except Exception as e:
            logging.error(f"Error retrieving order with ID {order_id}: {e}")
            return None

    def get_position_by_symbol(self, symbol: str) -> Position:
        try:
            return self.trading_client.get_open_position(symbol)
        except Exception as e:
            logging.error(f"Error retrieving position for symbol {symbol}: {e}")
            return None
