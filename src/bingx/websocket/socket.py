
import json
import websockets
import gzip
import io
from src.bingx.websocket.socket_base import BingxSocketBase
from src.config.globals import BINGX_SOCKET_URL
from loguru import logger
import time
from asyncio import Queue

swap_path = "/swap-market"
URL = BINGX_SOCKET_URL + swap_path


class MarketSocket(BingxSocketBase):
    
    def __init__(self, queue: Queue):
        self.ws = None
        self.msg_queue = queue
        super().__init__()
        self.start_time = time.time()
        
    async def start(self):
        async with websockets.connect(URL) as ws:
            self.ws = ws
            logger.info("Connected to the socket")
            await self.subscribe(channel="SOL-USDT@depth100@500ms")
            while True:
                recv = await self.ws.recv()
                message = await self.on_message(recv)
                if message == "Ping":
                    await self.pong(self.ws)
                else:
                    await self.msg_queue.put(message)
