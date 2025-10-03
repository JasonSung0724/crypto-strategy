from dotenv import load_dotenv

from src.bingx.api_base import BingxBase
from src.config.globals import BINGX_API_URL
from src.lib.requests_hadler import RequestsHandler

load_dotenv()

BINGX_API_KEY = os.getenv("BINGX_API_KEY")
BINGX_API_SECRET = os.getenv("BINGX_API_SECRET")



class BingxApi(BingxBase):

    def __init__(self, api_key: str, api_secret: str):
        self.api_key = api_key
        self.api_secret = api_secret
        super().__init__(api_key, api_secret)

    
