# -*- coding: utf-8 -*-
"""
Created on Sun Feb 13 17:40:21 2022

@author: Noah
"""

import time
import numpy as np
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By

opt = Options() #the variable that will store the selenium options
opt.add_experimental_option("debuggerAddress", "localhost:9222") #this allows bulk-dozer to take control of your Chrome Browser in DevTools mode.
s = Service(r'C:\Users\ResetStoreX\AppData\Local\Programs\Python\Python39\Scripts\chromedriver.exe') #Use the chrome driver located at the corresponding path
driver = webdriver.Chrome(service=s, options=opt) #execute the chromedriver.exe with the previous conditions

#Why using MarkPrices: https://support.btse.com/en/support/solutions/articles/43000557589-index-price-and-mark-price#:~:text=Index%20Price%20is%20an%20important,of%20cryptocurrencies%20on%20major%20exchanges.&text=Mark%20Price%20is%20the%20price,be%20fair%20and%20manipulation%20resistant.

if driver.current_url == 'https://data.binance.vision/?prefix=data/futures/um/daily/markPriceKlines/ALICEUSDT/1h/' :   
    number = 2 #initialize an int variable to 2 because the desired web elements in this page starts from 2
    counter = 0
    the_dictionary_links = {}
    while number <= np.size(driver.find_elements(By.XPATH, '//*[@id="listing"]/tr')): #iterate over the tbody array
        data_file_name = driver.find_element(By.XPATH, f'//*[@id="listing"]/tr[{number}]/td[1]/a').text
        if data_file_name.endswith('CHECKSUM') == False:
            the_dictionary_links[data_file_name] = driver.find_element(By.XPATH, f'//*[@id="listing"]/tr[{number}]/td[1]/a').get_attribute('href')
            print(f'Saving {data_file_name} and its link for later use')
            counter += 1            
        number += 1
    print(counter)
    i = 0
    o = 0
    for i,o in the_dictionary_links.items():
        driver.get(o)
        print(f'Downloading {i}')
        time.sleep(1.8)
        