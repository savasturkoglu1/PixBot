import numpy as np
from client import iClient
from binance.client import Client
from binance.enums import *
#from db import DataBase
from binance.exceptions import BinanceAPIException
import time
import json
from logger import Logs

class Trade:
    def __init__(self,client, coin):
        ## objects
        self.client = client
        self.symbol = coin
        #self.df     = DataBase()
        self.Logs = Logs()
              

        ## order constants
        self.marginRate = 50
        self.stopRate = 2
        self.profitRate = 7
        
        self.side = None
        self.leverage=5

         
        ## take profi order 
        self.profitSide = None
        self.takeProfit = False
        self.takeProfitStatus = False
        self.profitOrderId = None
        self.profitOrder = None
        self.profitLimit = 0

        ## stop order
        self.stopSide = None
        self.stopLimit = 0
        self.stopOrderId = None
        self.stopOrder = None
        self.setStopStatus = False
        
        ## trade order
        self.position = None 
        self.order = None
        self.balance = 0
        self.tradeMargin =0
        self.quantity = 0        
        self.tradePrice = 0
        self.buyPrice = 0
        self.sellPrice = 0
        self.order = None
        self.orderType = None
        self.orderStatus = 'NEW'
        self.orderId = None
        self.forceTrade = False
        self.forceTradeCount =0

        
        
    def _trade(self):
        pass
    
    def _order(self, **kwargs):
        self._checkPosition()
        if kwargs['order_type'] == 'OPEN_LONG':

    @classmethod
    def _setPrice(self, price, trade_type = 'LONG'):
        self._setLeverage()
        self._checkBalance()
        self.quantity = round((self.tradeMargin/price)*self.leverage)    
        self.tradePrice = price
        self.side = 'BUY' if trade_type== 'LONG' else  'SELL' 
        ## set stop     
        self.stopLimit = round((100-self.stopRate)*price/100,3) if trade_type== 'LONG' else round((100+self.stopRate)*price/100,3)

        self.stopSide = 'SELL' if trade_type== 'LONG' else  'BUY'

        ## set profit
        self.profitLimit = round((100+self.profitRate)*price/100,3) if trade_type== 'LONG' else round((100-self.profitRate)*price/100,3)
        self.profitSide = 'SELL' if trade_type== 'LONG' else  'BUY'

    def _checkBalance(self):
        balance = self.client.futures_account_balance()
        usdt_balance = [d for d in balance if d['asset'] == 'USDT']
        balanceUsdt=usdt_balance[0]['withdrawAvailable']
        self.balance =float(balanceUsdt)
        self.tradeMargin =self.marginRate*(float(balanceUsdt)/100)
        

    def _live(self, data):
        if self.order is not  None:
            if self.orderStatus !='FILLED':
                self._checkOrder()
            if self.setStopStatus == False and self.takeProfit == False:
                self._setStop()
            if self.takeProfitStatus == False:
                self._takeProfit()
            if self.takeProfitStatus == True:
                self._checkProfit()    
        if self.forceTrade:
            if self.orderStatus != 'FILLED':                              
                    self._forceTrade()

    def _forceTrade(self):
        if self.forceTradeCount == 0:
            order_type = self.order['side']
            self._cancelOrder(self.order)
            if order_type == 'BUY':
                self._buy(self.tradePrice)
            if order_type == 'SELL':
                self._sell(self.tradePrice)

        else:
            self.forceTradeCount = self.forceTradeCount-1

    def _buy(self, buy_price=0, side='OPEN', trade_type = 'MARKET', force_trade = False, force_trade_count =3):
         ## check current  position
         self._checkPosition()
         if self.position==1: 
                return
         if self.position ==0:
                side = 'CLOSE'
         if self.position is None:
                if side== 'TWO_WAY':
                   side = 'OPEN'       
         if side =='CLOSE':
            if self.position !=0:
                 return         
         ##set trade constants
         self.buyPrice = buy_price        
         self.forceTrade = force_trade
         self.forceTradeCount = force_trade_count
         
         if side =='OPEN':     
           self._setPrice(buy_price)
         else:
               self.takeProfit = True 
              


         ## set params according market type
         
         params = dict( 
                symbol=self.symbol, 
                quantity=self.quantity, 
                side=Client.SIDE_BUY,
                type=trade_type,
                timeInForce=Client.TIME_IN_FORCE_GTC,                
                price = buy_price)

         if trade_type == 'MARKET':
            params = dict(
                symbol=self.symbol, 
                quantity=self.quantity,  
                side=Client.SIDE_BUY,
                type=Client.ORDER_TYPE_MARKET)
           


         ## place order
         
         try:
            order = self.client.futures_create_order(**params)
            if side == 'OPEN':    
                self.orderStatus = order['status']
                self.orderId = order['orderId']
                self.order = order
                self.position = 1    
                if order['status'] == 'FILLED':
                                            
                            self._setStop()
                            self._takeProfit() 
                else :
                    self._checkOrder()         
            else:
                if order['status'] == 'FILLED':                    
                    self._clearTrade()
                else:
                    self._checkOrder()

            self.Logs._writeLog('order success   '+ str(order))    
         except BinanceAPIException as e:
            self.Logs._writeLog('order error  '+ str(e))
         else:
             self.Logs._writeLog('order success   cofirm  '+ str(order))
         
         ## chek ortder status and set order
            
         
         
         
          
            


    def _sell(self, sell_price=0, side='OPEN',  trade_type='MARKET',force_trade = False,force_trade_count=3):

        ## check position

        
        self._checkPosition()
        if self.position ==0:
                return
        if self.position ==1:
            side = 'CLOSE'   
        if self.position == None:
                if side== 'TWO_WAY':
                   side = 'OPEN'         
        if side =='CLOSE':
            if self.position !=1:
                return         
        ## set orde constants        
        self.sellPrice =sell_price        
        self.forceTrade = force_trade
        self.forceTradeCount = force_trade_count
        if side =='OPEN':
           self._setPrice(sell_price, 'SHORT')
        else:
           self.takeProfit = True    
        if trade_type == 'MARKET':
            params = dict(
                    symbol=self.symbol, 
                    quantity=self.quantity, 
                    side=Client.SIDE_SELL,                    
                    type=Client.ORDER_TYPE_MARKET)
        else:
            params = dict(  symbol=self.symbol, 
                            quantity=self.quantity, 
                            side=Client.SIDE_SELL,
                            type=trade_type,
                            timeInForce=Client.TIME_IN_FORCE_GTC,                            
                            price = sell_price)
      

        try:
            order = self.client.futures_create_order(**params)
            

            if side =='OPEN':  
                self.orderStatus = order['status']
                self.orderId = order['orderId']
                self.order = order
                self.position =0   
                if order['status'] == 'FILLED':
                                      
                        self._setStop() 
                        self._takeProfit()
                else :
                  self._checkOrder()         
            else:
                if order['status'] == 'FILLED':
                    
                    self._clearTrade()
                else:
                    self._checkOrder()
            self.Logs._writeLog('order success   '+ str(order))    
        except BinanceAPIException as e:
            self.Logs._writeLog('order error  '+ str(e))
        else:
             self.Logs._writeLog('order success   cofirm'+ str(order))

        
        
                
    def _setStop(self):
        if  self.setStopStatus:
            return
        if self.position ==None:
            return     
        if  True: # self.orderStatus == 'FILLED':
            
            order = self.client.futures_create_order( 
                       symbol=self.symbol, 
                         quantity=self.quantity, 
                        side= self.stopSide,
                        type='STOP',
                        price = self.stopLimit,           
                        stopPrice = self.stopLimit,
                        timeInForce=Client.TIME_IN_FORCE_GTC
                        )
            if order['orderId']:
                self.stopOrderId = order['orderId']
                self.setStopStatus = True
                self.stopOrder  = order      

    def _takeProfit(self):
        p = self.quantity//2
        
        if  self.takeProfitStatus:
            return
        if self.position ==None:
            return     
        if  True: # self.orderStatus == 'FILLED':
            
            order = self.client.futures_create_order( 
                        symbol=self.symbol, 
                        quantity=p, 
                        side= self.profitSide,
                        type='TAKE_PROFIT',
                        price = self.profitLimit,           
                        stopPrice = self.profitLimit,
                        timeInForce=Client.TIME_IN_FORCE_GTC
                        )
            if order['orderId']:
                self.profitOrderId = order['orderId']
                self.takeProfitStatus = True
                self.profitOrder  = order 

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
        self.stopSide = None
        self.takeProfit = False
        self.orderStatus = 'NEW'
        self.profitSide = None
        self.takeProfit = False
        self.takeProfitStatus = False
        self.profitOrderId = None
        self.profitOrder = None
        self.profitLimit = 0


       # self._cancelOrder(self.stopOrder)
       

    def _setLeverage(self):
        self.client.futures_change_leverage(symbol=self.symbol, leverage=self.leverage)
        # self._checkPosition()
        # if self.position ==0:
        #     self.client.futures_change_leverage(symbol=self.symbol, leverage=self.leverage)
        #     self.leverage = l


                
        
    
    def _cancelOrder(self, order):
        p = self.client.futures_cancel_order(symbol=self.symbol, orderId = order['orderId'])
        if p['status'] == 'CANCELED':
            
            if order['side'] == 'BUY':
                if self.setStopStatus:
                     self._cancelOrder(self.stopOrder)
                self._clearTrade()
            if order['side'] == 'STOP':
                self.stopOrderId = 0
                self.setStopStatus = False 
    def _checkPosition(self):
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


    def _cancelOrders(self):
        self.client.futures_cancel_all_open_orders(symbol = self.symbol)
       
    def _checkProfit(self):
        order = self.client.futures_get_order(symbol=self.symbol,orderId=self.profitOrderId)

        if order['status'] == 'FILLED':
           p = self.quantity//2
           self.quantity = self.quantity-p

    def _checkOrder(self):
        order = self.client.futures_get_order(symbol=self.symbol,orderId=self.orderId)
       
        self.orderStatus = order['status']
       # if order['status'] == 'FILLED':
        if self.takeProfit == True:
               
                self._clearTrade()
        else: 
                if self.order['side'] == 'BUY':
                    self.position =1
                    
                else:
                    self.position =0
                self._setStop() 
                self._takeProfit()   
