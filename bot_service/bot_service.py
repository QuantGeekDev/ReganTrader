from database_manager.database_manager import DatabaseManager
from configuration_manager.configuration_manager import ConfigurationManager
from core_bot_engine.core_bot_engine import CoreBotEngine
from strategy_manager.strategy_manager import StrategyManager
from account_manager.account_manager import AccountManager


class BotService:
    def __init__(self):
        self.db_manager = DatabaseManager()
        self.config_manager = ConfigurationManager(self.db_manager)
        self.account_manager = AccountManager(api_key=self.config_manager.get_config('api_key'),
                                              secret_key=self.config_manager.get_config('api_secret'),
                                              paper=self.config_manager.get_config('paper'))
        self.strategy_manager = StrategyManager(self.config_manager)
        self.bot = None

    def start_bot(self):
        if self.bot is None:
            self.bot = CoreBotEngine(self.config_manager, self.account_manager)
        self.bot.start_trading()

    def stop_bot(self):
        if self.bot is not None:
            self.bot.stop_trading()
            self.bot = None

    def get_settings(self):
        return self.config_manager.get_config('user_config')

    def update_settings(self, new_settings):
        self.config_manager.set_config('user_config', new_settings)

    def get_all_strategies(self):
        return self.strategy_manager.get_all_strategies()

    def set_active_strategy(self, strategy_name):
        self.config_manager.set_active_strategy(strategy_name)

    def get_active_strategy(self):
        return self.config_manager.get_active_strategy()
