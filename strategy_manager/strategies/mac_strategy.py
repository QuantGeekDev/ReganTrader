from .strategy_template import StrategyTemplate

class MovingAverageCrossover(StrategyTemplate):
    def __init__(self, short_window=10, long_window=20):
        super().__init__(short_window=short_window, long_window=long_window)
        self.short_window = short_window
        self.long_window = long_window

    def should_buy(self, symbol, date, data):
        # implement logic here
        pass

    def should_sell(self, symbol, date, data):
        # implement logic here
        pass

    def calculate_signals(self, data):
        # implement logic here
        pass
