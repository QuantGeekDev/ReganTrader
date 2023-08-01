from data_provider_interface.data_provider_interface import DataProviderInterface

from alpaca.data.timeframe import TimeFrame, TimeFrameUnit
from account_manager.account_manager import AccountManager
from alpaca.trading.enums import OrderSide
import pandas as pd
from data_provider_interface.data_provider import DataProvider
from data_provider_interface.connectors.alpaca.alpaca_connector import AlpacaConnector

class BotTestSuite:
    def __init__(self, api_key, secret_key):
        self.api_key = api_key
        self.secret_key = secret_key
        self.alpaca_connector = AlpacaConnector(api_key=self.api_key, secret_key=self.secret_key)
        self.data_provider = DataProvider(self.alpaca_connector)

        print('CryptoBot Test Suite Enabled')

    def account_manager_test(self):
        print('Running Account Manager Test...')

        account_manager = AccountManager(api_key=self.api_key, secret_key=self.secret_key)

        if account_manager.get_orders():
            print('Test 3/4')

        if account_manager.get_all_positions():
            print('Test 4/4')
        print('Account Manager Test Success')

    def data_provider_test(self):
        print('Running Data Provider Interface Test...')
        symbol = 'BTC/USD'  # specify a crypto symbol to fetch data

        alpaca_connector = AlpacaConnector(api_key=self.api_key, secret_key=self.secret_key)
        data_provider = DataProvider(alpaca_connector)

        # Initiate an empty list to store the test results
        test_results = []

        methods = ['bars', 'trades', 'latest_quote', 'latest_trade', 'latest_bar', 'snapshot', 'latest_orderbook']
        for i, method in enumerate(methods):
            result = data_provider.get_data(method, symbol_or_symbols=symbol,
                                            timeframe=TimeFrame.Hour if method in ['bars', 'trades'] else None)
            if result:
                print(f'Test {i + 1}/{len(methods)}: {method} Success')
                test_results.append({'Test': method, 'Result': 'Success', 'Data': result})
            else:
                print(f'Test {i + 1}/{len(methods)}: {method} Failed')
                test_results.append({'Test': method, 'Result': 'Failed', 'Data': None})

        # Convert the test results into a DataFrame
        df = pd.DataFrame(test_results)
        print(df)

