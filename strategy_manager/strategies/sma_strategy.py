import pandas as pd
import numpy as np


class SmaStrategy:
    def __init__(self, short_period, long_period, historical_data_manager, trade_manager, performance_measurement):
        self.short_period = short_period
        self.long_period = long_period
        self.historical_data_manager = historical_data_manager
        self.trade_manager = trade_manager
        self.performance_measurement = performance_measurement

    def calculate_sma(self, data, window):
        """
        Calculate the Simple Moving Average (SMA) for a given data series and window.
        """
        return data.rolling(window=window).mean()

    def generate_signals(self, symbol):
        """
        Generate trading signals based on the SMA crossover strategy.
        """
        # Get historical data
        data = self.historical_data_manager.get_historical_data(symbol)

        # Calculate short and long period SMAs
        data['short_sma'] = self.calculate_sma(data['close'], self.short_period)
        data['long_sma'] = self.calculate_sma(data['close'], self.long_period)

        # Generate signals based on SMA crossover
        data['signal'] = np.where(data['short_sma'] > data['long_sma'], 1, 0)  # 1 means buy, 0 means sell

        # Identify trade points where the signal changes
        data['positions'] = data['signal'].diff()

        # Create DataFrame with only rows where positions change
        trades = data[data['positions'] != 0]

        # Vectorize trade execution
        buy_trades = trades[trades['positions'] == 1]
        sell_trades = trades[trades['positions'] == -1]

        # Note: Make sure the place_order method in the trade manager can handle multiple orders at once
        if not buy_trades.empty:
            self.trade_manager.place_order(symbol, 'buy', buy_trades.index)
        if not sell_trades.empty:
            self.trade_manager.place_order(symbol, 'sell', sell_trades.index)

        # Evaluate performance
        performance = self.performance_measurement.evaluate(data['close'], data['signal'])

        return data, performance

