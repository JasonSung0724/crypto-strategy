from loguru import logger
import os
from src.bingx.socket import MarketSocket
from dotenv import load_dotenv
import asyncio

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
    market_socket = MarketSocket()
    await market_socket.start()
    
if __name__ == "__main__":
    asyncio.run(main())