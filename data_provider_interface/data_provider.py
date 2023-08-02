from .data_provider_interface import DataProviderInterface
from retry import retry


class DataProvider(DataProviderInterface):
    def __init__(self, connector, config_manager):  # Add config_manager argument here
        super().__init__(connector, config_manager)  # Pass config_manager to the superclass

    @retry(Exception, tries=3, delay=2)
    def retry_request(self, fn, *args, **kwargs):
        def wrapper():
            return fn(*args, **kwargs)

        return wrapper()
