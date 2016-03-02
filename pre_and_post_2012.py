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

    
# ASSUMPTIONS: each input dataframe should have identical cusip_id
# Processing applied only to pre-2012 data
def pre2012(df):
    print "Cleaning pre-2012 data..."
    
    df = sameday_corrections(df)
    df = reversals(df)
    
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
    
    df = df.drop(trds_to_drop.index, axis = 0)
    
    return df

def reversals(df):
    # Identify reversals
    df_R = df[df['asof_cd'] == "R"]
    # Also, Reversals must have report day > execution date
    df_R = df_R[df_R['trd_rpt_dt'] > df_R['trd_exctn_dt']]
    
    # All reversals will be deleted
    trds_to_drop = df_R
    
    nRev = trds_to_drop.shape[0]
    print "Number of Reversals is", nRev
    
    for idx, trd in df_R.iterrows():
        # Filtre out trades with same execution date
        day_trds = df[df['trd_exctn_dt'] == trd['trd_exctn_dt']]
        # Avoid matching Reversals with itself
        day_trds = day_trds[day_trds['asof_cd'] != "R"]
        
        # Find trades that match with the Reversal trade
        match = np.all([day_trds['trd_exctn_tm'] == trd['trd_exctn_tm'], \
                       day_trds['rptd_pr'] == trd['rptd_pr'], \
                       day_trds['entrd_vol_qt'] == trd['entrd_vol_qt'], \
                       day_trds['rpt_side_cd'] == trd['rpt_side_cd'], \
                       day_trds['cntra_mp_id'] == trd['cntra_mp_id']], \
                       axis = 0)
        Rmatch = day_trds[match]
        
        if Rmatch.shape[0] > 0:
            # Only use at most 1 match of reversal
            trds_to_drop = trds_to_drop.append(Rmatch.iloc[0])
    
    nMatch = trds_to_drop.shape[0] - nRev
    print "Number of Reverasal match is", nMatch
    
    df = df.drop(trds_to_drop.index, axis = 0)
    
    return df

def post2012(df):
    print "Cleaning post-2012 data..."
    
    df = sameday_corrections_post(df)
    return df

def sameday_corrections_post(df):
    # Delete the following:

    # 1. cancellations and corrections
    df_temp_deleteI_NEW = df[df['trc_st'].isin(["X", "C"])]

    # 2. Reversals
    df_temp_deleteII_NEW = df[df['trc_st'] == "Y"]

    # 3. Raw data with cancellations, reversals, and corrections removed
    df_temp_raw = df[~df['trc_st'].isin(["X", "C", "Y"])]

    merge_columns = ['cusip_id', 'entrd_vol_qt', 'rptd_pr',
        'trd_exctn_dt', 'trd_exctn_tm', 'rpt_side_cd', 'cntra_mp_id', 
        'msg_seq_nb']

    # inner merge temp_raw and temp_deleteI_NEW on merge columns
    # keep index of temp_deleteI_NEW (same as original parameter df)
    df_temp_raw2_del_rows = pd.merge(df_temp_raw[list(merge_columns)], 
        df_temp_deleteI_NEW[list(merge_columns)],
        how = 'inner', on=merge_columns, right_index=True)

    #---- Uncomment print statements to verify right number of columns removed
    # at each step. ------------

    #print('df_temp_raw shape: ', df_temp_raw.shape)
    #print('df_temp_raw2_del_rows shape: ', df_temp_raw2_del_rows.shape)

    # Drop merged columns from temp_raw and temp_deleteI_NEW
    df_temp_raw2 = df_temp_raw.drop(df_temp_raw2_del_rows.index, axis=0)

    #print('df_temp_raw_2 shape: ', df_temp_raw2.shape)

    df_temp_raw3_del_rows = pd.merge(df_temp_raw2[list(merge_columns)], 
        df_temp_deleteII_NEW[list(merge_columns)],
        how = 'inner', on=merge_columns, right_index=True)

    #print('df_temp_raw3_del_rows shape: ', df_temp_raw3_del_rows.shape)

    df_temp_raw3 = df_temp_raw2.drop(df_temp_raw3_del_rows.index, axis=0)  

    #print('df_temp_raw3 shape: ', df_temp_raw3.shape)  

    return df_temp_raw3


def AgencyTransac(df):
    print "Cleaning agency transactions..."
    
    # Isolate transactions with customers, without commission
    rows_to_clean = np.all([df['cntra_mp_id'] == 'C', df['cmsn_trd'] == 'N'], \
                           axis = 0)
    df_temp1 = df[rows_to_clean]
    
    # Identify and drop agency transactions
    rows_buyAg = np.all([df_temp1['rpt_side_cd'] == 'B', \
                         df_temp1['buy_cpcty_cd'] == 'A'], axis = 0)
    rows_sellAg = np.all([df_temp1['rpt_side_cd'] == 'S', \
                          df_temp1['sell_cpcty_cd'] == 'A'], axis = 0)
    df_temp2 = df_temp1[np.any([rows_buyAg, rows_sellAg], axis = 0)]
    
    df_temp3 = df.drop(df_temp2.index, axis = 0)
    
    return df_temp3

## For testing only
if __name__ == "__main__":
    df0 = pd.read_csv('C:\Users\Alex\Desktop\Industry Project\\trace_data.csv', \
                     low_memory=False) # To silent warnings

    # common pre-processing for all data
    df1 = Initial_deletes(df0)
    
    # Extract data before Feb 6, 2012
    df_pre2012 = df1[df1['trd_rpt_dt'] < 20120206]
    df_post2012 = df1[df1['trd_rpt_dt'] >= 20120206]

    df_pre2012 = pre2012(df_pre2012)
    print "Dimension of processed pre2012 dataset is", df_pre2012.shape
    
    df_post2012 = post2012(df_post2012)
    print "Dimension of processed post2012 dataset is", df_post2012.shape

    # Recombine the pre-/post-2012 data frames
    df2 = pd.concat([df_pre2012, df_post2012], ignore_index = True)
    print "Dimension of recombined dataset is", df2.shape
    
    df3 = AgencyTransac(df2)
    print "Dimension of dataset without agency transaction is", df3.shape
    