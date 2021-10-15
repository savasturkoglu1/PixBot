
import numpy as np
import pandas as pd
import json, pprint

import pickle
#from graph import iPlot
from numpy import savetxt
from datetime import datetime

from strategy import Strategy
from env import base_path

class Data:
    def __init__(self,client, coin):
        
       
        self.coin = coin
        self.client = client
        self.Strategy = Strategy(self.client, self.coin)
        self.max_len = 1000
        ## data frames

        self.df_5m = None
        self.df_15m = None
        self.df_30m = None
        self.df_1h = None
        self.df_1m = None
              
        

        
        
        self.time = self.df_5m.tail(1).iloc[0]['Time'] if self.df_1m is not None else 0

    def _setDataframes(self):
        self.df_1m = pd.read_csv(base_path+'/data/'+self.coin+'_1m.csv',usecols=['Time', 'Open','High' ,'Low', 'Close','Volum'])#
        self.df_5m = pd.read_csv(base_path+'/data/'+self.coin+'_5m.csv',usecols=['Time', 'Open','High' ,'Low', 'Close','Volum'])#   
        self.df_15m = pd.read_csv(base_path+'/data/'+self.coin+'_15m.csv',usecols=['Time', 'Open','High' ,'Low', 'Close','Volum'])#
        self.df_30m = pd.read_csv(base_path+'/data/'+self.coin+'_30m.csv',usecols=['Time', 'Open','High' ,'Low', 'Close','Volum'])# 
        self.df_1h = pd.read_csv(base_path+'/data/'+self.coin+'_1h.csv',usecols=['Time', 'Open','High' ,'Low', 'Close','Volum'])#
       


    def _dataProcess(self, msg):
      
        if self.df_1m is None:
            self._setDataframes()
            
        resp = json.loads(json.dumps(msg))
        row = resp.get("k")
        event_time = resp.get('E')

        ''' df shortener'''
        if self.df_5m.shape[0]>1200:
            self.df_5m = self.df_5m.tail(self.max_len).copy()  
            self.df_15m = self.df_15m.tail(self.max_len).copy()        
            self.df_30m = self.df_30m.tail(self.max_len).copy()
            self.df_1h = self.df_1h.tail(self.max_len).copy()
        
     

        '''  clear duplicates '''
        self.df_15m = self.df_15m.drop_duplicates(subset=['Time'], keep='last')
        self.df_30m = self.df_30m.drop_duplicates(subset=['Time'], keep='last')
        self.df_1h = self.df_1h.drop_duplicates(subset=['Time'], keep='last')
        self.df_5m = self.df_5m.drop_duplicates(subset=['Time'], keep='last')


        
       
        
        if event_time >=row["T"]:  #!= self.time:
            
             print(row["t"], event_time)
             self.df_5m = self._dataConvert(300000, self.df_5m)
             self.df_15m = self._dataConvert(900000, self.df_15m)             
             self.df_30m = self._dataConvert(900000*2, self.df_30m)  
             self.df_1h = self._dataConvert(900000*4, self.df_1h)  
               
             
             self.Strategy._process( row, self.df_5m, self.df_15m,self.df_30m, self.df_1h ) 
             
             self.time = row['t']
             time = datetime.utcfromtimestamp(int(self.time//1000)).strftime("%Y-%m-%d %H:%M:%S")
             
             print( 'time ', time )


        w = {
                "Time" :int(row['t']),
                "Open" :float(row["o"]),
                "High" :float(row["h"]),
                "Low" :float(row["l"]),
                "Close":float(row["c"]),
                "Volum":float(row['v'])
               
            }
       

        index_names = self.df_1m[ self.df_1m['Time'] == int(row['t']) ].index
        self.df_1m.drop(index_names, inplace = True)
        self.df_1m = self.df_1m.append(w, ignore_index=True )
        
        
    def _dataConvert(self, ms, df):
        

        
        if self.df_1m.iloc[-1].to_dict()['Time']%ms==0:
                 df = df.append(self.df_1m.tail(1), ignore_index=True)
            
        else:
            last_row =df.iloc[-1].to_dict()
            row = self.df_1m.iloc[-1].to_dict()


            Close = row['Close'] 
            High = max(last_row['High'], row['High'])
            Low = min(last_row['Low'], row['Low'])  
            #Volum = last_row['Volum'] + row['Volum']        
           
            df.loc[df.index[-1],['Close','High','Low']] = [Close, High, Low]
        return df