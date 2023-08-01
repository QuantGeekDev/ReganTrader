from .data_provider_interface import DataProviderInterface
from retry import retry


class DataProvider(DataProviderInterface):
    def __init__(self, connector):
        super().__init__(connector)

    @retry(Exception, tries=3, delay=2)
    def retry_request(self, fn, *args, **kwargs):
        def wrapper():
            return fn(*args, **kwargs)

        return wrapper()
