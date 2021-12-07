## import packages
###binance client 
from binance.client import Client

import pandas as pd 
from datetime import datetime
from datetime import timedelta

from env  import base_path



class GetData:

    def __init__(self, client,coin,look_back=1200, look_back_short=1):

        self.client = client
        self.coin   = coin
        self.file_path = '/home/savas/Desktop/BotDev/src/data/' #base_path+'/data/'
        
        self.look_back = look_back
        self.look_back_short = look_back_short

        ## periods
        self.periods = ['_5m'] #,'_30m','_1h','_5m','_15m'
        self.intervals = {
                    '_1m' : Client.KLINE_INTERVAL_1MINUTE,
                    '_5m' : Client.KLINE_INTERVAL_5MINUTE,
                    '_15m' : Client.KLINE_INTERVAL_15MINUTE,
                    '_30m' : Client.KLINE_INTERVAL_30MINUTE,
                    '_1h' : Client.KLINE_INTERVAL_1HOUR,
                    '_2h' : Client.KLINE_INTERVAL_2HOUR,
                    '_4h' : Client.KLINE_INTERVAL_4HOUR
        }
        ## dates        

        self.from_date_back = self._dailyPriod(self.look_back)
        self.from_date_back_short = self._dailyPriod(self.look_back_short)
        self.day_name =  datetime.today().strftime('%Y-%m-%d')
        
        
    def _dailyPriod(self, look_back):
        day = datetime.now()
        d = timedelta(days = look_back)
        k=day-d
        k.strftime('%d %B, %Y')
        return  k.strftime('%d %B, %Y')
        

    

    def _getData(self):

  
        for period in self.periods:
            back= self.from_date_back
            # if period in self.periods[:2]:
            #     back = self.from_date_back_short
            path = self.file_path+self.coin+period+'_long.csv'
            print(self.coin, self.intervals[period], back)
            data_ = self.client.get_historical_klines(self.coin, self.intervals[period], back)  
            df = pd.DataFrame(data_)
            
            df =df.rename(columns={0: "Time", 1: "Open", 2:"High", 3:"Low", 4:"Close", 5:"Volum", 6:"CloseTime" }) #7:"Quote" , 8:"TradeNumber", 9:"BaseAsset", 10:"QuoteAsset"
            df.to_csv(path)


if __name__ == '__main__':
   
    
    from client import iClient
    c = ['XRPUSDT', 'XLMUSDT', 
'LINKUSDT', 'LTCUSDT','CHZUSDT','BNBUSDT','BCHUSDT','VETUSDT','XTZUSDT', 'DASHUSDT','HOTUSDT',
'NEOUSDT','ATOMUSDT', 'BTTUSDT', 'SOLUSDT', 'EOSUSDT','AVAXUSDT', 'FILUSDT','BTCUSDT','ETHUSDT'] 
    coins = ['XRPUSDT', 'BNBUSDT', 'LTCUSDT'] #'ETHUSDT', 'DOTUSDT','XRPUSDT', #'BTCUSDT', 'AVAXUSDT', 'ADAUSDT', 'LTCUSDT', 'DOTUSDT','XRPUSDT'
    for i in coins:
        d = GetData(iClient().client,i)
        d._getData()