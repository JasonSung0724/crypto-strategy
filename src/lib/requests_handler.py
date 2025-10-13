import requests
import json
from loguru import logger


class ResponseHandler:

    @staticmethod
    def process(response: requests.Response) -> dict:
        code = response.status_code
        data = ResponseHandler.parse_json(response)
        result = {"code": code, "data": data, "success": True if 200 <= code <= 299 else False}
        if result["success"]:
            logger.debug(json.dumps(result, indent=4))
        else:
            logger.error(json.dumps(result, indent=4))
        return result

    @staticmethod
    def parse_json(response: requests.Response) -> dict:
        res_text = response.text
        if res_text:
            result = json.loads(res_text)
            return result
        return res_text


def log_info(func):
    def wrapper(*args, **kwargs):
        method = str(func.__name__).upper()
        url = kwargs.get("url", "")
        data = kwargs.get("data", "")
        headers = kwargs.get("headers", "")
        message = f"\n{"-"*20}\nMethod: {method}\nURL: {url}\nData: {data}\nHeaders: {headers}\n{"-"*20}"
        logger.info(message)
        return func(*args, **kwargs)

    return wrapper


class RequestsHandler:

    @log_info
    @staticmethod
    def get(url: str, headers: dict = None, params: dict = None) -> ResponseHandler.process:
        return ResponseHandler.process(requests.get(url, headers=headers))

    @log_info
    @staticmethod
    def post(url: str, data: dict = None, headers: dict = None) -> ResponseHandler.process:
        return ResponseHandler.process(requests.post(url, data=data, headers=headers))

    @log_info
    @staticmethod
    def put(url: str, data: dict = None, headers: dict = None) -> ResponseHandler.process:
        return ResponseHandler.process(requests.put(url, data=data, headers=headers))

    @log_info
    @staticmethod
    def delete(url: str, data: dict = None, headers: dict = None) -> ResponseHandler.process:
        return ResponseHandler.process(requests.delete(url, headers=headers, data=data))

    @log_info
    @staticmethod
    def patch(url: str, data: dict = None, headers: dict = None) -> ResponseHandler.process:
        return ResponseHandler.process(requests.patch(url, data=data, headers=headers))
