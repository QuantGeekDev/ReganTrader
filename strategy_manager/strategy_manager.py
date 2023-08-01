import logging
import importlib

class StrategyManager:
    def __init__(self, db_manager, settings):
        self.db_manager = db_manager
        self.settings = settings
        self.strategy = None
        self.strategy_parameters = None
        self.strategy_registry = {}  # A registry of available strategies

    def load_strategy(self, strategy_name):
        """
        Load a trading strategy by its name. The strategy parameters are fetched from the database.
        """
        try:
            self.strategy_parameters = self.db_manager.get_strategy_parameters(strategy_name)
            if self.strategy_parameters:
                # Assume that the strategy is a class in a module with the same name in the strategies package
                strategy_module = importlib.import_module(f'.strategies.{strategy_name}', package='strategy_manager')
                strategy_class = getattr(strategy_module, strategy_name)
                self.strategy = strategy_class(**self.strategy_parameters)
                self.strategy_registry[strategy_name] = strategy_class  # Add strategy to the registry
                self.set_strategy_active(strategy_name)  # Set this strategy as active
                logging.info(f"Loaded strategy {strategy_name} with parameters {self.strategy_parameters}")
            else:
                logging.error(f"No parameters found for strategy {strategy_name}")
                raise Exception(f"No parameters found for strategy {strategy_name}")
        except ImportError:
            logging.error(f"Error importing strategy {strategy_name}")
            raise
        except AttributeError:
            logging.error(f"Strategy {strategy_name} not found in module")
            raise
        except Exception as e:
            logging.error(f"Error loading strategy {strategy_name}: {e}")
            raise

    def set_strategy_active(self, strategy_name):
        """
        Set a certain strategy as active.
        """
        # First set all strategies to inactive
        for name in self.strategy_registry:
            is_purchased, _ = self.db_manager.retrieve_strategy(name)
            self.db_manager.store_strategy(name, is_purchased, is_active=False)

        # Then set the desired strategy to active
        is_purchased, _ = self.db_manager.retrieve_strategy(strategy_name)
        self.db_manager.store_strategy(strategy_name, is_purchased, is_active=True)

    def get_active_strategy(self):
        """
        Get the currently active strategy from the database.
        """
        for strategy_name in self.strategy_registry:
            is_purchased, is_active = self.db_manager.retrieve_strategy(strategy_name)
            if is_active:
                return strategy_name
        logging.info("No active strategy found.")
        return None

    def get_strategy(self):
        """
        Return the currently loaded strategy.
        """
        if self.strategy is not None:
            return self.strategy
        else:
            logging.error("No strategy is currently loaded.")
            raise Exception("No strategy is currently loaded.")
