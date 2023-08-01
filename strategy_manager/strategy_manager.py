import logging
import importlib

class StrategyManager:
    def __init__(self, db_manager):
        self.db_manager = db_manager
        self.strategy = None
        self.strategy_parameters = None

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

    def get_strategy(self):
        """
        Return the currently loaded strategy.
        """
        if self.strategy is not None:
            return self.strategy
        else:
            logging.error("No strategy is currently loaded.")
            raise Exception("No strategy is currently loaded.")
