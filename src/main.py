from loguru import logger
import os
from dotenv import load_dotenv
import asyncio
from src.bingx.services.market_data import MarketData
from src.strategy.real_time_monitor import RealTimeMonitor
from src.lib.notification import TelegramNotification


logger.remove()
log_format = "<green>{time:YYYY-MM-DD HH:mm:ss.SSS}</green> | <level>{level: <8}</level> | <cyan>{name}</cyan>:<cyan>{function}</cyan>:<cyan>{line}</cyan> - <level>{message}</level>"
logger.add(
    sink=lambda msg: print(msg, end=""),
    level="INFO",
    format=log_format,
    colorize=True,
    serialize=False,
)

logger.add(
    "./logs/main.log",
    level="WARNING",
    format=log_format,
    rotation="1 day",
    retention="7 days",
    compression="zip",
)

load_dotenv()

BINGX_API_KEY = os.getenv("BINGX_API_KEY")
BINGX_API_SECRET = os.getenv("BINGX_API_SECRET")
TELEGRAM_BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")


async def main():
    notification = TelegramNotification(token=TELEGRAM_BOT_TOKEN, chat_id="-1003146797346")
    notification.send_message(message="Start monitoring")
    market = MarketData(api_key=BINGX_API_KEY, api_secret=BINGX_API_SECRET)
    strategy = RealTimeMonitor(market_data=market, notification=notification)
    tasks = await strategy.tasks_setup(kline_interval="15m")

    await asyncio.gather(*tasks)

    logger.error("Monitoring shutdown")
    notification.send_message(message="Start monitoring")


if __name__ == "__main__":
    asyncio.run(main())
