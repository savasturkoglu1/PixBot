
import xgboost as xgb

import pickle
import pandas as pd 
import numpy as np
from datetime import datetime
import mplfinance as mpf
import talib
class CspSignal:
    
    def __init__(self):
        
       # self.model_path = "/home/savas/Desktop/BotDev/backtest/data/xgb_ETHUSDT.model"
        self.model_path = "/home/savas/Desktop/PixBot/source/model/xgb_large_withdir_20000.model"
        self.model = None
        
        self.cols = ['stick_body_ratio', 'candle_length_perc',
       'body_length_perc',  'body_from_top', 'body_from_bottom','prev_close_ratio','prev_open_ratio', 'direction']
        

        self.short_flag = False
        self.long_flag = False
        self.signal = None
        
        self.stop_limit = None
        self.stop_price = None
        self.leverage = None
        

       

        self._model()
        
    def _model(self):    

        self.model = xgb.XGBClassifier()
        booster = xgb.Booster()
        booster.load_model(self.model_path)
        #model = xgb.Booster(model_file=file_name)
        self.model._Booster = booster
   
    def _candle(self,df):
        data=[]
    
        for i,row in enumerate( df.to_dict('records')):
                prev_row = df.iloc[i-1] if i>0 else None
                row['direction'] =   1 if  row['Open']<row['Close'] else -1
                row['candle_length'] =  np.abs(row['High']-row['Low'])
                row['candle_body'] =  np.abs(row['Open']-row['Close'])
                row['stick_body_ratio'] =  row['candle_body']/row['candle_length']
                row['candle_length_perc'] =  (row['High']-row['Low'])/row['Low']
                #row['candle_length_perc'] = row['candle_length_perc']  if row['direction'] == 1 else -1*row['candle_length_perc']
                row['body_length_perc'] =  np.abs(row['Close']-row['Open'])/row['Open']
                
                row['prev_open_ratio'] = (row['Open']-prev_row['Close'])/prev_row['Close'] if prev_row is not None else np.nan
                row['prev_close_ratio'] = (row['Close']-prev_row['Open'])/prev_row['Open'] if  prev_row is not None else np.nan
                if row['direction'] == 1:
                        row['body_from_top'] =  np.abs(row['High']-row['Close'])/row['Close']
                        row['body_from_bottom'] =  np.abs(row['Open']-row['Low'])/row['Open']
                else:
                        row['body_from_top'] =  np.abs(row['High']-row['Open'])/row['Open']
                        row['body_from_bottom'] =  np.abs(row['Close']-row['Low'])/row['Close']
                data.append(row)
        return pd.DataFrame.from_dict(data)
    

    def _signal(self,df):
        df = self._candle(df)
        df['atr'] = atr = talib.ATR(df.High, df.Low, df.Close, timeperiod=14).tolist()
        data = df.iloc[-1].to_dict()
        close = df.iloc[-1].Close
        atr = df.iloc[-1].atr
        
        row ={'Time':data['Time'],'position':np.nan,
        'open_long':np.nan,'close_long':np.nan,'open_short':np.nan,
        'close_short':np.nan,'stop_price':np.nan, 'trailing_stop':np.nan,
                'leverage':np.nan,'take_profit':np.nan, 'stop_limit':np.nan}
        
        a = np.array(df[self.cols][-4:-1])
        a = a.ravel()
        p = self.model.predict_proba([a])
        p = p.tolist()[0]
 
        if p[0]>0.8 and data['Close']>data['Open']:
            self.signal = 0
        elif p[1]>0.84 and data['Close']<data['Open']:
            self.signal = 1
        else:
            self.signal = None


        if self.signal == 1 and self.short_flag is True:
            row['close_short'] = close
            row['position'] = 'CLOSE_SHORT'
            self.short_flag = False 

        elif self.signal==0 and self.long_flag is True:
            row['close_long'] = close
            row['position'] = 'CLOSE_LONG'
            self.long_flag = False    

        elif self.signal == 1  and self.long_flag is False:
             row['open_long'] = close
             row['position'] = 'OPEN_LONG'
             self.long_flag = True           
                         
             self.stop_price = close-2*atr          
             
        elif self.signal ==0  and  self.short_flag is False:

             row['open_short'] = close
             row['position'] = 'OPEN_SHORT'
             self.short_flag = True         
                    
            
             self.stop_price =close+2*atr
            
             
       
        
        if self.long_flag is True or self.short_flag is True:
           self.stop_limit = np.abs(close-self.stop_price)/close*100            
           self.leverage  =max(min(np.ceil(3/self.stop_limit) ,7),3)
           
           take_profit = None
           if   True: # 
                # if self.long_flag is True:
                #      take_profit = (1.02)*data['Close'] #+self.stop_limit/100
                # if self.short_flag is True:
                #      take_profit =(1-.02)*data['Close'] #(1-self.stop_limit/100*3)*data['Close']
                if self.long_flag is True:
                     take_profit = (1+self.stop_limit/100*2)*data['Close']
                if self.short_flag is True:
                     take_profit =(1-self.stop_limit/100*2)*data['Close']
           row['leverage'] = self.leverage
           row['stop_limit'] = self.stop_limit
           row['trailing_stop'] = False
           row['stop_price'] = self.stop_price #*(1.001) if self.short_flag is True else self.stop_price*(1-0.001)
           row['take_profit'] = None
                   
        return row