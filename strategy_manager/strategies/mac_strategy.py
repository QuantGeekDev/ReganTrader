# mac_strategy.py

from .strategy_template import StrategyTemplate
import pandas as pd
import numpy as np


class MovingAverageCrossover(StrategyTemplate):
    def __init__(self, short_window=10, long_window=20, **kwargs):
        super().__init__(**kwargs)
        self.short_window = short_window
        self.long_window = long_window
        self.short_mavg = np.array([])
        self.long_mavg = np.array([])

    def should_buy(self, symbol, date, data):
        signals = self.calculate_signals(data.tail(1))
        return signals.loc[date, 'signal'] == 1

    def should_sell(self, symbol, date, data):
        signals = self.calculate_signals(data.tail(1))
        return signals.loc[date, 'signal'] == -1

    def calculate_signals(self, data):
        # Update the short and long moving averages
        self.short_mavg = np.append(self.short_mavg, data['close'].mean())
        self.long_mavg = np.append(self.long_mavg, data['close'].mean())
        if len(self.short_mavg) > self.short_window:
            self.short_mavg = self.short_mavg[1:]
        if len(self.long_mavg) > self.long_window:
            self.long_mavg = self.long_mavg[1:]

        # Create signals
        signals = pd.DataFrame(index=data.index)
        signals['signal'] = 0.0

        # Create signal for when short moving average crosses long moving average upwards
        signals['signal'][np.mean(self.short_mavg) > np.mean(self.long_mavg)] = 1.0

        # Create signal for when short moving average crosses long moving average downwards
        signals['signal'][np.mean(self.short_mavg) < np.mean(self.long_mavg)] = -1.0

        # Generate trading orders
        signals['orders'] = signals['signal'].diff()

        return signals
