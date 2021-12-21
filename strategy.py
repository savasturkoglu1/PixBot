

from indicator import  Indicator
from env import base_path
import pandas as pd
import numpy as np
from signals import Signals
from priceAction import PriceAction
from cspSignal import CspSignal

from candleSignal import CandleSignal
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
        self.Signal = Signals()
        self.PA = PriceAction()
        self.Trade = Trade(self.client, self.coin)
        self.Logs = Logs()
      #  self.CSP = CspSignal(self.coin)
        self.Candle  = CandleSignal()
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
        self.bot_type = 'INDICATOR' #'PACTION' # 'INDICATOR', 
        # if self.coin == 'XRPUSDT':
        #     self.bot_type = 'INDICATOR'
        # if self.bot_type == 'INDICATOR':
        #      self.rafined = pd.read_csv(base_path+'/source/rafine_ocmarket_'+self.coin+'.csv')
        #      self.strategies = pd.read_csv(base_path+'/source/strategies.csv')
    def _process(self, live ,df_1m, df_5m, df_15m, df_30m, df_1h, candle_close):

        ## set data frames
        self.df_1m = df_1m
        self.df_5m = df_5m
        self.df_15m = df_15m
        self.df_30m = df_30m
        self.df_1h = df_1h
        self.live  = live
        self.candle_close = candle_close

        #self.Trade._live(live)
        # if self.bot_type=='PACTION':
        #        self._priceActionSignals()
        # if self.bot_type=='INDICATOR':
        #        self._indicatorSignal()
        self._candleSignal()
    def _candleSignal(self):
            self.Trade._live(self.live)
            self.df = self.df_1m       
                
            

            self.position = self.Trade.position
            if self.position is None:
                self.Candle.long_flag = False
                self.Candle.short_flag = False
            
            
            params = None
              
            self.signals =  self.Candle._signal(self.df[-1000:], self.df_5m)
            params = self._tradeParams()
            
            
            print(self.coin,self.signals, params)
            if  params is not None  : 
                self.Logs._writeLog(self.coin+'-ind order params   '+ str(params)+'\n'+str(self.params))   
                self.Trade._order(**params)    
    def _cspSignal(self):
        self.Trade._live(self.live)
        self.df = self.df_5m       
            
        

        self.position = self.Trade.position
        if self.position is None:
            self.CSP.long_flag = False
            self.CSP.short_flag = False
        
        
        params = None
        if self.candle_close is True:    
           self.signals =  self.CSP._signal(self.df[-500:])
           params = self._tradeParams()
        
        
        print(self.coin,self.signals, params)
        if  params is not None  : 
           self.Logs._writeLog(self.coin+'-ind order params   '+ str(params)+'\n'+str(self.params))   
           self.Trade._order(**params)
    def _indicatorSignal(self):
        self.Trade._live(self.live)
        # self._getMarket()
        # self._getStrategy()
        self.params = {'Unnamed: 0': 58338,
                'atr_len': np.nan,
                'ema_len': np.nan,
                'ema_length': np.nan,
                'filter_period': 'FIXED',
                'ma_len': np.nan,
                'ma_type': np.nan,
                'macd_ma_type': 'EMA',
                'macd_period': '[8, 13, 8]',
                'macd_src_type': 'EMA',
                'macd_type': 'soft',
                'multipiler': np.nan,
                'pmax_ma_type': np.nan,
                'price_filter': False,
                'signal_filter': 'CCI',
                'stop_indicator': 'atr',
                'strategy': 'MACD',
                'take_profit': False,
                'till': np.nan,
                'time_frame': '5m',
                'trailing_stop': False,
                'trend_period': 144,
                'trend_type': 'FALSE',
                'unique': 'S6HEYQEX' }

        

        self.df = self.df_5m
        
            
        

        self.position = self.Trade.position
        if self.position is None:
           self.Signal.clear_trade = True
        else:
            self.Signal.clear_trade = False
        
        
        params = None
        if self.candle_close is True:    
           self.signals =  self.Signal._getSignal(self.df, self.params)
           params = self._tradeParams()
        
        
        print(self.coin,self.signals, params)
        if  params is not None  : 
           self.Logs._writeLog(self.coin+'-ind order params   '+ str(params)+'\n'+str(self.params))   
           self.Trade._order(**params)
    def _priceActionSignals(self):
        ## check trade position
        self.Trade._live(self.live)
        self.position = self.Trade.position
        if self.position is None:
           self.PA.long_flag = False
           self.PA.short_flag = False
           self.PA.trade_len = 0
           self.PA.entry_point =None               
           self.PA.entry_index = None  
           
           self.position = None
        ## get signal
        print(self.candle_close)
        if self.candle_close:
            self.signals = self.PA._getSignal(self.df_5m)
            self.close = False
            ## set order
        if self.signals is not None:
            if self.close is True:
                self.signals['close_position'] = None
                if self.signals['open_position'] == 'OPEN_LONG':
                    if self.live['Close'] < self.signals['open_long']:
                        self.signals['open_position'] = None
                    else:     
                        self.signals['open_position'] ='OPEN_LONG' 
                        self.signals['open_long'] =  self.live['Close']
                if self.signals['open_position'] == 'OPEN_SHORT':
                    if self.live['Close'] > self.signals['open_short']:
                        self.signals['open_position'] = None
                    else:     
                        self.signals['open_position'] = 'OPEN_SHORT'
                        self.signals['open_short'] =  self.live['Close']
            

            params = self._tradeParams()
            
            print(self.coin,self.signals, params)
            if params is not None:
                    self.Logs._writeLog(self.coin+'- order params   '+ str(params)+'\n'+str(self.signals)) 
                    if self.signals['close_position'] is not None:
                        self.close = True   
                                          
                    elif self.signals['open_position'] is not None:
                        self.params = None
                        self.close = False
                        
                    self.Trade._order(**params)  
    
    def _tradeParams(self):
        params=None
        if self.signals['position'] == 'CLOSE_LONG' or self.signals['position'] == 'CLOSE_SHORT':
            params=dict(
                order_type=self.signals['position'],
                trade_type='LONG' if self.signals['position'] == 'CLOSE_LONG' else 'SHORT',
                price=self.signals['close_long'] if self.signals['position'] == 'CLOSE_LONG' else self.signals['close_short'],
                
            )
        elif self.signals['position'] == 'OPEN_LONG' or self.signals['position'] == 'OPEN_SHORT':
            p = self.signals['open_long'] if self.signals['position'] == 'OPEN_LONG' else self.signals['open_short']
            params=dict(
                order_type=self.signals['position'],
                trade_type='LONG' if self.signals['position'] == 'OPEN_LONG' else 'SHORT',
                price=round(p, self.prc[self.coin]),
                stop_price =round(self.signals['stop_price'], self.prc[self.coin]),
                stop_limit =round(self.signals['stop_limit'],3),
                profit_price=round(self.signals['take_profit'], self.prc[self.coin]) if self.signals['take_profit'] is not None else None,
                leverage=self.signals['leverage'],
                take_profit = self.signals['take_profit']
            )
        
        return params
    
    def _tradeParamsPa(self):
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
                leverage=self.signals['leverage'],
                take_profit = self.signals['take_profit']
            )
        
        return params
    

    


   

  