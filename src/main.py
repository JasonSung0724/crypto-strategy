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

logger.remove()
logger.add(
    sink=lambda msg: print(msg, end=""),
    level="INFO",
    format="<green>{time:YYYY-MM-DD HH:mm:ss.SSS}</green> | <level>{level: <8}</level> | <cyan>{name}</cyan>:<cyan>{function}</cyan>:<cyan>{line}</cyan> - <level>{message}</level>",
    colorize=True,
    serialize=False
)

load_dotenv()

BINGX_API_KEY = os.getenv("BINGX_API_KEY")
BINGX_API_SECRET = os.getenv("BINGX_API_SECRET")

async def main():
    market_data = MarketData(api_key=BINGX_API_KEY, api_secret=BINGX_API_SECRET)
    rise_top, fall_top = market_data.get_top_fluctuations()
    channels = [item[0] + "@kline_1m" for item in rise_top] + [item[0] + "@kline_1m" for item in fall_top]
    msg_queue = Queue()
    message_handle = MessageHandle(queue=msg_queue)
    market_socket = MarketSocket(channels=channels, queue=msg_queue)
    tasks = [market_socket.start(), message_handle.start()]
    await asyncio.gather(*tasks)

    
if __name__ == "__main__":
    asyncio.run(main())

# def main():
#     market_data = MarketData(api_key=BINGX_API_KEY, api_secret=BINGX_API_SECRET)
#     analyzer = Analyzer(symbol="DOOD-USDT", market_data=market_data)
#     for k, df in analyzer.data_collection().items():
#         df = analyzer.extend_indicator(df)
#         analyzer.data[k] = df
#     plot_timeseries(df=analyzer.data["1h"], y_cols=["upper_shadow_pct", "lower_shadow_pct"], time_col="time", title="DOOD-USDT Shadow Percentage")


# if __name__ == "__main__":
#     main()

