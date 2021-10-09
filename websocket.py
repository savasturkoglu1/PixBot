
### binace websocker 
from binance.websockets import BinanceSocketManager

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
        self.Data = Data(self.Client, self.coin)
        self.GetData = GetData(self.Client, self.coin)

        self.bm = BinanceSocketManager(self.Client)
        self.connection_key = None
        

    def _process(self, msg):
       
        if msg['e'] == 'error':
            self._stopSocket(self.coin)
            self._startSocket()
        print(msg)
       # self.Data._dataProcess(msg)

    def _startSocket(self):
        
        self._lookBack() 
        
        '''  start socket '''
        self.connection_key =self.bm.start_kline_socket(self.coin,  self._process, interval=Client.KLINE_INTERVAL_5MINUTE) 
        self.bm.start()


    def _stopSocket(self):
 
        ''' stop socket'''
    
        if self.connection_key is None:
            return 
        self.bm.stop_socket(self.connection_key)
        self.connection_key=None
    
    def _lookBack(self):

        '''  get 10 days data  '''

        self.GetData._getData()



if __name__ == '__main__':
    s = Socket()
    s._startSocket('BTCUSDT')