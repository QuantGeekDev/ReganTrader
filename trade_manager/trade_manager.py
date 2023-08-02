import logging
from order_execution_engine.order_execution_engine import OrderExecutionEngine
from risk_manager.risk_manager import RiskManager
from alpaca.trading.enums import OrderType, OrderSide, TimeInForce


class TradeManager:
    def __init__(self, config_manager, db_manager):
        self.order_execution_engine = OrderExecutionEngine(config_manager)
        self.db_manager = db_manager
        self.risk_manager = RiskManager(config_manager, db_manager)
        self.open_positions = {}  # A dictionary to track open positions
        self.open_orders = {}  # A dictionary to track open orders
        # Initialize logging
        self.logger = logging.getLogger(__name__)
        self.logger.setLevel(logging.INFO)
        handler = logging.StreamHandler()
        handler.setFormatter(logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s'))
        self.logger.addHandler(handler)

    def process_signals(self, signals):
        for signal in signals:
            try:
                if self.risk_manager.check_order_risk(signal):  # Check the risk for each signal
                    # Unpacking the signal into the order parameters
                    order_type = signal.get('order_type')
                    symbol = signal.get('symbol')
                    qty = signal.get('qty')
                    notional = signal.get('notional')
                    side = signal.get('side', OrderSide.BUY)  # default to BUY if not provided
                    tif = signal.get('tif', TimeInForce.DAY)  # default to DAY if not provided
                    extended_hours = signal.get('extended_hours', False)  # default to False if not provided
                    client_order_id = signal.get('client_order_id')
                    order_class = signal.get('order_class')
                    take_profit = signal.get('take_profit')
                    stop_loss = signal.get('stop_loss')
                    limit_price = signal.get('limit_price')
                    stop_price = signal.get('stop_price')

                    self.order_execution_engine.create_order(order_type, symbol, qty, notional, side, tif,
                                                             extended_hours,
                                                             client_order_id,
                                                             order_class, take_profit, stop_loss, limit_price,
                                                             stop_price)
            except Exception as e:
                self.logger.error(f"Failed to process signal: {signal}. Exception: {str(e)}")

    def check_market_risk(self):
        """
        Check market risk and rebalance if necessary.
        This could be called periodically.
        """
        if self.risk_manager.check_market_risk():
            self.rebalance_portfolio()

    def rebalance_portfolio(self):
        """
        Rebalance the portfolio based on the risk parameters.
        """
        pass  # TODO: Implement the rebalancing logic here

    def cancel_all_orders(self):
        try:
            self.order_execution_engine.cancel_orders()
            logging.info(f"Canceled all orders.")
            self.open_positions = {}
        except Exception as e:
            logging.error(f"Error canceling all orders: {e}")

    def close_all_positions(self):
        try:
            self.order_execution_engine.close_all_positions()
            logging.info(f"Closed all positions.")
            self.open_positions = {}
        except Exception as e:
            logging.error(f"Error closing all positions: {e}")

    def update_open_positions(self):
        """Updates the open positions using the AccountManager instance."""
        positions = self.order_execution_engine.get_positions()
        self.open_positions = {pos['symbol']: pos['qty'] for pos in positions}

    def update_open_orders(self):
        """Updates the open orders using the OrderExecutionEngine instance."""
        orders = self.order_execution_engine.get_orders()
        self.open_orders = {order.id: order for order in orders if order.status == 'open'}

    def check_order_status(self):
        """Checks the status of open orders and removes them from the open_orders list if they've been filled."""
        filled_orders = []
        for order_id, order in self.open_orders.items():
            updated_order = self.order_execution_engine.get_order_by_id(order_id)
            if updated_order.status == 'filled':
                filled_orders.append(order_id)
                self.logger.info(f"Order {order_id} for symbol {order.symbol} has been filled.")

        for order_id in filled_orders:
            del self.open_orders[order_id]
