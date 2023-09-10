import time
import logging
from data_provider_interface.data_provider import DataProvider
from strategy_manager.strategy_manager import StrategyManager
from trade_manager.trade_manager import TradeManager
from order_execution_engine.order_execution_engine import OrderExecutionEngine
from data_provider_interface.connectors.alpaca.alpaca_connector import AlpacaConnector
from historical_data_manager.historical_data_manager import HistoricalDataManager
from alpaca.data import TimeFrame, TimeFrameUnit

class CoreBotEngine:
    def __init__(self, config_manager, account_manager):
        self.logger = logging.getLogger(__name__)
        self.logger.setLevel(logging.INFO)
        handler = logging.StreamHandler()
        handler.setFormatter(logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s'))
        self.logger.addHandler(handler)

        try:
            self.config_manager = config_manager
            # Fetch API keys from config_manager
            api_key = self.config_manager.get_connection_setting('api_key')
            secret_key = self.config_manager.get_connection_setting('api_secret')

            self.connector = AlpacaConnector(api_key, secret_key)
            self.data_provider = DataProvider(connector=self.connector, config_manager=self.config_manager)
            self.historical_data_manager = HistoricalDataManager(self.data_provider)
            self.strategy_manager = StrategyManager(self.config_manager)
            self.trade_manager = TradeManager(config_manager, account_manager)
            self.order_execution_engine = OrderExecutionEngine(self.config_manager)
            self.is_trading = False
            self.latest_data_time = None
        except Exception as e:
            self.logger.error(f"An error occurred during initialization: {e}")
            raise e

    def start_trading(self):
        try:
            # Fetch the name of the active strategy
            active_strategy_name = self.config_manager.get_active_strategy()
            if active_strategy_name is None:
                self.logger.error("No active strategy set. Please set an active strategy before trading.")
                return

            # Load the strategy
            strategy = self.strategy_manager.load_strategy(active_strategy_name)
            if strategy is None:
                self.logger.error(f"Failed to load the strategy: {active_strategy_name}")
                return
            self.is_trading = True
            market_data = None

            while self.is_trading:
                self.logger.info(f"self.is_trading is {self.is_trading}")
                try:
                    symbol = ['BTC/USD']
                    timeframe = TimeFrame.Hour
                    # Add your logic to fetch trading_interval and data_update_interval
                    trading_interval = 60  # replace with actual value
                    data_update_interval = 300  # replace with actual value

                    if self.latest_data_time is None or time.time() - self.latest_data_time > data_update_interval:
                        market_data = self.historical_data_manager.get_historical_data(symbol, timeframe)
                        self.logger.info(f"market data is {market_data}")
                        self.latest_data_time = time.time()

                    signals = strategy.calculate_signals(market_data.tail(1))
                    self.trade_manager.process_signals(signals)
                    time.sleep(trading_interval)
                except Exception as e:
                    self.logger.error(f"An error occurred while trading: {e}")
                time.sleep(trading_interval)
        except Exception as e:
            self.logger.error(f"An error occurred while loading the strategy: {e}")
            raise e

    def stop_trading(self):
        self.is_trading = False
        self.logger.info("Trading has been stopped.")
