import time
import logging
from database_manager.database_manager import DatabaseManager
from data_provider_interface.data_provider_interface import DataProviderInterface
from strategy_manager.strategy_manager import StrategyManager
from trade_manager.trade_manager import TradeManager
from order_execution_engine.order_execution_engine import OrderExecutionEngine
from configuration_manager.configuration_manager import ConfigurationManager
from data_provider_interface.connectors.alpaca.alpaca_connector import AlpacaConnector
from historical_data_manager.historical_data_manager import HistoricalDataManager
from alpaca.data import TimeFrame, TimeFrameUnit

class CoreBotEngine:
    def __init__(self):
        self.db_manager = DatabaseManager()
        self.config_manager = ConfigurationManager(self.db_manager)
        self.connector = AlpacaConnector

        # Initialize Data Provider Interface, Strategy Manager, and Trade Management
        self.data_provider = DataProviderInterface(self.config_manager, connector=self.connector)
        self.historical_data_manager = HistoricalDataManager(self.data_provider, self.db_manager)
        self.strategy_manager = StrategyManager(self.config_manager, self.db_manager)
        self.trade_manager = TradeManager(self.config_manager, self.db_manager)

        # Initialize OrderExecutionEngine
        self.order_execution_engine = OrderExecutionEngine(self.config_manager)

        # Flag to control the trading loop
        self.is_trading = False

        # Initialize logging
        self.logger = logging.getLogger(__name__)
        self.logger.setLevel(logging.INFO)
        handler = logging.StreamHandler()
        handler.setFormatter(logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s'))
        self.logger.addHandler(handler)

    def start_trading(self):
        # Load the trading strategy
        strategy_settings = self.config_manager.get_config("strategy")
        strategy = self.strategy_manager.load_strategy(strategy_settings)

        # Begin the trading loop
        self.is_trading = True
        while self.is_trading:
            try:
                # Define the parameters for the data request
                symbol = ['BTC/USD']  # Or any other symbol that you want to trade
                timeframe = TimeFrame.Day  # Or any other timeframe that is relevant to your strategy

                # Get the latest market data
                market_data = self.historical_data_manager.get_historical_data(symbol, timeframe)

                # Execute the trading strategy
                signals = strategy.calculate_signals(market_data)

                # Process the signals
                self.trade_manager.process_signals(signals)

                # Sleep for a while before next iteration
                time.sleep(self.config_manager.get_config('settings')['trading_interval'])
            except Exception as e:
                self.logger.error(f"An error occurred while trading: {e}")
                self.stop_trading()

    def stop_trading(self):
        self.is_trading = False
        self.logger.info("Trading has been stopped.")

    def update_settings(self, new_settings):
        self.config_manager.set_config("settings", new_settings)
