from asyncio import Queue
import asyncio
from symtable import Symbol
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
        self.msg_queue = Queue()
        self.msg_handler = MessageHandle(self)
        self.market_data = market_data
        if symbols == ["ALL"]:
            self.symbols = list(self.market_data.get_all_fluctuations().keys())
        else:
            self.symbols = symbols
        self.long_time = 96
        self.short_time = 48
        self.kline_data: dict[str, pd.DataFrame] = {symbol: None for symbol in self.symbols}
        self.indicator = {
            "moving_average": [self.short_time, self.long_time],
            "fluctuation_rate": self.long_time,
            "shadow_pct": [],
            "boolinger_band": self.short_time,
        }
        self.notification_queue = Queue()
        self.notification = notification
        self.kline_interval = None

    async def notification_handler(self):
        while True:
            buffer = []
            await asyncio.sleep(10)

            while not self.notification_queue.empty():
                message = await self.notification_queue.get()
                buffer.append(message)

            if buffer:
                self.notification.send_message(message="\n".join(buffer))

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
        trigger = False
        current_price = float(kline.iloc[-1]["close"])
        notified = bool(kline.iloc[-1]["notified"])
        price_change = float(kline.iloc[-1]["price_change"])
        avg_fluc_pct = float(kline.iloc[-1]["avg_fluc_pct"])
        max_fluc_pct = float(kline.iloc[-1]["max_fluc_pct"])
        volume = max(float(kline.iloc[-1]["volume"]), float(kline.iloc[-2]["volume"]))
        avg_volume = float(kline.iloc[-1]["avg_volume"])
        long_ma = float(kline.iloc[-1][f"{self.long_time}MA"])
        short_ma = float(kline.iloc[-1][f"{self.short_time}MA"])
        pre_long_ma = float(kline.iloc[-2][f"{self.long_time}MA"])
        pre_short_ma = float(kline.iloc[-2][f"{self.short_time}MA"])
        upper_band = float(kline.iloc[-1]["upper_band"])
        lower_band = float(kline.iloc[-1]["lower_band"])
        upper_shadow_pct = float(kline.iloc[-1]["upper_shadow_pct"])
        lower_shadow_pct = float(kline.iloc[-1]["lower_shadow_pct"])

        if not notified:

            if upper_shadow_pct > 0.5:
                logger.warning(f"Rapid price retracement: {kline.iloc[-1]['symbol']} within {self.kline_interval} ({round((upper_shadow_pct*100), 2)}%)")
                trigger = True
                await self.notification_queue.put(
                    f"Rapid price retracement: {kline.iloc[-1]['symbol']} within {self.kline_interval} ({round(((upper_shadow_pct)*100), 2)}%)"
                )
            if lower_shadow_pct > 0.5:
                logger.warning(f"Rapid price retracement: {kline.iloc[-1]['symbol']} within {self.kline_interval} ({round((lower_shadow_pct*100), 2)}%)")
                trigger = True
                await self.notification_queue.put(
                    f"Rapid price retracement: {kline.iloc[-1]['symbol']} within {self.kline_interval} ({round(((lower_shadow_pct)*100), 2)}%)"
                )

            if current_price > upper_band:
                logger.warning(f"Price above upper band: {kline.iloc[-1]['symbol']}")
                trigger = True
                await self.notification_queue.put(f"Price above upper band: {kline.iloc[-1]['symbol']}")

            if current_price < lower_band:
                logger.warning(f"Price below lower band: {kline.iloc[-1]['symbol']}")
                trigger = True
                await self.notification_queue.put(f"Price below lower band: {kline.iloc[-1]['symbol']}")

            if volume > avg_volume * 3:
                logger.warning(f"Fast volume change: {kline.iloc[-1]['symbol']} ({volume/avg_volume*100}%)")
                trigger = True
                await self.notification_queue.put(
                    f"Fast volume change: {kline.iloc[-1]['symbol']} ({round(((volume/avg_volume)*100), 2)}%)\n Average: {avg_volume}, Current: {volume}"
                )

            if abs(price_change) > avg_fluc_pct * 2 and abs(price_change) > max_fluc_pct:
                logger.warning(f"Fast price change: {kline.iloc[-1]['symbol']} ({price_change*100}%)")
                trigger = True
                await self.notification_queue.put(
                    f"Fast price change: {kline.iloc[-1]['symbol']} ({round((price_change*100), 2)}%) within {self.kline_interval}"
                )

            if (long_ma > short_ma and pre_long_ma < pre_short_ma) or (long_ma < short_ma and pre_long_ma > pre_short_ma):
                logger.warning(f"MA crossover: {kline.iloc[-1]['symbol']}")
                trigger = True
                await self.notification_queue.put(f"MA crossover: {kline.iloc[-1]['symbol']}")

        if trigger:
            logger.warning(f"Trigger: {kline.iloc[-1]['symbol']}")
            kline.at[kline.index[-1], "notified"] = True

    async def tasks_setup(self, kline_interval: str = "15m"):
        self.kline_interval = kline_interval
        channels_list = []
        limit = 200
        length = len(self.symbols)
        tasks = [self.msg_handler.start()]
        if self.notification:
            tasks.append(self.notification_handler())
        for i in range(0, length, limit):
            channels_list.append(self.symbols[i : i + limit])
        for channels in channels_list:
            channels = [f"{channel}@kline_{kline_interval}" for channel in channels]
            market_socket = MarketSocket(queue=self.msg_queue, channels=channels)
            tasks.extend(market_socket.start())
        return tasks
