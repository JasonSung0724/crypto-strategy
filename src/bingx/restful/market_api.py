from src.lib.requests_handler import RequestsHandler
from src.bingx.restful.api_base import APIBase
from loguru import logger


class MarketAPI:

    def __init__(self, base: APIBase):
        self.base = base

    def get_symbols(self):
        url = self.base.gen_url(path="/openApi/swap/v2/quote/contracts")
        response = RequestsHandler.get(url=url, headers=self.base.headers)
        return response

    def change_24h(self):
        url = self.base.gen_url(path="/openApi/swap/v2/quote/ticker")
        response = RequestsHandler.get(url=url, headers=self.base.headers)
        return response

    def mark_price_and_funding_rate(self):
        url = self.base.gen_url(path="/openApi/swap/v2/quote/premiumIndex")
        response = RequestsHandler.get(url=url, headers=self.base.headers)
        return response

    def kline(self, symbol: str, interval: str, limit: int = 100, star_time: str = None, end_time: str = None):
        params = {"symbol": symbol, "interval": interval, "limit": limit}
        if star_time:
            params["startTime"] = star_time
        if end_time:
            params["endTime"] = end_time
        url = self.base.gen_url(path="/openApi/swap/v3/quote/klines", urlpa=params)
        response = RequestsHandler.get(url=url, headers=self.base.headers)
        return response
