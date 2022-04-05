
import numpy as np
import pandas as pd
import json, pprint

import pickle
#from graph import iPlot
from numpy import savetxt
from datetime import datetime

from strg  import Strategy
from env import base_path

class Data:
    def __init__(self,client, coin):
        
       
        self.coin = coin
        self.client = client
        self.Strategy = Strategy(self.client, self.coin)
        self.max_len = 3000
        ## data frames

        self.df_5m = None
        self.df = None
        self.df_30m = None
        self.df_1h = None
        self.df_1m = None
        
        self.timer =0
        

    def _setDataframes(self):
        self.df = pd.read_csv(base_path+'/data/'+self.coin+'_1h.csv',usecols=['Time', 'Open','High' ,'Low', 'Close','Volum','CloseTime'])#
      
       


    def _dataProcess(self, msg):
        self.timer +=1
        if self.df is None:
            self._setDataframes()
            
        resp = json.loads(json.dumps(msg))
        row = resp.get("k")
       
        w = {
                "Time" :int(row['t']),
                "CloseTime":int(row['T']),
                "Open" :float(row["o"]),
                "High" :float(row["h"]),
                "Low" :float(row["l"]),
                "Close":float(row["c"]),
                "Volum":float(row['v'])
               
            }
       
        close_candle = row['x']
        
        if self.timer%120==0:
            self.Strategy._live(w)
            print(msg) 
        if close_candle:
             
             self.df = self.df.append(w, ignore_index=True )           
                             
                           
             self.Strategy._signal(  self.df,self.df_1h ) 
             
             self.time = row['t']
             time = datetime.utcfromtimestamp(int(self.time//1000)).strftime("%Y-%m-%d %H:%M:%S")
             self._writeData()
             print( 'time ', time )


        
        
    def _dataConvert(self, ms):
        df =self.df
        df['TimeH'] = df.Time.apply(lambda x: x//ms)
        d= df.groupby(['TimeH']).agg({ 'Time':'min','Low':'min', 'High':'max',
         'Open':'first', 'Close':'last',"CloseTime":"last", 'Volum':'sum'}).reset_index()
        return d

    
    def _writeData(self):

         self.df.to_csv(base_path+'/data/obs/'+self.coin+'_obs_1h.csv')      
        # self.df_1h.to_csv(base_path+'/data/obs/'+self.coin+'df_1h.csv')
        