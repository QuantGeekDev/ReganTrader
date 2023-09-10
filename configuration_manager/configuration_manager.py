from database_manager.database_manager import ConnectionSettingsManager, StrategySettingsManager, RiskSettingsManager
from sqlalchemy.exc import SQLAlchemyError
import logging

logger = logging.getLogger(__name__)


class ConfigurationManager:
    def __init__(self, db_url):
        try:
            self.conn_manager = ConnectionSettingsManager(db_url)
            self.strategy_manager = StrategySettingsManager(db_url)
            self.risk_manager = RiskSettingsManager(db_url)
            logger.info("ConfigurationManager initialized successfully.")
        except SQLAlchemyError as e:
            logger.error(f"Failed to initialize ConfigurationManager: {e}")

    # Connection Settings
    def get_connection_setting(self, key):
        try:
            conn_settings = self.conn_manager.get(filter_by={'id': 1})
            return getattr(conn_settings, key, None)
        except SQLAlchemyError as e:
            logger.error(f"Failed to get connection setting: {e}")
            return None

    def set_connection_setting(self, key, value):
        try:
            existing_setting = self.conn_manager.get(filter_by={'id': 1})
            if existing_setting is None:
                logging.info("No existing connection settings found. Creating new record.")
                self.conn_manager.add(id=1, **{key: value})
            else:
                self.conn_manager.update(filter_by={'id': 1}, **{key: value})
        except SQLAlchemyError as e:
            logging.error(f"Database error in set_connection_setting: {str(e)}")

    # Get strategy settings
    def get_strategy_setting(self, key):
        try:
            strategy_settings = self.strategy_manager.get(filter_by={'id': 1})
            return getattr(strategy_settings, key, None)
        except SQLAlchemyError as e:
            logger.error(f"Failed to get strategy setting: {e}")
            return None

    def set_strategy_setting(self, key, value):
        try:
            existing_setting = self.strategy_manager.get(filter_by={'id': 1})
            if existing_setting is None:
                logger.info("No existing strategy settings found. Creating new record.")
                self.strategy_manager.add(id=1, **{key: value})
            else:
                self.strategy_manager.update(filter_by={'id': 1}, **{key: value})
            logger.info(f"Set strategy setting {key} to {value}.")
        except SQLAlchemyError as e:
            logger.error(f"Failed to set strategy setting: {e}")


    # Strategy Management
    def get_all_strategies(self):
        return self.strategy_manager.get_all_strategies()


    def set_active_strategy(self, strategy_name):
        try:
            existing_strategy = self.strategy_manager.get(filter_by={'id': 1})
            if existing_strategy is None:
                logger.info("No existing active strategy found. Creating new record.")
                self.strategy_manager.add(id=1, strategy_name=strategy_name)
            else:
                self.strategy_manager.update(filter_by={'id': 1}, strategy_name=strategy_name)
            logger.info(f"Set active strategy to {strategy_name}.")
        except SQLAlchemyError as e:
            logger.error(f"Failed to set active strategy: {e}")

    def get_active_strategy(self):
        try:
            strategy_settings = self.strategy_manager.get(filter_by={'id': 1})
            if strategy_settings is None:
                logger.warning("No active strategy found. You may need to set one.")
                return None
            return getattr(strategy_settings, 'strategy_name', None)
        except SQLAlchemyError as e:
            logger.error(f"Failed to get active strategy: {e}")
            return None

    # Risk Settings
    def get_risk_setting(self, key):
        try:
            risk_settings = self.risk_manager.get(filter_by={'id': 1})
            return getattr(risk_settings, key, None)
        except SQLAlchemyError as e:
            logger.error(f"Failed to get risk setting: {e}")
            return None

    def set_risk_setting(self, key, value):
        try:
            self.risk_manager.update(filter_by={'id': 1}, **{key: value})
            logger.info(f"Updated risk setting {key} to {value}.")
        except SQLAlchemyError as e:
            logger.error(f"Failed to update risk setting: {e}")
