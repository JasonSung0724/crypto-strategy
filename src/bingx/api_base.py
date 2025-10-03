import os
import time
import hmac
from loguru import logger
from hashlib import sha256
from src.config.globals import BINGX_API_URL


class BingxBase:
    
    
    def __init__(self, api_key: str, api_secret: str):
        self.api_key = api_key
        self.api_secret = api_secret
        self.headers = {
            "X-BX-APIKEY": api_key,
        }

    def get_sign(self, api_secret: str, payload: dict={}):
        signature = hmac.new(api_secret.encode("utf-8"), payload.encode("utf-8"), digestmod=sha256).hexdigest()
        return signature

    def parseParam(self, paramsMap):
        sortedKeys = sorted(paramsMap)
        paramsStr = "&".join(["%s=%s" % (x, paramsMap[x]) for x in sortedKeys])
        if paramsStr != "":
            return paramsStr + "&timestamp=" + str(int(time.time() * 1000))
        else:
            return paramsStr + "timestamp=" + str(int(time.time() * 1000))

    def gen_url(self, path: str, urlpa: str={}):
        urlpa = self.parseParam(urlpa)
        url = "%s%s?%s&signature=%s" % (BINGX_API_URL, path, urlpa, self.get_sign(self.api_secret, urlpa))
        return url