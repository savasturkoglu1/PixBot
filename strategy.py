

from indicator import  Indicator
from env import base_path
import pandas as pd
import numpy as np
from signals import Signals
from priceAction import PriceAction
from trade import Trade
from logger import Logs
class Strategy:

    def __init__(self, client,coin):
        
        ## market
        
        self.coin = coin
        self.client = client
        



        ## defaults
        self.atr_tresh = {
            'BTCUSDT':0.96,
            'ETHUSDT':1.2,
            'DOTUSDT':2.02,
            'ADAUSDT':1.42,
            'XRPUSDT':1.2
        }

        self.prc = {
            'BTCUSDT':0,
            'ETHUSDT':2,
            'DOTUSDT':2,
            'ADAUSDT':3,
            'XRPUSDT':4
        }

        ## objects
        self.Indicator = Indicator()
        self.Signal = Signals()
        self.PA = PriceAction()
        self.Trade = Trade(self.client, self.coin)
        self.Logs = Logs()

        ### sources
        self.rafined = None#pd.read_csv(base_path+'/source/rafine_ocmarket_'+self.coin+'.csv')
        self.strategies =None#pd.read_csv(base_path+'/source/strategies.csv')
        

        ## data framse        
        self.df_15m = None
        self.df_30m = None
        self.df_1h = None
        self.df_5m = None
        self.df_1m = None
        self.live = None        
        self.market_ind = None

        ## params
        self.market = None
        self.stg = None
        self.df = None
        self.signals = None
        self.params = None
        self.position = None
        self.intval =60000
        
        self.close = False
        self.candle_close = None
        self.trade_signal = None
        self.trade_count = None
        self.trade_perm = False
        self.bot_type = 'PACTION' #'PACTION' # 'INDICATOR', 
        # if self.coin == 'XRPUSDT':
        #     self.bot_type = 'INDICATOR'
        # if self.bot_type == 'INDICATOR':
        #     self.rafined = pd.read_csv(base_path+'/source/rafine_ocmarket_'+self.coin+'.csv')
        #     self.strategies = pd.read_csv(base_path+'/source/strategies.csv')
    def _process(self, live ,df_1m, df_5m, df_15m, df_30m, df_1h, candle_close):

        ## set data frames
        self.df_1m = df_1m
        self.df_5m = df_5m
        self.df_15m = df_15m
        self.df_30m = df_30m
        self.df_1h = df_1h
        self.live  = live
        self.candle_close = candle_close

        self.Trade._live(live)
        if self.bot_type=='PACTION':
               self._priceActionSignals()
        if self.bot_type=='INDICATOR':
               self._indicatorSignal()
        
    
    def _priceActionSignals(self):
        ## check trade position
        self.Trade._live(self.live)
        self.position = self.Trade.position
        if self.position is None:
           self.PA.long_flag = False
           self.PA.short_flag = False
           self.trade_len = 0
           self.entry_point =None               
           self.entry_index = None  
        ## get signal
        print(self.candle_close)
        if self.candle_close:
            self.signals = self.PA._getSignal(self.df_5m)
            
            ## set order
        if self.signals is not None:
            if self.close is True:
                self.signals['close_position'] = None
                if self.signals['open_position'] == 'OPEN_LONG':
                    if self.live['Close'] <= self.signals['open_long']:
                        self.signals['open_position'] = None
                    else:     
                        self.signals['open_position'] = self.live['Close']
                if self.signals['open_position'] == 'OPEN_SHORT':
                    if self.live['Close'] >= self.signals['open_short']:
                        self.signals['open_position'] = None
                    else:     
                        self.signals['open_position'] = self.live['Close']
            

            params = self._tradeParams()
            
            print(self.coin,self.signals, params)
            if params is not None:
                    self.Logs._writeLog(self.coin+'- order params   '+ str(params)+'\n'+str(self.signals)) 
                    if self.signals['close_position'] is not None:
                        self.close = True  
                    else:
                        self.close = False
                    self.Trade._order(**params)  

    def _tradeParams(self):
        params=None
        if self.signals['close_position'] is not None :
            #self.signals['position'] == 'CLOSE_LONG' or self.signals['position'] == 'CLOSE_SHORT'
            params=dict(
                order_type=self.signals['close_position'],
                trade_type='LONG' if self.signals['close_position'] == 'CLOSE_LONG' else 'SHORT',
                price=self.signals['close_long'] if self.signals['close_position'] == 'CLOSE_LONG' else self.signals['close_short'],
                
            )
        elif self.signals['open_position'] is not None:
        #self.signals['position'] == 'OPEN_LONG' or self.signals['position'] == 'OPEN_SHORT':
            p = self.signals['open_long'] if self.signals['open_position'] == 'OPEN_LONG' else self.signals['open_short']
            params=dict(
                order_type=self.signals['open_position'],
                trade_type='LONG' if self.signals['open_position'] == 'OPEN_LONG' else 'SHORT',
                price=round(p, self.prc[self.coin]),
                stop_price =round(self.signals['stop_price'], self.prc[self.coin]),
                stop_limit =round(self.signals['stop_limit'],3),
                profit_price=round(self.signals['take_profit'], self.prc[self.coin]) if self.signals['take_profit'] is not None else None,
                leverage=self.signals['leverage']
            )
        
        return params
    

    


   

  