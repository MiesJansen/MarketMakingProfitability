import pandas as pd

import pre_and_post_2012 as cln
import liquidity_proxy as lpx
import MMP_config as cfg

## TO-DO: Reporting stats to a log file

## For testing only
if __name__ == "__main__":
    '''df0 = pd.read_csv(cfg.DATA_PATH + cfg.DATA_NAME + ".csv", \
                     low_memory=False) # To silent warnings'''

    df0 = pd.read_csv('C:\Users\Alex\Desktop\Industry_Project\\BAC.HQO_CHK.HE_raw.csv')

    # .csv file downloaded from TRACE should already sort by bond symbol
    #  and each bond symbol corresponds to an unique cusip_id
    cusip_id_list = df0['cusip_id'].unique().tolist()

    df_list = []
    for cusip_id in cusip_id_list:
        #print "Cleaning cusip_id", cusip_id
        
        # dataframe holding all trades of ONE bond at a time
        df1 = df0.loc[df0['cusip_id'] == cusip_id]

        df2 = cln.clean_bond(df1, cfg.DATA_PATH)
        df_list.append(df2)
        
    lpx.Calculate_First_Proxy(df_list)
