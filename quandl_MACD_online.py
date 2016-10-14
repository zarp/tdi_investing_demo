import pandas as pd
import numpy as np
#import matplotlib.pylab as plt #if uncommenting - add to requirements.txt before pushing to heroku
from statsmodels.tsa.stattools import adfuller

from bokeh.models.widgets import Select
from bokeh.io import output_file, show, vform
    
#Moving Average  
def MA(df, n):
    """ df - dataframe. n - number of days
    THIS IS NOT AN EXPONENTIAL MOVING AVERAGE
    CHANGE TO COLUMN ENTRY NAME"""
    #MA = pd.Series(pd.rolling_mean(df['BCHARTS/COINBASEUSD - Close'], n), name = 'MA_' + str(n))  #and change name of MA col to something more descriptive 
    EMA = pd.Series(pd.ewm(df['BCHARTS/COINBASEUSD - Close'], span=n).mean(), name = 'EMA_' + str(n))
    #pd.ewma(arg,span=5)
    df = df.join(EMA)  #MA 
    return df


def MACD(df, column):
    """ df - dataframe. n - number of days
    THIS IS NOT AN EXPONENTIAL MOVING AVERAGE
    CHANGE TO COLUMN ENTRY NAME"""
    #MA = pd.Series(pd.rolling_mean(df['BCHARTS/COINBASEUSD - Close'], n), name = 'MA_' + str(n))  #and change name of MA col to something more descriptive 


    EMA26 = pd.Series( pd.Series.ewm(df[column], span=26).mean(), name = column+'_EMA_26' ) #emaslow
    EMA12 = pd.Series( pd.Series.ewm(df[column], span=12).mean(), name = column+'_EMA_12' ) #emafast
    
    #pd.ewma(arg,span=5)
    df = df.join(EMA26) #MA
    df = df.join(EMA12)
    df[column+'_MACD']=df[column+'_EMA_12']-df[column+'_EMA_26']
    signal_line = pd.Series(pd.Series.ewm(df[column+'_MACD'], span=9).mean(), name = column + '_MACD_signal_line' ) #signal line
    df = df.join(signal_line)
    df[column+'_buy']=df[column+'_MACD']-df[column+'_MACD_signal_line'] # if buy>0: buy. if buy<0 sell. May add some margins later
    return df

def buy_to_bull(inp_float):
    if isinstance(inp_float,float):
        if inp_float==0:
            return None
        if inp_float>0:
            return True
        else:
            return False
    else:
        return None

if __name__ == "__main__" :
    filename="merged_bcharts_n_baverage_daily_inner.csv"
    #https://www.analyticsvidhya.com/blog/2016/02/time-series-forecasting-codes-python/
    data=pd.read_csv(filename)

    #td=pd.to_numeric(td)
    #print data.head()
    td=data[['Date','BCHARTS/COINBASEUSD - Close']]
    td=td[td['BCHARTS/COINBASEUSD - Close'].notnull()]
    td.set_index(['Date'],inplace=True)

    td.index = pd.to_datetime(td.index)


    #print 'cols=',list(td.columns.values)
    #print 'aaa=',type(td['BCHARTS/COINBASEUSD - Close'].iloc[0])
    print(td.index) #is it dtype='datetime64[ns]' ? if not- fix
    print(td.head())
    print(td['2015']) #accessing all entries from 2015

    #A TS is said to be stationary if its statistical properties such as mean, variance, autocovariance remain constant over time. But why is it important? Most of the TS models work on the assumption that the TS is stationary.

    #plt.plot(td)
    td=MACD(td)
    td['buy']=td['buy'].apply(buy_to_bull)

    td.to_csv("metaderp.csv")
    #test_stationarity(td['BCHARTS/COINBASEUSD - Close'])

    #plt.show()

