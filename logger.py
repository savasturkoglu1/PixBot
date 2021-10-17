#importing the module 
import logging 
from env import base_path
from datetime import datetime


 



class Logs():
    def __init__(self):
        
        self.logday ='2021-10-16'
        self.logger=logging.getLogger() 
        self.logger.setLevel(logging.DEBUG)
        self._setLogger()
        

    def _writeLog(self, message, level='info'):
        self._setLogger()
        if level == "info":
                self.logger.info(message)
        elif level == "warning":
            self.logger.warning(message)
        elif level == "error":
            self.logger.error(message)
        elif level == "debug":
            self.logger.debug(message) 
       
    def _setLogger(self):
        d = datetime.today().strftime('%Y-%m-%d')
        

        if d !=self.logday:
            d = d.replace('-','_')
            self.logday = d
            file_n = base_path+'/logs/trade_logs_'+d+'.log'
            #file = open(file_n,'a+')
            logging.basicConfig(filename=file_n, 
                                format='%(asctime)s %(message)s', 
                                filemode='w')
            self.logger=logging.getLogger() 
            self.logger.setLevel(logging.DEBUG)