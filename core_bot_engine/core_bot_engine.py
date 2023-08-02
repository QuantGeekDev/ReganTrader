import time
import logging
from database_manager.database_manager import DatabaseManager
from data_provider_interface.data_provider import DataProvider  # Change this line
from strategy_manager.strategy_manager import StrategyManager
from trade_manager.trade_manager import TradeManager
from order_execution_engine.order_execution_engine import OrderExecutionEngine
from data_provider_interface.connectors.alpaca.alpaca_connector import AlpacaConnector
from historical_data_manager.historical_data_manager import HistoricalDataManager
from alpaca.data import TimeFrame, TimeFrameUnit


class CoreBotEngine:
    def __init__(self, config_manager):
        self.logger = logging.getLogger(__name__)  # Move logger initialization here
        self.logger.setLevel(logging.INFO)
        handler = logging.StreamHandler()
        handler.setFormatter(logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s'))
        self.logger.addHandler(handler)
        try:
            self.db_manager = DatabaseManager()
            self.config_manager = config_manager
            self.connector = AlpacaConnector
            self.data_provider = DataProvider(connector=self.connector, config_manager=self.config_manager)  # Change this line
            self.historical_data_manager = HistoricalDataManager(self.data_provider, self.db_manager)
            self.strategy_manager = StrategyManager(self.config_manager, self.db_manager)
            self.trade_manager = TradeManager(self.config_manager, self.db_manager)
            self.order_execution_engine = OrderExecutionEngine(self.config_manager)
            self.is_trading = False
            self.latest_data_time = None  # Initialize the latest_data_time variable
        except Exception as e:
            self.logger.error(f"An error occurred during initialization: {e}")
            raise e

    def start_trading(self):
        try:
            active_strategy = self.config_manager.get_config("strategy")
            strategy = self.strategy_manager.load_strategy(active_strategy)
            self.is_trading = True
            market_data = None  # Initialize market_data variable
            while self.is_trading:
                try:
                    symbol = ['BTC/USD']
                    timeframe = TimeFrame.Day
                    # Check if market data needs to be updated
                    if self.latest_data_time is None or time.time() - self.latest_data_time > self.config_manager.get_config('settings')['data_update_interval']:
                        # Get the latest market data
                        market_data = self.historical_data_manager.get_historical_data(symbol, timeframe)
                        self.latest_data_time = time.time()

                    # Execute the trading strategy only for the new data
                    signals = strategy.calculate_signals(market_data.tail(1))

                    # Process the signals
                    self.trade_manager.process_signals(signals)

                    time.sleep(self.config_manager.get_config('settings')['trading_interval'])
                except Exception as e:
                    self.logger.error(f"An error occurred while trading: {e}")
                    self.stop_trading()
        except Exception as e:
            self.logger.error(f"An error occurred while loading the strategy: {e}")
            raise e

    def stop_trading(self):
        self.is_trading = False
        self.logger.info("Trading has been stopped.")

    def update_settings(self, new_settings):
        try:
            self.config_manager.set_config("settings", new_settings)
        except Exception as e:
            self.logger.error(f"An error occurred while updating settings: {e}")
            raise e
