

from indicator import  Indicator
from env import base_path
import pandas as pd
import numpy as np
from signal import Signal


class Strategy:

    def __init__(self, client,coin):
        
        self.coin = coin
        self.client = client

        self.Indicator = Indicator()
        self.Signal = Strategy()
        
        self.rafined = pd.read_csv(base_path+'/source/rafined.csv')
        self.strategies = pd.read_csv(base_path+'/source/strategies.csv')
        self.params = None
        ## data framse
        
        self.df_15m = None
        self.df_30m = None
        self.df_1h = None
        self.live = None
        self.market = None
        self.market_ind = None
        
        self.df = None
        self.signals = None

    def _process(self, live , df_15m, df_30m, df_1h):

        ## set data frames
      
        self.df_15m = df_15m
        self.df_30m = df_30m
        self.df_1h = df_1h
        self.live  = live
        

        self._getMarket()
        self._getStrategy()

        if self.params['time_frame'] == '30m':
            self.df = self.df_30m
        elif self.params['time_frame'] == '1h':
            self.df = self.df_1h
        else:
            self.df = self.df_15m    

        self.signals =  self.Signal._getSignal(self.df, **self.params)
        
       
    

    def _getStrategy(self):
        r = self.rafined[(self.rafined.coin==self.coin)&(self.rafined.market==self.market)]
        if r.shape[0]<1:
            self.params = None
        row = r.loc[r['trade_index'].idxmax()].to_dict()
        #.tail(1).to_dict('records')[0]
        self.stg = row['strategy']
        
        self.params = self.strategies[self.strategies.unique==row['strategy']].to_dict('records')[0]


    def _updateStrategy(self):
        pass


    def _getMarket(self):
        
        ind = self.Indicator._envIndicators(self.df_1h)
        row = ind.iloc[-1].to_dict()
        self.market_ind = ind
        atr_tresh = self.df_1h['natr'].median()
       
        adx = row['adxm']
        at = row['natr']
        t =None
        v=None
         
        if adx<25:
            v='low'
        
        elif adx>=25:
              v='high'

        if at<=atr_tresh:
              t='low'          
        else :
              t='high'       
        self.market = t+v
         