# -*- coding: utf-8 -*-
"""
Created on Thu Jun  2 10:53:31 2022

@author: Noah
"""

from binance.client import Client
import numpy as np
import pandas as pd
import statsmodels.api as sm
import scipy.stats as sps
import matplotlib.pyplot as plt

#personal API key and Secret Key from your Binance account

api_key = "your binance api key"

secret_key = "your binance secret key"

client = Client(api_key= api_key, api_secret= secret_key, tld= "com")

#first of all, set UTC as your timezone in your desired trading chart (only coins paired against USDT/BUSD) on Binance
#if you are living in Colombia, remember to add 5 hours to both start date and end date.
#the code below only works with trading pairs which are paired against the USDT or some major currency/stablecoin like that one
trading_pair = "PONDUSDT"
start_date_unix = "1652349600000"
end_date_unix = str(int(start_date_unix[:-3])+(15*60*1025)-1)+"999"

klines = client.get_historical_klines(symbol=trading_pair, interval="15m", start_str = start_date_unix, end_str=end_date_unix)

df_trading_pair = pd.DataFrame(klines)

#drop unnecesary columns
df_trading_pair.drop(5, inplace = True, axis=1)
df_trading_pair.drop(7, inplace = True, axis=1)
df_trading_pair.drop(8, inplace = True, axis=1)
df_trading_pair.drop(9, inplace = True, axis=1)
df_trading_pair.drop(10, inplace = True, axis=1)
df_trading_pair.drop(11, inplace = True, axis=1)

# Rename the column names for best practices
df_trading_pair.rename(columns = { 0 : 'Start Date', 
                          1 : 'Open Price',
                          2 : 'High Price',
                          3 : 'Low Price',
                          4 :'Close Price',
                          6 :'End Date',
                          }, inplace = True)

# Convert Unix Time values to actual dates
df_trading_pair['Start Date'] = pd.to_datetime(df_trading_pair['Start Date'], unit='ms')
df_trading_pair['End Date'] = pd.to_datetime(df_trading_pair['End Date'], unit='ms')
df_trading_pair = df_trading_pair[['End Date','Close Price']]
df_trading_pair = df_trading_pair.set_index('End Date', inplace=False)
df_trading_pair = df_trading_pair.astype({'Close Price': 'float'})

# Save the trading days data
df_trading_days = df_trading_pair.index[:]

##Bollinger Bands Stuff start here
lookback = 20 #how many trading 15 minutes back are we calculating the moving average and standard deviation for the bands for
width = 2 #how many standard deviations of the price defined by the looback do we use to define the trading range of the price
fee = 0.0000
df_trading_pair["MA"] = df_trading_pair['Close Price'].rolling(lookback).mean()
df_trading_pair["STd"] = df_trading_pair['Close Price'].rolling(lookback).std()
df_trading_pair["Upper"] = df_trading_pair["MA"] + width*df_trading_pair['STd']
df_trading_pair["Lower"] = df_trading_pair["MA"] - width*df_trading_pair['STd']

# Visualising the price
plt.figure(figsize=(8, 6), dpi=80)
plt.title(f'Bollinger Bands applied to the {trading_pair} trading pair', fontsize = 12)
plt.rc('xtick', labelsize = 8)
plt.ylabel('Price (USDT)', fontsize=10)
plt.plot(df_trading_pair["Close Price"], label = "Close Price")
plt.plot(df_trading_pair["MA"], label = "Moving Average")
plt.plot(df_trading_pair["Upper"], label = "Upper Band")
plt.plot(df_trading_pair["Lower"], label = "Lower Band")
plt.legend(loc='lower right', fontsize = "x-small")       


df_trading_pair["Return"] = df_trading_pair["Close Price"].pct_change().shift(-1).fillna(0)

#Base the decision on the so called "Impulse" to extract signals
df_trading_pair["Impulse"] = (df_trading_pair["Close Price"] - df_trading_pair["Lower"])/(df_trading_pair["Upper"] - df_trading_pair["Lower"])
#As Bollinger Bands are based on reversals, we would be inclined to long the asset expecting a positive correction
#If the Impulse value is 0 or lower, and we would be inclined to short the asset expecting a negative correction
#If the Impulse value is 1 or greater. And we would remain in position until we cross the MA (Moving Average)

df_trading_pair = df_trading_pair.dropna(axis=0)
old_signal = 0

signals = np.array([])
gross = np.array([])
net = np.array([])

for t in range(0, len(df_trading_pair)):
    if df_trading_pair["Impulse"][t] >= 1:
        signal = -1
    elif df_trading_pair["Impulse"][t] <= 1:
        signal = 1
    #if none of the above is true, we need to check if we were in position we crossed the relevant MA (Moving Average)     
    elif old_signal*(df_trading_pair["Impulse"][t] - 0.5) > 0:
        signal = 0
    else: 
        signal = old_signal
        
    gross_return = signal*df_trading_pair['Return'][t]
    net_return = gross_return - fee*abs(signal - old_signal)
    signals = np.append(signals, signal)
    gross = np.append(gross, gross_return)
    net = np.append(net, net_return)
    old_signal = signal
    
# Backtesting    
plt.figure(figsize=(8, 6), dpi=80)
plt.title(f'Backtesting of Bollinger Bands for the {trading_pair} trading pair', fontsize = 12)
plt.rc('xtick', labelsize = 8)
plt.ylabel('Initial Investment (USDT)', fontsize=10)
plt.plot(df_trading_days[lookback-2:] ,np.append(100, 100*np.cumprod(1 + df_trading_pair["Return"])), label = "Buy & Hold Strategy")
plt.plot(df_trading_days[lookback-2:] ,np.append(100, 100*np.cumprod(1 + gross)), label = "Bollinger Bands Strategy")
plt.plot(df_trading_days[lookback-2:] ,np.append(100, 100*np.cumprod(1 + net)), label = "Bollinger Bands Strategy after fees")
plt.legend(loc='lower right', fontsize = "x-small")       
