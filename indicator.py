import talib
import ta
import pandas as pd 
import numpy as np
import ast

import json

class Indicator:

    
    def __init__(self):
        pass

    def _calcIndicator(self, df, **kwargs ):

       
        bb_upper, basis , bb_lower = talib.BBANDS(df.Close, timeperiod=20, nbdevup=2, nbdevdn=2, matype=0)
        

        ## data dict
        data = {
                'bb_dif':100 * (bb_upper - bb_lower)/bb_lower,
                'bb_upper':bb_upper,
                'bb_lower':bb_lower,
                'sma_20': basis,
                'atr':talib.ATR(df.High, df.Low, df.Close, timeperiod=5),
                'adx_trend':talib.ADX(df.High, df.Low, df.Close, timeperiod=14)
        }

       
        data['trend_short'] = getattr(talib, 'EMA')(df.Close, 55)
        data['trend_long'] = getattr(talib, 'EMA')(df.Close, 144)
        
        if kwargs['trend_type'] == 'EMA':            
            data['kairi_ema'] = np.abs(100 * (data['trend_short'] - data['trend_long'])/data['trend_long'])
            data['kairi_long']= self._kairi(df.Close, 144)
            data['kairi_short']= self._kairi(df.Close, 55)     

        elif kwargs['trend_type'] == 'ROCEMA144':
            data['roc_ema'] = talib.ROC(data['trend_long'], 21)
        
        if kwargs['strategy'] == 'MACD':
            mp=ast.literal_eval(kwargs['macd_period'])
            filter_period = mp[0]
            if kwargs['macd_src_type'] == 'DEMA':
                macd_src = talib.DEMA(df.Close, timeperiod=8)
            elif kwargs['macd_src_type'] == 'EMA':
                    macd_src = talib.EMA(df.Close, timeperiod=8)
            elif kwargs['macd_src_type'] == 'TEMA':
                macd_src = talib.TEMA(df.Close, timeperiod=8)
            elif kwargs['macd_src_type'] == 'KAMA':
                macd_src = talib.KAMA(df.Close, timeperiod=8)
            elif kwargs['macd_ma_type'] == 'ZLEMA':
                macd_src = self._zlema(df.Close)
            else :
                macd_src = df.Close
            
            macd, macdsignal, macdhist = self._MACD(macd_src, fast_length=mp[0],
         slow_length=mp[1], signal_length=mp[2], macd_ma_type=kwargs['macd_ma_type'])  
                  
            data['macd'] = macd
            data['macd_signal'] = macdsignal
            data['macd_hist'] = macdhist
        if kwargs['strategy'] == 'TILLSON':
            filter_period = kwargs['ema_len']
            data['till'] = self._tillson(df,kwargs['ema_len'], kwargs['till'])
        if kwargs['strategy'] == 'MA':
            el=ast.literal_eval(kwargs['ema_length'])
            filter_period = el[0]
            if kwargs['ma_type'] == 'ZLEMA':
                data['ema_short']=self._zlema(df.Close, el[0])            
                data['ema_mid']=self._zlema(df.Close, el[1])
            else:
                data['ema_short']=getattr(talib, kwargs['ma_type'])(df.Close, el[0])            
                data['ema_mid']=getattr(talib, kwargs['ma_type'])(df.Close, el[1]) 
             
        if kwargs['strategy'] == 'PMAX':
           if kwargs['pmax_ma_type'] == 'ZLEMA':
               data['pmax_ma'] = self._zlema(df.Close,kwargs['ma_len'])
           else:
               data['pmax_ma'] = getattr(talib, kwargs['pmax_ma_type'])((df.High+df.Low)/2, kwargs['ma_len'])
           data['pmax_atr'] = talib.ATR(df.High, df.Low, df.Close, timeperiod=kwargs['atr_len'])
           data['pmax_l']= data['pmax_ma']-data['pmax_atr']*kwargs['multipiler']
           data['pmax_s']= data['pmax_ma']+data['pmax_atr']*kwargs['multipiler']

        ## macd
        

        ## filter

        
        if kwargs['signal_filter'] == 'ADX':            
            adx = ta.trend.ADXIndicator(df.High, df.Low, df.Close, 
            window=int(filter_period) if kwargs['filter_period'] == 'DYN' else 13, fillna= False)
            data['adx'] = adx.adx()
            data['adx_neg'] = adx.adx_neg()
            data['adx_pos'] = adx.adx_pos()
        if kwargs['signal_filter'] == 'CCI':
            data['cci']=talib.CCI(df.High, df.Low, df.Close,
            timeperiod=filter_period if kwargs['filter_period'] == 'DYN' else 21)
            
        if kwargs['signal_filter'] == 'PPO':
            data['ppo'] = talib.PPO(df.Close,
            fastperiod= kwargs['ema_length'][0] if kwargs['filter_period']=='DYN' else 10,
            slowperiod=kwargs['ema_length'][1] if kwargs['filter_period']=='DYN' else 21, matype=0)
        if kwargs['signal_filter'] == 'ROC':
            data['roc'] = talib.ROC(df.Close,timeperiod=filter_period if kwargs['filter_period'] == 'DYN' else 13 )
        if kwargs['signal_filter'] == 'RSI':
            data['rsi'] = talib.RSI(df.Close,timeperiod=filter_period if kwargs['filter_period'] == 'DYN' else 13)
     
        
        
        
        for i in data.keys():
            if i not in df:
                df.assign(key=np.nan)

        for key, value in data.items():
           
            df[key] = value
                  

        return df.dropna()
    def _priceActionIndicators(self, df):
        trend_long=talib.EMA(df.Close, timeperiod=89)              
        trend_short=talib.EMA(df.Close, timeperiod=34)
       # adx=ta.trend.ADXIndicator(df.High, df.Low, df.Close, window=14, fillna= False)
        data = { 
                
              #  'bb_dif':100 * (bb_upper - bb_lower)/bb_lower,
              #  'bb_upper':bb_upper,
              #  'bb_lower':bb_lower,                                               
                'trend_long':trend_long,                 
                'trend_short':trend_short,    
                'kri_ema':np.abs(100 * (trend_short - trend_long)/trend_long),                
                'atr':talib.ATR(df.High, df.Low, df.Close, timeperiod=14),
                'adxm':talib.ADX(df.High, df.Low, df.Close, timeperiod=14),
                'rsi':talib.RSI(df.Close, timeperiod=14),
               # 'hv': self._historicalVolatility(df, 14),
                #'volume_osc':self._volOsc(df,14 )
               

                
                
            }
        for i in data.keys():
            if i not in df:
                df.assign(key=np.nan)

        for key, value in data.items():
           # print(key, print(value))
            df[key] = value
        return df   
    def _envIndicators(self, df):
       # bb_upper, basis , bb_lower = talib.BBANDS(df.Close, timeperiod=20, nbdevup=2, nbdevdn=2, matype=0)
        trend_long=talib.EMA(df.Close, timeperiod=144)              
        trend_short=talib.EMA(df.Close, timeperiod=55)
       # adx=ta.trend.ADXIndicator(df.High, df.Low, df.Close, window=14, fillna= False)
        data = { 
                
              #  'bb_dif':100 * (bb_upper - bb_lower)/bb_lower,
              #  'bb_upper':bb_upper,
              #  'bb_lower':bb_lower,                                               
                'trend_long':trend_long,                 
                'trend_short':trend_short,    
                'kri_ema':np.abs(100 * (trend_short - trend_long)/trend_long),                
                'atr':talib.ATR(df.High, df.Low, df.Close, timeperiod=14),
                'adxm':talib.ADX(df.High, df.Low, df.Close, timeperiod=14),
                'natr':self._atrDist(df),
               # 'hv': self._historicalVolatility(df, 14),
                #'volume_osc':self._volOsc(df,14 )
               

                
                
            }
        for i in data.keys():
            if i not in df:
                df.assign(key=np.nan)

        for key, value in data.items():
           # print(key, print(value))
            df[key] = value
        return df   
    def _zlema(self,src, period=13):


        EMA1= talib.EMA(src,period)
        EMA2= talib.EMA(EMA1,period)
        Difference= EMA1 - EMA2
        return EMA1 + Difference

    def _atrDist(self,df):
        g = talib.ATR(df.High, df.Low, df.Close, timeperiod=14)
        return g/df.Close*100
    def _volOsc(self, df,leng):
        i=df.Volum.to_list()
        top = np.array(sorted(i,reverse=True)[:len(i)//100]).mean()
        ema = talib.EMA(df.Volum, leng)
        return ema/top
    def _volumeOscilator(self, df, short_len, long_len):
            
            i=df.Volum.to_list()
            top = np.array(sorted(i,reverse=True)[len(i)//100:]).mean()

            
            short = talib.EMA(df.Volum, short_len)
            long_ = talib.EMA(df.Volum, long_len)
            osc = 100 * (short - long_) / long_
            return osc

    def _historicalVolatility(self, df,leng):
        df['hv'] = np.log(df['Close']/df['Close'].shift())
        r= 100*talib.STDDEV(df.hv, timeperiod=leng, nbdev=1)*np.sqrt(365)
        return r
    def _iVol(self, df, period):
        mx = talib.MAX(df.High, timeperiod=period)
        mn = talib.MIN(df.Low, timeperiod=period)
        return (mx-mn)/mn*100
    
    def _tillson(self,df,ma_length, a1):

        e1 = talib.EMA((df.High + df.Low + 2 * df.Close) / 4, ma_length)
        e2 = talib.EMA(e1, ma_length)
        e3 = talib.EMA(e2, ma_length)
        e4 = talib.EMA(e3, ma_length)
        e5 = talib.EMA(e4, ma_length)
        e6 = talib.EMA(e5, ma_length)
        c1 = -a1 * a1 * a1
        c2 = 3 * a1 * a1 + 3 * a1 * a1 * a1
        c3 = -6 * a1 * a1 - 3 * a1 - 3 * a1 * a1 * a1
        c4 = 1+ 3 * a1 + a1 * a1 * a1 + 3 * a1 * a1
        T3 = c1 * e6 + c2 * e5 + c3 * e4 + c4 * e3
        return T3


        # self.ind =  pd.DataFrame(data)
        # return self.ind
    def _MACD(self, src,  fast_length=12, slow_length=26,
        signal_length=9,macd_ma_type='EMA', signal_ma_type = 'EMA'):
        if macd_ma_type == 'ZLEMA':
            fast_ = self._zlema(src, fast_length)
            slow_ = self._zlema(src, slow_length)
        else:
            fast_ =getattr(talib, macd_ma_type)(src, fast_length)  #talib.WMA(src, fast_length)
            slow_ = getattr(talib, macd_ma_type)(src, slow_length) 
        macd = fast_-slow_
        signal = talib.EMA(macd, signal_length) #getattr(talib, signal_ma_type)(macd,signal_length )

        hist = macd-signal
        return macd, signal, hist

    def _kairi(self, src, length):

        sma = talib.EMA(src, length)

        kri = 100 * (src - sma) / sma
        return kri
    def _volume(self, volume, shortlen, longlen):
        short = talib.EMA(volume, shortlen)
        long_ = talib.EMA(volume, longlen)
        return 100 * (short - long_) / long_