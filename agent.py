import pickle
import talib
import pandas as pd 
import numpy as np
from env import base_path 
from logger import Logs
from dtw import DTWGridCluster
class Agent:
    
    def __init__(self, coin):
        self.storage_path = base_path+"/source/model/"
        self.candle_cluster = pd.read_csv(self.storage_path+'candle_cluster.csv', low_memory=False)
        
     
        self.coin = coin
        self.Logs = Logs(self.coin)
        self.ClusterModel = DTWGridCluster()
        self.ClusterModel.loadModel('grid_dtw_npma_96')

        self.models = {
          
             'dtw':{
                 'name': 'candle',
                 'model': 'rl_dtw_96_multi_state_.pkl',              
                 'states':1600,
                 'cluster':'candle_cluster.pkl',

             }
         }
        
        self.model = self.models['dtw']
        self.state_size = self.model['states']+1

        self.q_table = None
        self.t_table = None
        self.q_matrix = None
        self.s_table  = None
        self.s_trade = None
        
       
        self.loadModel()

        ## trade vals
        self.state_list= []
        self.expected_pnl = 0

    def getState(self,input_data,n_past):
            X = list()
            for window_start in range(len(input_data)):              
              past_end = window_start + n_past
            
              if past_end > len(input_data):
                break
            
              past   = input_data[window_start:past_end]
              
              X.append(past)
            X =np.array(X)
            
           # X = X.reshape(X.shape[0], -1)
           
            p =  self.ClusterModel.predict(X)
            st = np.append([np.nan]*(n_past-1), p)
            return st
    
    def data(self, df):
            df['atr'] = talib.ATR(df.High, df.Low, df.Close, timeperiod=14)            
            max_ = talib.MAX(df.Close, timeperiod=200)
            min_ = talib.MIN(df.Close, timeperiod=200)
            df['np'] = (df.Close-min_)/(max_-min_)
            df['npma'] = talib.SMA(df.np, 5)
            df['state'] = self.getState(df.npma.to_numpy(),96)
            return df

    def loadModel(self):
        with open(self.storage_path+self.model['model'], 'rb') as fid: #_gaus4var
            model = pickle.load(fid)
        #model = model[self.coin]   
        self.q_table = model['q_table']
        self.t_table = model['t_table']
        self.s_table = model['s_table']
        self.s_trade = model['s_trade']
      
    def signal(self, df, instant_pnl, position):
        
        df = self.data(df)

        s = df.iloc[-1].state
        data = df.iloc[-1].to_dict()
        if s !=s:
            print(s)
            return 2,1
        state = int(s)
       
        if position == 1:
            state = state+self.state_size
        elif position == 0:
            state = state + self.state_size*2
       
        action = np.argmax(self.q_table[state])
        target = self.q_table[state,action]
        
        if target<=0:
            action =2
        
        if position == 1:
            state = state+self.state_size
        elif position == 0:
            state = state + self.state_size*2
       
        action = np.argmax(self.q_table[state])
        target = self.q_table[state,action]

        leverage = 3
        
        expected_pnl =0
        if action !=2:
            expected_pnl = self.s_trade[state,action*2]
            risk =min(self.s_trade[state,action*2+1], 1)

            
            tresh = 0.5 if action ==1 else 0.35
            if target<tresh :
                action = 2
            else:
                self.expected_pnl = target
               # leverage = min(max(np.ceil(expected_pnl/risk*2),2),10)
        
       
        if action == 1 :
            if data['npma']<0.8:# and data['Close']>data['Open'] :
                action = 1
            else:
                action = 2
        
        if action ==0 :
            if  data['npma']>0.2:# and data['Close']<data['Open'] :
                action == 0
            else: action =2
        
        

        if position is not None:
            if instant_pnl<self.expected_pnl:
                 action = 2
       
                
        


       
        print('agent', state, action, leverage, target, instant_pnl) 
        self.Logs._writeLog(self.coin+'-agent signals  --state: '+str(state)+'-- action:'+ str(action)+'-- leverage:'+ str(leverage)+'-- statevaluse:'+ str(target))      
        return action,leverage