

from indicator import  Indicator
from env import base_path
import pandas as pd
import numpy as np
import talib
from agent import Agent
from trade import Trade
from logger import Logs

class Strategy:

    def __init__(self, client,coin):
        
        ## market
        
        self.coin = coin
        self.client = client
        self.prc = {
            'BTCUSDT':0,
            'ETHUSDT':2,
            'DOTUSDT':2,
            'AVAXUSDT':2,
            'ADAUSDT':0,
            'XRPUSDT':4,
            'ATOMUSDT':3,
            'LINKUSDT':2,
            'XLMUSDT':4
        }
        

        ## objects
        self.Indicator = Indicator()      
        self.Agent = Agent(self.coin)
        self.Trade = Trade(self.client, self.coin)
        self.Logs = Logs(self.coin)

        ## data framse        
        self.df_15m = None
        self.df_30m = None
        self.df_1h = None
        self.df_5m = None
        self.df_1m = None
        self.live = None        
      

        ## params
       
        self.df = None
        
        
        self.intval =60000
        

        self.long_flag = False
        self.short_flag = False
        self.position = None
        self.entry_price = None

    def _signal(self, live ,df_1m, df_5m, df_15m, df_30m, candle_close):

        ## set data frames
        self.df_1m = df_1m
        self.df_5m = df_5m
        self.df_15m = df_15m
        self.df_30m = df_30m
        
        self.live  = live
        self.candle_close = candle_close

        self.Trade._live(self.live)        

        self.position = self.Trade.position
        if self.position is None:
                self.long_flag = False
                self.short_flag = False

        instant_pnl = 0
        if self.position == 1:
            instant_pnl = (live['Close']-self.entry_price)/self.entry_price*100
        elif self.position == 0:
            instant_pnl = (self.entry_price-live['Close'])/self.entry_price*100
        
        signal,leverage = 2,1
        if candle_close:
          signal, leverage = self.Agent.signal(self.df_15m, instant_pnl, self.position)

        if signal !=2:
            
            params = self._params(signal,self.live, leverage)

            print(self.coin, params)
            self.Logs._writeLog(self.coin+'-agent order params   '+ str(params))   
            self.Trade._order(**params)

   
    
    def _params(self, signal, df, leverage):
        df['atr'] = talib.ATR(df.High, df.Low, df.Close, timeperiod=14).tolist()
        data = df.iloc[-1].to_dict()
        close = df.iloc[-1].Close
        atr = df.iloc[-1].atr
        row = {}
        if signal == 1 and self.short_flag is True:
            row['price'] = round(close, self.prc[self.coin])
            row['order_type'] = 'CLOSE_SHORT'
            row['trade_type'] = 'SHORT'
            self.short_flag = False 
            self.entry_price = None

        elif signal==0 and self.long_flag is True:
            row['price'] = round(close, self.prc[self.coin])
            row['order_type'] = 'CLOSE_LONG'
            row['trade_type'] = 'LONG'
            self.long_flag = False    
            self.entry_price = None

        elif signal == 1  and self.long_flag is False and  self.short_flag is False:
             row['price'] = round(close, self.prc[self.coin])
             row['order_type'] = 'OPEN_LONG'
             row['trade_type'] = 'LONG'
             self.long_flag = True           
             self.entry_price = close             
             self.stop_price =close-2*atr         
             
        elif signal ==0  and  self.short_flag is False and self.long_flag is False:

             row['price'] = round(close, self.prc[self.coin])
             row['order_type'] = 'OPEN_SHORT'
             row['trade_type'] = 'SHORT'
             self.short_flag = True        
             self.entry_price = close 
             self.stop_price =close+2*atr
        
        if self.long_flag is True or self.short_flag is True:
           self.stop_limit = np.abs(close-self.stop_price)/close*100            
           

           if self.long_flag is True:
                    take_profit = (1+self.stop_limit/100*3)*data['Close']
           if self.short_flag is True:
                    take_profit =(1-self.stop_limit/100*3)*data['Close']
           row['leverage'] = leverage
           row['stop_limit'] = round(self.stop_limit,3)
           row['trailing_stop'] = False
           row['stop_price'] = round(self.stop_price, self.prc[self.coin]) 
           row['take_profit'] = take_profit
           row['profit_price'] = round(take_profit, self.prc[self.coin])
        return row

 

    


   

  