# -*- coding: utf-8 -*-
"""
Created on Wed Mar 09 15:19:34 2016

@author: Chandler
"""

import csv
import tablib
a = list()
b = list()
with open('one-month-data.csv') as csvfile:
    reader = csv.DictReader(csvfile)
    for row in reader:
        a.append(row['cusip_id'])

b = list(set(a))        

headers = ('cusip_id')
data = b

data = tablib.Dataset(*data,headers = headers)
open('id.csv','wb').write(data.csv)