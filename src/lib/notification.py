from inspect import FrameInfo
import requests
from loguru import logger
from src.config.globals import TELEGRAM_BOT_URL
from src.lib.requests_handler import RequestsHandler


class TelegramNotification:

    def __init__(self, token: str, chat_id: str):
        self.token = token
        self.domain = TELEGRAM_BOT_URL
        self.chat_id = chat_id

    def get_me(self):
        path = "/getMe"
        url = self.domain + self.token + path
        return RequestsHandler.get(url)

    def get_updates(self):
        path = "/getUpdates"
        url = self.domain + self.token + path
        return RequestsHandler.get(url=url)

    def send_message(self, message: str):
        path = "/sendMessage"
        url = self.domain + self.token + path + f"?chat_id={self.chat_id}&text={message}"
        return RequestsHandler.get(url=url)
