import logging
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
    def __init__(self, api_key, secret_key, paper=True):
        self.trading_client = TradingClient(api_key=api_key, secret_key=secret_key, paper=paper)
        self.logger = logging.getLogger(__name__)
        self.order_class_mapping = {
            OrderType.MARKET: MarketOrderRequest,
            OrderType.LIMIT: LimitOrderRequest,
            OrderType.STOP: StopOrderRequest,
            OrderType.STOP_LIMIT: StopLimitOrderRequest,
            OrderType.TRAILING_STOP: TrailingStopOrderRequest
        }

    def create_order(self, order_type, symbol, qty=None, notional=None, side=OrderSide.BUY, tif=TimeInForce.DAY,
                     extended_hours=False, client_order_id=None, order_class=None, take_profit=None,
                     stop_loss=None, limit_price=None, stop_price=None, trail_price=None, trail_percent=None):
        request_class = self.order_class_mapping.get(order_type)
        if not request_class:
            self.logger.error(f"Unsupported order type: {order_type}")
            raise ValueError("Unsupported order type")

        params = {
            'symbol': symbol,
            'side': side,
            'time_in_force': tif,
            'extended_hours': extended_hours,
        }

        optional_params = ['qty', 'notional', 'client_order_id', 'order_class', 'take_profit',
                           'stop_loss', 'limit_price', 'stop_price', 'trail_price', 'trail_percent']
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

    def close_position(self, symbol_or_asset_id, close_options: ClosePositionRequest = None):
        try:
            response = self.trading_client.close_position(symbol_or_asset_id, close_options=close_options)
            self.logger.info(f"Position for {symbol_or_asset_id} closed successfully.")
            return response
        except Exception as e:
            self.logger.error(f"Failed to close position for {symbol_or_asset_id}: {e}")
            raise
