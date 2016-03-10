import pandas as pd
import numpy as np
import statsmodels.api as sm
from patsy import dmatrices

# TO-DO: Reporting stats to a log file
# TO-DO: keep deleted observations to a separate file

# A directory for holding raw/processed data
# DO NOT push any data file to Github
DATA_PATH = './data/'
DATA_PATH_1 = 'C:\Users\Alex\Desktop\Industry Project\\'
DATA_NAME = 'BAC.HQO_20100331_20140330'


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

def Final_Clean(df):
    print
    print "Cleaning inter-dealer transactions..."
    # Identify one of interdealer transactions, e.g. buy side, and remove it
    rows_interdealer = np.all([df['cntra_mp_id'] == 'D', \
                               df['rpt_side_cd'] == 'B'], axis = 0)
    df_temp1 = df[~rows_interdealer]
    
    # Is there a need to label inter-dealer trades' report side to 'D'?
    ## Re-value 'rpt_side_cd' to 'D', representing inter-dealer transactions
    #rows_interdealer = np.all([df['cntra_mp_id'] == 'D', \
                               #df['rpt_side_cd'] == 'S'], axis = 0)
    #df_temp1.loc[rows_interdealer, 'rpt_side_cd'] = 'D'
    print "Remaining observations", df_temp1.shape[0]

    print
    print "Removing When-Issued trades..."
    df_temp2 = df_temp1[df_temp1['wis_fl'] != 'Y']
    print "Remaining observations", df_temp2.shape[0]
    
    print
    print "Removing trades on irrelavant markets..."
    df_temp3 = df_temp2[~df_temp2['trdg_mkt_cd'].isin(["P1", "P2", "S2"])]
    print "Remaining observations", df_temp3.shape[0]
    
    print
    print "Removing trades of special price..."
    df_temp4 = df_temp3[df_temp3['spcl_trd_fl'] != 'Y']
    print "Remaining observations", df_temp4.shape[0]
    
    # It is unclear how to deal with scrty_type_cd = 'C' / NA
    #print
    #print "Removing equity linked note/not a cash trade..."
    
    print
    print "Removing trades of abnormal long settlement period..."
    df_temp5 = df_temp4[~(df_temp4['days_to_sttl_ct'] >= 6)]
    print "Remaining observations", df_temp5.shape[0]
    
    # It is unclear how to deal with 'C' from SAS code
    #print
    #print "Removing trades of non-cash sales..."

    print
    print "Removing all commissioned trades..."
    df_temp6 = df_temp5[df_temp5['cmsn_trd'] == 'N']
    print "Remaining observations", df_temp6.shape[0]
    
    print
    print "Removing automatic give-up trades..."
    df_temp7 = df_temp6[~df_temp6['agu_qsr_id'].isin(["A", "Q"])]
    print "Remaining observations", df_temp7.shape[0]
    
    return df_temp7

def Calculate_First_Proxy(df):
    #price = rptd_pr
    #yield = yld_pt
    #volume = entrd_vol_qt
    #yield sign = yld_sign_cd
    #date = trd_exctn_dt

    df['rptd_pr_1'] = df['rptd_pr'].shift(-1)
    df['yld_pt_1'] = df['yld_pt'].shift(-1)

    df['numeric_sign'] = np.where(df['yld_sign_cd'] == '+', 1, ' ')
    # -1 if (-) and +1 for blanks
    df['volume_and_sign'] = np.where(df['yld_sign_cd'] == '-', -1, 1)
    df['volume_and_sign'] = df['volume_and_sign'] * df['entrd_vol_qt']

    # convert int64 date series to DateTime series
    df['trd_exctn_dt'] = pd.to_datetime(df['trd_exctn_dt'], format='%Y%m%d')
    # set DateTime series as index od dataframe
    df = df.set_index('trd_exctn_dt')
       
    res_summary_list = []   #stores regression outputs

    # Group dataframe on index by month and year
    for date, df_group in df.groupby(pd.TimeGrouper("M")):
        #run linear regression using equation (2) from pdf 
        y,X = dmatrices('rptd_pr_1 ~ rptd_pr + volume_and_sign', data=df_group, return_type='dataframe')
        mod = sm.OLS(y,X)
        res = mod.fit()
        #store regression for ouput for each month
        res_summary_list.append([date, res])

    #print regression output summary for each month
    for date, res in res_summary_list:
        print date.month, '-', date.year
        print res.params, '\n'
        #print (res.summary())

    #df.to_csv('output.csv')

    #run linear regression using equation (2) from pdf 


## For testing only
if __name__ == "__main__":
    '''df0 = pd.read_csv(DATA_PATH_1 + DATA_NAME + "_raw.csv", \
                     low_memory=False) # To silent warnings'''

    df0 = pd.read_csv('C:\Users\Alex\Desktop\Industry_Project\\trace_data.csv')

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
    
    df4 = Final_Clean(df3)
    
    # TO-DO: sort entries by execution date and time before outputting
    df4.to_csv(DATA_PATH + DATA_NAME + "_clean.csv")

    Calculate_First_Proxy(df4)