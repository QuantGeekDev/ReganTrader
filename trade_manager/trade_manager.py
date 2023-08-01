import logging
from order_execution_engine.order_execution_engine import OrderExecutionEngine

class TradeManager:
    def __init__(self, order_execution_engine, risk_manager):
        self.order_execution_engine = order_execution_engine
        self.risk_manager = risk_manager
        self.open_positions = {}  # A dictionary to track open positions

    def place_order(self, symbol, order_type, order_amount, current_price, stop_loss=None, take_profit=None):
        """
        Place an order of the given type for the given symbol.
        """
        try:
            # Check the risk associated with the trade
            if not self.risk_manager.check_risk(symbol, order_type, order_amount, current_price, stop_loss, take_profit):
                logging.warning(f"Risk check failed for {order_type} order of {order_amount} {symbol}")
                return

            # Execute the order
            self.order_execution_engine.execute_order(symbol, order_type, order_amount)

            logging.info(f"Placed {order_type} order for {order_amount} {symbol}")

            # Update open positions
            if order_type == 'buy':
                self.open_positions[symbol] = order_amount
            elif order_type == 'sell' and symbol in self.open_positions:
                self.open_positions[symbol] -= order_amount
                if self.open_positions[symbol] <= 0:
                    del self.open_positions[symbol]

        except Exception as e:
            logging.error(f"Error placing {order_type} order for {order_amount} {symbol}: {e}")
            raise

    def cancel_order(self, symbol):
        """
        Cancel any open orders for the given symbol.
        """
        try:
            self.order_execution_engine.cancel_order(symbol)
            logging.info(f"Canceled order for {symbol}")

            # Update open positions
            if symbol in self.open_positions:
                del self.open_positions[symbol]
        except Exception as e:
            logging.error(f"Error canceling order for {symbol}: {e}")
            raise
