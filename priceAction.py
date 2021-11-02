import pandas as pd
import numpy as np 
from indicator import Indicator
import talib 
class  PriceAction():
    def __init__(self):
        self.Indicator = Indicator()
       

        self.df = None
        self.position = None

        self.long_flag = False
        self.short_flag = False

        self.buy_point = None
        self.sell_point = None
        self.range = 14
        
        self.trade_price = None
        self.stop_price = None
        self.profit_price = None
        self.trade_len = 0
        self.check_len = 13
        self.signal_time = 0
        
        self.signal = None
        self.trend = None
        self.stop_limit = None
        self.leverage = 2
        self.candle_start = 'Open'
        self.candle_end   = 'Close'
        self.entry_point = None
        self.max_inde = 0
        self.min_index = 0
        self.percentage =0
        self.max_ = 0
        self.min_ =0
        self.ratios = [0, 0.236, 0.382, 0.5 , 0.618, 0.786,1]

    def _getSignal(self,df):
         self.df = self.Indicator._priceActionIndicators(df)
         return  self._signal(self.df)
    def _signal(self,df):
         
        '''set data'''
        data = df.iloc[-1].to_dict()
        close  = df.iloc[-1].Close
       
        row ={'Time':data['Time'],'position':np.nan,'open_position':np.nan, 'close_position':np.nan,
        'open_long':np.nan,'close_long':np.nan,'open_short':np.nan,
        'close_short':np.nan,'stop_price':np.nan, 'trailing_stop':np.nan,
                'leverage':np.nan,'take_profit':np.nan, 'stop_limit':np.nan}
        

        
        atr =talib.ATR(df.High, df.Low, df.Close, timeperiod=14).tolist()
        self._pSetter(df)

        if close<self.sell_point:
            self.signal = 0
        elif close>self.buy_point:
            self.signal = 1
        else:
            self.signal = None

        self.trend = 2    
        if self._miMaxRatio(df, self.check_len)<0.34:
              self.trend = None
        

        if self.signal == 1 and self.short_flag is True:
            row['close_short'] = data['Close']
            self.short_flag = False
            self.trade_len = 0
            self.entry_point =None
            
            row['position'] = 'CLOSE_SHORT'
            row['close_position'] = 'CLOSE_SHORT'

        elif self.signal==0 and self.long_flag is True:
            row['close_long'] = data['Close']
            self.long_flag = False
            self.entry_point = None
           
            self.trade_len = 0
            row['position'] = 'CLOSE_LONG'
            row['close_position'] = 'CLOSE_LONG'
        else:
            row['close_position'] =  None
        
        if  self.long_flag is True or self.short_flag is True:
                    self.trade_len +=1
        if self.long_flag is False and self.short_flag is False:
                  self.entry_index = None

        if self.signal == 1 and self.trend in [1,2] and self.long_flag is False:
             row['open_long'] = data['Close']
             self.long_flag = True
             self.entry_point = data['Close']
             self.entry_index = df.tail(1).index[-1]
             
             self.trade_len = 1             
           

            # self.sell_point =             
             self.stop_price = data['Close']-atr[-1]*1.21
             # min(max(data['Close']-atr[-1]*1.5,df[-3:-1]['Close'].min()),data['Close']*(1-.0013))
             
             row['open_position'] = 'OPEN_LONG'
             row['position'] = 'OPEN_LONG'
        elif self.signal == 0 and self.trend in [0,2] and self.short_flag is False:

             row['open_short'] = data['Close']
             self.short_flag = True 
             
             self.entry_point = data['Close']
             self.entry_index = df.tail(1).index[-1]
             self.trade_len=1         
            
             self.stop_price =data['Close']+atr[-1]*1
             #max(min(data['Close']+atr[-1]*1.5 ,df[-3:-1]['Close'].max()),data['Close']*(1.0013))       
            # self.buy_point =df[-5:-1]['Open'].max()
              
             row['open_position'] = 'OPEN_SHORT'
             row['position'] = 'OPEN_SHORT'
        else:

            row['open_position'] = None
            
        

        if self.long_flag is True or self.short_flag is True:
           self.stop_limit = np.abs(data['Close']-self.stop_price)/data['Close']*100            
           self.leverage  =   max(min(np.ceil(0.89/self.stop_limit) ,5),2)

           take_profit = None
           if   False: # 
                if self.long_flag is True:
                     take_profit = (1+self.stop_limit/100*3)*data['Close']
                if self.short_flag is True:
                     take_profit =(1-self.stop_limit/100*3)*data['Close']
           row['leverage'] = self.leverage
           row['stop_limit'] = self.stop_limit
           row['stop_price'] = self.stop_price*(1.0005) if self.short_flag is True else self.stop_price*(1-0.0005)
           row['take_profit'] = take_profit
        
      
        
        
        return row

    def _longBox(self, df):
       
        trade_range = self.trade_len+14
        df= df.tail(3000).reset_index(drop=True)
        self.max_index = df[-trade_range:-1]['Close'].idxmax()
        self.min_index = df[-trade_range:-1]['Close'].idxmin()

        max_ = df[-trade_range:-1]['Close'].max()
        min_  = df[-trade_range:-1]['Close'].min()
        
        
        min_max_ratio = (max_-min_)/min_*100

        sel_level = '0.236' 
        buy_level = '0.786'
        if min_max_ratio >4:

            sel_level = '0.236' 
            buy_level = '0.786' 
            tresh = 0.003
        else:
            # sel_level =  '0.382'
            # buy_level =  '0.618'
            tresh = 0.0005
        fib_levels = self._calculateFib(min_, max_ )
        
        
        if self.max_index>self.min_index:
            
                self.buy_point =  max_
                self.sell_point =  fib_levels[sel_level]*(1-tresh)
                
        elif self.max_index<self.min_index:
                
                self.sell_point = min_
                self.buy_point = fib_levels[buy_level]*(1+tresh)
    def _calculateFib(self,  min_, max_):
        
               
        levels = {}
        diff = max_-min_
        for i in self.ratios:
            levels[str(i)]= max_-i*diff
        return levels    
     
    def _pSetter(self,df):

        trade_ratio = np.abs(self.entry_point-df.iloc[-2].Close)/self.entry_point*100 if self.entry_point is not None else 5
        df= df.tail(3000).reset_index(drop=True)
        trade_range = max(self.trade_len+3, 5)
        
        self.max_index = df[-trade_range:-1]['Close'].idxmax()
        self.min_index = df[-trade_range:-1]['Close'].idxmin()
        max_ = df[-trade_range:-1]['Close'].max()
        min_  = df[-trade_range:-1]['Close'].min()

        self.percentage = (max_-min_)/min_*100

        if self.trade_len >7 and self.percentage>0.55:          
             
            self._longBox(df)    
        else:
            if self.max_index>self.min_index:
                r =1  if  self._candleType(df.iloc[self.max_index-1]) == 'BULL' else 2 
                
                if self.trade_len>5 or self.sell_point is None :
                   self.sell_point = min(df.iloc[self.max_index-r].Open, df.iloc[self.max_index-r].Close)*(1-0.0003)
                
                self.buy_point  = max_ 
                self.stop_price = max_
            elif self.max_index<self.min_index:
                r =1  if  self._candleType(df.iloc[self.max_index-1]) == 'BEAR' else 2 
                
                if self.trade_len>5 or self.buy_point is None:
                  self.buy_point = max(df.iloc[self.min_index-r].Open, df.iloc[self.min_index-r].Close)*(1+0.0003)
                self.sell_point  = min_ 
                self.stop_price = min_

    def _miMaxRatio(self, df, check_len):
    
        r =(df.tail(check_len).Close.max()-df.tail(check_len).Close.min())/df.tail(check_len).Close.min()*100  
        return r 
  
    def _candleType(self, row):
        candle_length= np.abs(row['High']-row['Low'])
        body_length= np.abs(row['Open']-row['Close'])
        stick_body_ratio= body_length/candle_length*100
        direction=  'BULL' if  row['Open']<row['Close'] else 'BEAR'
        direction=  'DOJI' if stick_body_ratio<5 else  direction
        return direction

              















