import json


class ConfigurationManager:
    def __init__(self, db_manager):
        self.db_manager = db_manager

    def get_config(self, key):
        """Get a configuration value from the database"""
        value = self.db_manager.retrieve_configuration(key)
        return json.loads(value) if value is not None else None

    # get_bot_config, get_strategy_parameters, etc. can be refactored to use get_config

    def set_config(self, key, value):
        """Set a configuration value in the database"""
        self.db_manager.insert_configuration(key, json.dumps(value))
