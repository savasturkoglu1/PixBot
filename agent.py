import pickle
import talib
import pandas as pd 
import numpy as np
from env import base_path 
class Agent:
    
    def __init__(self, coin):
        self.storage_path = base_path+"/source/model/"
        self.candle_cluster = pd.read_csv(self.storage_path+'candle_cluster.csv', low_memory=False)

        self.cols =  list(talib.get_function_groups()['Pattern Recognition']) 
        self.coin = coin
      

        self.models = {
           
             'candle':{
                 'name': 'candle',
                 'model': 'rl_candle.pkl',              
                 'states':2800,
                 'cluster':'candle_cluster.pkl',

             }
         }
        
        self.model = self.models['candle']
        self.state_size = self.model['states']+1

        self.q_table = None
        self.t_table = None
        self.q_matrix = None
        
       
        self.loadModel()

        ## trade vals
        self.state_list= []
        self.expected_pnl = 0
    def candlestick(self,df):
        

            op = df['Open'].astype(float)
            hi = df['High'].astype(float)
            lo = df['Low'].astype(float)
            cl = df['Close'].astype(float)

            candle_names = talib.get_function_groups()['Pattern Recognition']

          

            
            # create columns for each candle
            for candle in candle_names:
                # below is same as;
                # df["CDL3LINESTRIKE"] = talib.CDL3LINESTRIKE(op, hi, lo, cl)
                df[candle] = getattr(talib, candle)(op, hi, lo, cl)
            return df
    def data(self, df):
        df =self.candlestick(df)
        df = pd.merge(df, self.candle_cluster,how='left',  on=self.cols)
        df = df.dropna().reset_index(drop=True)
        return df

    def loadModel(self):
        with open(self.storage_path+self.model['model'], 'rb') as fid: #_gaus4var
            model = pickle.load(fid)
       
        self.q_table = model['q_table']
        self.t_table = model['t_table']
      
    def signal(self, df, instant_pnl, position):
        
        df = self.data(df)
        state = int(df.iloc[-1].state)
       
        if position == 1:
            state = state+self.state_size
        elif position == 0:
            state = state + self.state_size*2
       
        action = np.argmax(self.q_table[state])
        val = self.q_table[state,action]
        
        if val<=0:
            action =2
        
        leverage = 1
        if position is None:
            if action !=2:
                t = 0.2 if action == 1 else 0.18
                v = self.q_table[state,action]
                if v<t:
                    action = 2
                else:
                    self.expected_pnl = v
                    leverage = max(np.ceil(self.expected_pnl/0.35),2)
        else:
              if instant_pnl< self.expected_pnl*2:
                          action = 2
              
                
        


       
        print('agent', state, action, leverage, self.expected_pnl)     
        return action,leverage