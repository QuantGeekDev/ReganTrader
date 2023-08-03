import logging
from threading import Thread
import time
from alpaca.trading.client import TradingClient
from alpaca.trading.requests import (
    LimitOrderRequest,
    StopOrderRequest,
    MarketOrderRequest,
    StopLimitOrderRequest,
    TrailingStopOrderRequest,
    ClosePositionRequest
)
from alpaca.trading.enums import OrderType, OrderSide, TimeInForce


class OrderExecutionEngine:
    def __init__(self, config_manager):
        user_config = config_manager.get_config('user_config')

        api_key = user_config.get('api_key')
        secret_key = user_config.get('api_secret')
        paper = user_config.get('paper')

        # Log the values before initializing the TradingClient
        self.logger = logging.getLogger(__name__)
        self.logger.info(f"Initializing TradingClient with api_key: {api_key}, secret_key: {secret_key}, paper: {paper}")

        self.trading_client = TradingClient(api_key=api_key,
                                            secret_key=secret_key,
                                            paper=paper)
        self.config_manager = config_manager
        self.extended_hours = config_manager.get_config('extended_hours')
        self.tif = config_manager.get_config('time_in_force')
        self.logger = logging.getLogger(__name__)
        self.order_class_mapping = {
            OrderType.MARKET: MarketOrderRequest,
            OrderType.LIMIT: LimitOrderRequest,
            OrderType.STOP: StopOrderRequest,
            OrderType.STOP_LIMIT: StopLimitOrderRequest,
            OrderType.TRAILING_STOP: TrailingStopOrderRequest
        }

    def create_order(self, order_type, symbol, qty=None, notional=None, side=OrderSide.BUY, client_order_id=None,
                     order_class=None, take_profit=None, stop_loss=None, limit_price=None, stop_price=None):

        request_class = self.order_class_mapping.get(order_type)
        if not request_class:
            self.logger.error(f"Unsupported order type: {order_type}")
            raise ValueError("Unsupported order type")

        params = {
            'symbol': symbol,
            'side': side,
            'time_in_force': self.tif,  # get from instance variable
            'extended_hours': self.extended_hours,  # get from instance variable
        }

        optional_params = ['qty', 'notional', 'client_order_id', 'order_class', 'take_profit',
                           'stop_loss', 'limit_price', 'stop_price']
        for param_name in optional_params:
            param_value = locals().get(param_name)
            if param_value is not None:
                params[param_name] = param_value

        order_data = request_class(**params)

        try:
            response = self.trading_client.submit_order(order_data=order_data)
            self.logger.info(f"Order submitted successfully: {response}")
            return response
        except Exception as e:
            self.logger.error(f"Order submission failed: {e}")
            raise

    def cancel_orders(self):
        try:
            response = self.trading_client.cancel_orders()
            self.logger.info("All orders cancelled successfully.")
            return response
        except Exception as e:
            self.logger.error(f"Failed to cancel orders: {e}")
            raise

    def close_all_positions(self, cancel_orders=True):
        try:
            response = self.trading_client.close_all_positions(cancel_orders=cancel_orders)
            self.logger.info("All positions closed successfully.")
            return response
        except Exception as e:
            self.logger.error(f"Failed to close all positions: {e}")
            raise

    def get_positions(self):
        """Get all the current open positions."""
        try:
            positions = self.trading_client.get_all_positions()
            self.logger.info("Fetched all open positions successfully.")
            return positions
        except Exception as e:
            self.logger.error(f"Failed to fetch all open positions: {e}")
            raise

    def get_open_position_by_id(self, symbol_or_asset_id):
        """Get the open position for a single asset."""
        try:
            position = self.trading_client.get_open_position(symbol_or_asset_id)
            self.logger.info(f"Fetched open position for {symbol_or_asset_id} successfully.")
            return position
        except Exception as e:
            self.logger.error(f"Failed to fetch open position for {symbol_or_asset_id}: {e}")
            raise

    def get_orders(self, filter=None):
        """Get all orders."""
        try:
            orders = self.trading_client.get_orders(filter)
            self.logger.info("Fetched all orders successfully.")
            return orders
        except Exception as e:
            self.logger.error(f"Failed to fetch all orders: {e}")
            raise

    def get_order_by_id(self, order_id, filter=None):
        """Get a specific order by its ID."""
        try:
            order = self.trading_client.get_order_by_id(order_id, filter)
            self.logger.info(f"Fetched order {order_id} successfully.")
            return order
        except Exception as e:
            self.logger.error(f"Failed to fetch order {order_id}: {e}")
            raise

    def cancel_order_by_id(self, order_id):
        """Cancel a specific order by its ID."""
        try:
            self.trading_client.cancel_order_by_id(order_id)
            self.logger.info(f"Cancelled order {order_id} successfully.")
        except Exception as e:
            self.logger.error(f"Failed to cancel order {order_id}: {e}")
            raise

    def replace_order_by_id(self, order_id, order_data=None):
        """Replace a specific order by its ID."""
        try:
            updated_order = self.trading_client.replace_order_by_id(order_id, order_data)
            self.logger.info(f"Replaced order {order_id} successfully.")
            return updated_order
        except Exception as e:
            self.logger.error(f"Failed to replace order {order_id}: {e}")
            raise

    def close_position(self, symbol_or_asset_id, close_options=None):
        """Close the position for a single asset."""
        try:
            closed_order = self.trading_client.close_position(symbol_or_asset_id, close_options)
            self.logger.info(f"Closed position for {symbol_or_asset_id} successfully.")
            return closed_order
        except Exception as e:
            self.logger.error(f"Failed to close position for {symbol_or_asset_id}: {e}")
            raise
