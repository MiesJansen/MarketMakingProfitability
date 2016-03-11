"""
Created on Wed Mar 09 15:19:34 2016

@author: Chandler
@edit by Tom on Fri Mar 11
"""

import pandas as pd

import MMP_config as cfg

# a file containing a list of bond symbols and cusip_id of trades 
#  executed within 1 month before the last date of concern, from enhanced TRACE
BOND_LIST = "list"
CUSIP_LIST = "cusip_id_list"

df = pd.read_csv(cfg.DATA_PATH + BOND_LIST + ".csv", \
                 low_memory=False) # To silent warnings

# Obtain a unique list of cusip_id's
df['cusip_id'].astype(str)
cusip_id_list = df['cusip_id'].unique().tolist()

ids = pd.DataFrame(cusip_id_list)
ids.to_csv(cfg.DATA_PATH + CUSIP_LIST + ".csv", index = False, header = False)