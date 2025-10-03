
import json
import websockets
import gzip
import io
from src.bingx.socket_base import BingxSocketBase
from src.config.globals import BINGX_SOCKET_URL
from loguru import logger

swap_path = "/swap-market"
URL = BINGX_SOCKET_URL + swap_path
CHANNEL= {"id":"e745cd6d-d0f6-4a70-8d5a-043e4c741b40","reqType": "sub","dataType":"BTC-USDT@depth5@500ms"}

class MarketSocket(BingxSocketBase):
    
    def __init__(self):
        self.ws = None
        super().__init__(URL, CHANNEL)
        
    async def start(self):
        async with websockets.connect(self.url) as ws:
            self.ws = ws
            logger.info("Connected to the socket")
            while True:
                recv = await self.ws.recv()
                message = await self.on_message(recv)
                message