# -*- coding: utf-8 -*-
"""
Created on Thu May 26 22:22:48 2022

@author: Noah
"""
import numpy as np
import matplotlib.pyplot as plt
import yfinance as yf
import statsmodels.api as sm
import scipy.stats as sps

#specifying the maximum power of 2
power = 10

#rolling sample lenght
n = 2**power

ticker = "^GSPC"
start = "2015-12-31"
end = "2021-06-16"

#downloading data
raw_data = yf.download(ticker, start, end)['Close']
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

#visualising the Hurst exponent
plt.figure(1)
plt.title('Historical Hurst Exponent of S&P500', fontsize=10)
plt.rc('xtick', labelsize = 8)
plt.ylim(0.4, 0.6)
plt.plot(raw_data.index[n:], hursts)
plt.plot(raw_data.index[n:], np.ones(len(hursts))*0.5)

#visualising the t-stat and critical values
plt.figure(2)
plt.title('T values in hypothesis testing of Hurst Exponent for the S&P500', fontsize=10)
plt.rc('xtick', labelsize = 8)
plt.plot(raw_data.index[n:], tstats)
plt.plot(raw_data.index[n:], np.ones(len(tstats))*sps.t.ppf(0.005, res.df_resid)) #the greater than 2.8 the better
plt.plot(raw_data.index[n:], np.ones(len(tstats))*sps.t.ppf(0.995, res.df_resid)) #get very worried


#visualising the p-values
plt.figure(3)
plt.title('P values in hypothesis testing of Hurst Exponent for the S&P500', fontsize=10)
plt.rc('xtick', labelsize = 8)
plt.plot(raw_data.index[n:], pvalues)
plt.plot(raw_data.index[n:], np.ones(len(pvalues))*0.05) #reject h0 if pvalue is less than 0.05
plt.plot(raw_data.index[n:], np.ones(len(pvalues))*0.001) #reject h0 because either a highly rare data result has been observed, or the null hypothesis is incorrect.

#visualising the price
plt.figure(4)
plt.title('S&P500 Price')
plt.rc('xtick', labelsize = 8)
plt.plot(raw_data.index[n:], raw_data[1024:])
