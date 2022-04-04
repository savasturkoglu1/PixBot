#importing the module 
import logging 
from env import base_path
from datetime import datetime

import logging.config
 




class Logs():
    def __init__(self, coin='_'):
        
        self.logday ='2021-10-16'
        self.logger=logging.getLogger()
        self.logger.setLevel(logging.INFO)
        self.coin =coin
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
        

        if True:# d !=self.logday:
            self.logday = d
            d = d.replace('-','_')
            
            file_n = base_path+'/logs/trade_logs_'+d+'.log'
            #file = open(file_n,'a+')
            rfh = logging.handlers.RotatingFileHandler(
                filename=file_n, 
                mode='w',
                maxBytes=3*1024*1024,
                backupCount=10,
                encoding=None,
                delay=0
            )
          
            # logging.config.dictConfig({
            #     'version': 1,
            #     # Other configs ...
            #     'disable_existing_loggers': True
            # })
            logging.basicConfig( 
                                format='%(asctime)s %(message)s', 
                                handlers=[ rfh ])
            self.logger=logging.getLogger() 
            self.logger.setLevel(logging.DEBUG)