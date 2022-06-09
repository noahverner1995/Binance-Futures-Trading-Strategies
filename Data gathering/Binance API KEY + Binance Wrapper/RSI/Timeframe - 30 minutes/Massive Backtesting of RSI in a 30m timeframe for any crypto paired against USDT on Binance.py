# -*- coding: utf-8 -*-
"""
Created on Tue Jun  7 17:40:49 2022

@author: Noah
"""

from binance.client import Client
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt

plt.style.use('dark_background')


#personal API key and Secret Key from your Binance account

api_key = "your binance api key"

secret_key = "your binance secret key"

client = Client(api_key= api_key, api_secret= secret_key, tld= "com")

trading_pairs = [dictionary["symbol"] for dictionary in client.get_all_tickers()] # get all trading pairs 

usdt_trading_pairs = [usdt_pair for usdt_pair in trading_pairs if usdt_pair.endswith("USDT")] # extract only usdt trading pairs

deprecated_trading_pairs = []

not_wanted_coins = ["TUSD", "BUSD", "USDC", "USDP", "USTC", "DAI", "AUD", "BIDR", "BRL", "BCHSV", "BULL", "BEAR",
                    "EUR", "GBP", "RUB", "TRY", "UAH", "IDRT", "NGN", "UP", "DOWN", "BCHABC"]
#Delete not wanted coins
for ticket in usdt_trading_pairs[:]:
    for coin in not_wanted_coins:
        if coin in ticket:
            usdt_trading_pairs.remove(ticket)
            
#Delete trading pairs which don't have data at all
cloned_trading_pairs = usdt_trading_pairs

for suspicious_trading_pair in usdt_trading_pairs:
    start_date_unix = "1652349600000"
    end_date_unix = str(int(start_date_unix[:-3])+(30*60*1025)-1)+"999"

    klines = client.get_historical_klines(symbol=suspicious_trading_pair, interval="30m", start_str = start_date_unix, end_str=end_date_unix)

    #First check that such trading pair exists, if not remove that trading pair from the usdt_trading_pairs list
    if not klines:
        print(f"This trading pair {suspicious_trading_pair} has no data!")
        deprecated_trading_pairs.append(suspicious_trading_pair)
        cloned_trading_pairs.remove(suspicious_trading_pair)

usdt_trading_pairs = cloned_trading_pairs

#Now do the big process
profitable_trading_pairs = []

for trading_pair in usdt_trading_pairs:
    start_date_unix = "1652349600000"
    end_date_unix = str(int(start_date_unix[:-3])+(30*60*1025)-1)+"999"

    klines = client.get_historical_klines(symbol=trading_pair, interval="30m", start_str = start_date_unix, end_str=end_date_unix)

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

    ## Moving Averages start here

    df_trading_pair["MA 7"] = df_trading_pair['Close Price'].rolling(7).mean()
    df_trading_pair["MA 13"] = df_trading_pair['Close Price'].rolling(13).mean()
    df_trading_pair["MA 20"] = df_trading_pair['Close Price'].rolling(20).mean()

    ## RSI starts here
    rsi_period = 14
    rsi_oversold = 30
    rsi_overbought = 70

    fee = 0.0005

    df_trading_pair["Return"] = df_trading_pair['Close Price'].pct_change().shift(-1).fillna(0)
    df_trading_pair["Up"] = np.maximum(df_trading_pair['Close Price'].diff(), 0) #This method will return a series of upward price changes with 0s if such price changes are negative
    df_trading_pair["Down"] = np.maximum(-df_trading_pair['Close Price'].diff(), 0) #This method will return a series of downward price changes with 0s if such price changes are positive
    df_trading_pair["RS"] = df_trading_pair["Up"].rolling(rsi_period).mean()/df_trading_pair["Down"].rolling(rsi_period).mean()

    df_trading_pair["RSI"] = 100 - 100/(1 + df_trading_pair["RS"])

    ## Simulating Trading Strategy  REVISAR LA FORMA EN COMO CALCULA LOS VALORES DE LAS COLUMNAS "UP" Y "DOWN" DADO QUE NO CONCUERDAN DICHOS VALORES CON LOS QUE SE MUESTRAN EN BINANCE/TRADINGVIEW EN LAS MISMAS CONDICIONES 

    start = rsi_period
    df_trading_pair["Signal"] = 1*(df_trading_pair["RSI"] < rsi_oversold) - 1*(df_trading_pair["RSI"] > rsi_overbought)
    BnH_return = np.array(df_trading_pair["Return"][start+1:]) #We start investing at the start + 1 because we expect to get a return when the next candle closes, and we do it until the very end  
    RSI_gross_return = np.array(df_trading_pair["Return"][start+1:])*np.array(df_trading_pair["Signal"][start:-1]) #We expect to get the return until the penultimate candle
    RSI_net_return = RSI_gross_return - fee*abs(np.array(df_trading_pair["Signal"][start+1:]) - np.array(df_trading_pair["Signal"][start:-1])) #We pay fees depending on wether we trade or not and if we trade wether we trade twice or once  
    BnH = np.product(1+BnH_return)**(365/len(BnH_return)) - 1 #Annualized returns BnH strategy
    RSI = np.product(1+RSI_net_return)**(365/len(RSI_net_return)) - 1 #Annualized returns RSI strategy

    BnH_risk = np.std(BnH_return)*(365)**(1/2) # Risk of BnH strategy
    RSI_risk = np.std(RSI_net_return)*(365)**(1/2) # Risk of RSI strategy

    df_trading_pair = df_trading_pair.dropna(axis=0)
    
    if max(np.append(100, 100*np.cumprod(1 + RSI_gross_return))) > max(np.append(100, 100*np.cumprod(1 + df_trading_pair["Return"]))) >= 130 :
        profitable_trading_pairs.append(trading_pair)
    
    # Backtesting    
    plt.figure(figsize=(16, 12), dpi=80)
    plt.title(f'Backtesting of RSI for the {trading_pair} trading pair', fontsize = 20)
    plt.rc('xtick', labelsize = 10)
    plt.ylabel('Initial Investment (USDT)', fontsize=10)
    plt.plot(df_trading_days[rsi_period+4:] ,np.append(100, 100*np.cumprod(1 + df_trading_pair["Return"])), label = "Buy & Hold Strategy")
    plt.plot(df_trading_days[rsi_period:] ,np.append(100, 100*np.cumprod(1 + RSI_gross_return)), label = "RSI Strategy")
    plt.plot(df_trading_days[rsi_period:] ,np.append(100, 100*np.cumprod(1 + RSI_net_return)), label = "RSI Strategy after fees")
    plt.legend(loc='lower right', fontsize = "large") 
    plt.savefig(f'path/Backtesting of RSI for the {trading_pair} trading pair.png')
    plt.clf() #release memory
    plt.close() #kill the figure
