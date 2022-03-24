import numpy as np
from client import iClient
from binance.client import Client
from binance.enums import *
#from db import DataBase
from binance.exceptions import BinanceAPIException
import time
import json
from logger import Logs
import math

class Trade:
    def __init__(self,client, coin):
        ## objects
        self.Logs = Logs()
        self.client = client
        self.symbol = coin
    
        ## order constants
        self.marginRate = 0.97
        self.stopRate = 2
        self.profitRate = 7
        
        self.side = None
        self.leverage=5

        self.position = None 
        
        ## take profi order 
        self.profitSide = None
        self.takeProfit = False
        self.takeProfitStatus = False
        self.profitOrderId = None
        self.profitOrder = None
        self.profitLimit = 0
        self.profitPrice = None

        ## stop order
        self.stopSide = None
        self.stopLimit = None
        self.stopOrderId = None
        self.stopOrder = None
        self.setStopStatus = False
        self.stopPrice = None
        
        ## trade order
        
        self.order = None
        self.balance = 0
        self.tradeMargin =0
        self.quantity = 0        
        self.tradePrice = 0
        self.tradeClosePrice =0
        self.buyPrice = 0
        self.sellPrice = 0
        self.order = None
        self.orderType = None
        self.orderStatus = 'NEW'
        self.orderId = None
        self.forceTrade = False
        self.forceTradeCount =0
        self.triggerSide = None
        self.prc = {
            'BTCUSDT':3,
            'ETHUSDT':3,
            'DOTUSDT':1,
            'AVAXUSDT':0,
            'ADAUSDT':0,
            'XRPUSDT':1,
            'ATOMUSDT':2,
            'LINKUSDT':2,
            'XLMUSDT':0
        }
    

        

    def _live(self, data):
       # print(self.symbol, self.position, self.quantity)
        if self.order is not  None:
            
            # if self.orderStatus !='FILLED':
            #     self._checkOrder()
            if self.setStopStatus is False:
                self._setStop()
            if self.takeProfitStatus is False:
                self._takeProfit()
            self._checkPosition()
            if self.takeProfitStatus is True:
                self._checkProfit()
            if self.setStopStatus is True:
                self._checkStop()    
    def _order(self, **kwargs):
        self._checkPosition()
        params = None
        order_type = None
        if kwargs['order_type'] == 'OPEN_LONG':
            if self.position is not None:
               return
            self._setPrice(**kwargs)
            order_type = 'OPEN_LONG'
            params = dict( 
                symbol=self.symbol, 
                quantity=self.quantity, 
                side=Client.SIDE_BUY,
                type='MARKET',
               # timeInForce=Client.TIME_IN_FORCE_GTC,                
               # price = kwargs['price']
                )
        
        if kwargs['order_type'] == 'OPEN_SHORT':
            if self.position is not None:
               return
            self._setPrice(**kwargs)
            order_type = 'OPEN_SHORT'
            params = dict( 
                symbol=self.symbol, 
                quantity=self.quantity, 
                side=Client.SIDE_SELL,
                type='MARKET',
                #timeInForce=Client.TIME_IN_FORCE_GTC,                
               # price = kwargs['open_short']
                )
        if kwargs['order_type'] == 'CLOSE_LONG':
            if self.position != 1:
                   return
            order_type ='CLOSE_LONG'
            params = dict(  symbol=self.symbol, 
                            quantity=self.quantity, 
                            side=Client.SIDE_SELL,
                            type='MARKET'
                            #reduceOnly=True
                            #timeInForce=Client.TIME_IN_FORCE_GTC                            
                            #price = kwargs['close_price']
                            )
        if kwargs['order_type'] == 'CLOSE_SHORT':
            if self.position != 0:
                   return
            order_type ='CLOSE_SHORT'
            params = dict(  symbol=self.symbol, 
                            quantity=self.quantity, 
                            side=Client.SIDE_BUY,
                            type='MARKET'
                            #reduceOnly=True
                            #timeInForce=Client.TIME_IN_FORCE_GTC                            
                            #price = kwargs['close_price']
                            )
        if params is not None:
            self._placeOrder( order_type,params)
       

    def _placeOrder(self,order_type,params):
        self.Logs._writeLog('place order with :'+ str(self.symbol)+str(self.symbol))
        try:
            order = self.client.futures_create_order(**params)
            if order_type == 'OPEN_LONG' or order_type == 'OPEN_SHORT':   

                self.orderStatus = order['status']
                self.orderId = order['orderId']
                self.order = order
                self.position = 1 if order_type == 'OPEN_LONG' else 0    
                if True:#order['status'] == 'FILLED':
                                            
                            self._setStop()
                            if self.takeProfit is True:
                               self._takeProfit() 
                else :
                    self._checkOrder()         
            else:
                if True: #order['status'] == 'FILLED':                    
                    self._clearTrade()
                else:
                    self._checkOrder()

            self.Logs._writeLog('order success   '+ str(order))    
        except BinanceAPIException as e:
            self.Logs._writeLog('order error  '+ str(e))
         
      
   
    def _setPrice(self, **kwargs):
       
        self._checkBalance()
        
        self._setLeverage(int(kwargs['leverage']))
        self.takeProfit =True if kwargs['take_profit'] is not None else False
        self.quantity =round(self.tradeMargin/kwargs['price']*self.leverage,self.prc[self.symbol])   

       
        self.profiQuantity = self.quantity if kwargs['take_profit'] is not None else round(self.quantity/2 ,self.prc[self.symbol])   
        self.tradePrice = kwargs['price']
        self.side = 'BUY' if kwargs['trade_type']== 'LONG' else  'SELL' 
        ## set stop   

        
        self.stopLimit = kwargs['stop_limit']
        
        self.stopPrice = kwargs['stop_price']
        self.profitPrice = kwargs['profit_price']
        self.triggerSide = 'SELL' if kwargs['trade_type']== 'LONG' else  'BUY'
                
    def _setStop(self, typ='STOP'):
        if  self.setStopStatus is True:
            return
        if self.position is None:
            return     
        print('stop order :', self.symbol, self.quantity, self.stopPrice)
        if  True: # self.orderStatus == 'FILLED':
            if typ =='STOP':
                params = dict( 
                            symbol=self.symbol, 
                            quantity=self.quantity, 
                            side= self.triggerSide,
                            type='STOP',
                            reduceOnly=True,
                            price = self.stopPrice,           
                            stopPrice = self.stopPrice
                            #timeInForce=Client.TIME_IN_FORCE_GTC
                        )
            if typ=='TRAILING_STOP_MARKET':
                params = dict( 
                            symbol=self.symbol, 
                            quantity=self.quantity, 
                            side= self.triggerSide,
                            type='TRAILING_STOP_MARKET',
                            callbackRate=self.stopLimit
                            #price = self.stopPrice,           
                            #stopPrice = self.stopPrice
                            #timeInForce=Client.TIME_IN_FORCE_GTC
                        )
            try:
                order = self.client.futures_create_order(**params)
                if order['orderId']:
                    self.stopOrderId = order['orderId']
                    self.setStopStatus = True
                    self.stopOrder  = order 
            except BinanceAPIException as e:
                 self.Logs._writeLog('order error  '+ str(e))     

    def _takeProfit(self):
       
        if self.takeProfit is False:
            return
        if  self.takeProfitStatus is True:
            return
        if self.position is None:
            return  
        print('profit order :', self.symbol, self.profiQuantity, self.profitPrice)   
        if  True: # self.orderStatus == 'FILLED':
            try:
                order = self.client.futures_create_order( 
                            symbol=self.symbol, 
                            quantity=self.profiQuantity, 
                            side= self.triggerSide,
                            type='TAKE_PROFIT',
                            price = self.profitPrice,     
                            reduceOnly=True,     
                            stopPrice = self.profitPrice
                            #timeInForce=Client.TIME_IN_FORCE_GTC
                            )
                
                if order['orderId']:
                    self.profitOrderId = order['orderId']
                    self.takeProfitStatus = True
                    self.profitOrder  = order 
                self.Logs._writeLog('profit order success   '+ str(order))  
            except BinanceAPIException as e:
                 self.Logs._writeLog('order error  '+ str(e))  

    def _clearTrade(self):
        
        self._cancelOrders()
        self.stopLimit = 0
        self.quantity   = 0
        self.setStopStatus = False
        self.position = None
        self.order = None
        self.orderId  =0,
        self.forceTrade = False
        self.forceTradeCount =3
        self.stopOrderId = None,
        self.stopOrder   = None
        self.buyPrice =0
        self.sellPrice =0
        self.tradePrice =0
        self.triggerSide = None
        self.takeProfit = False
        self.orderStatus = 'NEW'
        self.profitSide = None
        self.takeProfit = False
        self.takeProfitStatus = False
        self.profitOrderId = None
        self.profitOrder = None
        self.profitLimit = 0
        self.profitPrice = None
        self.stopPrice = None
        self.leverage =5
       # self._cancelOrder(self.stopOrder)
       

    def _setLeverage(self, leverage):
        self.leverage = leverage
        self.client.futures_change_leverage(symbol=self.symbol, leverage=self.leverage)

    #''' check current usdt balance '''
    def _checkBalance(self):
        
        balance = self.client.futures_account_balance()
        usdt_balance = [d for d in balance if d['asset'] == 'USDT']
        wdth_balance=usdt_balance[0]['withdrawAvailable']
        total_balance =usdt_balance[0]['balance'] 
        margin = self.marginRate*float(total_balance)
        margin = margin if margin <float(wdth_balance) else float(wdth_balance)*0.9
        self.balance =float(total_balance)
        self.tradeMargin =margin


    def _cancelOrder(self, order):
        
        p = self.client.futures_cancel_order(symbol=self.symbol, orderId = order['orderId'])
        if p['status'] == 'CANCELED':
            
            if order['type'] == 'MARKET':
                if self.setStopStatus is True:
                     self._cancelOrder(self.stopOrder)
                if self.takeProfitStatus is True:
                     self._cancelOrder(self.profitOrder)
                self._clearTrade()
            if order['type'] == 'STOP':
                self.stopOrderId = None
                self.setStopStatus = False 
                self.stopOrder  = None
            if order['type'] == 'TAKE_PROFİT':
                self.profitOrderId = None
                self.takeProfitStatus = False 
                self.profitOrder  = None

   # ''' check position of current coin '''
    def _checkPosition(self):
        try:
            p = self.client.futures_position_information(symbol=self.symbol)
            
            if  float(p[0]['positionAmt']) < 0:
                self.position =0
                self.quantity = np.abs(float(p[0]['positionAmt']))
            elif float(p[0]['positionAmt']) >0 :
                self.position =1 
                self.quantity = np.abs(float(p[0]['positionAmt']))     
            else:
                self.position = None
                self._clearTrade()
            
        except BinanceAPIException as e:
                 self.Logs._writeLog('order error  '+ str(e))
 
            


    def _cancelOrders(self):
        self.client.futures_cancel_all_open_orders(symbol = self.symbol)
        
       
    def _checkProfit(self):
        
        self.Logs._writeLog('profit order  '+ str(self.profitOrderId)) 

        try:
            order = self.client.futures_get_order(symbol=self.symbol,orderId=self.profitOrderId)
            self.Logs._writeLog('profit order  '+ str(order)) 
            if order['status'] == 'FILLED':
            
                self.quantity = self.quantity-self.profiQuantity
                self.stopLimit = self.tradePrice
                self.takeProfitStatus = False
                if self.quantity>0:
                    self._cancelOrder(self.stopOrder)
                    self._setStop() #'TRAILING_STOP_MARKET'
                else:
                    self._clearTrade()
        except BinanceAPIException as e:
                 self.Logs._writeLog('order error  '+ str(e))  
    def _checkStop(self):
        
        order = self.client.futures_get_order(symbol=self.symbol,orderId=self.stopOrderId)

        if order['status'] == 'FILLED':
           
           self._clearTrade()

    def _checkOrder(self):
        order = self.client.futures_get_order(symbol=self.symbol,orderId=self.orderId)
       
        self.orderStatus = order['status']
        if self.order['side'] == 'BUY':
            self.position =1
            self._setStop() 
            self._takeProfit()
                    
        elif self.order['side'] == 'SELL':
            self.position =0
            self._setStop() 
            self._takeProfit()
        else:
            self.position = None
        # self._setStop() 
        # self._takeProfit()   


if __name__ == '__main__':
     from client import iClient
     t = Trade(iClient().client,'XRPUSDT')
     p ={'order_type': 'OPEN_SHORT', 'trade_type': 'SHORT', 'price': 1.137, 'stop_price': 1.134, 'stop_limit': 0.22, 'profit_price': 1.132, 'leverage': 5.0}
     t._order(**p)