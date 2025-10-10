from asyncio import Queue, sleep
from loguru import logger
from src.bingx.services.market_data import MarketData
from src.bingx.websocket.message_handle import MessageHandle
from src.bingx.websocket.socket import MarketSocket
import pandas as pd
from src.bingx.services.analysis import Analyzer
from src.lib.notification import TelegramNotification


class RealTimeMonitor:

    def __init__(self, market_data: MarketData, symbols: list[str] = ["ALL"], notification: TelegramNotification = None):
        self.analyzer = Analyzer(market_data)
        self.queue = Queue()
        self.msg_handler = MessageHandle(self)
        self.market_data = market_data
        if symbols == ["ALL"]:
            self.symbols = list(self.market_data.get_all_fluctuations().keys())
        else:
            self.symbols = symbols
        self.kline_data: dict[str, pd.DataFrame] = {symbol: None for symbol in self.symbols}
        self.indicator = {"moving_average": [48, 96], "fluctuation_rate": 96, "shadow_pct": []}
        self.notification_queue = Queue()
        self.notification = notification

    async def notification_handler(self):
        while True:
            message = await self.notification_queue.get()
            self.notification.send_message(message=message)

    async def kline_data_recv(self, data):
        limit = {"1m": 1440, "5m": 288, "15m": 288, "1d": 7}
        symbol = data["symbol"]
        if isinstance(self.kline_data[symbol], pd.DataFrame):
            df = self.kline_data[symbol]
            prev_time = df.iloc[-1]["time"]
            if prev_time == data["time"]:
                df2 = pd.DataFrame([data])
                df2 = self.analyzer.extend_indicator(df2, indicator=self.indicator)
                notified = bool(df.iloc[-1]["notified"])
                df2["notified"] = notified
                df.iloc[[-1]].update(df2.iloc[[0]])
            else:
                df = df.drop(index=0)
                df = pd.concat([df, pd.DataFrame([data])])
                df = self.analyzer.extend_indicator(df, indicator=self.indicator)
        else:
            df = self.market_data.get_kline(symbol=symbol, interval=self.kline_interval, limit=limit[self.kline_interval])
            df["notified"] = False
            df = self.analyzer.extend_indicator(df, indicator=self.indicator)
            self.kline_data[symbol] = df
            return

        await self.strategy_analysis(df)

    async def strategy_analysis(self, kline: pd.DataFrame):
        notified = kline.iloc[-1]["notified"]
        price_change = kline.iloc[-1]["price_change"]
        avg_fluc_pct = kline.iloc[-1]["avg_fluc_pct"]
        max_fluc_pct = kline.iloc[-1]["max_fluc_pct"]
        if abs(price_change) < avg_fluc_pct and not notified:
            logger.warning(f"Price change: {kline.iloc[-1]['symbol']} ({price_change*100}%)")
            kline.at[kline.index[-1], "notified"] = True
            await self.notification_queue.put(f"Price change: {kline.iloc[-1]['symbol']} ({price_change*100}%)")

        if abs(price_change) > max_fluc_pct * 2:
            logger.warning(f"Fast price change: {kline.iloc[-1]['symbol']} ({price_change*100}%)")
            kline.at[kline.index[-1], "notified"] = True
            await self.notification_queue.put(f"Fast price change: {kline.iloc[-1]['symbol']} ({price_change*100}%)")

    async def tasks_setup(self, kline_interval: str = "15m"):
        self.kline_interval = kline_interval
        channels_list = []
        limit = 200
        length = len(self.symbols)
        tasks = [self.msg_handler.start()]
        for i in range(0, length, limit):
            channels_list.append(self.symbols[i : i + limit])
        for channels in channels_list:
            channels = [f"{channel}@kline_{kline_interval}" for channel in channels]
            market_socket = MarketSocket(queue=self.queue, channels=channels)
            tasks.append(market_socket.start())
        return tasks
