# -*- coding: utf-8 -*-
"""
Created on Sun Feb 13 17:40:21 2022

@author: Noah
"""

import time
from datetime import date, timedelta
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service

opt = Options() #the variable that will store the selenium options
opt.add_experimental_option("debuggerAddress", "localhost:9222") #this allows bulk-dozer to take control of your Chrome Browser in DevTools mode.
s = Service(r'your_chromedriver.exe_path') #Use the chrome driver located at the corresponding path
driver = webdriver.Chrome(service=s, options=opt) #execute the chromedriver.exe with the previous conditions

#Why using MarkPrices: https://support.btse.com/en/support/solutions/articles/43000557589-index-price-and-mark-price#:~:text=Index%20Price%20is%20an%20important,of%20cryptocurrencies%20on%20major%20exchanges.&text=Mark%20Price%20is%20the%20price,be%20fair%20and%20manipulation%20resistant.

if driver.current_url == 'https://data.binance.vision/?prefix=data/futures/um/daily/markPriceKlines/XRPUSDT/1h/':
    
    #Set your desired start date and end date
    start_date = date(2022, 1, 2)
    end_date = date(2022, 2, 13)
    delta = timedelta(days=1)
    
    #iterate over the dates
    while start_date <= end_date:
        
        date_string = str(start_date)
        
        filename = "XRPUSDT"+"-"+"1h"+"-"+date_string+".zip"
        
        #create a download link for this particular page
        download_link = driver.current_url+filename
        
        #go to the download link
        driver.get(download_link)
        
        #print what's being downloaded and wait 2 seconds before repeating the process with the next date
        print(f'Downloading {filename}')
        time.sleep(2)
        
        #count it
        start_date += delta
        
