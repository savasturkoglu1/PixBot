import pandas as pd 
from indicator import Indicator
import numpy as np 
class Signals:
    def __init__(self):
       
        self.Indicator = Indicator()
        
        ## 
        self.df = None
        self.data = None
        ## sgnals
        self.strategy = None
        self.ema_strategy = None
        self.main_signal = None
        self.signal_filter = None
        self.ema_long_flag = False
        self.ema_short_flag = False
        self.trend      = None

        

        self.signal_price = None
        self.price_signal = None

        ## flasgs
        self.long_flag = False
        self.short_flag = False

        # trade params
        self.stop_limit = 2
        self.leverage   = 5
        self.stop_price = None
        self.take_profit = None
        self.trailing_stop = None

        self.till_prev= None
        ## pmax 
        self.pmax=None
        self.dr=1
        self.obs = pd.DataFrame()
        self.row = None
        self.om  = {}
        self.prev_close = None
       
         
        
   
    def _getSignal(self,df, params):
       
        #print(params)
        ind = self.Indicator._calcIndicator(df, **params)      
       
        return self._signal(ind, **params)
       
        

  
    def _signal(self,ind , **kwargs):
        data = ind.iloc[-1].to_dict()
        self.row ={
        'Time':data['Time'],'position':np.nan,
        'open_long':np.nan,'close_long':np.nan,'open_short':np.nan,
        'close_short':np.nan,'stop_price':np.nan,'trailing_stop':np.nan,
         'leverage':np.nan,'take_profit':np.nan, 'stop_limit':np.nan}
          #'Time':data['Time'],'Close':data['Close'],'High':data['High'],'Low':data['Low'],'Open':data['Open'],
        
        close = data['Close']
        ## trend
        
        if kwargs['trend_type'] == 'EMA':            
            if data['kairi_ema']>0.2 :
                    if data['trend_long']>data['trend_short']:
                        self.trend=0
                    if  data['trend_short']> data['trend_long']:
                        self.trend = 1                
            else:
                    self.trend = None    

           
           
                    
        elif kwargs['trend_type'] == 'MAPRICE':            
            if data['trend_long']>close:
                        self.trend=0
            if  close> data['trend_long']:
                        self.trend = 1
        elif kwargs['trend_type'] == 'ROCEMA144':
            if  data['roc_ema']>0.1:                    
                    self.trend=1
            elif  data['roc_ema']<-0.1:
                    self.trend =0
            else:
                self.trend = None 
                 
        else:
            self.trend = 2
        # if data['trend_long']>close:
        #                 self.trend=0
        # if  close> data['trend_long']:
        #                 self.trend = 1
        if data['adx_trend'] >30:
               self.trend = 2

   

        ## signal filter
       
        
        if kwargs['signal_filter'] == 'ADX':

            if  data['adx_pos']>data['adx_neg'] and data['adx']>15:
                    
                    self.signal_filter=1
            elif  data['adx_pos']<data['adx_neg'] and data['adx']>15:
                    self.signal_filter =0  
            else:
                self.signal_filter = None
        

        elif kwargs['signal_filter'] == 'PPO':
    
            if  data['ppo']>0:
                    
                    self.signal_filter=1
            elif  data['ppo']<0:
                    self.signal_filter =0  
            else:
                self.signal_filter = None
   
        elif kwargs['signal_filter'] == 'ROC':
        
            if  data['roc']>0:
                    
                    self.signal_filter=1
            elif  data['roc']<0:
                    self.signal_filter =0  
            else:
                self.signal_filter = None
        elif kwargs['signal_filter'] == 'RSI':
        
            if  data['rsi']>60:
                    
                    self.signal_filter=1
            elif  data['rsi']<40:
                    self.signal_filter =0  
            else:
                self.signal_filter = None

        ## treshold filter for only ema strategy
        elif kwargs['signal_filter'] == 'TRS':            
          
            self.signal_filter = 2 if np.abs(data['ema_short']-data['ema_mid'])/data['ema_mid']*100>0.30 else None
        else:
            self.signal_filter =2

        ## macd signal
        if kwargs['strategy'] == 'MACD':
            if kwargs['macd_type'] == 'soft':
                if data['macd']>data['macd_signal'] and self.signal_filter in [1,2]:
                    self.main_signal = 1
                    
                    
                elif  data['macd']<data['macd_signal'] and self.signal_filter in [0,2]:
                    self.main_signal = 0
                    
                else:
                    self.main_signal = None
                    

            if  kwargs['macd_type'] == 'hard': 

                if data['macd']>data['macd_signal'] and self.signal_filter in [1,2] and data['macd']<0:
                    self.main_signal = 1
                    # self.signal_price = close
                    # self.wait = 1
                    
                elif  data['macd']<data['macd_signal'] and self.signal_filter in [0,2] and data['macd']>0:
                    self.main_signal = 0
                    # self.signal_price = close
                    # self.wait = 1
                else:
                    self.main_signal = None
                    # self.signal_price = None
                    # self.wait = None
        ## ema signal
        
        if kwargs['strategy'] == 'MA':
            
            if self.signal_filter in [1,2] and data['ema_short'] > data['ema_mid'] :
                self.main_signal = 1

            elif self.signal_filter in [0,2] and data['ema_short'] < data['ema_mid']:
                self.main_signal = 0

            else:
                self.main_signal = None 
        
        if kwargs['strategy'] == 'PMAX':
            self._pMax(data, **kwargs)

        if kwargs['strategy'] == 'TILLSON':
            if self.till_prev is None:
                self.till_prev = data['till']
                self.main_signal = None
            else:
               
                if data['till']>self.till_prev and self.signal_filter in [1,2]:
                    self.main_signal =1
                    
                if data['till']< self.till_prev and self.signal_filter in [0,2]:
                    self.main_signal = 0 
                self.till_prev = data['till'] 

        ##price filter 
        ## decision

        if  self.trend in [1,2]  and self.main_signal==1  and self.long_flag is False and self.short_flag is False :
           # if self._priceFilter(data, **kwargs) is True:
                self.long_flag = True                
                self.row['open_long'] = close
                self.row['position'] = 'OPEN_LONG'
                self._tradeStrategy(data,**kwargs)
                #print(mark,'time:',datetime.utcfromtimestamp(int(data['Time']//1000)).strftime("%Y-%m-%d %H:%M"), {k: v for k, v in kwargs.items() if v==v}, 'long')
                

        if self.trend in [0,2] and self.main_signal ==0 and   self.short_flag is False and self.long_flag is False:
           # if self._priceFilter(data, **kwargs) is True:
                self.short_flag = True
                self.row['open_short'] = close
                self.row['position'] = 'OPEN_SHORT'
                self._tradeStrategy(data,**kwargs)
                #print(mark,'time:',datetime.utcfromtimestamp(int(data['Time']//1000)).strftime("%Y-%m-%d %H:%M"), {k: v for k, v in kwargs.items() if v==v}, 'short')
            
        if self.main_signal == 0  and self.long_flag is True:
            self.long_flag = False 
            self.row['close_long'] =  close 
            self.row['position'] = 'CLOSE_LONG' 
 
        if self.main_signal == 1  and self.short_flag is True:
            
            self.short_flag = False
            self.row['close_short'] =  close
            self.row['position'] = 'CLOSE_SHORT' 
        
        
         ## trade strategy
        #if self.long_flag or self.short_flag:
        self.prev_close = close
        return self.row
    def _tradeStrategy(self,data,**kwargs):
       
        # if kwargs['stop_indicator'] == 'bb':
        #     if self.long_flag is True:
        #         self.stop_price = data['bb_lower']
        #     if self.short_flag is True:
        #         self.stop_price = data['bb_upper']    

        if True: #kwargs['stop_indicator'] == 'atr':
            if self.long_flag is True:
                self.stop_price = data['Close']-2*data['atr']
            if self.short_flag is True:
                self.stop_price = data['Close']+2*data['atr']
            #print(data['atr'], self.stop_price)

        if kwargs['stop_indicator'] != 'solid':
            self.stop_limit = np.abs(data['Close']-self.stop_price)/data['Close']*100
            
            self.leverage  =max(min(np.ceil(3/self.stop_limit) ,6),2)
          
            
        else:
            if self.short_flag is True:
                self.stop_price = 1.02*data['Close']
            if self.long_flag is True:
                self.stop_price = 0.98*data['Close']
            self.leverage = 5

        if  kwargs['trailing_stop'] is True: #True: #
            self.trailing_stop = self.stop_limit
        else:
            self.trailing_stop = None
        if  True: #kwargs['take_profit']  is 
            if self.long_flag is True:
                self.take_profit = (1+self.stop_limit/100*2.5)*data['Close']
            if self.short_flag is True:
                self.take_profit = (1-self.stop_limit/100*2.5)*data['Close']
        else:
            self.take_profit = None
       # self.dec = len(str(data['Close']).split('.')[1])
        self.row.update({
            'stop_price':self.stop_price,
            'trailing_stop':self.trailing_stop,           
            'leverage':self.leverage,
            'take_profit':self.take_profit,
            'stop_limit':self.stop_limit })
                
    def _priceFilter(self,data, **kwargs):
        signal = True
        if  kwargs['price_filter'] is True: #
            if self.prev_close is not None:
                if self.main_signal == 1   :
                    if data['Close']> self.prev_close:         
                      signal = True
                      
                    else:
                        signal = False
                        #self.prev_close = data['Close']
                elif self.main_signal ==0 :
                    if data['Close']< self.prev_close:
                        signal = True
                        
                    else:
                         signal = False
                         #self.prev_close = data['Close']
                else:
                    #self.prev_close = None
                    signal = False
                
                return signal
                      
            else:
                #self.signal_price = data['Close']
                return False
        else:
            return signal

    def _pMax(self, data, **kwargs):
        # ma = data['pmax_ma']
        # atr = data['pmax_atr']

        
        
        if self.dr ==1:
            if self.pmax is None:
                self.pmax = data['pmax_l']

            else:
                if data['pmax_ma']>self.pmax:
                    self.pmax = max(self.pmax,data['pmax_l'])
                    self.main_signal = 1                    
                else:                    
                    self.pmax=data['pmax_s']
                    self.dr = -1
                    self.main_signal = 0          
        elif self.dr ==-1:
            if self.pmax is None:
                self.pmax = data['pmax_s']                
            else:
                if data['pmax_ma']<self.pmax:
                    self.pmax=min(self.pmax, data['pmax_s'])
                    self.main_signal = 0                     
                else:                    
                    self.pmax= data['pmax_l']
                    self.dr = 1
                    self.main_signal = 1
           
