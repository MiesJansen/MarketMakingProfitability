"""
Created on Wed Mar 09 15:19:34 2016

@author: Chandler
@edit by Tom on Fri Mar 11
"""

import pandas as pd
import numpy as np

import MMP_config as cfg

# a file containing a list of bond symbols and cusip_id of trades 
#  executed within 1 month before the last date of concern, from enhanced TRACE
BOND_LIST = "list"
CUSIP_LIST = "cusip_id_list"

df = pd.read_csv(cfg.DATA_PATH + BOND_LIST + ".csv", \
                 low_memory=False) # To silent warnings

# Obtain a unique list of cusip_id's
df['cusip_id'].astype(str)
cusip_id_list = df.drop_duplicates(['cusip_id'])

# Remove empty entries
cusip_id_list = cusip_id_list[cusip_id_list['cusip_id'].notnull()]
cusip_id_list = cusip_id_list[cusip_id_list['company_symbol'].notnull()]
cusip_id_list = cusip_id_list[cusip_id_list['bond_sym_id'] != '.']

# Output the whole list to csv
cusip_id_list.to_csv(cfg.DATA_PATH + CUSIP_LIST + ".csv", \
                     index = False, header = True)

# Break into smaller sub-dataframe due to TRACE 2GB limitation
ids = cusip_id_list['cusip_id']
ids_lists = np.array_split(ids, cfg.NUM_SUB_DF)
for i in range(cfg.NUM_SUB_DF):
    ids_lists[i].to_csv(cfg.DATA_PATH + CUSIP_LIST + str(i) + ".txt", sep = ' ', \
                        index = False, header = False)

