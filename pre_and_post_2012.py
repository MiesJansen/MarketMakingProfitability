import pandas as pd
import numpy as np

# Uncomment print statements in the code to see detailed debug logs in console

def remove_cols(df, rm_columns):
    # find common elements in to_drop columns and imported dataframe columns
    cols_to_remove = [col for col in df.columns if col in rm_columns]
    df = df.drop(cols_to_remove, axis = 1)
    
    return df

# dropping rows and columns, applied to all data
def Initial_deletes(df):
    # enhanced TRACE columns that are not useful in analysis
    COLS_TO_REMOVE = ['company_symbol', 'sale_cndtn2_cd', 'dissem_fl', 'SUB_PRDCT',\
                      'STLMNT_DT', 'TRD_MOD_3', 'TRD_MOD_4', 'LCKD_IN_IND', \
                      'PR_TRD_DT', 'buy_cmsn_rt', 'sell_cmsn_rt']
    
    df = remove_cols(df, COLS_TO_REMOVE)

    return df


# Processing applied only to pre-2012 data
def pre2012(df):
    #print "Cleaning pre-2012 data..."
    
    df = sameday_corrections(df)
    df = reversals(df)
    
    return df

# Adjust trade cancellations and corrections within the same day
def sameday_corrections(df):
    dfsize = df.shape[0]
    
    # 1. Mark of cancellation(C) and correction(W) orders 
    tradesCW = df[df['trc_st'].isin(["C", "W"])]
    
    left_columns = ['trd_rpt_dt', 'msg_seq_nb']
    right_columns = ['trd_rpt_dt', 'orig_msg_seq_nb']
    # Merge on trade report date (sameday) and 
    #  original message sq # from CW entries with msg sq # of raw trade data
    # Keep the index of left dataframe (the raw trade) so we know which rows to
    #  delete from it
    trds_to_drop = pd.merge(left = df[left_columns],
                            right = tradesCW[right_columns],
                            left_on = left_columns, right_on = right_columns,
                            how = 'inner', left_index = True)
    # Delete any matched entries
    df = df.drop(trds_to_drop.index, axis = 0)
    
    # 2. Delete cancellation trades themselves
    df = df[df['trc_st'] != "C"]
    
    #print "Number of sameday correction is", (dfsize - df.shape[0])

    return df


def reversals(df):
    # Identify reversals
    df_R = df[df['asof_cd'] == "R"]
    # Also, Reversals must have report day > execution date
    df_R = df_R[df_R['trd_rpt_dt'] > df_R['trd_exctn_dt']]
    
    merge_columns = ['trd_exctn_dt', 'trd_exctn_tm', 'rptd_pr', 'entrd_vol_qt',
                     'rpt_side_cd', 'cntra_mp_id']
    # Note: each Reversal might find multiple matches, but since this is very
    #  unlikely, we would NOT guarantee only 1 match is removed
    trds_to_drop = pd.merge(df[merge_columns], df_R[merge_columns],
                            on = merge_columns, how = 'inner', left_index = True)
    df = df.drop(trds_to_drop.index, axis = 0)
    
    #print "Number of Reversals is", df_R.shape[0]
    #print "Number of Reverasal match is", (trds_to_drop.shape[0] - df_R.shape[0])
        
    return df

def post2012(df):
    #print "Cleaning post-2012 data..."
    
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
    #print "Cleaning agency transactions..."
    
    # Isolate transactions with customers, without commission
    rows_to_clean = np.all([df['cntra_mp_id'] == 'C', df['cmsn_trd'] == 'N'], \
                           axis = 0)
    df_temp1 = df[rows_to_clean]
    
    # Identify and drop agency transactions
    rows_buyAg = np.all([df_temp1['rpt_side_cd'].values == 'B', \
                         df_temp1['buy_cpcty_cd'].values == 'A'], axis = 0)
    rows_sellAg = np.all([df_temp1['rpt_side_cd'].values == 'S', \
                          df_temp1['sell_cpcty_cd'].values == 'A'], axis = 0)
    df_temp2 = df_temp1[np.any([rows_buyAg, rows_sellAg], axis = 0)]
    
    df_temp3 = df.drop(df_temp2.index, axis = 0)
    
    return df_temp3


