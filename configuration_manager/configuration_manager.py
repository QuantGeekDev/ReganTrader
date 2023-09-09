import json
from sqlalchemy import select, insert, update, delete
from sqlalchemy.exc import SQLAlchemyError
import logging


class ConfigurationManager:
    def __init__(self, db_manager):
        self.db_manager = db_manager

    def get_connection_setting(self, key):
        """Get a connection setting from the database"""
        user_config = self.db_manager.retrieve_configuration(key, 'connection_settings')
        if user_config is not None:
            user_config = json.loads(user_config)
            if key in user_config:
                return user_config[key]
        return None

    def set_connection_setting(self, key, value):
        """Set a connection setting in the database"""
        user_config = self.get_connection_setting(key)
        if user_config is None:
            user_config = {}
        user_config[key] = value
        self.db_manager.insert_configuration(key, json.dumps(user_config), 'connection_settings')

    def get_bot_setting(self, key):
        """Get a bot setting from the database"""
        value = self.db_manager.retrieve_configuration(key, 'bot_settings')
        try:
            return json.loads(value) if value is not None else None
        except json.JSONDecodeError:
            logging.error(f'Error decoding JSON for key "{key}", value was: {value}')
            return None

    def set_bot_setting(self, key, value):
        """Set a bot setting in the database"""
        self.db_manager.insert_configuration(key, json.dumps(value), 'bot_settings')

    def get_shared_strategy_setting(self, key):
        """Get a shared strategy setting from the database"""
        value = self.db_manager.retrieve_configuration(key, 'shared_strategy_settings')
        try:
            return json.loads(value) if value is not None else None
        except json.JSONDecodeError:
            logging.error(f'Error decoding JSON for key "{key}", value was: {value}')
            return None

    def set_shared_strategy_setting(self, key, value):
        """Set a shared strategy setting in the database"""
        self.db_manager.insert_configuration(key, json.dumps(value), 'shared_strategy_settings')

    def get_strategy_parameters(self, strategy_name):
        """
        Get the parameters for a specific strategy from the database.
        """
        strategy_parameters = self.db_manager.retrieve_configuration(strategy_name, 'strategy_settings')
        if strategy_parameters:
            return json.loads(strategy_parameters)
        else:
            return None

    def set_strategy_setting(self, strategy_name, parameters):
        """
        Set the parameters for a specific strategy in the database.
        """
        self.db_manager.insert_configuration(strategy_name, json.dumps(parameters), 'strategy_settings')

    def set_active_strategy(self, strategy_name):
        logging.info(f"Setting active strategy {strategy_name}")
        self.db_manager.insert_configuration('active_strategy', strategy_name, 'user_strategies')

    def get_active_strategy(self):
        logging.info("Retrieving active strategy")
        return self.db_manager.retrieve_configuration('active_strategy', 'strategy_name')

    def store_strategy(self, strategy_name: str, is_purchased: bool, is_active: bool):
        try:
            with self.db_manager.engine.begin() as connection:
                connection.execute(insert(self.db_manager.user_strategies).values(strategy_name=strategy_name,
                                                                                  is_purchased=is_purchased,
                                                                                  is_active=is_active))
        except SQLAlchemyError as e:
            logging.error(f"Error storing strategy: {e}")
            raise

    def retrieve_strategy(self, strategy_name: str):
        logging.info(f"Retrieving strategy {strategy_name}")
        try:
            with self.db_manager.engine.begin() as connection:
                result = connection.execute(select(self.db_manager.user_strategies.c.is_purchased,
                                                   self.db_manager.user_strategies.c.is_active)
                                            .where(self.db_manager.user_strategies.c.strategy_name == strategy_name))
                row = result.fetchone()

                if row is None:
                    logging.info("Strategy not found.")
                    return None, None

                is_purchased, is_active = row

                logging.info(f"Retrieved strategy: {is_purchased}, {is_active}")
                return is_purchased, is_active
        except SQLAlchemyError as e:
            logging.error(f"Error retrieving strategy: {e}")
            raise
