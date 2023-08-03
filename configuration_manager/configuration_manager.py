import json


class ConfigurationManager:
    def __init__(self, db_manager):
        self.db_manager = db_manager

    def get_config(self, key):
        """Get a configuration value from the database"""
        if key in ['api_key', 'api_secret', 'paper']:
            user_config = self.db_manager.retrieve_configuration('user_config')
            if user_config is not None:
                user_config = json.loads(user_config)
                if key in user_config:
                    return user_config[key]
            return None
        value = self.db_manager.retrieve_configuration(key)
        return json.loads(value) if value is not None else None

    def set_config(self, key, value):
        """Set a configuration value in the database"""
        if key in ['api_key', 'api_secret', 'paper']:
            user_config = self.get_config('user_config')
            if user_config is None:
                user_config = {}
            user_config[key] = value
            self.db_manager.insert_configuration('user_config', json.dumps(user_config))
        else:
            self.db_manager.insert_configuration(key, json.dumps(value))

    def get_strategy_parameters(self, strategy_name):
        """
        Get the parameters for a specific strategy from the database.
        """
        strategy_parameters = self.db_manager.get_config(strategy_name)
        if strategy_parameters:
            return json.loads(strategy_parameters)
        else:
            return None
