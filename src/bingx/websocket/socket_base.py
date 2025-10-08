import gzip
import io
import json
import uuid
from loguru import logger

class BingxSocketBase():
    
    def __init__(self):
        self.ws = None
        self.subscribed_channels = {}

    def _gen_id(self) -> str:
        return str(uuid.uuid4())

    async def on_message(self, message):
        compressed_data = gzip.GzipFile(fileobj=io.BytesIO(message), mode='rb')
        decompressed_data = compressed_data.read()
        utf8_data = decompressed_data.decode('utf-8')
        return utf8_data
    
    async def subscribe(self, channels: list[str]):
        for channel in channels:
            subscribed_id = self._gen_id()
            format = {"id":subscribed_id,"reqType": "sub","dataType":channel}
            await self.ws.send(json.dumps(format))
            self.subscribed_channels[channel] = {"id":subscribed_id}
            logger.info(f"Subscribed to {channel}")

    async def unsubscribe(self, channel: str):
        subscribed_id = self.subscribed_channels[channel]["id"]
        format = { "id": subscribed_id, "reqType": "unsub", "dataType": channel}
        await self.ws.send(json.dumps(format))
        self.subscribed_channels.pop(channel)

    async def pong(self, ws):
        await ws.send("Pong")
