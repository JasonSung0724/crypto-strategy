from loguru import logger
import os
from src.bingx.websocket.socket import MarketSocket
from src.bingx.websocket.message_handle import MessageHandle
from dotenv import load_dotenv
import asyncio
from asyncio import Queue
from src.bingx.restful.factory import Bingx
from src.bingx.services.market_data import MarketData
from src.bingx.services.analysis import Analyzer
import pandas as pd
from src.lib.chart import plot_timeseries
from pathlib import Path
import numpy as np
from datetime import datetime
from src.strategy.real_time_monitor import RealTimeMonitor

logger.remove()
logger.add(
    sink=lambda msg: print(msg, end=""),
    level="INFO",
    format="<green>{time:YYYY-MM-DD HH:mm:ss.SSS}</green> | <level>{level: <8}</level> | <cyan>{name}</cyan>:<cyan>{function}</cyan>:<cyan>{line}</cyan> - <level>{message}</level>",
    colorize=True,
    serialize=False,
)

load_dotenv()

BINGX_API_KEY = os.getenv("BINGX_API_KEY")
BINGX_API_SECRET = os.getenv("BINGX_API_SECRET")


async def main():
    strategy = RealTimeMonitor(market_data=MarketData(api_key=BINGX_API_KEY, api_secret=BINGX_API_SECRET))
    tasks = await strategy.tasks_setup()

    await asyncio.gather(*tasks)


if __name__ == "__main__":
    asyncio.run(main())


# def main():
#     market = MarketData(api_key=BINGX_API_KEY, api_secret=BINGX_API_SECRET)
#     kline = market.get_kline(symbol="BTC-USDT", interval="5m", limit=10)
#     logger.info(kline)


# if __name__ == "__main__":
#     main()
