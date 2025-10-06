from src.bingx.restful.api_base import APIBase
from src.lib.requests_handler import RequestsHandler
from src.bingx.restful.market_api import MarketAPI


class Bingx(APIBase):

    def __init__(self, api_key: str, api_secret: str):
        super().__init__(api_key, api_secret)
        self.market = MarketAPI(self)
