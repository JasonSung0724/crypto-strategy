import datetime
from loguru import logger
from src.bingx.services.market_data import MarketData
from src.bingx.restful.factory import Bingx
import pandas as pd
import numpy as np

class Analyzer:

    def __init__(self, symbol: str, market_data: MarketData):
        self.symbol = symbol
        self.market_data = market_data
        self.data = None
    
    def data_collection(self):
        k1m = self.market_data.get_kline(symbol=self.symbol, interval="1m", limit=1440)
        k5m = self.market_data.get_kline(symbol=self.symbol, interval="5m", limit=288)
        k15m = self.market_data.get_kline(symbol=self.symbol, interval="15m", limit=96)
        k1h = self.market_data.get_kline(symbol=self.symbol, interval="1h", limit=48)
        k4h = self.market_data.get_kline(symbol=self.symbol, interval="4h", limit=24)
        self.data = {"1m": k1m, "5m": k5m, "15m": k15m, "1h": k1h, "4h": k4h}
        return {"1m": k1m, "5m": k5m, "15m": k15m, "1h": k1h, "4h": k4h}

    def analysis(self, data: pd.DataFrame):
        pass
        
    def extend_indicator(self, data: pd.DataFrame):
        self.moving_average(data)
        self.fluctuation_rate(data)
        self.shadow_pct(data)
        return data
    

    def moving_average(self, kline: pd.DataFrame, period: list[int] = [6, 24, 48]):
        for p in period:
            kline[f"{p}MA"] = kline["close"].rolling(window=p).mean().round(4)
        return kline
    
    def fluctuation_rate(self, kline: pd.DataFrame, avg_period: int = 24):
        cols = ["high", "low", "close", "open"]
        kline[cols] = kline[cols].apply(pd.to_numeric, errors="coerce")
        up = (kline["high"] - kline["open"]) / kline["open"]
        down = (kline["low"] - kline["open"]) / kline["open"]
        kline["max_fluc_pct"] = np.maximum(up, down.abs()).round(4)
        kline["avg_fluc_pct"] = kline["max_fluc_pct"].rolling(window=avg_period).mean().round(4)
        return kline
    
    def shadow_pct(self, kline: pd.DataFrame):
        cols = ["high", "low", "close", "open"]
        kline[cols] = kline[cols].apply(pd.to_numeric, errors="coerce")
        sec_high = np.maximum(kline["open"], kline["close"])
        sec_low = np.minimum(kline["open"], kline["close"])
        kline["upper_shadow_pct"] = ((kline["high"] - sec_high) / sec_high).round(4)
        kline["lower_shadow_pct"] = ((sec_low - kline["low"]) / sec_low).round(4)
        return kline
