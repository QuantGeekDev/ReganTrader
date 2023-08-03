import logging
import importlib
import os
from configuration_manager.configuration_manager import ConfigurationManager
from database_manager.database_manager import DatabaseManager
from strategy_manager.strategies.MovingAverageCrossover import MovingAverageCrossover

class StrategyManager:
    def __init__(self, config_manager:ConfigurationManager, db_manager:DatabaseManager):
        self.strategy_dict = {
            'MovingAverageCrossover': MovingAverageCrossover}
        self.config_manager = config_manager
        self.db_manager = db_manager
        self.strategy = None
        self.strategy_parameters = None
        self.strategy_registry = {}  # A registry of available strategies

        # Mapping from class names to filenames
        self.strategy_map = {
            'MovingAverageCrossover': 'MovingAverageCrossover'
            # Add more mappings as needed
        }

    def get_all_strategies(self):
        strategies_folder = os.path.join(os.path.dirname(__file__), "strategies")
        return [file[:-3] for file in os.listdir(strategies_folder) if file.endswith('.py') and file != "__init__.py"]

    def load_strategy(self, strategy_name):
        """
        Load a trading strategy by its name. The strategy parameters are fetched from the database.
        If no parameters are found, the strategy is instantiated with its default parameters.
        """
        try:
            self.strategy_parameters = self.config_manager.get_config(strategy_name)

            # Get the filename corresponding to the strategy name
            strategy_module_name = self.strategy_map.get(strategy_name)

            if not strategy_module_name:
                raise ValueError("Invalid strategy name")

            strategy_module = importlib.import_module(f'.strategies.{strategy_module_name}', package='strategy_manager')
            print(dir(strategy_module))  # Print all attributes of the strategy module
            strategy_class = getattr(strategy_module, strategy_name)

            if self.strategy_parameters:
                # If parameters for the strategy were found in the database, use them to instantiate the strategy
                self.strategy = strategy_class(**self.strategy_parameters)
                logging.info(f"Loaded strategy {strategy_name} with parameters {self.strategy_parameters}")
            else:
                # If no parameters were found in the database, instantiate the strategy with its default parameters
                self.strategy = strategy_class()
                logging.info(f"Loaded strategy {strategy_name} with default parameters")

            self.strategy_registry[strategy_name] = strategy_class  # Add strategy to the registry
            self.set_strategy_active(strategy_name)  # Set this strategy as active

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
