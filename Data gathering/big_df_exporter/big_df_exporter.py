# -*- coding: utf-8 -*-
"""
Created on Sat Feb 19 04:02:57 2022

@author: Noah
"""

import pandas as pd
import os

def check_path(infile):
    return os.path.exists(infile)   

first_entry = input('Tell me the path where your csv files are located at: ')

while True:
    
    if check_path(first_entry) == False:
        print('\n')
        print('This PATH is invalid!')
        first_entry = input('Tell me the RIGHT PATH in which your csv files are located: ')
        
    elif check_path(first_entry) == True:
        print('\n')
        final_output = first_entry
        break

big_df = pd.DataFrame() 
for name in os.listdir(first_entry):
    if name.endswith(".csv"):
        print(name)
        current_df_path = first_entry+"\\"+name
        df = pd.read_csv(current_df_path, header=None)
        big_df = big_df.append(df, ignore_index=True)
print("")        
print("the final df is the following")
print("")

#drop unnecesary columns
big_df.drop(5, inplace = True, axis=1)
big_df.drop(7, inplace = True, axis=1)
big_df.drop(8, inplace = True, axis=1)
big_df.drop(9, inplace = True, axis=1)
big_df.drop(10, inplace = True, axis=1)
big_df.drop(11, inplace = True, axis=1)

# Rename the column names for best practices
big_df.rename(columns = { 0 : 'Start Date', 
                          1 : 'Open Price',
                          2 : 'High Price',
                          3 : 'Low Price',
                          4 :'Close Price',
                          6 :'End Date',
                          }, inplace = True)

# Convert Unix Time values to actual dates
big_df['Start Date'] = pd.to_datetime(big_df['Start Date'], unit='ms')
big_df['End Date'] = pd.to_datetime(big_df['End Date'], unit='ms')

print(big_df)

#big_df.to_csv('path.csv')

#get an index from a particular value e.i: 2022-02-13 23:59:59.999
#str(big_df['End Date'].loc[lambda x: x=='2022-02-13 23:59:59.999'].index).split('[', 1)[1].split(']')[0]
#also, remember to call big_df_2 = big_df.iloc[start index : end index + 1 ] because iloc ommits the last value of end index.

#Use this sentence big_df_2 = big_df_2[['End Date','Close Price']] and big_df_2.set_index('End Date', inplace=True) to update 
#the df you want to export with only the close prices and end dates