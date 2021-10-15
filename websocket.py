
### binace websocker 
from binance import ThreadedWebsocketManager

from binance.client import Client


import numpy as np 
import pandas as pd 

import json, pprint
from client import iClient
from getData import GetData
from data import Data

class Socket:

    def __init__(self, coin, client):
        
        self.coin = coin
        self.Client = client
        self.Data = Data(self.Client.client, self.coin)
        self.GetData = GetData(self.Client.client, self.coin)

        self.bm = ThreadedWebsocketManager(api_key=self.Client.api_key, api_secret=self.Client.api_secret)
        self.connection_key = None
        

    def _process(self, msg):
       
        if msg['e'] == 'error':
            self._stopSocket(self.coin)
            self._startSocket()
        
        self.Data._dataProcess(msg)

    def _startSocket(self):
        
       
        self._lookBack() 
        
        self.bm.start()
        '''  start socket '''
        self.connection_key =self.bm.start_kline_socket( callback= self._process,symbol=self.coin, interval=Client.KLINE_INTERVAL_1MINUTE) #)
       # self.bm.start()


    def _stopSocket(self):
 
        ''' stop socket'''
    
        if self.connection_key is None:
            return 
        self.bm.stop_socket(self.connection_key)
        self.connection_key=None
    
    def _lookBack(self):

        '''  get 10 days data  '''

        #self.GetData._getData()



if __name__ == '__main__':
    s = Socket()
    s._startSocket('BTCUSDT')