def Final_Clean(df):
    #print "Cleaning inter-dealer transactions..."
    # Identify one of interdealer transactions, e.g. buy side, and remove it
    rows_interdealer = np.all([df['cntra_mp_id'] == 'D', \
                               df['rpt_side_cd'] == 'B'], axis = 0)
    df_temp1 = df[~rows_interdealer]
    
    # Is there a need to label inter-dealer trades' report side to 'D'?
    ## Re-value 'rpt_side_cd' to 'D', representing inter-dealer transactions
    #rows_interdealer = np.all([df['cntra_mp_id'] == 'D', \
                               #df['rpt_side_cd'] == 'S'], axis = 0)
    #df_temp1.loc[rows_interdealer, 'rpt_side_cd'] = 'D'
    #print "Remaining observations", df_temp1.shape[0]

    #print "Removing When-Issued trades..."
    df_temp2 = df_temp1[df_temp1['wis_fl'] != 'Y']
    #print "Remaining observations", df_temp2.shape[0]
    
    #print "Removing trades on irrelavant markets..."
    df_temp3 = df_temp2[~df_temp2['trdg_mkt_cd'].isin(["P1", "P2", "S2"])]
    #print "Remaining observations", df_temp3.shape[0]
    
    #print "Removing trades of special price..."
    df_temp4 = df_temp3[df_temp3['spcl_trd_fl'] != 'Y']
    #print "Remaining observations", df_temp4.shape[0]
    
    # It is unclear how to deal with scrty_type_cd = 'C' / NA
    #print
    #print "Removing equity linked note/not a cash trade..."
    
    #print "Removing trades of abnormal long settlement period..."
    df_temp5 = df_temp4[~(df_temp4['days_to_sttl_ct'] >= 6)]
    #print "Remaining observations", df_temp5.shape[0]
    
    # It is unclear how to deal with 'C' from SAS code
    #print
    #print "Removing trades of non-cash sales..."

    #print "Removing all commissioned trades..."
    df_temp6 = df_temp5[df_temp5['cmsn_trd'] == 'N']
    #print "Remaining observations", df_temp6.shape[0]
    
    #print "Removing automatic give-up trades..."
    df_temp7 = df_temp6[~df_temp6['agu_qsr_id'].isin(["A", "Q"])]
    #print "Remaining observations", df_temp7.shape[0]
    
    return df_temp7




def Tailor_Data(df):
    # Note: we haven't done any cleaning regarding scrty_ty_cd and sale_cndtn_cd,
    #  due to unknown property of these columns
    COLS_TO_REMOVE = ['trd_rpt_dt', 'trd_rpt_tm', 'msg_seq_nb', 'trc_st',\
                      'scrty_type_cd', 'wis_fl', 'cmsn_trd', 'asof_cd', \
                      'days_to_sttl_ct', 'sale_cndtn_cd', 'rpt_side_cd', \
                      'buy_cpcty_cd', 'sell_cpcty_cd', 'cntra_mp_id', \
                      'agu_qsr_id', 'spcl_trd_fl', 'trdg_mkt_cd', 'orig_msg_seq_nb']
    
    df = remove_cols(df, COLS_TO_REMOVE)

    return df


## ASSUMPTIONS: each input dataframe should have identical cusip_id, i.e.
##  representing a particular bond
def clean_bond(df, data_dir, doOutput):
    # common pre-processing for all data
    df1 = Initial_deletes(df)
    
    # Extract data before Feb 6, 2012
    df_pre2012 = df1[df1['trd_rpt_dt'] < 20120206]
    df_post2012 = df1[df1['trd_rpt_dt'] >= 20120206]

    df_pre2012 = pre2012(df_pre2012)
    #print "Dimension of processed pre2012 dataset is", df_pre2012.shape
    
    df_post2012 = post2012(df_post2012)
    #print "Dimension of processed post2012 dataset is", df_post2012.shape

    # Recombine the pre-/post-2012 data frames
    df2 = pd.concat([df_pre2012, df_post2012], ignore_index = True)
    #print "Dimension of recombined dataset is", df2.shape
    
    df3 = AgencyTransac(df2)
    #print "Dimension of dataset without agency transaction is", df3.shape
    
    df4 = Final_Clean(df3)
    #print "Dmension of clean dataset is", df4.shape
    
    # Tailor data for regression (i.e. removing unwanted columns)
    df5 = Tailor_Data(df4)
    
    # Output non-empty dataframs to csv
    if (df5.shape[0] > 0) and (doOutput is True):
        bond_name = df5.iloc[0]['cusip_id']
        df5.to_csv(data_dir + bond_name + "_clean.csv", index = False)
        
    # Note: this dataframe is not sorted by execution date and time
    #  this needs to be handled while calculating proxies.
    
    return df5