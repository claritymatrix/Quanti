import numpy as np
import pandas as pd
import tushare as ts



if __name__ == '__main__':

    ts.set_token("25799613aa8715bb9bcc8788b295db8f95b9cdd4774a64389df0abdb")

    pro = ts.pro_api()

    df = pro.balancesheet(ts_code = '600507.SH',start_date = '20181220',end_date = '20190430')

    # print(df)

    df.to_csv('600507.csv')
