# -*- coding: utf-8 -*-
"""
Created on Mon Mar 21 17:13:05 2016

@author: Chandler

This script runs independently from main.py to clean manually downloaded data
 from Datastream database
"""

import csv
import tablib
import os
import pandas as pd
a = []
b = []
c = []
d = []
e = []
f = []
g = []
h = []
df = pd.DataFrame()
df1 = pd.DataFrame()
os.chdir('C:\Users\Chandler\Desktop\liquidity project\data')
with open('bondData.csv','rU') as csvfile:
    reader = csv.DictReader(csvfile,delimiter = ',',dialect = csv.excel_tab)
    for row in reader:
        a.append(row['Type'])
        b.append(row['NAME'])
        c.append(row['ISIN CODE'])
        d.append(row['COUPON'])
        e.append(row['MOODY\'S RATING'])
        f.append(row['BORROWER SIC'])
        g.append(row['AMOUNT ISSUED'])
        h.append(row['AMOUNT OUTSTANDING'])
        

df['Type'] = a
df['NAME'] = b
df['ISIN CODE'] = c
df['COUPON'] = d
df['MOODY\'S RATING'] = e
df['BORROWER SIC'] = f
df['AMOUNT ISSUED'] = g
df['AMOUNT OUTSTANDING'] = h
df1 = df.drop_duplicates(cols='ISIN CODE', take_last=True)
df1.to_csv('bondData(cleaned).csv')
