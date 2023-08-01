import backtrader as bt
import datetime
import yfinance as yf
import pandas

cerebro = bt.Cerebro()

df = yf.download('AAPL', start='2010-01-01')

feed = bt.feeds.PandasData(dataname=df)

cerebro.adddata(feed)

cerebro.run()
cerebro.plot()
class BacktestingEngine:
    def __init__(self):
        pass

    def run_backtest(self, strategy):
        print(f"Running backtest for strategy: {strategy}")
