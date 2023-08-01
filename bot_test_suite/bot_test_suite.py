from data_provider_interface.data_provider_interface import DataProviderInterface
from alpaca.data.timeframe import TimeFrame, TimeFrameUnit
from account_manager.account_manager import AccountManager
from alpaca.trading.enums import OrderSide


class BotTestSuite:
    def __init__(self, api_key, secret_key):
        self.api_key = api_key
        self.secret_key = secret_key

        print('CryptoBot Test Suite Enabled')

    def account_manager_test(self):
        print('Running Account Manager Test...')

        account_manager = AccountManager(api_key=self.api_key, secret_key=self.secret_key)

        # Test the get_account_details method
        # if account_manager.get_account_details():
        #     print('Test 1/4')
        #
        # # Test the get_assets method
        # if account_manager.get_assets():
        #     print('Test 2/4')
        # Test the get_orders method
        if account_manager.get_orders():
            print('Test 3/4')

        # Test the get_positions method
        if account_manager.get_all_positions():
            print('Test 4/4')
        print('Account Manager Test Success')

    def data_provider_test(self):
        print('Running Data Provider Interface Test...')

        symbol = 'BTC/USD'  # specify a crypto symbol to fetch data
        time_interval = TimeFrame.Day

        data_provider = DataProviderInterface(api_key=self.api_key, secret_key=self.secret_key)

        # Test the get_crypto_bars method
        if data_provider.get_crypto_bars(symbol_or_symbols=symbol, timeframe=TimeFrame.Hour):
            print('Test 1/6')

        # # Test the get_crypto_trades method
        if data_provider.get_crypto_trades(symbol_or_symbols=symbol, timeframe=TimeFrame.Hour):
            print('Test 2/6')
        #
        # # Test the get_crypto_latest_quote method
        if data_provider.get_crypto_latest_quote(symbol_or_symbols=symbol):
            print('Test 3/6')
        #
        # # Test the get_crypto_latest_trade method
        if data_provider.get_crypto_latest_trade(symbol_or_symbols=symbol):
            print('Test 4/6')
        #
        # # Test the get_crypto_latest_bar method
        if data_provider.get_crypto_latest_bar(symbol_or_symbols=symbol):
            print('Test 5/6')
        #
        # # Test the get_crypto_snapshot method
        if data_provider.get_crypto_snapshot(symbol_or_symbols=symbol):
            print('Test 6/6')
