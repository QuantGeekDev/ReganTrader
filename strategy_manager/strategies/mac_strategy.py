# mac_strategy.py

from .strategy_template import StrategyTemplate
import pandas as pd

class MovingAverageCrossover(StrategyTemplate):
    def __init__(self, short_window=10, long_window=20, **kwargs):
        super().__init__(**kwargs)
        self.short_window = short_window
        self.long_window = long_window

    def should_buy(self, symbol, date, data):
        # Use data directly here, remove fetching of historical data
        # You can modify this part based on how your data looks like
        signals = self.calculate_signals(data)
        return signals.loc[date, 'signal'] == 1

    def should_sell(self, symbol, date, data):
        # Use data directly here, remove fetching of historical data
        # You can modify this part based on how your data looks like
        signals = self.calculate_signals(data)
        return signals.loc[date, 'signal'] == -1

    def calculate_signals(self, data):
        # Generate the short and long moving averages
        short_mavg = data['close'].rolling(window=self.short_window, min_periods=1, close='right').mean()
        long_mavg = data['close'].rolling(window=self.long_window, min_periods=1, close='right').mean()

        # Create signals
        signals = pd.DataFrame(index=data.index)
        signals['signal'] = 0.0

        # Create signal for when short moving average crosses long moving average upwards
        signals['signal'][short_mavg > long_mavg] = 1.0

        # Create signal for when short moving average crosses long moving average downwards
        signals['signal'][short_mavg < long_mavg] = -1.0

        # Generate trading orders
        signals['orders'] = signals['signal'].diff()

        return signals
