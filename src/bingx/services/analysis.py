import datetime
from loguru import logger
from src.bingx.services.market_data import MarketData
from src.bingx.restful.factory import Bingx
import pandas as pd
import numpy as np


class Analyzer:

    def __init__(self, market_data: MarketData):
        self.market_data = market_data
        self.data = None

    def analysis(self, data: pd.DataFrame):
        pass

    def extend_indicator(
        self,
        data: pd.DataFrame,
        indicator: dict[str, list[int]] = {"moving_average": [6, 48, 180], "fluctuation_rate": 24, "shadow_pct": [], "boolinger_band": 20},
    ) -> pd.DataFrame:
        for k, v in indicator.items():
            if k == "moving_average":
                data = self.moving_average(data, period=v)
            elif k == "fluctuation_rate":
                data = self.fluctuation_rate(data, avg_period=v)
            elif k == "shadow_pct":
                data = self.shadow_pct(data)
            elif k == "boolinger_band":
                data = self.boolinger_band(data, period=v)
        return data

    def boolinger_band(self, kline: pd.DataFrame, period: int) -> pd.DataFrame:
        cols = ["high", "low", "close", "open"]
        kline[cols] = kline[cols].apply(pd.to_numeric, errors="coerce")
        multiplier = 2
        kline["middle_band"] = kline["close"].rolling(window=period).mean()
        kline["std_dev"] = kline["close"].rolling(window=period).std()
        kline["upper_band"] = kline["middle_band"] + (multiplier * kline["std_dev"])
        kline["lower_band"] = kline["middle_band"] - (multiplier * kline["std_dev"])
        kline["band_width"] = kline["upper_band"] - kline["lower_band"]
        kline.drop(columns=["std_dev"], inplace=True)
        return kline

    def moving_average(self, kline: pd.DataFrame, period: list[int]) -> pd.DataFrame:
        for p in period:
            kline[f"{p}MA"] = kline["close"].rolling(window=p).mean().round(4)
        return kline

    def fluctuation_rate(self, kline: pd.DataFrame, avg_period: int = 24) -> pd.DataFrame:
        cols = ["high", "low", "close", "open"]
        kline[cols] = kline[cols].apply(pd.to_numeric, errors="coerce")
        up = (kline["high"] - kline["open"]) / kline["open"]
        down = (kline["low"] - kline["open"]) / kline["open"]
        kline["highest_price"] = kline["high"].max()
        kline["lowest_price"] = kline["low"].min()
        kline["price_change"] = ((kline["close"] - kline["open"]) / kline["open"]).round(4)
        kline["max_fluc_pct"] = np.maximum(up, down.abs()).round(4)
        kline["avg_fluc_pct"] = kline["max_fluc_pct"].rolling(window=avg_period).mean().round(4)
        kline["avg_volume"] = kline["volume"].rolling(window=avg_period).mean().round(4)
        return kline

    def shadow_pct(self, kline: pd.DataFrame) -> pd.DataFrame:
        cols = ["high", "low", "close", "open"]
        kline[cols] = kline[cols].apply(pd.to_numeric, errors="coerce")
        sec_high = np.maximum(kline["open"], kline["close"])
        sec_low = np.minimum(kline["open"], kline["close"])
        kline["upper_shadow_pct"] = ((kline["high"] - sec_high) / sec_high).round(4)
        kline["lower_shadow_pct"] = ((sec_low - kline["low"]) / sec_low).round(4)
        return kline
