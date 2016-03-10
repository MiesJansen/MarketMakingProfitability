import pandas as pd

import pre_and_post_2012 as cln
import liquidity_proxy as lpx

## TO-DO: Reporting stats to a log file

# A directory for holding raw/processed data
# DO NOT push any data file to Github
DATA_PATH = './data/'
DATA_NAME = 'BAC.HQO_20100331_20140330'


## For testing only
if __name__ == "__main__":
    df0 = pd.read_csv(DATA_PATH + DATA_NAME + "_raw.csv", \
                     low_memory=False) # To silent warnings

    '''df0 = pd.read_csv('C:\Users\Alex\Desktop\Industry_Project\\trace_data.csv')'''

    # .csv file downloaded from TRACE should already sort by bond symbol
    #  and each bond symbol corresponds to an unique cusip_id
    cusip_id_list = df0['cusip_id'].unique().tolist()
    for cusip_id in cusip_id_list:
        #print "Cleaning cusip_id", cusip_id
        
        # dataframe holding all trades of ONE bond at a time
        df1 = df0.loc[df0['cusip_id'] == cusip_id]
        df2 = cln.clean_bond(df1, DATA_PATH)
        
        lpx.Calculate_First_Proxy(df2)