import logging
from sqlalchemy.exc import SQLAlchemyError
from database_manager.database_manager import DatabaseManager, ConnectionSettings, BotSettings, SharedStrategySettings, UserStrategies, \
    StrategySettings

logging.basicConfig(level=logging.DEBUG)


class ConfigurationManager:
    def __init__(self, db_manager: DatabaseManager):
        self.db_manager = db_manager

    def _get_setting(self, key, table_class):
        try:
            return self.db_manager.get_record(table_class, key)
        except SQLAlchemyError as e:
            logging.error(f"Error retrieving setting {key} from {table_class.__tablename__}: {e}")
            raise

    def _set_setting(self, key, value, table_class):
        try:
            self.db_manager.insert_or_update_record(table_class, key, value)
        except SQLAlchemyError as e:
            logging.error(f"Error setting {key} in {table_class.__tablename__}: {e}")
            raise

    def get_connection_setting(self, key):
        return self._get_setting(key, ConnectionSettings)

    def set_connection_setting(self, key, value):
        self._set_setting(key, value, ConnectionSettings)

    def get_bot_setting(self, key):
        return self._get_setting(key, BotSettings)

    def set_bot_setting(self, key, value):
        self._set_setting(key, value, BotSettings)

    def get_shared_strategy_setting(self, key):
        return self._get_setting(key, SharedStrategySettings)

    def set_shared_strategy_setting(self, key, value):
        self._set_setting(key, value, SharedStrategySettings)

    def get_strategy_parameters(self, strategy_name):
        return self._get_setting(strategy_name, StrategySettings)

    def set_strategy_parameters(self, strategy_name, parameters):
        self._set_setting(strategy_name, parameters, StrategySettings)

    def set_active_strategy(self, strategy_name):
        self._set_setting('active_strategy', strategy_name, UserStrategies)

    def get_active_strategy(self):
        return self._get_setting('active_strategy', UserStrategies)

    def store_strategy(self, strategy_name: str, is_purchased: bool, is_active: bool):
        self._set_setting(strategy_name, {'is_purchased': is_purchased, 'is_active': is_active}, UserStrategies)

    def retrieve_strategy(self, strategy_name: str):
        strategy_data = self._get_setting(strategy_name, UserStrategies)
        if strategy_data:
            return strategy_data.get('is_purchased'), strategy_data.get('is_active')
        return None, None

# Uncomment the following lines to test the class.
db_manager = DatabaseManager()
config_manager = ConfigurationManager(db_manager)
config_manager.set_connection_setting('api_key', 'testingthisshit')
print(config_manager.get_connection_setting('api_key'))
print(config_manager.get_connection_setting('api_secret'))