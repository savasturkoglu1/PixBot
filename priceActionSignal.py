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
        self.range = 9
        
        self.trade_price = None
        self.stop_price = None
        self.profit_price = None
        self.trade_len = 0
        self.check_len = 34
        self.signal_time = 0
        
        self.signal = None
        self.trend = None
        self.stop_limit = None
        self.leverage = 2
        self.candle_start = 'Open'
        self.candle_end   = 'Close'
        self.entry_point = None


    def _getSignal(self,df):
         self.df = self.Indicator._priceActionIndicators(df)
         return  self._signal(self.df)
    def _signal(self,df):
            

        '''df pprocess'''
        df = self.Indicator._priceActionIndicators(df)
        
        df = self._candleDataExtraction(df)
        df = df[-200:].copy().reset_index()
         
        '''set data'''
        data = df.iloc[-1].to_dict()
        close  = df.iloc[-1].Close
        candle_close  = True if (data['CloseTime']+1)%300000 ==0 else False
        row ={'Time':data['Time'],'position':np.nan,
        'open_long':np.nan,'close_long':np.nan,'open_short':np.nan,
        'close_short':np.nan,'stop_price':np.nan, 'trailing_stop':np.nan,
                'leverage':np.nan,'take_profit':np.nan, 'stop_limit':np.nan}
        

        ''' indicators '''
        # trend_short = data['trend_short']
        # trend_long= data['trend_long']
        # kema = data['kri_ema']
        # adx = data['adxm']
        rsi = data['rsi']

        ''' get candle stick pattern signal '''
        csp_signal = None #self._candlePattern(df[-3:]) if candle_close is True else None

        
        
        self._pointSetter(df)
       
                

        if self.sell_point is not None:
         
            if  close<self.sell_point or csp_signal == 'BEARISH':
                                        
                    self.signal = 0
                    self.signal_time +=1
                    
            else:
                self.signal_time = 0
                self.signal = None 
                if candle_close is True and self.long_flag is True:
                    self.trade_len +=1 
        
        elif self.buy_point is not None:

            if  close>self.buy_point or csp_signal == 'BULLISH': 
                if True: 
                    self.signal = 1
                    self.signal_time +=1
            else:
                self.signal_time = 0
                self.signal = None               
                
                if candle_close is True and self.short_flag is True:
                    self.trade_len +=1 


        
        
        if  self.signal_time<2:
              self.signal = None
       
        # if rsi >60:
        #     self.trend = 1
        # elif rsi<40:
        #     self.trend = 0
        # else:
        self.trend = 2    
        if self._miMaxRatio(df, self.check_len)<1:
              self.trend = None
        

        if self.signal == 1 and self.short_flag is True:
            row['close_short'] = data['Close']
            self.short_flag = False
            self.trade_len = 0
            self.entry_point =None
            
            row['position'] = 'CLOSE_SHORT'
            

        elif self.signal==0 and self.long_flag is True:
            row['close_long'] = data['Close']
            self.long_flag = False
            self.entry_point = None
           
            self.trade_len = 0
            row['position'] = 'CLOSE_LONG'
            

        elif self.signal == 1 and self.trend in [1,2] and self.long_flag is False:
             row['open_long'] = data['Close']
             self.long_flag = True
             self.entry_point = data['Close']
             
             self.trade_len = 0
             self.buy_point = None
             self.signal_time = 0
             self.sell_point = df[-5:-1]['Close'].min()
            
             self.stop_price = df[-3:-1]['Close'].min()
             

             row['position'] = 'OPEN_LONG'
        elif self.signal == 0 and self.trend in [0,2] and self.short_flag is False:
             row['open_short'] = data['Close']
             self.short_flag = True 
             
             self.entry_point = data['Close']
             self.trade_len=0 
             self.signal_time = 0
             self.sell_point = None
             self.stop_price =df[-3:-1]['Open'].max()  

            
             self.buy_point =df[-5:-1]['Open'].max()
              
             

             row['position'] = 'OPEN_SHORT'
            
        

        if self.long_flag is True or self.short_flag is True:
           self.stop_limit = np.abs(data['Close']-self.stop_price)/data['Close']*100            
           self.leverage  =   max(min(np.ceil(1/self.stop_limit) ,5),2)

           take_profit = None
           if   True: # 
                if self.long_flag is True:
                     take_profit = (1+self.stop_limit/100*3)*data['Close']
                if self.short_flag is True:
                     take_profit =(1-self.stop_limit/100*3)*data['Close']
           row['leverage'] = self.leverage
           row['stop_limit'] = self.stop_limit
           row['stop_price'] = self.stop_price*(1.001) if self.short_flag is True else self.stop_price*(1-0.001)
           row['take_profit'] = take_profit
        
      
        
        
        return row
        
    def _pointSetter(self, df):
        
        data = df.iloc[-1].to_dict()
        close = data['Close'] 
        trade_range =7 if self.short_flag is False and self.long_flag is False else   max(self.trade_len,3)
        
        
        sp =np.abs(close-df.iloc[-2].Open) / close *100
        

      
        point_range = -2 if sp< 1 else -1 
        point_range = -2 if self.trade_len<4 else point_range
        if self.trade_len>13:
            point_range = -3
        if self.trade_len>20:
            point_range = -5
        if self.trade_len>30:
            point_range = -6
        if self.trade_len >60:
            point_range  -8
        

       
        max_index = df[-trade_range:]['Close'].idxmax()
        min_index = df[-trade_range:]['Close'].idxmin()

        max_ = df.loc[max_index].Close
        min_  = df.loc[min_index].Close
        last_index = df.index[-1]
        
        bp = max(df.loc[min_index+point_range+1][self.candle_start],df.iloc[min_index+point_range+1][self.candle_end])

        sp = min(df.loc[max_index+point_range+1][self.candle_start], df.iloc[max_index+point_range+1][self.candle_end])
        
        trade_ratio = np.abs(self.entry_point-close)/self.entry_point*100 if self.entry_point is not None else 1
        if self.buy_point is None and self.sell_point is None:
            if min_index>max_index :
                self.buy_point =max(bp, min_*1.003)
                
            else:
                self.sell_point = min(sp, max_*(1-0.003))
        if self.sell_point is not None:  
            if trade_ratio>0.4 :             
               self.sell_point = min(sp, max_*(1-0.003))
             
               
        if self.buy_point is not  None:
            if trade_ratio>0.4 : 
               self.buy_point = max(bp, min_*1.003)  


    def _miMaxRatio(self, df, check_len):
    
        r =(df.tail(check_len).Close.max()-df.tail(check_len).Close.min())/df.tail(check_len).Close.min()*100  
        return r 
    # def _signal(self,df):
    #     df = df[-25:].copy().reset_index()
    #     df = self._candleDataExtraction(df)
    #     data = df.iloc[-1].to_dict()
    #     candle_close  = True if (data['CloseTime']+1)%300000 ==0 else False
    #     row ={'Time':data['Time'],'position':np.nan,
    #     'open_long':np.nan,'close_long':np.nan,'open_short':np.nan,
    #     'close_short':np.nan,'stop_price':np.nan, 'trailing_stop':np.nan,
    #             'leverage':np.nan,'take_profit':np.nan, 'stop_limit':np.nan}
        
    #     trend_short = data['trend_short']
    #     trend_long= data['trend_long']
    #     kema = data['kri_ema']
    #     adx = data['adxm']


    #     csp_signal = None#self._candlePattern(df[-3:]) if candle_close is True else None

    #     close  = df.iloc[-1].Close
    #     trade_range = 9 if self.short_flag is False and self.long_flag is False else  min(self.range, max(self.trade_len,3))
    #     min_ = df.tail(trade_range).Close.min()
    #     max_ = df.tail(trade_range).Close.max()
    #     sp =np.abs(close-df.iloc[-2].Open) / close *100

    #     point_range = -2 if sp<0.89 else -1 
    #     point_range = -2 if self.trade_len<4 else point_range
    #     if self.trade_len>13:
    #         point_range = -3
    #     if self.trade_len>30:
    #         point_range = -5
    #     if self.trade_len >60:
    #         point_range  -10     

        
        

    #     if self.buy_point is None and self.sell_point is None:

    #         sdf = df[-trade_range:-1].copy()
    #         max_index =  sdf['Close'].argmax()
    #         min_index =  sdf['Close'].argmin()
    #         if max_index<min_index:
    #             self.buy_point =max(sdf.iloc[min_index+point_range+1,:][self.candle_start], sdf.iloc[min_index+point_range+1,:][self.candle_end])
    #         else:
    #             self.sell_point =min(sdf.iloc[max_index+point_range+1,:][self.candle_start], sdf.iloc[max_index+point_range+1,:][self.candle_end])
    #         # if close== min_:
    #         #     self.buy_point =   max(df.iloc[-2][self.candle_start], df.iloc[-2][self.candle_end]) #max(df.iloc[-2][self.candle_start], df.iloc[-2][self.candle_end])  if sp<0.3 else
                
    #         # if close==max_:
    #         #     self.sell_point =   min(df.iloc[-2][self.candle_start], df.iloc[-2][self.candle_end])   
                

    #     elif self.sell_point is not None:
    #         if close == max_ : #and self.trade_len>5
    #             self.sell_point =  min(df.iloc[point_range][self.candle_start], df.iloc[point_range][self.candle_end])  
    #             #self.stop_price = data['High']
    #             if candle_close is True:
    #                 self.trade_len +=1 
    #             self.signal = None
    #             self.signal_time = 0
    #         elif  close<self.sell_point or csp_signal == 'BEARISH':
                                       
    #                 self.signal = 0
    #                 self.signal_time +=1
                    
    #         else:
    #             self.signal_time = 0
    #             self.signal = None
    #             sdf = df[-trade_range:-1].copy()
    #             mid =  sdf['Close'].argmax()
    #             self.sell_point = min(sdf.iloc[mid+point_range+1,:][self.candle_start], sdf.iloc[mid+point_range+1,:][self.candle_end])  
    #             if candle_close is True:
    #                 self.trade_len +=1 
        
    #     elif self.buy_point is not None:
    #         if close == min_ : #and self.trade_len>5
    #             self.buy_point =  max(df.iloc[point_range][self.candle_start], df.iloc[point_range][self.candle_end])  
    #             #self.stop_price = data['Low']
    #             if candle_close is True:
    #                 self.trade_len +=1  
    #             self.signal = None
    #             self.signal_time = 0
    #         elif  close>self.buy_point or csp_signal == 'BULLISH': 
                    
    #                 self.signal = 1
    #                 self.signal_time +=1
    #         else:
    #             self.signal_time = 0
    #             self.signal = None
    #             sdf = df[-trade_range:-1].copy()
    #             mid = sdf['Close'].argmin()
                
    #             self.buy_point = max(sdf.iloc[mid+point_range+1,:][self.candle_start], sdf.iloc[mid+point_range+1,:][self.candle_end]) 
                
    #             if candle_close is True:
    #                 self.trade_len +=1 


        
      
    #     self.trend = 2
        
    #     if  self.signal_time<2:
    #           self.signal = None
    #     if (df.tail(self.check_len).Close.max()-df.tail(self.check_len).Close.min())/df.tail(self.check_len).Close.min()*100<0.7:
    #           self.trend = None

    #     if self.signal == 1 and self.short_flag is True:
    #         row['close_short'] = data['Close']
    #         self.short_flag = False
    #         self.trade_len = 0
    #         row['position'] = 'CLOSE_SHORT'
            

    #     elif self.signal==0 and self.long_flag is True:
    #         row['close_long'] = data['Close']
    #         self.long_flag = False
    #         self.trade_len = 0
    #         row['position'] = 'CLOSE_LONG'
            

    #     elif self.signal == 1 and self.trend in [1,2] and self.long_flag is False:
    #          row['open_long'] = data['Close']
    #          self.long_flag = True
           
    #          self.buy_point = None
    #          self.trade_len = 0

    #          self.signal_time = 0
    #          self.sell_point = df.tail(trade_range)['Close'].min()
    #          #mid =  df.tail(trade_range)['Close'].argmax()
    #          #min(df.tail(trade_range).iloc[mid,:][self.candle_start], df.tail(trade_range).iloc[mid,:][self.candle_end]) 
    #          self.stop_price = min(df.iloc[-2]['High'], df.iloc[-2]['Low'])
             

    #          row['position'] = 'OPEN_LONG'
    #     elif self.signal == 0 and self.trend in [0,2] and self.short_flag is False:
    #          row['open_short'] = data['Close']
    #          self.short_flag = True 
    #          self.sell_point = None
    #          self.trade_len=0 
    #          self.signal_time = 0

    #          self.stop_price =max(df.iloc[-2]['High'], df.iloc[-2]['Low'])   

            
    #          self.buy_point =df.tail(trade_range)['Close'].max()
              
             

    #          row['position'] = 'OPEN_SHORT'
            
        

    #     if self.long_flag is True or self.short_flag is True:
    #        self.stop_limit = np.abs(data['Close']-self.stop_price)/data['Close']*100            
    #        self.leverage  =   max(min(np.ceil(1/self.stop_limit) ,5),2)

    #        take_profit = None
    #        if   True: # 
    #             if self.long_flag is True:
    #                  take_profit = (1+self.stop_limit/100*2)*data['Close']
    #             if self.short_flag is True:
    #                  take_profit =(1-self.stop_limit/100*2)*data['Close']
    #        row['leverage'] = self.leverage
    #        row['stop_limit'] = self.stop_limit
    #        row['stop_price'] = self.stop_price*(1.0007) if self.short_flag is True else self.stop_price*(1-0.0007)
    #        row['take_profit'] = take_profit
        
    #     ### filter
        
        
    #     return row
       

    def _setPoint(self,df, trade_range, point_range, side = 'BUY'):
         mid =  df.tail(trade_range)['Close'].argmax()                
         trade_point = min(df.tail(trade_range).iloc[mid+point_range+1,:][self.candle_start], df.tail(trade_range).iloc[mid+point_range+1,:][self.candle_end])  
         return trade_point
    def _candlePattern(self, df):
        
        
        df = self._candleDataExtraction(df)
        direction = None

        '''  adata process '''
        opens = df.tail(3).Open.to_list()
        closes = df.tail(3).Close.to_list()
        

        ''' tree soders '''
        if df.stick_body_ratio.min()>60:
            if df['direction'].to_list() ==3*['BULL']:
                direction = 'BULLISH'
            if df['direction'].to_list() ==3*['BEAR']:
                direction = 'BEARISH'
        
        return direction

    def _candleDataExtraction(self, df):

        df['direction'] = df.apply(lambda x :'BULL' if  x['Open']<x['Close'] else 'BEAR', axis=1 )
        df['candle_length'] = df.apply(lambda x : np.abs(x['High']-x['Low']), axis=1 )
        df['candle_body'] = df.apply(lambda x : np.abs(x['Open']-x['Close']), axis=1 )
        df['stick_body_ratio'] = df.apply(lambda x : x['candle_body']/x['candle_length']*100, axis=1 )

        return df

              















