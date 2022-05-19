# -*- coding: utf-8 -*-
"""
Created on Sun May 15 22:55:11 2022

@author: Noah
"""

import pandas as pd
import matplotlib.pyplot as plt

# Import the csv file without index
OHLC_df = pd.read_csv('pathfile.csv', index_col=0, parse_dates=['End Date'])

# Create a new df that only contains the date and close price from the previous imported df
close_price_df = OHLC_df[['End Date','Close Price']]

# Set the 'Date' column as the actual index
close_price_df.set_index('End Date', inplace=True) 

# set the breadth and length of the plot as a good mix of values
plt.figure(figsize=(14,5))

# set a grid background to the plot
plt.grid(True, axis ='y')
plt.grid(True, axis='x', which='major')

# set the color of the trend as blue
plt.plot(close_price_df, 'b')

# mark red dots to plot the discrete data
#plt.plot(close_price_df, 'ro')

# give a title to the plot
plt.title('SOLUSDT close price from June 29 2021 to February 13 2022')

# give a label to the x axis
plt.xlabel('Date')

# gove a label to the y axis
plt.ylabel('Close Price')
