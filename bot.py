from websocket import Socket
from client import iClient


class Bot:

    def __init__(self):
        self.wsockets = {}
        self.client = iClient()
        self.coins = [ 'LINKUSDT', 'XLMUSDT']
        # #'ADAUSDT', 'DOTUSDT','XRPUSDT',,'ADAUSDT', 'DOTUSDT', 'XRPUSDT','XRPUSDT','ETHUSDT',
    
    def _runBot(self, market='all'):

        if market=='all':
            for coin in self.coins:
                self.wsockets[coin] = Socket(coin, self.client)._startSocket()
        else:
            self.wsockets[market] = Socket(market, self.client)._startSocket()
                 

        
     
    def _stopBot(self, market='all'):
        if market=='all':
            for i in self.wsockets.items():
                i._stopSocket()
            self.wsockets = {}    
        else:
          self.wsockets[market]._stopSocket()  


 

if __name__ == '__main__':

    bot = Bot()
    bot._runBot()