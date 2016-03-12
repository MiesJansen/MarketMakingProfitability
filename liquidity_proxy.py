import pandas as pd
import numpy as np
import statsmodels.api as sm
from patsy import dmatrices
import matplotlib
import matplotlib.pyplot as plt
import copy

def Calculate_First_Proxy(df_list):     
    for idx, df in enumerate(df_list):
        df_list[idx] = Add_Proxy_Columns(df) #apply func to each df in list of dfs

    date_arr = []
    date_arr_list = [[]]        #list of lists of bond dates per bond - same for all
    liq_arr = []
    liq_arr_list = [[]]         #list of lists of liq coeff per bond
    liq_month_pairs = [[]]
    first_pass = True

    # Group dataframe on index by month and year
    for df in df_list: 
        for date, df_group in df.groupby(pd.TimeGrouper("M")):
            #Run regression per month to get INITIAL liquidity factor
            y,X = dmatrices('rptd_pr_1 ~ rptd_pr + volume_and_sign', 
                            data=df_group, return_type='dataframe')
            mod = sm.OLS(y,X)
            res = mod.fit()
            
            if first_pass:      #only need dates from one pass
                date_arr.append(date)   #store date
            liq_arr.append(res.params[2])   #res.params(2) = liquidity coefficient

        liq_arr_list.append(liq_arr)    #store all liq coeff for each month per bond
        liq_arr = []
        first_pass = False

    liq_arr_list.pop(0)     #pop empty df for first entry

    #create list of lists of liquidity coefficients per month
    num_months = len(date_arr)
    for i in range(0, num_months):
        liq_month_pairs.append([item[i] for item in liq_arr_list])

    liq_month_pairs.pop(0)  #pop empty first entry

    #perform equation three to get average liquidity per month
    num_bonds = len(df_list)
    liq_month_list = list((((item[0] + item[1]) / num_bonds))
                            for item in liq_month_pairs)

    df = Run_Regression(liq_month_list, date_arr)

    return df

def Add_Proxy_Columns(df):
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

def Run_Regression(liq_month_list, date_arr):
    liq_month_list_1 = copy.deepcopy(liq_month_list) #so don't change liq_month_list
    del liq_month_list[-1]   #delete last element
    liq_month_list = [0] + liq_month_list #so dataframe columns have same size

    df = pd.DataFrame()
    df['date'] = date_arr       
    df = df.set_index('date')   #set dates as index

    df['liq_month_list_1'] = liq_month_list_1   #liq month t
    df['liq_month_list'] = liq_month_list       #liq month t-1

    df['liq_delta_1'] = df['liq_month_list_1'] - df['liq_month_list']  #liq delta t
    df['liq_delta'] = df['liq_delta_1'].shift(1)                       #liq delta t-1
    df['liq_delta'][0] = 0      #so no NaN value

    #run linear regression using equation (2) from pdf 
    y,X = dmatrices('liq_delta_1 ~ liq_delta', 
        data=df, return_type='dataframe')
    mod = sm.OLS(y,X)
    res = mod.fit()
    
    #calculate the liquidty values from proxy equation
    df['liq_proxy_values'] = [res.params[0] + res.params[1] * item 
                        for item in df['liq_delta']]

    #set first liquidity proxy value to intercept of regression equation
    df['liq_proxy_values'][0] = res.params[0]

    #calculate thre residual term --> FINAL liquidity term
    df['residual_term'] = df['liq_delta_1'] - df['liq_proxy_values']

    return df

def Plot_Liquidity(df, col_name):
    # plot liquidity vs date for each individual bond
    plt.plot(df.index.values, df[col_name])   #possibly df.index.tolist()????
    plt.show()