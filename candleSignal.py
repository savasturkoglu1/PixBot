import talib
import pandas as pd
import numpy as np
class CandleSignal:
    
    def __init__(self):
             
       

        self.short_flag = False
        self.long_flag = False
        self.signal = None
        self.trade_len = None
       
        self.candle_names = talib.get_function_groups()['Pattern Recognition']
        self.candle_rankings = {
                    "CDL3LINESTRIKE_Bull": 1,
                    "CDL3LINESTRIKE_Bear": 2,
                    "CDL3BLACKCROWS_Bull": 3,
                    "CDL3BLACKCROWS_Bear": 3,
                    "CDLEVENINGSTAR_Bull": 4,
                    "CDLEVENINGSTAR_Bear": 4,
                    "CDLTASUKIGAP_Bull": 5,
                    "CDLTASUKIGAP_Bear": 5,
                    "CDLINVERTEDHAMMER_Bull": 6,
                    "CDLINVERTEDHAMMER_Bear": 6,
                    "CDLMATCHINGLOW_Bull": 7,
                    "CDLMATCHINGLOW_Bear": 7,
                    "CDLABANDONEDBABY_Bull": 8,
                    "CDLABANDONEDBABY_Bear": 8,
                    "CDLBREAKAWAY_Bull": 10,
                    "CDLBREAKAWAY_Bear": 10,
                    "CDLMORNINGSTAR_Bull": 12,
                    "CDLMORNINGSTAR_Bear": 12,
                    "CDLPIERCING_Bull": 13,
                    "CDLPIERCING_Bear": 13,
                    "CDLSTICKSANDWICH_Bull": 14,
                    "CDLSTICKSANDWICH_Bear": 14,
                    "CDLTHRUSTING_Bull": 15,
                    "CDLTHRUSTING_Bear": 15,
                    "CDLINNECK_Bull": 17,
                    "CDLINNECK_Bear": 17,
                    "CDL3INSIDE_Bull": 20,
                    "CDL3INSIDE_Bear": 20,
                    "CDLHOMINGPIGEON_Bull": 21,
                    "CDLHOMINGPIGEON_Bear": 21,
                    "CDLDARKCLOUDCOVER_Bull": 22,
                    "CDLDARKCLOUDCOVER_Bear": 22,
                    "CDLIDENTICAL3CROWS_Bull": 24,
                    "CDLIDENTICAL3CROWS_Bear": 24,
                    "CDLMORNINGDOJISTAR_Bull": 25,
                    "CDLMORNINGDOJISTAR_Bear": 25,
                    "CDLXSIDEGAP3METHODS_Bull": 27,
                    "CDLXSIDEGAP3METHODS_Bear": 26,
                    "CDLTRISTAR_Bull": 28,
                    "CDLTRISTAR_Bear": 76,
                    "CDLGAPSIDESIDEWHITE_Bull": 46,
                    "CDLGAPSIDESIDEWHITE_Bear": 29,
                    "CDLEVENINGDOJISTAR_Bull": 30,
                    "CDLEVENINGDOJISTAR_Bear": 30,
                    "CDL3WHITESOLDIERS_Bull": 32,
                    "CDL3WHITESOLDIERS_Bear": 32,
                    "CDLONNECK_Bull": 33,
                    "CDLONNECK_Bear": 33,
                    "CDL3OUTSIDE_Bull": 34,
                    "CDL3OUTSIDE_Bear": 39,
                    "CDLRICKSHAWMAN_Bull": 35,
                    "CDLRICKSHAWMAN_Bear": 35,
                    "CDLSEPARATINGLINES_Bull": 36,
                    "CDLSEPARATINGLINES_Bear": 40,
                    "CDLLONGLEGGEDDOJI_Bull": 37,
                    "CDLLONGLEGGEDDOJI_Bear": 37,
                    "CDLHARAMI_Bull": 38,
                    "CDLHARAMI_Bear": 72,
                    "CDLLADDERBOTTOM_Bull": 41,
                    "CDLLADDERBOTTOM_Bear": 41,
                    "CDLCLOSINGMARUBOZU_Bull": 70,
                    "CDLCLOSINGMARUBOZU_Bear": 43,
                    "CDLTAKURI_Bull": 47,
                    "CDLTAKURI_Bear": 47,
                    "CDLDOJISTAR_Bull": 49,
                    "CDLDOJISTAR_Bear": 51,
                    "CDLHARAMICROSS_Bull": 50,
                    "CDLHARAMICROSS_Bear": 40,
                    "CDLADVANCEBLOCK_Bull": 54,
                    "CDLADVANCEBLOCK_Bear": 54,
                    "CDLSHOOTINGSTAR_Bull": 55,
                    "CDLSHOOTINGSTAR_Bear": 55,
                    "CDLMARUBOZU_Bull": 71,
                    "CDLMARUBOZU_Bear": 57,
                    "CDLUNIQUE3RIVER_Bull": 60,
                    "CDLUNIQUE3RIVER_Bear": 60,
                    "CDL2CROWS_Bull": 61,
                    "CDL2CROWS_Bear": 61,
                    "CDLBELTHOLD_Bull": 62,
                    "CDLBELTHOLD_Bear": 63,
                    "CDLHAMMER_Bull": 65,
                    "CDLHAMMER_Bear": 65,
                    "CDLHIGHWAVE_Bull": 67,
                    "CDLHIGHWAVE_Bear": 67,
                    "CDLSPINNINGTOP_Bull": 69,
                    "CDLSPINNINGTOP_Bear": 73,
                    "CDLUPSIDEGAP2CROWS_Bull": 74,
                    "CDLUPSIDEGAP2CROWS_Bear": 74,
                    "CDLGRAVESTONEDOJI_Bull": 77,
                    "CDLGRAVESTONEDOJI_Bear": 77,
                    "CDLHIKKAKEMOD_Bull": 82,
                    "CDLHIKKAKEMOD_Bear": 81,
                    "CDLHIKKAKE_Bull": 85,
                    "CDLHIKKAKE_Bear": 83,
                    "CDLENGULFING_Bull": 84,
                    "CDLENGULFING_Bear": 91,
                    "CDLMATHOLD_Bull": 86,
                    "CDLMATHOLD_Bear": 86,
                    "CDLHANGINGMAN_Bull": 87,
                    "CDLHANGINGMAN_Bear": 87,
                    "CDLRISEFALL3METHODS_Bull": 94,
                    "CDLRISEFALL3METHODS_Bear": 89,
                    "CDLKICKING_Bull": 96,
                    "CDLKICKING_Bear": 102,
                    "CDLDRAGONFLYDOJI_Bull": 98,
                    "CDLDRAGONFLYDOJI_Bear": 98,
                    "CDLCONCEALBABYSWALL_Bull": 101,
                    "CDLCONCEALBABYSWALL_Bear": 101,
                    "CDL3STARSINSOUTH_Bull": 103,
                    "CDL3STARSINSOUTH_Bear": 103,
                    "CDLDOJI_Bull": 104,
                    "CDLDOJI_Bear": 104
                }
        self.long_ranks = {'CDLABANDONEDBABY': 1,
                        'CDLCONCEALBABYSWALL': 2,
                        'CDLTASUKIGAP': 3,
                        'CDLLADDERBOTTOM': 4,
                        'CDLCOUNTERATTACK': 5,
                        'CDL3WHITESOLDIERS': 6,
                        'CDLTRISTAR': 7,
                        'CDLUNIQUE3RIVER': 8,
                        'CDLHOMINGPIGEON': 9,
                        'CDLGAPSIDESIDEWHITE': 10,
                        'CDLMATHOLD': 11,
                        'CDLSTICKSANDWICH': 12,
                        'CDLXSIDEGAP3METHODS': 13,
                        'CDLMORNINGSTAR': 14,
                        'CDLHAMMER': 15,
                        'CDLHIKKAKE': 16,
                        'CDLSEPARATINGLINES': 17,
                        'CDLLONGLINE': 18,
                        'CDLHARAMI': 19,
                        'CDLGRAVESTONEDOJI': 20,
                        'CDLBELTHOLD': 21,
                        'CDL3OUTSIDE': 22,
                        'CDLMATCHINGLOW': 23,
                        'CDLHARAMICROSS': 24,
                        'CDLDOJISTAR': 25,
                        'CDLMARUBOZU': 26,
                        'CDLPIERCING': 27,
                        'CDLSHORTLINE': 28,
                        'CDLSPINNINGTOP': 29,
                        'CDL3INSIDE': 30,
                        'CDLDOJI': 31,
                        'CDLLONGLEGGEDDOJI': 32,
                        'CDLHIKKAKEMOD': 33,
                        'CDLCLOSINGMARUBOZU': 34,
                        'CDLRICKSHAWMAN': 35,
                        'CDLENGULFING': 36,
                        'CDLINVERTEDHAMMER': 37,
                        'CDLHIGHWAVE': 38,
                        'CDLDRAGONFLYDOJI': 39,
                        'CDLTAKURI': 40,
                        'CDLMORNINGDOJISTAR': 41,
                        'CDL3LINESTRIKE': 42,
                        'CDLRISEFALL3METHODS': 43,
                        'CDLEVENINGSTAR': 44,
                        'CDLUPSIDEGAP2CROWS': 45,
                        'CDLTHRUSTING': 46,
                        'CDL3STARSINSOUTH': 47,
                        'CDLSTALLEDPATTERN': 48,
                        'CDLEVENINGDOJISTAR': 49,
                        'CDLKICKING': 50,
                        'CDLSHOOTINGSTAR': 51,
                        'CDLBREAKAWAY': 52,
                        'CDLKICKINGBYLENGTH': 53,
                        'CDLHANGINGMAN': 54,
                        'CDLONNECK': 55,
                        'CDLADVANCEBLOCK': 56,
                        'CDL3BLACKCROWS': 57,
                        'CDLIDENTICAL3CROWS': 58,
                        'CDLINNECK': 59,
                        'CDLDARKCLOUDCOVER': 60,
                        'CDL2CROWS': 61}
        self.short_ranks = {'CDL3BLACKCROWS': 1,
                        'CDLTASUKIGAP': 2,
                        'CDLEVENINGDOJISTAR': 3,
                        'CDLEVENINGSTAR': 4,
                        'CDLIDENTICAL3CROWS': 5,
                        'CDL3INSIDE': 6,
                        'CDLTHRUSTING': 7,
                        'CDLHIKKAKEMOD': 8,
                        'CDLDARKCLOUDCOVER': 9,
                        'CDLADVANCEBLOCK': 10,
                        'CDLHARAMICROSS': 11,
                        'CDLSPINNINGTOP': 12,
                        'CDLBREAKAWAY': 13,
                        'CDLRISEFALL3METHODS': 14,
                        'CDLENGULFING': 15,
                        'CDLSHOOTINGSTAR': 16,
                        'CDLHIGHWAVE': 17,
                        'CDLSHORTLINE': 18,
                        'CDLDOJISTAR': 19,
                        'CDLHANGINGMAN': 20,
                        'CDLBELTHOLD': 21,
                        'CDLHARAMI': 22,
                        'CDLLONGLINE': 23,
                        'CDL3OUTSIDE': 24,
                        'CDLHIKKAKE': 25,
                        'CDLMARUBOZU': 26,
                        'CDLSEPARATINGLINES': 27,
                        'CDLCLOSINGMARUBOZU': 28,
                        'CDLSTALLEDPATTERN': 29,
                        'CDL3LINESTRIKE': 30,
                        'CDL2CROWS': 31,
                        'CDLGAPSIDESIDEWHITE': 32,
                        'CDLXSIDEGAP3METHODS': 33,
                        'CDLINNECK': 34,
                        'CDLCOUNTERATTACK': 35,
                        'CDLONNECK': 36,
                        'CDLTRISTAR': 37,
                        'CDLUPSIDEGAP2CROWS': 38,
                        'CDLINVERTEDHAMMER': 39,
                        'CDLDRAGONFLYDOJI': 40,
                        'CDLUNIQUE3RIVER': 41,
                        'CDL3STARSINSOUTH': 42,
                        'CDL3WHITESOLDIERS': 43,
                        'CDLTAKURI': 44,
                        'CDLSTICKSANDWICH': 45,
                        'CDLABANDONEDBABY': 46,
                        'CDLCONCEALBABYSWALL': 47,
                        'CDLDOJI': 48,
                        'CDLGRAVESTONEDOJI': 49,
                        'CDLKICKING': 50,
                        'CDLRICKSHAWMAN': 51,
                        'CDLPIERCING': 52,
                        'CDLMORNINGSTAR': 53,
                        'CDLMORNINGDOJISTAR': 54,
                        'CDLMATHOLD': 55,
                        'CDLMATCHINGLOW': 56,
                        'CDLHAMMER': 57,
                        'CDLLONGLEGGEDDOJI': 58,
                        'CDLLADDERBOTTOM': 59,
                        'CDLKICKINGBYLENGTH': 60,
                        'CDLHOMINGPIGEON': 61}
        #self._candleName()

    def _candlestick(self,df):
        

            op = df['Open'].astype(float)
            hi = df['High'].astype(float)
            lo = df['Low'].astype(float)
            cl = df['Close'].astype(float)

            for candle in self.candle_names:
                
                df[candle] =  getattr(talib, candle)(op, hi, lo, cl)
            
            return df
  
        
    def _pattern_signal(self,row):
        
        pattern_val = []
        ranks =[]
        trade = None
        rank = None
        match = None

        for key,val in row.items():
                if val >0:
                    ranks.append(self.long_ranks[key])
                    pattern_val.append(val)
                if val <0:
                    ranks.append(self.short_ranks[key])
                    pattern_val.append(val)
        if len(pattern_val)>0:
                if np.all(np.array(pattern_val)>0):
                        trade = 1
                        rank = min(ranks)
                        match = len(pattern_val)
                elif np.all(np.array(pattern_val)<0):
                        trade = 0
                        rank = min(ranks)
                        match = len(pattern_val)

        return trade, rank, match

            

    def _candleName(self):
        candle_names = talib.get_function_groups()['Pattern Recognition']
        exclude_items = ('CDLCOUNTERATTACK',
                                'CDLLONGLINE',
                                'CDLSHORTLINE',
                                'CDLSTALLEDPATTERN',
                                'CDLKICKINGBYLENGTH')

                                #'CDLLONGLEGGEDDOJI', 'CDLDOJI', 'CDLRICKSHAWMAN', 'CDLENGULFING','CDLSPINNINGTOP',

        self.candle_names = [candle for candle in candle_names if candle not in exclude_items]
       
    def _kairi(self, src, length):
        
        trend_long = talib.EMA(src, 144)
        trend_short = talib.EMA(src, 55)
     

        return 100 * (trend_short - trend_long)/trend_long
    def _data(self, df):
        df = self._candlestick(df)
        df['kairi'] =  self._kairi(df.Close,144)
        df['TimeH'] = df.Time.apply(lambda x: x//300000)
        d= df.groupby(['TimeH']).agg({ 'Time':'min','Low':'min', 'High':'max',
         'Open':'first', 'Close':'last', 'Volum':'sum'}).reset_index()
        
        d['rsi'] = talib.RSI(d.Close, timeperiod=14)
        df = pd.merge(df, d[['Time','rsi']],how='left',  on=['Time'])    
        return df
    def _signal(self,df, df_5m):
        
        df = self._data(df)
        

        
        data = df.iloc[-1].to_dict()
        close = df.iloc[-1].Close
        
        
        row ={'Time':data['Time'],'position':np.nan,
        'open_long':np.nan,'close_long':np.nan,'open_short':np.nan,
        'close_short':np.nan,'stop_price':np.nan, 'trailing_stop':np.nan,
                'leverage':np.nan,'take_profit':np.nan, 'stop_limit':np.nan}
        
     
        trade, rank,match = self._pattern_signal(df[self.candle_names].iloc[-2].to_dict())
        
        # if trade ==1 and rank<38 and match>2 and data['Close']>data['Open']:
        #     self.signal =1
        # elif trade == 0 and rank<40 and match>1 and  data['Close']<data['Open']:
        #     self.signal = 0
        # else:
        #     self.signal = None
        if trade ==1 and rank<37 and match>1 :# and data['Close']>=data['Open']:
                # if self.short_flag is False and self.long_flag is False:
                #     if data['Close']>=data['Open']:
                #        self.signal =1
                #     else:
                #        self.signal = None
                # else:
                    self.signal =1
        elif trade == 0 and rank<40 and  match>1:# and data['Close']<=data['Open']:
            # if self.short_flag is False and self.long_flag is False:
            #     if data['Close']<=data['Open']:
            #       self.signal =0
            #     else:
            #       self.signal = None
            # else:
               self.signal =0
        else:
            self.signal = None

        # signal_filter =None
        # if list(rsi)[-1]>57:
        #     signal_filter =1
        # elif list(rsi)[-1]<43:
        #     signal_filter =0

        # if list(kairi)[-1]>1.1 or list(kairi)[-1]< -1.07:
        #     signal_filter = 2

        signal_filter =None
        if data['rsi']>57:
            signal_filter =1
        elif data['rsi']<43:
            signal_filter =0
        if data['kairi']>1.1 or data['kairi']< -1.07:
            signal_filter = 2

        if self.signal == 1 and self.short_flag is True  and self.trade_len >3:
            row['close_short'] = close
            row['position'] = 'CLOSE_SHORT'
            self.short_flag = False 
            self.trade_len = None

        elif self.signal==0 and self.long_flag is True  and self.trade_len >3:
            row['close_long'] = close
            row['position'] = 'CLOSE_LONG'
            self.long_flag = False 
            self.trade_len = None 

        elif self.signal == 1  and self.long_flag is False and  self.short_flag is False and signal_filter in [1,2]:
             row['open_long'] = close
             row['position'] = 'OPEN_LONG'
             self.long_flag = True   
             self.trade_len = 1        
                         
             self.stop_price =   df[['Close','Open']].iloc[-2:].values.min()*(1-.001)
             #close-3*atr          
             
        elif self.signal ==0   and  self.short_flag is False  and self.long_flag is False  and signal_filter in [0,2]:
             row['position'] = 'OPEN_SHORT'
             row['open_short'] = close
             self.short_flag = True  
             self.trade_len = 1       
                    
            
             self.stop_price =  df[['Close','Open']].iloc[-2:].values.max()*1.001
        else:
            if self.trade_len is not None:
                  self.trade_len +=1
            
             
       
        
        if self.long_flag is True or self.short_flag is True:
           self.stop_limit = np.abs(close-self.stop_price)/close*100            
           self.leverage  = max(min(np.ceil(1/self.stop_limit) ,15),3)
           
           take_profit = None
           if   True: # 
                
                if self.long_flag is True:
                     take_profit = (1+self.stop_limit/100*4)*data['Close']
                if self.short_flag is True:
                     take_profit =(1-self.stop_limit/100*4)*data['Close']
           row['leverage'] = self.leverage
           row['stop_limit'] = self.stop_limit
           row['trailing_stop'] = False
           row['stop_price'] = self.stop_price #*(1.001) if self.short_flag is True else self.stop_price*(1-0.001)
           row['take_profit'] = take_profit
                   
        return row
        