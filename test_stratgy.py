import numpy as np
import pandas as pd

import backtrader as bt
import datetime
import backtrader.indicators as btind
import argparse
#
#class max_index_ind(bt.Indicator):
#
#    lines = ('maxwindow',)
#    def __init__(self,max_window):
#
#        self.params.max_window = max_window
#
#        self.adminperiod(self.params.max_window * 2)
#
#    def getmotivate(self,t,y):
#
#        return (y - t)/t
#
#    def getstockprice(self,input_array):
#        return input_array
#
#
#
#    def MAXWINDOW(self,input_array_01,input_array_02,input_array_03):
#
#        return new_array



#class max_index_ind(bt_Indicator):
#    lines = ('maxwindow',)
#
#
 #   def __init__(self,max_window):
  #      self.params.max_window = max_window
#
 #       self.adminperiod(self.params.max_window * 2)
#
 #   def getmotivate(self,t,y):
  #      return (y - t) / t
#
 #   def MAXWINDOW(self,input_array):
  #      getmotivate(input_array[-20],input_array[0])
#
#
 #   def next(self):
  #      self.lines.maxwindow[0] = self.MAXWINDOW(self.datas[0])
class mystrategy(bt.Strategy):

    params=(('exitbars',5),
            ('stake',100),
            ('mapperiod',40),
            ('devfactor',2.0),
            ('tail',False),
    )
    def log(self,txt,dt = None):
        '''Logging function for this strategy'''

        dt = dt or self.datas[0].datetime.date(0)

        print("%s,%s " %(dt.isoformat(),txt))


    def __init__(self):

        self.dataclose = self.datas[0].close
        self.order = None

        #self.macd = bt.indicators.MACD(self.datas[0])
        self.sma = btind.SMA(self.datas[0],subplot=False)
        self.bbrands = btind.BBands(self.datas[0],period = self.params.mapperiod,devfactor = self.params.devfactor)
        self.atr = btind.ATR(self.datas[0],plot = False)


        self.signaltop = btind.CrossOver(self.dataclose,self.bbrands.top,plot=False)

        self.signallow = btind.CrossOver(self.dataclose,self.bbrands.bot,plot = False)



        self.buyprice = None
        self.buycomm = None




    def notify_order(self,order):

        if order.status in [order.Submitted,order.Accepted]:
            return

        if order.status in [order.Completed]:
            if order.isbuy():
                #self.log("Buy executed %.2f" % order.executed.price)
                self.log("Buy executed price %.2f,cost: %.2f,comm %.2f" %(order.executed.price,
                                                                          order.executed.value,
                                                                          order.executed.comm))

                self.buyprice = order.executed.price
                self.buycomm = order.executed.comm

                # set sizer



            else:
                #self.log("Sell executed %.2f" % order.executed.price)
                self.log("Sell executed price %.2f ,cost %.2f, comm %.2f" %(order.executed.price,
                                                                            order.executed.value,
                                                                            order.executed.comm))


            self.bar_executed = len(self)

        elif order.status in [order.Canceled,order.Margin,order.Rejected]:
            self.log("Order Canceled/Margin/Rejected")

        self.order = None

    def notify_trade(self,trade):
            if not trade.isclosed:
                return
            self.log('Operation profit gross %.2f net %.2f' %(trade.pnl,trade.pnlcomm))

    def next(self):

        self.log('Close %.2f' % self.dataclose[0])


        if self.order:
            return
        if not self.position:
            if self.signaltop > 0.0:
                self.log('Buy Create %.2f' % self.dataclose[0])
                self.order = self.buy(size = 100)


        else:

            if (self.signallow < 0.0) or (self.dataclose[0] < self.sma[0]):
                self.log('Sell create %.2f' %self.dataclose[0])

                self.order = self.sell(size = 100)
#        if not self.position:
#            if self.dataclose[0] <= self.dataclose[-1]:
#                self.log('Buy create %.2f' %self.dataclose[0])
#                self.order = self.buy()
#        else:
#            if self.dataclose[-1] > self.dataclose[0]:
#                self.log("sell create %.2f" %self.dataclose[0])
#                self.order = self.sell()
#





def add_data():

    dataframe = pd.read_csv('000651.csv',index_col = 0,parse_dates = True)

    dataframe['openinterest'] = 0


    #print(dataframe)

    return dataframe

def parser_args():
    """parse args used to get command line args"""
    parser = argparse.ArgumentParser(description='ATR')

    parser.add_argument('--fromdate','-f',default='2011-01-01',help="Start date in YYYY-MM-DD format")

    parser.add_argument('--todate','-t',default='2018-12-31',help="end date in YYYY-MM-DD format")

    parser.add_argument('--cash',default='10000',type=int,help='starting cash')

    parser.add_argument('--comm',default='0.0012',type=float,help='Commission for operation')

    parser.add_argument('--stake',default=1,type=int,help="Stake to apply in each operation")

    return parser.parse_args()






def runstrategy():
    """run strategy is use to run strategy"""

    args = parser_args()


    fromdate = datetime.datetime.strptime(args.fromdate,"%Y-%m-%d")
    todate = datetime.datetime.strptime(args.todate,"%Y-%m-%d")




    cerebro = bt.Cerebro()

    cerebro.broker.setcash(args.cash)


    data = bt.feeds.PandasData(dataname = add_data(),fromdate = fromdate,todate=todate)


    cerebro.adddata(data)
    cerebro.addstrategy(mystrategy)
    cerebro.broker.setcommission(commission = args.comm)


    print("Start Protfolio Value:%.2f" %cerebro.broker.getvalue())
    cerebro.run()

    print("Final Protfolio Value:%.2f" % cerebro.broker.getvalue())
    cerebro.plot()



if __name__ == "__main__":
    runstrategy()
