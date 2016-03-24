"""
Created on Wed Mar 09 15:19:34 2016

@author: Chandler

This script runs independently from main.py to produce a set of cusip ids to be
 used for requesting data from enhanced TRACE database
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

## FIX The assumption and workaround below is due to not having data of historical
##  amount outstanding for each bond, which is a critical scaling factor for liquidity
##  measure calculation. With proper data, the assumption and workaround is not
##  needed.
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
df_datastream = pd.read_csv(cfg.DATA_PATH + "bond_list_datastream.csv")
## FIX with historical rating data from FISD, this segmentation would be better
##  applied while calculating liquidity proxies for each month
ddf_segments = dm.SegmentByRating(df_cusip_TRACE, df_datastream)

# Output bond cusips based on rating segmentation results
for seg in cfg.RATING_SEGS:
    #print "Number of " + seg + " bond = " + str(ddf_segments[seg].shape[0])
    if not ddf_segments[seg].empty:
        ddf_segments[seg].to_csv(cfg.DATA_PATH + "MOODY_RATING_cusips_" + \
                                 seg + ".csv")
        ddf_segments[seg]["cusip_id"].to_csv(cfg.DATA_PATH + "cusip_ids_MOODY_RATING_" +\
                                             seg + ".txt", sep = ' ',
                                             index = False, header = False)

ddf_segments = dm.SegmentBySIC(df_cusip_TRACE, df_datastream)

# Output bond cusips based on rating segmentation results
for seg in cfg.INDUSTRY_SEGS:
    #print "Number of " + seg + " bond = " + str(ddf_segments[seg].shape[0])
    if not ddf_segments[seg].empty:
        ddf_segments[seg].to_csv(cfg.DATA_PATH + "INDUSTRY_SIC_cusips_" + \
                                 seg + ".csv")
        ddf_segments[seg]["cusip_id"].to_csv(cfg.DATA_PATH + "cusip_ids_INDUSTRY_SIC_" +\
                                             seg + ".txt", sep = ' ',
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
