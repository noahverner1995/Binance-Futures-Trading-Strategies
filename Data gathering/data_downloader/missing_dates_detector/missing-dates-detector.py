# -*- coding: utf-8 -*-
"""
Created on Tue Feb 15 18:36:18 2022

@author: Noah
"""

import os
from datetime import datetime, timedelta

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

date_tuple = () 

#extract the dates from the csv filenames
for name in os.listdir(first_entry):
    if name.endswith(".csv"):
        x = (name.partition('-')[-1]).partition('-')[-1].removesuffix(".csv")
        print(f'adding {x} to the tuple')
        date_tuple = date_tuple + (x,)
        print(f'current tuple has the following elements: {date_tuple}')
        
# to datetime
readable_date_tuple = tuple([datetime.fromisoformat(s) for s in date_tuple])

# now make a date range based on min and max dates in readable_date_tuple
date_range = [min(readable_date_tuple)+timedelta(n) for n in range((max(readable_date_tuple)-min(readable_date_tuple)).days+1)]

missing_dates = set(date_range) - set(readable_date_tuple)

print(sorted(missing_dates))

