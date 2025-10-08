from asyncio import Queue
from src.bingx.services.market_data import MarketData
from src.bingx.websocket.message_handle import MessageHandle
from src.bingx.websocket.socket import MarketSocket


class RealTimeMonitor:

    def __init__(self, market_data: MarketData, symbols: list[str] = ["ALL"]):
        self.queue = Queue()
        self.msg_handler = MessageHandle(self)
        self.market_data = market_data
        if symbols == ["ALL"]:
            self.symbols = list(self.market_data.get_all_fluctuations().keys())[:1]
        else:
            self.symbols = symbols
        self.kline_data = {symbol: None for symbol in self.symbols}

    async def kline_data_recv(self, data):
        limit = {"15m": 672, "1d": 7}
        symbol = data["symbol"]
        if not self.kline_data[symbol]:
            self.kline_data[symbol] = self.market_data.get_kline(symbol=symbol, interval=self.kline_interval, limit=limit[self.kline_interval])
        else:
            pass

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
