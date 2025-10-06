from src.lib.requests_handler import RequestsHandler
from src.bingx.restful.api_base import APIBase
from loguru import logger


class ListenKey(APIBase):

    def __init__(self, api_key: str, api_secret: str):
        super().__init__(api_key, api_secret)
        self.listen_key = None
        self.path = "/openApi/user/auth/userDataStream"

    def get_listen_key(self) -> dict:
        url = self.gen_url(self.path)
        res = RequestsHandler.post(url=url, headers=self.headers)
        if res["code"] == 200 and res["data"]:
            self.listen_key = res["data"]["listenKey"]
            return self.listen_key
        res["success"] = False
        return res
    
    def extend_listen_key(self, listen_key: str=None) -> dict:
        if not listen_key and not self.listen_key:
            logger.error("No listen key to extend")
            return None
        payload = {
            "listenKey": listen_key if listen_key else self.listen_key
        }
        url = self.gen_url(self.path)
        res = RequestsHandler.put(url=url, headers=self.headers, data=payload)
        return res
    
    def delete_listen_key(self, listen_key: str=None) -> dict:
        if not listen_key and not self.listen_key:
            logger.error("No listen key to delete")
            return None
        payload = {
            "listenKey": listen_key if listen_key else self.listen_key
        }
        url = self.gen_url(self.path)
        res = RequestsHandler.delete(url=url, headers=self.headers, data=payload)
        return res