from configuration_manager.configuration_manager import ConfigurationManager
from core_bot_engine.core_bot_engine import CoreBotEngine
from strategy_manager.strategy_manager import StrategyManager
from account_manager.account_manager import AccountManager
import logging

# Get logger instance
logger = logging.getLogger(__name__)

class BotService:
    def __init__(self, db_url):
        try:
            self.config_manager = ConfigurationManager(db_url)
            self.account_manager = AccountManager(
                api_key=self.config_manager.get_connection_setting('api_key'),
                secret_key=self.config_manager.get_connection_setting('api_secret'),
                paper=self.config_manager.get_connection_setting('paper')
            )
            self.strategy_manager = StrategyManager(self.config_manager)
            self.bot = None
            logger.info("BotService initialized successfully.")
        except Exception as e:
            logger.error(f"Failed to initialize BotService: {e}")

    def start_bot(self):
        if self.bot is None:
            self.bot = CoreBotEngine(self.config_manager, self.account_manager)
        self.bot.start_trading()

    def stop_bot(self):
        if self.bot is not None:
            self.bot.stop_trading()
            self.bot = None

    def get_connection_setting(self, key):
        return self.config_manager.get_connection_setting(key)

    def set_connection_setting(self, key, value):
        self.config_manager.set_connection_setting(key, value)

    def get_bot_setting(self, key):
        return self.config_manager.get_bot_setting(key)

    def set_bot_setting(self, key, value):
        self.config_manager.set_bot_setting(key, value)


    def get_all_strategies(self):
        strategies = self.strategy_manager.get_all_strategies()
        if strategies is None:
            logger.error("No strategies are available.")
            return []
        return strategies

    def set_active_strategy(self, strategy_name):
        self.config_manager.set_active_strategy(strategy_name)

    def get_active_strategy(self):
        return self.config_manager.get_active_strategy()
