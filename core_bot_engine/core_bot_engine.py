
import time
import logging
from database_manager.database_manager import DatabaseManager
from data_provider_interface.data_provider_interface import DataProviderInterface
from strategy_manager.strategy_manager import StrategyManager
from trade_manager.trade_manager import TradeManager

class CoreBotEngine:
    def __init__(self):
        # Initialize the Database Management and get the last saved settings
        self.db_manager = DatabaseManager()
        self.settings = self.db_manager.get_settings()

        # Initialize Data Provider Interface, Strategy Manager, and Trade Management
        self.data_provider = DataProviderInterface(self.settings)
        self.strategy_manager = StrategyManager(self.settings, self.db_manager)
        self.trade_management = TradeManager(self.settings, self.db_manager)

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
        strategy = self.strategy_manager.load_strategy()

        # Start the data provider
        self.data_provider.start()

        # Begin the trading loop
        self.is_trading = True
        while self.is_trading:
            try:
                # Get the latest market data
                market_data = self.data_provider.get_data()

                # Execute the trading strategy
                signals = strategy.execute(market_data)

                # Process the signals
                self.trade_management.process_signals(signals)

                # Sleep for a while before next iteration
                time.sleep(self.settings['trading_interval'])
            except Exception as e:
                self.logger.error(f"An error occurred while trading: {e}")
                self.stop_trading()

    def stop_trading(self):
        self.is_trading = False
        self.data_provider.stop()
        self.logger.info("Trading has been stopped.")

    def update_settings(self, new_settings):
        self.settings = new_settings
        self.db_manager.save_settings(new_settings)
        self.logger.info("Settings have been updated.")
