import pickle
import numpy as np
from env import base_path 
class DTWGridCluster:
    
    def __init__(self, x_step = 12, y_step = 1):
       
       self.centroids = {}
       self.g_matrix = None

       self.x_step = x_step
       self.y_step = y_step
       self.y_bound = [-11,11]
       self.y_range = None
       self.x_range = None       
       self.sm_tresh = 0.8
       
       ## file path
       self.file_path =base_path+"/source/model/"

       self.cont = False

    def fit(self, data):
      if self.cont is False:
          self.y_range =np.arange(self.y_bound[0], self.y_bound[1],self.y_step)
          self.x_range =np.array(range(0, len(data[0]), self.x_step))
          self.gridMatrix()
      if len(self.centroids) == 0:
             p = self.gridPath(data[0])
            
             self.centroids[0] = {'center':data[0], 'path':p }

      for ind, i in enumerate(data):
            
            fit_rate = 0
            cluster = None
            path = self.gridPath(i)
            for key, val in self.centroids.items():
                cent = val['center']                
                if np.abs(i[-1]-cent[-1])<=self.y_step and np.abs(i[0]-cent[0])<=self.y_step :
                  
                  intersect = list(set(path) & set(val['path']))
                  cur_fit = len(intersect)/len(val['path'])
                  if cur_fit>fit_rate:
                      fit_rate = cur_fit
                      cluster = key

                if fit_rate == 1:
                      break
            if fit_rate<self.sm_tresh:
              self.centroids[key+1] = {'center':i, 'path':path } 
            if ind%10000==0:
              print(len(self.centroids))

    def predict(self, data):
      preds = []
     
      if len(self.centroids) == 0:
             raise ValueError('fit the model before predict')
             

      for ind, i in enumerate(data):
            
            fit_rate = 0
            cluster = None
            path = self.gridPath(i)
            
            for key, val in self.centroids.items():
                cent = val['center']                
                if np.abs(i[-1]-cent[-1])<=self.y_step and np.abs(i[0]-cent[0])<=self.y_step :
                  
                  intersect = list(set(path) & set(val['path']))
                  cur_fit = len(intersect)/len(val['path'])
                  if cur_fit>fit_rate:
                      fit_rate = cur_fit
                      cluster = key
                      

                if fit_rate == 1:
                      break
            if fit_rate>self.sm_tresh:     
               preds.append(cluster)
            else:
               preds.append(np.nan)

           
      
      return preds

    def gridMatrix(self):
        t = np.zeros([len(self.x_range)+1,len(self.y_range)+1]).astype(int)
        x =0
        for i in range(len(self.x_range)+1):
          for j in range(len(self.y_range)+1):
            t[i,j] = x
            x +=1
        self.g_matrix =  t
    
    def gridPath(self, s):
      
      path = []
      for x, i in enumerate(self.x_range):
        
        for y,j in enumerate(self.y_range):
            
            for ind, k in enumerate(s[i:(x+1)*self.x_step]):
              if y==0 and k<j:
                    path.append(self.g_matrix[x,y-1])
                    break
              elif y == len(self.y_range)-1:
                if k>j:
                  path.append(self.g_matrix[x,y])
                  break
              else:
                if k>self.y_range[y-1] and k<j:
                  path.append(self.g_matrix[x,y+1])
                  break
      return path
    def loadModel(self, model_name):
      with open(self.file_path+model_name+'.pkl', 'rb') as fid:
            model = pickle.load(fid)
            self.centroids = model['centroids']
            self.g_matrix = model['g_matrix']
            self.x_step = model['params']['x_step']
            self.y_step = model['params']['y_step']
            self.y_bound = model['params']['y_bound']
            self.y_range = model['params']['y_range']
            self.x_range = model['params']['x_range']       
            self.sm_tresh = model['params']['sm_tresh']
            
     
            print('cluster model loaded')
      self.cont = True
    
    def saveModel(self, model_name = 'grid_dtw'):

      
      model = {
          'centroids':self.centroids,
          'g_matrix':self.g_matrix,
          'params':{
              'x_step':self.x_step,
              'y_step':self.y_step,
              'y_bound':self.y_bound,
              'y_range':self.y_range,
              'x_range':self.x_range,
              'sm_tresh':self.sm_tresh
          }
      }
      with open(self.file_path+model_name+'.pkl', 'wb') as fid:
          pickle.dump(model, fid)
          print('model saved') 



       
    