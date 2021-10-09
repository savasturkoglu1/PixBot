#importing the module 
import logging 
from env import base_path
from datetime import datetime


d = datetime.today().strftime('%Y-%m-%d')
d = d.replace('-','_')

file_n = base_path+'/logs/trade_logs_'+d+'.log'
#file = open(file_n,'a+')
logging.basicConfig(filename=file_n, 
					format='%(asctime)s %(message)s', 
					filemode='w') 



class Logs():
    def __init__(self):
        self.logger=logging.getLogger() 
        self.logger.setLevel(logging.DEBUG)


    def _writeLog(self, message, level='info'):
        
        if level == "info":
                self.logger.info(message)
        elif level == "warning":
            self.logger.warning(message)
        elif level == "error":
            self.logger.error(message)
        elif level == "debug":
            self.logger.debug(message) 
       