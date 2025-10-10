import asyncio
import websockets
from src.bingx.websocket.socket_base import BingxSocketBase
from src.config.globals import BINGX_SOCKET_URL
from loguru import logger
from websockets.exceptions import ConnectionClosedError
import time
from asyncio import Queue

swap_path = "/swap-market"
URL = BINGX_SOCKET_URL + swap_path


class MarketSocket(BingxSocketBase):

    def __init__(self, queue: Queue, channels: list[str]):
        self.ws = None
        self.msg_queue = queue
        self.channels = channels
        super().__init__()
        self.start_time = time.time()
        self.ping_interval = 5

    async def ws_connect(self):
        try:
            async with websockets.connect(URL) as ws:
                self.ws = ws
                logger.info("Connected to the socket")
                await self.subscribe(channels=self.channels)
                while True:
                    recv = await self.ws.recv()
                    message = await self.on_message(recv)
                    if message == "Ping":
                        pass
                    else:
                        await self.msg_queue.put(message)
        except (ConnectionClosedError, TimeoutError) as e:
            logger.error(f"Connection closed: {e}")
            self.ws = None
            await self.ws_connect()

    async def pong_loop(self):
        last_pong_time = time.time()
        while True:
            current_time = time.time()
            if current_time - last_pong_time > self.ping_interval and self.ws:
                await self.ws.pong()
                last_pong_time = current_time
            await asyncio.sleep(self.ping_interval / 2)

    def start(self) -> list[asyncio.Task]:
        return [self.ws_connect(), self.pong_loop()]
