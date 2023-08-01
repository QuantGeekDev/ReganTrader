from core_bot_engine.core_bot_engine import CoreBotEngine
from strategy_manager.strategy_manager import StrategyManager
from order_execution_engine.order_execution_engine import OrderExecutionEngine
from data_provider_interface.data_provider_interface import DataProviderInterface
from historical_data_manager.historical_data_manager import HistoricalDataManager
from ui_server.ui_server import app as ui_app
from notification_manager.notification_manager import NotificationManager
from trade_manager.trade_manager import TradeManager
from risk_manager.risk_manager import RiskManager
from database_manager.database_manager import db_manager
from logger_manager.logger_manager import LoggerManager
from backtesting_engine.backtesting_engine import BacktestingEngine
from performance_measurement.performance_measurement import PerformanceMeasurement
from bot_test_suite.bot_test_suite import BotTestSuite
from alpaca.data.timeframe import TimeFrame, TimeFrameUnit

# Remove API KEYs from Prod
API_KEY = "PKGUF4JBS4CNZDCNDLP8"
SECRET_KEY = "9DgYQ5rU1pmz4Bqgjb0acGzq6hOPGi8fBc44gL1m"

timeframe = TimeFrame.Hour
db_manager = db_manager


def main():
    # Create instances of each module
    # core_bot_engine = CoreBotEngine()
    # strategy_manager = StrategyManager()
    # order_execution_engine = OrderExecutionEngine()
    data_provider = DataProviderInterface(api_key=API_KEY, secret_key=SECRET_KEY)
    historical_data_manager = HistoricalDataManager(data_provider=data_provider, db_manager=db_manager)

    # ui_server = UIServer()
    # notification_manager = NotificationManager()
    # trade_manager = TradeManager()
    # risk_manager = RiskManager()
    # logger_component = LoggerManager()
    # backtesting_engine = BacktestingEngine()
    # performance_measurement = PerformanceMeasurement()

    # Call a method from each instance to confirm it works
    # core_bot_engine.start()
    # strategy_manager.load_strategy('Dummy Strategy')
    # order_execution_engine.place_order('Dummy Order')
    # historical_data_manager.get_historical_data('Dummy Data Request')
    # ui_server.start()
    # notification_manager.send_notification('Dummy Notification')
    # trade_manager.execute_trade('Dummy Trade')
    # risk_manager.evaluate_risk('Dummy Trade')
    # database_manager.save_data('Dummy Data')
    # logger_component.log('Dummy Message')
    # backtesting_engine.run_backtest('Dummy Strategy')
    # performance_measurement.measure_performance('Dummy Trade Data')

    # Run the Flask app
    ui_app.run(debug=False)
    # The following lines will only execute when the Flask app is terminated


if __name__ == "__main__":
    testsuite = BotTestSuite(api_key=API_KEY, secret_key=SECRET_KEY)
    testsuite.data_provider_test()
    testsuite.account_manager_test()
    # Call the main() function
    main()
