import pandas as pd

import pre_and_post_2012 as cln
import liquidity_proxy as lpx
import MMP_config as cfg
import Aggregate_Daily as ad
import Fama_French as ff

## TO-DO: Reporting stats to a log file

## For testing only
if __name__ == "__main__":
    # A list of dataframes with clean TRACE data for calculating proxy
    df_list = []
    if cfg.readRaw is True:    
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
        # output this to data path, avoiding mix with individual bond output
        final_df = pd.concat(df_list, ignore_index = True)
        final_df.to_csv(cfg.DATA_PATH + cfg.CLEAN_DATA_FILE + ".csv",\
                        index = False)

    # Do not process raw data file, read in processed data
    else: #readRaw == False
        # Read in by chunks to increase memory efficiency
        df_chunks = pd.read_csv(cfg.DATA_PATH + cfg.CLEAN_DATA_FILE + ".csv",
                                chunksize = 100000,
                                low_memory = False) # To silent warnings
        df1 = pd.concat(df_chunks, ignore_index = True)
        
        # Split data file by cusip_id, and create a list of dataframes
        cusip_iter = df1.groupby('cusip_id', sort = False)        
        for name, cusip_group in cusip_iter:
            df_list.append(cusip_group)
            
    # Temparory delete columns, later will put into clean code
    ## FIX: ADD these to cleaning algorithm
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
    
    # Calculate proxy liquidity measure 
    df1 = lpx.Calculate_First_Proxy(df_list_daily)
    # Plot the liquidity measure
    lpx.Plot_Liquidity(df1, 'residual_term')