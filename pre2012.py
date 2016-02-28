import pandas as pd
import numpy as np

# TO-DO: pre/post2012 code needs to be merge (now standalone).
# TO-DO: add some statistics, e.g. # of matched same day cancellation/correction
#        or even keep a copy of all deleted entries for record.

# enhanced TRACE columns that are not useful in analysis
COLS_TO_REMOVE = ['company_symbol', 'sale_cndtn2_cd', 'dissem_fl', 'SUB_PRDCT',\
                  'STLMNT_DT', 'TRD_MOD_3', 'TRD_MOD_4', 'LCKD_IN_IND', \
                  'PR_TRD_DT']

# dropping rows and columns, applied to all data
def Initial_deletes(df):    
    # delete items without cusip_id
    df = df[df['cusip_id'] != '']
    
    # find common elements in to_drop columns and imported dataframe columns
    cols_to_remove = [col for col in df.columns if col in COLS_TO_REMOVE]
    df.drop(cols_to_remove, axis = 1,inplace = True)

    return df

    
# Processing applied only to pre-2012 data
def pre2012(df):
    df = sameday_corrections(df)
    
    return df


# Adjust trade cancellations and corrections within the same day
def sameday_corrections(df):
    # Delete the following:
    # 1. cancellation trades themselves
    trds_to_drop = df[df['trc_st'] == "C"]
    
    # TO-FIX: this loop seems super inefficient (very slow).
    #         How to isolate trades of the same day better?
    # 2. original trade of cancellation(C) and correction(W) orders 
    tradesCW = df[df['trc_st'].isin(["C", "W"])]
    for idx, trd in tradesCW.iterrows():
        # Filtre out sameday trades
        day_trds = df[df['trd_rpt_dt'] == trd['trd_rpt_dt']]
        # Find matching message sequence number
        orig_trds = day_trds[day_trds['msg_seq_nb'] == trd['orig_msg_seq_nb']]
        trds_to_drop = trds_to_drop.append(orig_trds)
    
    df.drop(trds_to_drop.index, inplace = True)
    
    return df
    
    
    
## For testing only
if __name__ == "__main__":
    df = pd.read_csv('./data/BAC.HQO_20100331_20140330_raw.csv')

    # common pre-processing for all data
    df = Initial_deletes(df)
    
    # Extract data before Feb 6, 2012
    df_pre2012 = df[df['trd_rpt_dt'] < 20120206]
    df_post2012 = df[df['trd_rpt_dt'] >= 20120206]

    df_pre2012 = pre2012(df_pre2012)
    #df_post2012 = post2012(df_post2012)
    
    print(df_pre2012.shape)