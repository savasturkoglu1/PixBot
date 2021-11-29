### binace websocker 

from binance.client import Client

class iClient:

    def __init__(self):
        self.api_key = "JKjrsJHkJoCNckrlXBdTjFB01iTszkNXmcqzUOkBj3Z6XROjnINVShqtmicseG58"
        self.api_secret = "YraZCTbi5O1c2RzSbp0La5fZCPNoJR2t0Zl6PD20hBQwfhYKKK7pyiAEBUgs8Ex8"
        self.client = Client(self.api_key, self.api_secret, {"verify": False, "timeout": 20})
        