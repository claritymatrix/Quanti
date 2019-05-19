import numpy as np
import pandas as pd
from jqdatasdk import *



if __name__ == '__main__':


    auth('18380152997','2wsx3edc')
    df = get_price('600507.XSHG',start_date='2011-1-1 00:00:00',end_date='2019-4-23 12:00:00',
                   frequency='1d')


    #print(df['datetime.datetime'])


    #    print(df.index)
    #print(df)

    print(df.index)
    col_name = df.columns.tolist()

    col_name.insert(col_name.index('open'),'00:00:00')

    df.reindex(columns = col_name)

    df.to_csv('6005072.csv')
