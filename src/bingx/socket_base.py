import gzip
import io

class BingxSocketBase():
    
    def __init__(self, url: str, channel: dict):
        self.url = url
        self.channel = channel
        self.ws = None

    async def on_message(self, message):
        compressed_data = gzip.GzipFile(fileobj=io.BytesIO(message), mode='rb')
        decompressed_data = compressed_data.read()
        utf8_data = decompressed_data.decode('utf-8')
        return utf8_data
    
    async def pong(self, ws):
        ws.send("Pong")