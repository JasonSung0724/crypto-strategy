from asyncio import Queue
from loguru import logger
import pandas as pd
from src.bingx.services.market_data import MarketData
import json
import asyncio


class MessageHandle:
    def __init__(self, strategy):
        self.strategy = strategy

    async def handler(self, message):
        if "dataType" in message and "@kline" in message["dataType"]:
            interval = message["dataType"].split("@kline_")[1]
            symbol = message["s"]
            data = message["data"][0]
            high, low, close, open, volume, time = data["h"], data["l"], data["c"], data["o"], data["v"], data["T"]
            data = {"time": time, "open": open, "close": close, "high": high, "low": low, "volume": volume, "symbol": symbol, "interval": interval}
            await self.strategy.kline_data_recv(data)

    async def start(self):
        while True:
            message = await self.strategy.msg_queue.get()
            await self.handler(json.loads(message))
            await asyncio.sleep(0)
