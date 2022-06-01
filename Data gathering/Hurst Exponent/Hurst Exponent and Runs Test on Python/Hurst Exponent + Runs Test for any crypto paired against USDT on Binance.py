# -*- coding: utf-8 -*-
"""
Created on Wed May 25 22:30:24 2022

@author: Noah
"""

#Python-Binance docs https://python-binance.readthedocs.io/en/latest/_modules/binance/client.html#Client.get_historical_klines_generator

from binance.client import Client
import numpy as np
import pandas as pd
import statsmodels.api as sm
import scipy.stats as sps
import datetime
#import json

#personal API key and Secret Key from your Binance account

api_key = "your_binance_api_key"

secret_key = "your_binance_secret_key"

client = Client(api_key= api_key, api_secret= secret_key, tld= "com")

balance_account = client.get_account()

#print the balance account sortedly
#print(json.dumps(balance_account, sort_keys = False, indent =4))
#print("\n")

#should be "{}"
#print(client.ping())
#print("\n")

#should be "{'status': 0, 'msg': 'normal'}"
#print(client.get_system_status())
#print("\n")

df_balances = pd.DataFrame(balance_account["balances"])

#first of all, set UTC as your timezone in your desired trading chart (only coins paired against USDT/BUSD) on Binance
#if you are living in Colombia, remember to add 5 hours to both start date and end date.
#the code below only works with trading pairs which are paired against the USDT or some major currency/stablecoin like that one
trading_pair = "REEFUSDT"
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

#specifying the maximum power of 2
power = 10
#rolling sample lenght
n = 2**power

#downloading data
raw_data = df_trading_pair
returns = np.array(raw_data)[1:]/np.array(raw_data)[:-1]-1

#initializing arrays
hursts = np.array([])
tstats = np.array([])
pvalues = np.array([])

#calculating the rolling Hurst exponent 

for t in np.arange(n, len(returns)+1):
    #specifying the subsample
    data = returns[t-n:t]
    X = np.arange(2,power+1)
    Y = np.array([])
    for p in X:
        m = 2**p
        s = 2**(power-p)
        rs_array = np.array([])
        
        #moving across subsamples
        for i in np.arange(0, s):
            subsample = data[i*m:(i+1)*m]
            mean = np.average(subsample)
            deviate = np.cumsum(subsample-mean)
            difference = max(deviate) - min(deviate)
            stdev = np.std(subsample)
            rescaled_range = difference/stdev
            rs_array = np.append(rs_array, rescaled_range)
        
        #calculating the log2 of average rescaled range
        Y = np.append(Y, np.log2(np.average(rs_array)))
    
    reg = sm.OLS(Y, sm.add_constant(X))
    res = reg.fit()
    hurst = res.params[1]
    tstat = (res.params[1]-0.5)/res.bse[1]
    pvalue = 2*(1 - sps.t.cdf(abs(tstat), res.df_resid))
    hursts = np.append(hursts, hurst)
    tstats = np.append(tstats, tstat)
    pvalues = np.append(pvalues, pvalue)
print(f'Trading pair: {trading_pair}')
print('\n')
print("Start date (UTC): "+datetime.datetime.fromtimestamp(int(start_date_unix)/1000).strftime('%Y-%m-%d %H:%M:%S.%f'))
print("End date (UTC): "+datetime.datetime.fromtimestamp(int(end_date_unix)/1000).strftime('%Y-%m-%d %H:%M:%S.%f'))
print(f'Hurst Exponent was: {round(hursts[0], 4)}')
print(f'T stat was: {round(tstats[0], 3)}')
print(f'P value was: {round(pvalues[0], 6)}')
if pvalues > 0.05:
    print('According to the p-value, the times series of this trading pair is doing a random walk')
elif hursts[0] > 0.5 and pvalues < 0.05:
    print('According to the Hurst Exponent, the times series used is trending')
elif hursts[0] < 0.5 and pvalues < 0.05:
    print('According to the Hurst Exponent, the times series used is doing a mean-reversion')
print('\n')

## Testing market efficiency with Runs Test

returns = returns[returns != 0]
n = len(returns)
signs = np.sign(returns)

runs = signs[1:] - signs[:-1]
observed_runs = np.count_nonzero(runs == 2) + np.count_nonzero(runs == -2) +1
positive_returns = np.count_nonzero(signs == 1)
negative_returns = np.count_nonzero(signs == -1)
expected_runs = 2*positive_returns*negative_returns/n +1
stdev_runs = (expected_runs*(expected_runs - 1)/(n - 1))**(1/2)
z_stat = (observed_runs - expected_runs)/stdev_runs
p_value = 2*(1 - sps.norm.cdf(abs(z_stat)))

if p_value > 0.1:
    print('According to the Runs Test, this market is efficient')
elif z_stat > 0:
    print('According to the Runs Test, this market is mean-reverting')
else:
    print('According to the Runs Test, this market is trending')

print(f'Observed runs were: {observed_runs}')
print(f'Expected runs were: {int(expected_runs)}')
print(f'Standard deviations of runs were: {round(stdev_runs, 2)}')
print(f'Z stat was: {round(z_stat, 4)}')
print(f'P value was: {round(p_value, 4)}')
