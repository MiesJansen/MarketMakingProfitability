"""
Created on Wed Mar 09 15:19:34 2016

@author: Chandler
@edit by Tom on Fri Mar 11
"""

import pandas as pd
import numpy as np

import MMP_config as cfg
import DivideMarket as dm

# Two files containing lists of bond symbols, cusip_ids of trades executed within
#  1 month period at the beginning and at the end of the interested period,
#  respectively, from enhanced TRACE database
CUSIP_RAW_1 = "cusip_id_start_raw"
CUSIP_RAW_2 = "cusip_id_end_raw"


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
df_cusip_TRACE = pd.merge(left = df1, right = df2, on = ['cusip_id'], \
                          how = 'inner')

# Output the whole list to csv
df_cusip_TRACE.to_csv(cfg.DATA_PATH + cfg.CUSIP_LIST + "_TRACE.csv", \
                      index = False, header = True)

# Merge with Datastream data for bond characteristics, and divide bonds into
#  sub-markets by Moody's (current) Rating
## FIX with historical rating data from FISD, this division would be better
##  applied while calculating liquidity proxies for each month
df_datastream = pd.read_csv(cfg.DATA_PATH + "bond_list_datastream.csv")
df_IG, df_HY = dm.SegmentByRating(df_cusip_TRACE, df_datastream,
                                  cfg.MARKET_DELIMITER)

# Output investment grade and high yield results
if not df_IG.empty:
    #print "Number of Investment Grade bond =", df_IG.shape[0]
    df_IG.to_csv(cfg.DATA_PATH + cfg.MARKET_DELIMITER + "_cusips_IG.csv")
    df_IG["cusip_id"].to_csv(cfg.DATA_PATH + "cusip_ids_" +\
                             cfg.MARKET_DELIMITER + "_IG.txt", sep = ' ',
                             index = False, header = False)
if not df_HY.empty:
    #print "Number of High Yield bond =", df_HY.shape[0]
    df_HY.to_csv(cfg.DATA_PATH + cfg.MARKET_DELIMITER + "_cusips_HY.csv")
    df_HY["cusip_id"].to_csv(cfg.DATA_PATH + "cusip_ids_" +\
                             cfg.MARKET_DELIMITER + "_HY.txt", sep = ' ',
                             index = False, header = False)


# With market segments, the following is no longer necessary. Keep this as
#  comment, as it might become useful when number of corporate bonds increases
'''
# Break into smaller sub-dataframe due to TRACE 2GB limitation
ids = cusip_id_list['cusip_id']
ids_lists = np.array_split(ids, cfg.NUM_SUB_DF)
for i in range(cfg.NUM_SUB_DF):
    ids_lists[i].to_csv(cfg.DATA_PATH + CUSIP_LIST + str(i) + ".txt", sep = ' ', \
                        index = False, header = False)
'''
