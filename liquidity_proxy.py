import pandas as pd
import numpy as np
import statsmodels.api as sm
from patsy import dmatrices
import matplotlib
import matplotlib.pyplot as plt
import copy

import MMP_config as cfg

# month name string -> integer index mapping
month_list = pd.date_range(cfg.dt_start, cfg.dt_end, freq = 'M')
month_keys = dict(zip((''.join([str(dt.month), str(dt.year)]) for dt in month_list),\
                      range(48)))
num_months_CONST = len(month_keys)

def Calculate_First_Proxy(orig_df_list):
    df_list = []
    for df in orig_df_list:
        df = Add_Proxy_Columns(df)
        if df.shape[0] > 0:
            #apply func to each df in list of dfs, append to list if not 0 length
            df_list.append(Add_Proxy_Columns(df))


    #list of lists of liq coeff per bond
    liq_arr_list = []         
    liq_per_month = []

    print 'df_list size: ', len(df_list)
    for df in df_list:
        # A temporary array for holding liquidity beta for each month
        liq_arr = [np.nan] * num_months_CONST
        #print df['cusip_id'][0]
        
        # Group dataframe on index by month
        for date, df_group in df.groupby(pd.TimeGrouper("M")):
            month = ''.join([str(date.month),str(date.year)])
            month_key = month_keys[month]

            # When there are some data in current month,
            if df_group.shape[0] > 0:
                #Run regression per month to get INITIAL liquidity factor
                y,X = dmatrices('rptd_pr_1 ~ rptd_pr + volume_and_sign', 
                                data=df_group, return_type='dataframe')
                #print date, X.shape
                mod = sm.OLS(y,X)
                res = mod.fit()

                #set specific months with liquidity factors
                #res.params(2) = liquidity coefficient
                liq_arr[month_key] = res.params[2]

        liq_arr_list.append(liq_arr)    #store all liq coeff for each month per bond

    #print liq_arr_list
    
    for i in range(num_months_CONST):
        liq_per_month.append([item[i] for item in liq_arr_list])

    #perform equation (3) to get average liquidity per month
    for item in liq_per_month:
        # exclude month with no data
        num_bonds = sum([1 for x in item if not np.isnan(x)]) 
        liq_month_list = list(((np.nansum(item) / num_bonds))
                              for item in liq_per_month)

    #print len(liq_month_list), '\n', liq_month_list
    df = Run_Regression(liq_month_list)

    return df

def Add_Proxy_Columns(df):
    ##FIX: There are some "SettingWithCopyWarning" here, might be caused by
    ##      false positive of pandas new release.
    #price = rptd_pr | yield = yld_pt | volume = entrd_vol_qt
    #yield sign = yld_sign_cd | date = trd_exctn_dt

    df['rptd_pr_1'] = df['rptd_pr'].shift(-1)
    df['yld_pt_1'] = df['yld_pt'].shift(-1)

    # Remove the last row, because it does not contain delta
    df = df.drop(df.index[-1], inplace = False)

    # -1 if (-) and +1 for blanks
    df['volume_and_sign'] = np.where(df['yld_sign_cd'] == '-', -1, 1)
    df['volume_and_sign'] = df['volume_and_sign'] * df['entrd_vol_qt']

    # convert int64 date series to DateTime series
    df['trd_exctn_dt_idx'] = pd.to_datetime(df['trd_exctn_dt'], format='%Y%m%d')
    # set DateTime series as index od dataframe
    df = df.set_index('trd_exctn_dt_idx')
    
    return df

def Run_Regression(liq_month_list):
    df = pd.DataFrame(index = month_list)    #set dates as index

    df['liq_month_list_1'] = liq_month_list                   #liq month t
    df['liq_month_list'] = df['liq_month_list_1'].shift(1)    #liq month t-1
    # After shift, the first row is not longer valid data
    df = df.drop(df.index[0], inplace = False)

    df['liq_delta_1'] = df['liq_month_list_1'] - df['liq_month_list']  #liq delta t
    df['liq_delta'] = df['liq_delta_1'].shift(1)                       #liq delta t-1
    # After shift, the first row is not longer valid data
    df = df.drop(df.index[0], inplace = False)

    #run linear regression using equation (2) from pdf 
    y,X = dmatrices('liq_delta_1 ~ liq_delta', 
        data=df, return_type='dataframe')
    mod = sm.OLS(y,X)
    res = mod.fit()
    
    #calculate the liquidty values from proxy equation
    df['liq_proxy_values'] = [res.params[0] + res.params[1] * item \
                              for item in df['liq_delta']]

    #set first liquidity proxy value to intercept of regression equation
    df['liq_proxy_values'][0] = res.params[0]

    #calculate thre residual term --> FINAL liquidity term
    df['residual_term'] = df['liq_delta_1'] - df['liq_proxy_values']

    df['residual_term'] = df['residual_term'] * 100

    return df

def Plot_Liquidity(df, col_name):
    # plot liquidity vs date for each individual bond
    plt.plot(df.index.values, df[col_name])   #possibly df.index.tolist()????
    plt.show()