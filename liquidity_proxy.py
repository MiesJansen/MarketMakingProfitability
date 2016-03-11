import pandas as pd
import numpy as np
import statsmodels.api as sm
from patsy import dmatrices
import matplotlib
import matplotlib.pyplot as plt

def Calculate_First_Proxy(df_list):     
    for idx, df in enumerate(df_list):
        df_list[idx] = Modify_Columns(df)

    #res_array = []
    #res_array_list = [[]]   #stores regression outputs
    date_arr = []
    date_arr_list = [[]]         #stores datetime objects
    liq_arr = []
    liq_arr_list = [[]]
    liq_month_pairs = [[]]

    # Group dataframe on index by month and year
    for df in df_list: 
        for date, df_group in df.groupby(pd.TimeGrouper("M")):
            #run linear regression using equation (2) from pdf 
            y,X = dmatrices('rptd_pr_1 ~ rptd_pr + volume_and_sign', 
                data=df_group, return_type='dataframe')
            mod = sm.OLS(y,X)
            res = mod.fit()
            #store regression for ouput for each month
            #res_array.append([date, res])
            date_arr.append(date)
            liq_arr.append(res.params[2])

        #res_array_list.append(res_array)
        date_arr_list.append(date_arr)
        liq_arr_list.append(liq_arr)

        #res_array.clear()
        date_arr = []
        liq_arr = []

    liq_arr_list.pop(0)
    date_arr_list.pop(0)
    num_months = len(date_arr_list[0])
    for i in range(0, num_months):
        liq_month_pairs.append([item[i] for item in liq_arr_list])

    liq_month_pairs.pop(0)

    num_bonds = len(df_list)
    print ((liq_month_pairs[0][0] + liq_month_pairs[0][1]) / num_bonds)
    liq_month_list = list((((item[0] + item[1]) / num_bonds))
                            for item in liq_month_pairs)
    
    print liq_month_list

    # plot liquidity vs date for each individual bond
    '''for date_list, liquidity_list in zip(date_array_list, liquidity_array_list):
        plt.plot(date_list, liquidity_list)
        plt.show()'''

def Modify_Columns(df):
    #price = rptd_pr | yield = yld_pt | volume = entrd_vol_qt
    #yield sign = yld_sign_cd | date = trd_exctn_dt

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

    return df
