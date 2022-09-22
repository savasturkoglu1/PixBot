### binace websocker 

from binance.client import Client

class iClient:

    def __init__(self):
        self.api_key = "--"
        self.api_secret = "--"
        self.client = Client(self.api_key, self.api_secret, {"timeout": 60}) #"verify": False, 
     
        
