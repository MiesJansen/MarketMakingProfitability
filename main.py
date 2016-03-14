import pandas as pd

import pre_and_post_2012 as cln
import liquidity_proxy as lpx
import MMP_config as cfg

## TO-DO: Reporting stats to a log file

## For testing only
if __name__ == "__main__":
    # Due to large size of raw TRACE data, read by chunks and concat into one
    #  dataset
    df_chunks = pd.read_csv(cfg.DATA_PATH + cfg.DATA_NAME + ".csv", chunksize = 100000,\
                            low_memory=False) # To silent warnings
    df0 = pd.concat(df_chunks, ignore_index = True)

    # .csv file downloaded from TRACE should already sort by bond symbol
    #  and each bond symbol corresponds to an unique cusip_id
    cusip_id_list = df0['cusip_id'].unique().tolist()

    df_list = []
    for cusip_id in cusip_id_list:
        #print "Cleaning cusip_id", cusip_id
        
        # dataframe holding all trades of ONE bond at a time
        df1 = df0.loc[df0['cusip_id'] == cusip_id]

        df2 = cln.clean_bond(df1, cfg.OUTPUT_PATH, cfg.doOutput)
        df_list.append(df2)
    
    # Output the entire cleaned list to one file, in case of further usage    
    # output this to data path, avoiding mix with individual bond output
    final_df = pd.concat(df_list, ignore_index = True)
    final_df.to_csv(cfg.DATA_PATH + "list_clean.csv", index = False)
    
    df1 = lpx.Calculate_First_Proxy(df_list)
    lpx.Plot_Liquidity(df1, 'residual_term')
    