"""
Created on Wed Mar 09 15:19:34 2016

@author: Chandler
@edit by Tom on Fri Mar 11
"""

import pandas as pd
import numpy as np

import MMP_config as cfg

# Two files containing lists of bond symbols, cusip_ids of trades executed within
#  1 month period at the beginning and at the end of the interested period,
#  respectively, from enhanced TRACE database
CUSIP_RAW_1 = "cusip_id_start_raw"
CUSIP_RAW_2 = "cusip_id_end_raw"
# Output file of unique cusip ids
CUSIP_LIST = "cusip_id_list"


def unique_cusip(cusip_raw_file):
    df = pd.read_csv(cfg.DATA_PATH + cusip_raw_file + ".csv", \
                    low_memory=False) # To silent warnings    

    # Obtain a unique list of cusip_id's
    df['cusip_id'] = df['cusip_id'].astype(str)
    df_cusip = df.drop_duplicates(['cusip_id'])
    
    # Remove empty entries
    df_cusip = df_cusip[df_cusip['cusip_id'].notnull()]
    df_cusip = df_cusip[df_cusip['company_symbol'].notnull()]
    df_cusip = df_cusip[df_cusip['bond_sym_id'] != '.']    
    
    return df_cusip
    

# Main
# --------------------------------------------
df1 = unique_cusip(CUSIP_RAW_1)
df2 = unique_cusip(CUSIP_RAW_2)

# Find the commonly traded cusip id in two sets (so bonds do not mature or
#  issue during the period of interest)
## ASSUMPTION: when there are no issue or mature, the outstanding amount of the
##  market stays constant
cusip_id_list = pd.merge(left = df1, right = df2, on = ['cusip_id'], \
                         how = 'inner')

# Output the whole list to csv
cusip_id_list.to_csv(cfg.DATA_PATH + CUSIP_LIST + ".csv", \
                     index = False, header = True)

# Break into smaller sub-dataframe due to TRACE 2GB limitation
ids = cusip_id_list['cusip_id']
ids_lists = np.array_split(ids, cfg.NUM_SUB_DF)
for i in range(cfg.NUM_SUB_DF):
    ids_lists[i].to_csv(cfg.DATA_PATH + CUSIP_LIST + str(i) + ".txt", sep = ' ', \
                        index = False, header = False)

