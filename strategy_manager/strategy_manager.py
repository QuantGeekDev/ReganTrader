import logging
import importlib
import os
from configuration_manager.configuration_manager import ConfigurationManager
from strategy_manager.strategies.MovingAverageCrossover import MovingAverageCrossover


class StrategyManager:
    def __init__(self, config_manager: ConfigurationManager):
        self.strategy_dict = {
            'MovingAverageCrossover': MovingAverageCrossover}
        self.config_manager = config_manager
        self.strategy = None
        self.strategy_parameters = None
        self.strategy_registry = {}  # A registry of available strategies

        # Mapping from class names to filenames
        self.strategy_map = {
            'MovingAverageCrossover': 'MovingAverageCrossover'
            # Add more mappings as needed
        }

    def load_available_strategies(self):
        self.strategy_dict = {}
        strategy_folder = os.path.join(os.path.dirname(__file__), 'strategies')
        for filename in os.listdir(strategy_folder):
            if filename.endswith('.py') and filename != 'AbstractStrategy.py':
                strategy_name = filename[:-3]  # Remove .py
                strategy_module = importlib.import_module(f'.strategies.{strategy_name}', package='strategy_manager')
                self.strategy_dict[strategy_name] = getattr(strategy_module, strategy_name)
    def get_all_strategies(self):
        return list(self.strategy_dict.keys())

    def load_strategy(self, strategy_name):
        try:
            # Commenting out the line that fetches strategy parameters
            # self.strategy_parameters = self.config_manager.get_strategy_parameters(strategy_name)

            strategy_class = self.strategy_dict.get(strategy_name)
            if strategy_class is None:
                logging.error(f"Invalid strategy name: {strategy_name}")
                return None

            # Instantiate the strategy without any parameters
            self.strategy = strategy_class()
            logging.info(f"Loaded strategy {strategy_name} with default parameters: {self.strategy.__dict__}")

            self.strategy_registry[strategy_name] = strategy_class  # Add strategy to the registry
            self.set_strategy_active(strategy_name)  # Set this strategy as active
            return self.strategy
        except Exception as e:
            logging.error(f"Unhandled error loading strategy {strategy_name}: {e}")
            raise
    # def load_strategy(self, strategy_name):
    #     """
    #     Load a trading strategy by its name. The strategy parameters are fetched from the database.
    #     If no parameters are found, the strategy is instantiated with its default parameters.
    #     """
    #     try:
    #         self.strategy_parameters = self.config_manager.get_strategy_parameters(strategy_name)
    #
    #         # Get the filename corresponding to the strategy name
    #         strategy_module_name = importlib.import_module(f'.strategies.{strategy_name}', package='strategy_manager')
    #
    #         if not strategy_module_name:
    #             raise ValueError(f"Invalid strategy name: {strategy_name}")
    #
    #         # Add debug logs to track the import process
    #         logging.debug(f"Importing strategy module: {strategy_module_name}")
    #         strategy_module = importlib.import_module(f'.strategies.{strategy_module_name}', package='strategy_manager')
    #
    #         # Check if the strategy class exists in the module
    #         if not hasattr(strategy_module, strategy_name):
    #             raise AttributeError(f"Strategy class {strategy_name} not found in module {strategy_module_name}")
    #
    #         strategy_class = self.strategy_dict.get(strategy_name)
    #         if strategy_class is None:
    #             raise ValueError(f"Invalid strategy name: {strategy_name}")
    #
    #         if self.strategy_parameters:
    #             # If parameters for the strategy were found in the database, use them to instantiate the strategy
    #             try:
    #                 self.strategy = strategy_class(**self.strategy_parameters)
    #                 logging.info(f"Loaded strategy {strategy_name} with parameters {self.strategy_parameters}")
    #             except TypeError:
    #                 logging.error(
    #                     f"The parameters in the database do not match the expected parameters"
    #                     f" for the strategy {strategy_name}")
    #                 raise
    #         else:
    #             # If no parameters were found in the database, instantiate the strategy with its default parameters
    #             self.strategy = strategy_class()
    #             logging.info(f"Loaded strategy {strategy_name} with default parameters")
    #
    #         self.strategy_registry[strategy_name] = strategy_class  # Add strategy to the registry
    #         self.set_strategy_active(strategy_name)  # Set this strategy as active
    #
    #     except ImportError as e:
    #         logging.error(f"Error importing strategy {strategy_name}: {e}")
    #         raise
    #     except AttributeError as e:
    #         logging.error(f"Error loading strategy {strategy_name}: {e}")
    #         raise
    #     except Exception as e:
    #         logging.error(f"Unhandled error loading strategy {strategy_name}: {e}")
    #         raise

    def set_strategy_active(self, strategy_name):
        """
        Set a certain strategy as active.
        """
        self.config_manager.set_active_strategy(strategy_name)

    def get_active_strategy(self):
        """
        Get the currently active strategy from the database.
        """
        return self.config_manager.get_active_strategy()

    def get_strategy(self):
        """
        Return the currently loaded strategy.
        """
        if self.strategy is not None:
            return self.strategy
        else:
            logging.error("No strategy is currently loaded.")
            raise Exception("No strategy is currently loaded.")
