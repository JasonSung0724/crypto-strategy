from loguru import logger
from src.bingx.restful.factory import Bingx
import heapq
import pandas as pd
import numpy as np


class MarketData:
    def __init__(self, api_key: str, api_secret: str):
        self.bing = Bingx(api_key=api_key, api_secret=api_secret)
        self.fluctuations_list = None

    def get_all_fluctuations(self):
        res = self.bing.market.change_24h()
        data = {item["symbol"]: float(item["priceChangePercent"]) for item in res["data"]["data"]}
        self.fluctuations_list = data
        return data

    def get_top_fluctuations(self, top_n: int = 10):
        self.get_all_fluctuations()
        rise_heap = []
        fall_heap = []

        for k, v in self.fluctuations_list.items():
            if 0 < v < 1000:
                if len(rise_heap) < top_n:
                    heapq.heappush(rise_heap, (v, k))
                else:
                    heapq.heappushpop(rise_heap, (v, k))
            elif -90 < v < 0:
                abs_drop = -v
                if len(fall_heap) < top_n:
                    heapq.heappush(fall_heap, (abs_drop, k))
                else:
                    heapq.heappushpop(fall_heap, (abs_drop, k))

        rise_top = [(k, v) for v, k in sorted(rise_heap, reverse=True)]
        fall_top = [(k, -v) for v, k in sorted(fall_heap, reverse=True)]
        return rise_top, fall_top

    def get_kline(self, symbol: str, interval: str, limit: int = 100, star_time: str = None, end_time: str = None) -> pd.DataFrame:
        support_interval = ["1m", "3m", "5m", "15m", "30m", "1h", "2h", "4h", "6h", "8h", "12h", "1d", "3d", "1w", "1M"]
        if interval not in support_interval:
            logger.error(f"Unsupported interval: {interval}")
            raise ValueError(f"Unsupported interval: {interval}")
        res = self.bing.market.kline(symbol=symbol, interval=interval, limit=limit, star_time=star_time, end_time=end_time)
        data = res["data"]
        if "data" in data and data["code"] == 0:
            kline = pd.DataFrame(data["data"])
            kline["symbol"] = symbol
            kline["interval"] = interval
            kline = kline.sort_values("time").set_index("time")
            return kline.reset_index()
        else:
            msg = res["msg"] if "msg" in res else res
            logger.error(f"\nFailed to get kline\nCode :{res['code']}\nMessage :{msg}")
            raise ValueError(f"\nFailed to get kline\nCode :{res['code']}\nMessage :{msg}")
