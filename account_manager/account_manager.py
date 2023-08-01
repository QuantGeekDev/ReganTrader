from alpaca.trading.client import TradingClient
from alpaca.trading.requests import GetAssetsRequest, MarketOrderRequest, LimitOrderRequest, GetOrdersRequest
from alpaca.trading.enums import AssetClass, OrderSide, TimeInForce, QueryOrderStatus


class AccountManager:
    def __init__(self, api_key, secret_key, paper=True):
        self.trading_client = TradingClient(api_key=api_key, secret_key=secret_key, paper=paper)

    def get_account_details(self):
        return self.trading_client.get_account()

    def get_assets(self, asset_class=AssetClass.CRYPTO):
        search_params = GetAssetsRequest(asset_class=asset_class)
        return self.trading_client.get_all_assets(search_params)

    def get_orders(self, status=QueryOrderStatus.OPEN, side=OrderSide.SELL):
        request_params = GetOrdersRequest(status=status, side=side)
        return self.trading_client.get_orders(filter=request_params)

    def cancel_all_orders(self):
        return self.trading_client.cancel_orders()

    def get_positions(self):
        return self.trading_client.get_all_positions()

    def close_all_positions(self, cancel_orders=True):
        return self.trading_client.close_all_positions(cancel_orders=cancel_orders)
