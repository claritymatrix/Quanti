import numpy as np
import pandas as pd

import backtrader as bt
import datetime
import backtrader.indicators as btind
import argparse
import math
import queue

class max_window_ind(bt.Indicator):

    params = dict(maxwindow=20,)

    def __init__(self,maxwindow):
        self.params.maxwindow = maxwindow

        self.adminperiod(self.params.maxwindow * 2)

    def getmotive(self,x,y):

        return (y - x) / x

class cash():


    def __init__(self,cash,stake = 10):


        self.cash = cash
        self.one_cash = cash / stake
        self.top = stake
        self.trade_queue = queue.Queue(stake)


    def empty():

        return self.trade_queue.empty()



    def full():
        return self.trade_queue.full()



class mystrategy(bt.Strategy):

    params=(('exitbars',5),
            ('mapperiod',180),
            ('mapperiod02',20),
            ('sellflag',0),
            ('buyflag',0),
            ('ownprice',0),
    )
    def log(self,txt,dt = None):
        '''Logging function for this strategy'''

        dt = dt or self.datas[0].datetime.date(0)

        print("%s,%s " %(dt.isoformat(),txt))


    def __init__(self):

        self.dataclose = self.datas[0].close
        self.order = None


        #self.macd = bt.indicators.MACD(self.datas[0])
        #self.sma05 = btind.SMA(self.datas[0],period = self.params.mapperiod,subplot=False)
        self.sma20 = btind.SMA(self.datas[0],period = self.params.mapperiod02,subplot = False)
        self.bbrands = btind.BBands(self.datas[0],subplot = False)
        self.max20 = bt.talib.MAX(self.datas[0],period = self.params.mapperiod02,plot = False)

        self.min20 = bt.talib.MIN(self.datas[0],period = self.params.mapperiod02,plot = False)
        self.atr = btind.ATR(self.datas[0],plot = False)




        self.signaltop = btind.CrossOver(self.dataclose,self.bbrands.top,plot=False)

        self.signalcrossover = btind.CrossOver(self.dataclose,self.sma20,plot = False)
        self.signallow = btind.CrossOver(self.datas[0],self.bbrands.bot)
        self.signaltop = btind.CrossOver(self.datas[0],self.bbrands.top)




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

                #self.params.ownprice = order.executed.value


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

        #print("buyflag is %.2f,sellfalg is %.2f" %(self.params.buyflag,self.params.sellflag))
        #if (self.signalcrossover > 0.0) and (self.params.buyflag == 0): #
        #    self.params.buyflag = 1

        #    if (self.signaltop > 0.0) and (self.params.sellflag == 0):
#
        #        self.params.sellflag = 1


        if not self.position:

            #if  (self.signallow > 0.0) and (self.params.buyflag == 1):

            if (self.signallow < 0.0):

                #self.params.buyflag = 0
                #self.sellflag = 0



                self.order = self.buy(size = 6000)

                self.log('Buy Create %.2f ' %(self.dataclose[0]))


        else:
            #print('the crossover signal is %.2f' % self.signalcrossover[0])
            #if  (self.signalcrossover <  0.0) and (self.params.sellflag == 1) and (self.params.ownprice < self.dataclose[0]):

            if   (self.signaltop > 0.0)and (self.dataclose[0] > self.params.ownprice):
                #self.params.sellflag = 0
                self.log('Sell Create %.2f ' %(self.dataclose[0]))
                self.order = self.sell(size = 6000)






def add_data(filename = '002475.csv'):

    dataframe = pd.read_csv(filename,index_col = 0,parse_dates = True)

    dataframe['openinterest'] = 0


    #print(dataframe)

    return dataframe

def parser_args():
    """parse args used to get command line args"""
    parser = argparse.ArgumentParser(description='ATR')


    parser.add_argument('--stockid','-s',default='002475.csv',help="input the stock file name like 000651.csv")

    parser.add_argument('--fromdate','-f',default='2011-01-01',help="Start date in YYYY-MM-DD format")

    parser.add_argument('--todate','-t',default='2020-1-18',help="end date in YYYY-MM-DD format")

    parser.add_argument('--cash',default='18000000',type=int,help='starting cash')

    parser.add_argument('--comm',default='0.0012',type=float,help='Commission for operation')

    parser.add_argument('--stake',default=3,type=int,help="Stake to apply in each operation")

    return parser.parse_args()






def runstrategy():
    """run strategy is use to run strategy"""

    args = parser_args()


    fromdate = datetime.datetime.strptime(args.fromdate,"%Y-%m-%d")
    todate = datetime.datetime.strptime(args.todate,"%Y-%m-%d")




    cerebro = bt.Cerebro()

    cerebro.broker.setcash(args.cash)


    data = bt.feeds.PandasData(dataname = add_data(args.stockid),fromdate = fromdate,todate=todate)


    cerebro.adddata(data)
    cerebro.addstrategy(mystrategy)
    cerebro.broker.setcommission(commission = args.comm)


    print("Start Protfolio Value:%.2f" %cerebro.broker.getvalue())
    cerebro.run()

    print("Final Protfolio Value:%.2f" % cerebro.broker.getvalue())
    cerebro.plot()



if __name__ == "__main__":
    runstrategy()
