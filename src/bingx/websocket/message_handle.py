from asyncio import Queue
from loguru import logger
import pandas as pd
from src.bingx.services.market_data import MarketData
import json


class MessageHandle:
    def __init__(self, strategy):
        self.strategy = strategy

    async def handler(self, message):
        if "dataType" in message and "@kline" in message["dataType"]:
            symbol = message["s"]
            data = message["data"][0]
            high, low, close, open, volume, time = data["h"], data["l"], data["c"], data["o"], data["v"], data["T"]
            data = {"high": high, "low": low, "close": close, "open": open, "volume": volume, "time": time}
            return data
        logger.info(message)

    async def start(self):
        while True:
            message = await self.strategy.queue.get()
            await self.handler(json.loads(message))
