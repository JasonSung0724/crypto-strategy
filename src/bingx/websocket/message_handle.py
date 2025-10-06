from asyncio import Queue
from loguru import logger

class MessageHandle:
    def __init__(self, queue: Queue):
        self.queue = queue
        
    async def handler(self, message: str):
        logger.info(message)

    async def start(self):
        while True:
            message = await self.queue.get()
            await self.handler(message)

