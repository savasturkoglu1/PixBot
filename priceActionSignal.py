import pandas as pd
import numpy as np 
from indicator import Indicator

class  PriceAction():
    def __init__(self):
        self.Indicator = Indicator()
       

        self.df = None
        self.position = None

        self.long_flag = False
        self.short_flag = False

        self.buy_point = None
        self.sell_point = None
        self.range = 5
        
        self.trade_price = None
        self.stop_price = None
        self.profit_price = None
        self.trade_len = 0
        
        self.signal = None
        self.trend = None
        self.stop_limit = None
        self.leverage = 2
        self.candle_start = 'Low'
        self.candle_end   = 'High'


    def _getSignal(self,df):
         self.df = self.Indicator._priceActionIndicators(df)
         return  self._signal(self.df[-20:])
    def _signal(self,df):
        
        data = df.iloc[-1].to_dict()

        row ={'Time':data['Time'],'position':np.nan,
        'open_long':np.nan,'close_long':np.nan,'open_short':np.nan,
        'close_short':np.nan,'stop_price':np.nan, 'trailing_stop':np.nan,
                'leverage':np.nan,'take_profit':np.nan, 'stop_limit':np.nan}
        
        trend_short = data['trend_short']
        trend_long= data['trend_long']
        kema = data['kri_ema']
        adx = data['adxm']


        csp_signal = self._candlePattern(df)

        close  = df.iloc[-1].Close
        range_ = 14 #5 if self.position is None else max(self.range, self.trade_len)
        min_ = df.tail(range_).Close.min()
        max_ = df.tail(range_).Close.max()
        sp =np.abs(close-df.iloc[-2].Low) / close *100

        p_range = -2 if sp<0.89 else -1 
        p_range = p_range if self.trade_len<15 else -3
       

        if self.buy_point is None and self.sell_point is None:
            if close== min_:
                self.buy_point =   max(df.iloc[p_range][self.candle_start], df.iloc[p_range][self.candle_end]) #max(df.iloc[p_range][self.candle_start], df.iloc[p_range][self.candle_end])  if sp<0.3 else
                self.stop_price = data['Low']
            if close==max_:
                self.sell_point =   min(df.iloc[p_range][self.candle_start], df.iloc[p_range][self.candle_end])   
                self.stop_price = data['High']

        elif self.sell_point is not None:
            if close == max_ : #and self.trade_len>5
                self.sell_point =  min(df.iloc[p_range][self.candle_start], df.iloc[p_range][self.candle_end])  
                self.stop_price = data['High']
                self.trade_len +=1 
                self.signal = None
            elif  close<self.sell_point or csp_signal == 'BEARISH':
                                       
                    self.signal = 0
            else:
                self.signal = None
                self.trade_len +=1
        
        elif self.buy_point is not None:
            if close == min_ : #and self.trade_len>5
                self.buy_point =  max(df.iloc[p_range][self.candle_start], df.iloc[p_range][self.candle_end])  
                self.stop_price = data['Low']
                self.trade_len +=1 
                self.signal = None
            elif  close>self.buy_point or csp_signal == 'BULLISH': 
                    
                    self.signal = 1
            else:
                self.signal = None
                self.trade_len +=1


        
      
        self.trend = 2

        
        if self.signal == 1 and self.trend in [1,2] and self.long_flag is False:
             row['open_long'] = data['Close']
             self.long_flag = True
           
             self.buy_point = None
             self.trade_len = 0
             self.sell_point = min(df.iloc[-2][self.candle_start], df.iloc[-2][self.candle_end])
             row['position'] = 'OPEN_LONG'
        if self.signal == 0 and self.trend in [0,2] and self.short_flag is False:
             row['open_short'] = data['Close']
             self.short_flag = True 
             self.sell_point = None
             self.trade_len=0        
             self.buy_point = max(df.iloc[-2][self.candle_start], df.iloc[-2][self.candle_end])
             row['position'] = 'OPEN_SHORT'
        if self.signal == 1 and self.short_flag is True:
            row['close_short'] = data['Close']
            self.short_flag = False
            self.trade_len = 0
            row['position'] = 'CLOSE_SHORT'

        if self.signal==0 and self.long_flag is True:
            row['close_long'] = data['Close']
            self.long_flag = False
            self.trade_len = 0
            row['position'] = 'CLOSE_LONG'

        if self.long_flag is True or self.short_flag is True:
           self.stop_limit = np.abs(data['Close']-self.stop_price)/data['Close']*100            
           self.leverage  =max(min(np.ceil(1/self.stop_limit) ,5),2)

           take_profit = None
           if   True: # 
                if self.long_flag is True:
                     take_profit = (1+self.stop_limit/100*2)*data['Close']
                if self.short_flag is True:
                     take_profit =(1-self.stop_limit/100*2)*data['Close']
           row['leverage'] = self.leverage
           row['stop_limit'] = self.stop_limit
           row['stop_price'] = self.stop_price
           row['take_profit'] = take_profit
        
        return row
       


    def _candlePattern(self, df):
        
        direction = None
        '''  adata process '''
        df['candle_length'] = df.apply(lambda x : np.abs(x['High']-x['Low']), axis=1 )
        df['candle_body'] = df.apply(lambda x : np.abs(x['Open']-x['Close']), axis=1 )
        df['stic_body_ratio'] = df.apply(lambda x : x['candle_body']/x['candle_length']*100, axis=1 )
        opens = df.tail(3).Open.to_list()
        closes = df.tail(3).Close.to_list()
        

        ''' tree soders '''
        if df.stic_body_ratio.min()>70:
            if opens == sorted(opens) and closes==sorted(closes):
                direction = 'BULLISH'
            if opens == sorted(opens , reverse=True) and closes==sorted(closes, reverse=True):
                direction = 'BEARISH'
        
        return direction

            


              















