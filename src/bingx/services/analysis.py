import datetime
from loguru import logger
from src.bingx.services.market_data import MarketData
from src.bingx.restful.factory import Bingx


class Analyzer:

    def __init__(self, symbol: str, market_data: MarketData):
        self.symbol = symbol
        self.market_data = market_data

    def analysis(self):
        k1m = self.market_data.get_kline(symbol=self.symbol, interval="1m", limit=1440)
        k5m = self.market_data.get_kline(symbol=self.symbol, interval="5m", limit=288)
        k15m = self.market_data.get_kline(symbol=self.symbol, interval="15m", limit=96)
        k1h = self.market_data.get_kline(symbol=self.symbol, interval="1h", limit=48)
        k4h = self.market_data.get_kline(symbol=self.symbol, interval="4h", limit=24)
