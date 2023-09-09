# AbstractStrategy.py

from abc import ABC, abstractmethod


class StrategyTemplate(ABC):
    """
    A base class for trading strategies.
    Each strategy should implement the 'should_buy', 'should_sell', and 'calculate_signals' methods.
    """

    @abstractmethod
    def __init__(self, **kwargs):
        """
        Initialize a new instance of the strategy. All strategy parameters should be passed as keyword arguments.

        :param kwargs: A dictionary of strategy parameters.
        """
        self.parameters = kwargs

    @abstractmethod
    def should_buy(self, symbol, date, data):
        """
        Determine whether we should buy a given symbol on a given date, based on the provided data.

        :param symbol: The symbol to evaluate.
        :param date: The date to evaluate.
        :param data: The historical data to use for calculations.
        :return: True if we should buy the symbol, otherwise False.
        """
        pass

    @abstractmethod
    def should_sell(self, symbol, date, data):
        """
        Determine whether we should sell a given symbol on a given date, based on the provided data.

        :param symbol: The symbol to evaluate.
        :param date: The date to evaluate.
        :param data: The historical data to use for calculations.
        :return: True if we should sell the symbol, otherwise False.
        """
        pass

    @abstractmethod
    def calculate_signals(self, data):
        """
        Calculate trading signals for the given data.

        :param data: The historical data to use for calculations.
        :return: A DataFrame with the calculated signals.
        """
        pass
