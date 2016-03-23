import pandas as pd

import pre_and_post_2012 as cln
import liquidity_proxy as lpx
import matplotlib.pyplot as plt
import numpy as np

import Display_Graphs as dg
import MMP_config as cfg
import Aggregate_Daily as ad
import Fama_French as ff
import Test_Formula as tf

## TO-DO: Reporting stats to a log file

def Set_Yield_Range(df_list, min_yield, max_yield):
    # Remove outlier bonds
    df_list_daily_clean = []
    for df in df_list_daily:
        if (df['yld_pt'].max() <= max_yield) and (df['yld_pt'].min() >= min_yield):
            df_list_daily_clean.append(df)

    return df_list_daily_clean

def Read_Raw():
    df_list = []
    for datafile in cfg.RAW_DATA_NAMES:
        # Due to large size of raw TRACE data, read by chunks and concat into
        #  one dataset
        df_chunks = pd.read_csv(cfg.DATA_PATH + datafile + ".csv",
                                chunksize = 100000,
                                low_memory = False) # To silent warnings
        df0 = pd.concat(df_chunks, ignore_index = True)
        
        # .csv file downloaded from TRACE should already sort by bond symbol
        #  and each bond symbol corresponds to an unique cusip_id
        cusip_id_list = df0['cusip_id'].unique().tolist()
        
        for cusip_id in cusip_id_list:
            #print "Cleaning cusip_id", cusip_id
            
            # dataframe holding all trades of ONE bond at a time
            df1 = df0.loc[df0['cusip_id'] == cusip_id]
            
            df2 = cln.clean_bond(df1, cfg.OUTPUT_PATH, cfg.doOutput)
            if (df2.shape[0] > 0):
                df_list.append(df2)
    
    # Output the entire cleaned list to one file, in case of further usage
    final_df = pd.concat(df_list, ignore_index = True)
    final_df.to_csv(cfg.DATA_PATH + cfg.CLEAN_DATA_FILE + ".csv",\
                    index = False)

    return df_list

def Read_Clean():
    df_list = []
    # Read in by chunks to increase memory efficiency
    df_chunks = pd.read_csv(cfg.DATA_PATH + cfg.CLEAN_DATA_FILE + ".csv",
                            chunksize = 100000,
                            low_memory = False) # To silent warnings
    df1 = pd.concat(df_chunks, ignore_index = True)
    
    # Split data file by cusip_id, and create a list of dataframes
    cusip_iter = df1.groupby('cusip_id', sort = False)
    for name, cusip_group in cusip_iter:
        df_list.append(cusip_group)

    return df_list

def Get_Daily_Df(df_list):
    ## FIX Temparory delete columns, later should put into clean code to reduce
    ##  size of the dataframe as early as possible
    df_list_new = []
    col_names = ['cusip_id', 'trd_exctn_dt', 'entrd_vol_qt', 'yld_sign_cd', 'yld_pt']
    for df in df_list:
        df = df.loc[:, col_names]
        df_list_new.append(df)
    
    # Aggregate data into daily summary
    df_list_daily = ad.Group_Daily(df_list_new)
    
    # Output the daily summary
    daily_df = pd.concat(df_list_daily, ignore_index = False)
    daily_df.to_csv(cfg.DATA_PATH + cfg.CLEAN_DATA_FILE + "_daily.csv",\
                    index = True)

    return df_list_daily

def Read_Daily_Df():
    # Read in by chunks to increase memory efficiency
    df_chunks = pd.read_csv(cfg.DATA_PATH + cfg.CLEAN_DATA_FILE + "_daily.csv",
                                index_col = False, chunksize = 100000,
                                low_memory = False) # To silent warnings
    df_daily = pd.concat(df_chunks, ignore_index = True)
    
    # Split data file by cusip_id, and create a list of dataframes
    cusip_iter = df_daily.groupby('cusip_id', sort = False)
    for name, cusip_group in cusip_iter:
        try:
            cusip_group.index = pd.to_datetime(cusip_group['trd_exctn_dt_idx'],\
                                               format = '%Y-%m-%d')
        except Exception:
            cusip_group.index = pd.to_datetime(cusip_group['trd_exctn_dt_idx'],\
                                               format = '%m/%d/%Y')
        df_list_daily.append(cusip_group)

    return df_list_daily

def Isolate_FF_Cols(df_list_daily_clean):
    df_list_ff = []
    col_names = ['trd_exctn_dt', 'cusip_id', 'yld_pt']
    for df in df_list_daily_clean:
        df = df.loc[:, col_names]
        df_list_ff.append(df)

    return df_list_ff

if __name__ == "__main__":
    # A list of dataframes with clean TRACE data for calculating proxy
    df_list_daily = []
    if cfg.readDaily is False:
        df_list = []
        if cfg.readRaw is True:
            print "Preprocessing raw TRACE data..."
            df_list = Read_Raw()
    
        else: # Read processed data, not raw data
            print "Reading preprocessed TRACE data..."
            df_list = Read_Clean()
        
        # Aggregate trades on same day into one trade for each day
        print "Aggregating data into daily summary..."
        df_list_daily = Get_Daily_Df(df_list)
    
    else: #readDaily == True
        print "Reading aggregated daily summary..."
        df_list_daily = Read_Daily_Df()

    # Remove bonds whose yield exceeds range. The range is found emperically by
    #  inspecting existance of special features of bonds with extremely high/low
    #  yield in the aggregated daily yield dataframe
    ## FIX this is a temp workaround for not being able to differentiate special
    ##  bonds such as callable, internotes and etc. Bonds with these special
    ##  features will cause unusual yield in TRACE data. Need FISD or Bloomberg
    ##  data to really fix this workaround.
    df_list_daily_clean = Set_Yield_Range(df_list_daily, -4.0, 6.0) #(df, min, max)

    # Graph and output to a file the total traindg volume per month 
    dg.Monthly_Volume_Graph(df_list_daily_clean)

    # Isolate columns for Fama French Regression
    df_list_ff = Isolate_FF_Cols(df_list_daily_clean)
    
    # Calculate proxy liquidity measure, and output to a data file
    print "Calculating liquidity measure and liquidity risk..."
    df_liq = lpx.Calculate_First_Proxy(df_list_daily_clean)
    df_liq.to_csv(cfg.DATA_PATH + cfg.CLEAN_DATA_FILE + "_liquidity.csv",\
                  index = True)
    
    # Prepare liquidity measure for Fama French regression
    df_liq_ff = df_liq.loc[:, 'residual_term']
    
    # Plot the market liquidity risk
    dg.Liquidity_Graphs(df_liq)
    
    print "Running Fama French regression..."
    ff.FamaFrenchReg(df_list_ff, df_liq_ff)

    # Test actual bond yields against predicted bond yield from Fama French Beta factors
    tf.Test_Liquidity(df_list_daily_clean, df_liq)
















    