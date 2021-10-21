

from indicator import  Indicator
from env import base_path
import pandas as pd
import numpy as np
from signals import Signals
from priceActionSignal import PriceAction
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

        self.trade_signal = None
        self.trade_count = None
        self.trade_perm = False
        self.bot_type = 'PACTION' # 'INDICATOR', 
        if self.bot_type == 'INDICATOR':
            self.rafined = pd.read_csv(base_path+'/source/rafine_ocmarket_'+self.coin+'.csv')
            self.strategies = pd.read_csv(base_path+'/source/strategies.csv')
    def _process(self, live ,df_1m, df_5m, df_15m, df_30m, df_1h):

        ## set data frames
        self.df_1m = df_1m
        self.df_5m = df_5m
        self.df_15m = df_15m
        self.df_30m = df_30m
        self.df_1h = df_1h
        self.live  = live

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

        ## get signal
        self.signals = self.PA._getSignal(self.df_5m)
        
        ## set order
        params = self._tradeParams()
        print(self.coin,self.signals, params)
        if params is not None:
                self.Logs._writeLog(self.coin+'- order params   '+ str(params)+'\n'+str(self.signals))   
                self.Trade._order(**params)  
    def _indicatorSignal(self):
        self.Trade._live(self.live)
        self._getMarket()
        self._getStrategy()

        if self.params['time_frame'] == '30m':
            self.df = self.df_30m
            self.intval = self.intval*30
        elif self.params['time_frame'] == '1h':
            self.df = self.df_1h
            self.intval = self.intval*60
        elif self.params['time_frame'] == '5m':
            self.df = self.df_5m
            self.intval = self.intval*5
        else:
            self.df = self.df_15m 
            self.intval = self.intval*15
        
            
       
        self.position = self.Trade.position
        if self.position is None:
           self.Signal.long_flag = False
           self.Signal.short_flag = False
                
        self.signals =  self.Signal._getSignal(self.df, self.params)
        params = self._tradeParams()
        
        
        
        if  params is not None and self.trade_perm is True : 
           self.Logs._writeLog(self.coin+'- order params   '+ str(params)+'\n'+str(self.params))   
           self.Trade._order(**params)
           self.trade_perm = False
           self.trade_count = None
           self.trade_signal = None

    def _tradeParams(self):
        params=None
        if self.signals['position'] == 'OPEN_LONG' or self.signals['position'] == 'OPEN_SHORT':
            params=dict(
                order_type=self.signals['position'],
                trade_type='LONG' if self.signals['position'] == 'OPEN_LONG' else 'SHORT',
                price=self.signals['open_long'] if self.signals['position'] == 'OPEN_LONG' else self.signals['open_short'],
                stop_price =round(self.signals['stop_price'], self.prc[self.coin]),
                stop_limit =round(self.signals['stop_limit'],3),
                profit_price=round(self.signals['take_profit'], self.prc[self.coin]) if self.signals['take_profit'] is not None else None,
                leverage=self.signals['leverage']
            )
        if self.signals['position'] == 'CLOSE_LONG' or self.signals['position'] == 'CLOSE_SHORT':
            params=dict(
                order_type=self.signals['position'],
                trade_type='LONG' if self.signals['position'] == 'CLOSE_LONG' else 'SHORT',
                price=self.signals['close_long'] if self.signals['position'] == 'CLOSE_LONG' else self.signals['close_short'],
                
            )
        return params
    

    def _getStrategy(self):
        r = self.rafined[self.rafined.market==self.market]
        if r.shape[0]<1:
            self.params = None
        row = r.loc[r['balance_i'].idxmax()].to_dict()
        #.tail(1).to_dict('records')[0]
        self.stg = row['strategy']
         
        self.params = self.strategies[self.strategies.unique==row['strategy']].to_dict('records')[0]


    def _updateStrategy(self, data, market):
         dt = self.rafined[(self.rafined.coin==self.coin)&(self.rafined.strategy==self.stg)&(self.rafined.market==market)]
         ky=  dt['trade_index'].idxmax()
         k=dt.loc[ky].to_dict() 
        
         d = k

         total_pnl = d['total_pnl']+data['pnl']
         trade_count = d['trade_count']+1
         profit_trade = d['profit_trade'] if data['pnl']<0 else d['profit_trade']+1
         loss_trade = d['loss_trade'] if data['pnl']>0 else d['loss_trade']+1
         profit = d['profit'] if data['pnl']<0 else d['profit']+data['pnl']
         loss = d['loss'] if data['pnl']>0 else d['loss']+data['pnl']
         max_profit = d['max_profit'] if data['pnl']<d['max_profit'] else data['pnl']

         #trade index
         trade_index = ((total_pnl)/(trade_count))*profit_trade/max(loss_trade,1)

         self.rafined.loc[ky, ['total_pnl','trade_count', 'profit_trade', 
         'loss_trade','profit', 'loss', 'max_profit', 'trade_index']] = [total_pnl, trade_count,
          profit_trade, loss_trade, profit, loss, max_profit, trade_index]


    def _getMarket(self):
        
        ind = self.Indicator._envIndicators(self.df_1h)
        row = ind.iloc[-1].to_dict()
        self.market_ind = ind
        
       
        adx = row['adxm']
        at = row['natr']
        t =None
        v=None
         
        if adx<25:
            v='low'
        
        elif adx>=25:
              v='high'

        if at<=self.atr_tresh[self.coin]:
              t='low'          
        else :
              t='high'       
        self.market = t+v
         