from loguru import logger
import os
from src.bingx.websocket.socket import MarketSocket
from dotenv import load_dotenv
import asyncio
from asyncio import Queue
from src.bingx.restful.factory import Bingx
from src.bingx.services.market_data import MarketData
from src.bingx.services.analysis import Analyzer

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

# async def main():
#     msg_queue = Queue()
#     market_socket = MarketSocket()
#     await market_socket.start()
    
# if __name__ == "__main__":
#     asyncio.run(main())

def main():
    market_data = MarketData(api_key=BINGX_API_KEY, api_secret=BINGX_API_SECRET)
    rise, fall = market_data.get_top_fluctuations() 
    for symbol, _ in rise:
        analyzer = Analyzer(symbol=symbol, market_data=market_data)
        analyzer.analysis()
    for symbol, _ in fall:
        analyzer = Analyzer(symbol=symbol, market_data=market_data)
        analyzer.analysis()

if __name__ == "__main__":
    main()
