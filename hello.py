
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import backtrader as bt
import datetime
from jqdatasdk import *

def finance_balance_sheet():

    stock_sheet = Stock('000905.XSHG','2019-04-23','2011-01-01')
    stock_sheet.plot_data()


    # stock_data.to_csv('egg.csv')

class Stock:
    def __init__(self,stock_id,stock_end_date,stock_start_date='2011-01-01'):
        self.stock_id  = stock_id
        self.stock_start_date = stock_start_date
        self.stock_end_date = stock_end_date
        self.stock_data = self.stock_query()
        self.stock_data.fillna(0,inplace=True)
        #self.stock_data.to_csv('000905.csv')

    def stock_query(self):

        return get_price(self.stock_id,start_date= self.stock_start_date,
                       end_date=self.stock_end_date)

    def write_to_csv(self,filepath,filename,filetpye='.csv'):

        self.stock_data.to_csv(filepath +filename+filetpye)

    def plot_data(self):



        stock_data_m5 = self.stock_data['close'].rolling(window=5).mean()
        stock_data_m10 = self.stock_data['close'].rolling(window=10).mean()
        stock_data_m60 = self.stock_data['close'].rolling(window=60).mean()

        #stock_data_mean = pd.DataFrame([stock_data_m5,stock_data_m10,stock_data_m60])

        # stock_data_mean.plot()
        #
        # plt.show()

        stock_data_m60.plot(color='r')
        #stock_data_m10.plot()
        stock_data_m5.plot(color='b')

        plt.show()

class TestStrategy(bt.Strategy):

    def log(self, txt, dt=None):
        ''' Logging function for this strategy'''
        dt = dt or self.datas[0].datetime.date(0)
        print('%s, %s' % (dt.isoformat(), txt))

    def __init__(self):
        # Keep a reference to the "close" line in the data[0] dataseries
        self.dataclose = self.datas[0].close

        self.order = None

        def notify(self, order):
            if order.status in [order.Submitted, order.Accepted]:
                # Buy/Sell order submitted/accepted to/by broker - Nothing to do
                return

            # Check if an order has been completed
            # Attention: broker could reject order if not enougth cash
            if order.status in [order.Completed, order.Canceled, order.Margin]:
                if order.isbuy():
                    self.log('BUY EXECUTED, %.2f' % order.executed.price)
                elif order.issell():
                    self.log('SELL EXECUTED, %.2f' % order.executed.price)

                self.bar_executed = len(self)

            # Write down: no pending order
            self.order = None

        def next(self):

            # Simply log the closing price of the series from the reference
            self.log('Close, %.2f' % self.dataclose[0])

            # Check if an order is pending ... if yes, we cannot send a 2nd one
            if self.order:
                return

            # Check if we are in the market
            if not self.position:

                # Not yet ... we MIGHT BUY if ...
                if self.dataclose[0] < self.dataclose[-1]:
                    # current close less than previous close

                    if self.dataclose[-1] < self.dataclose[-2]:
                        # previous close less than the previous close

                        # BUY, BUY, BUY!!! (with default parameters)
                        self.log('BUY CREATE, %.2f' % self.dataclose[0])

                        # Keep track of the created order to avoid a 2nd order
                        self.order = self.buy()

            else:

                # Already in the market ... we might sell
                if len(self) >= (self.bar_executed + 5):
                    # SELL, SELL, SELL!!! (with all possible default parameters)
                    self.log('SELL CREATE, %.2f' % self.dataclose[0])

                    # Keep track of the created order to avoid a 2nd order





    def next(self):
        # Simply log the closing price of the series from the reference
        self.log('Close, %.2f' % self.dataclose[0])



if __name__ == '__main__':


    # auth('18380152997','2wsx3edc')
    # finance_balance_sheet()


    cerebro = bt.Cerebro()

    cerebro.addstrategy(TestStrategy)


    data_000905 = pd.read_csv('000905.csv',index_col= 0,parse_dates=True)

    data_000905['openinterest'] = 0

    data = bt.feeds.PandasData(dataname = data_000905,
                               fromdate = datetime.datetime(2011,1,1),todate = datetime.datetime(2019,2,11))

    cerebro.adddata(data)



    cerebro.broker.setcash(100000.00)
    print('Starting Protfolio Value:%2f' %cerebro.broker.getvalue())

    cerebro.run()

    print('Final Protfolio Value:%2f' %cerebro.broker.getvalue())

    cerebro.plot()