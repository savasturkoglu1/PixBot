import pickle
import talib
import pandas as pd 
import numpy as np
from env import base_path 
from logger import Logs
class Agent:
    
    def __init__(self, coin):
        self.storage_path = base_path+"/source/model/"
        self.candle_cluster = pd.read_csv(self.storage_path+'candle_cluster.csv', low_memory=False)
        
        self.cols =  list(talib.get_function_groups()['Pattern Recognition']) 
        self.coin = coin
        self.Logs = Logs(self.coin)

        self.models = {
           
             'candle':{
                 'name': 'candle',
                 'model': 'rl_candle_1h_sstate.pkl',              
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
        df = pd.merge(df, self.candle_cluster,how='left',  on=talib.get_function_groups()['Pattern Recognition'])
       # df = df.dropna().reset_index(drop=True)
        return df

    def loadModel(self):
        with open(self.storage_path+self.model['model'], 'rb') as fid: #_gaus4var
            model = pickle.load(fid)
       
        self.q_table = model['q_table']
        self.t_table = model['t_table']
      
    def signal(self, df, instant_pnl, position):
        
        df = self.data(df)

        s = df.iloc[-1].state
        if s !=s:
            print(s)
            return 2,1
        state = int(s)
       
        # if position == 1:
        #     state = state+self.state_size
        # elif position == 0:
        #     state = state + self.state_size*2
       
        action = np.argmax(self.q_table[state])
        target = self.q_table[state,action]
        
        if target<=0:
            action =2
        
        leverage = 1
        if action == 1:
                    
                    

                self.expected_pnl = target
                self.opposit = self.q_table[state,0]*-1
                leverage = max(np.ceil(target/0.15),2)
                if self.opposit/target<0.7:
                    action = 2
        elif action == 0:
          
                self.expected_pnl = target
                self.opposit = self.q_table[state,1]*-1
                leverage = max(np.ceil(target/0.15),2)
                if self.opposit/target<0.7:
                        action = 2
       
                
        


       
        print('agent', state, action, leverage, target, instant_pnl) 
        self.Logs._writeLog(self.coin+'-agent signals  --state: '+str(state)+'-- action:'+ str(action)+'-- leverage:'+ str(leverage)+'-- statevaluse:'+ str(val))      
        return action,leverage