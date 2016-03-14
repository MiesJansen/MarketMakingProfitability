import pandas as pd
import numpy as np
import statsmodels.api as sm
from patsy import dmatrices
import matplotlib
import matplotlib.pyplot as plt
import copy

num_months_CONST = 49
month_keys = {'32010' : 0, '42010': 1, '52010': 2, '62010': 3, '72010': 4, '82010': 5,
              '92010': 6, '102010': 7, '112010': 8, '122010': 9, '12011': 10, '22011': 11,
              '32011': 12, '42011' : 13, '52011': 14, '62011': 15, '72011': 16, '82011': 17,
              '92011': 18, '102011': 19, '112011': 20, '122011': 21, '12012': 22, '22012': 23,
              '32012': 24, '42012': 25, '52012': 26, '62012': 27, '72012': 28, '82012': 29,
              '92012': 30, '102012': 31, '112012': 32, '122012': 33, '12013': 34, '22013': 35,
              '32013': 36, '42013': 37, '52013': 38, '62013': 39, '72013': 40, '82013': 41,
              '92013': 42, '102013': 43, '112013': 44, '122013': 45, '12014': 46, '22014': 47,
              '32014': 48}

def Calculate_First_Proxy(df_list):     
    for idx, df in enumerate(df_list):
        df_list[idx] = Add_Proxy_Columns(df) #apply func to each df in list of dfs

    date_arr = []
    date_arr_list = [[]]        #list of lists of bond dates per bond - same for all
    liq_arr = [0] * num_months_CONST
    liq_arr_list = [[]]         #list of lists of liq coeff per bond
    liq_per_month = [[]]
    first_pass = True

    counter = 0
    print 'df_list size: ', len(df_list)
    # Group dataframe on index by month and year
    for df in df_list: 
        #print df['cusip_id'][0]
        #if (df['cusip_id'][0] == '023650AH7' or df['cusip_id'][0] == '023650AG9'):
        #   print df
        for date, df_group in df.groupby(pd.TimeGrouper("M")):
            #Run regression per month to get INITIAL liquidity factor
            try:
                y,X = dmatrices('rptd_pr_1 ~ rptd_pr + volume_and_sign', 
                                data=df_group, return_type='dataframe')
                #print date, X.shape
                mod = sm.OLS(y,X)
                res = mod.fit()
            
                if first_pass:      #only need dates from one pass
                    date_arr.append(date)   #store date

                month =  ''.join([str(date.month),str(date.year)])
                month_key = month_keys[month]
                #set specific months with liquidity factos | otherwise set to 0
                liq_arr[month_key] = res.params[2]   #res.params(2) = liquidity coefficient
            except ValueError:  #X has zero rows
                if first_pass:      #only need dates from one pass
                    date_arr.append(date)   #store date

                liq_arr[month_key] = 0

        liq_arr_list.append(liq_arr)    #store all liq coeff for each month per bond
        liq_arr = [0] * num_months_CONST     #clear liq_arr
        first_pass = False

    liq_arr_list.pop(0)     #pop empty df for first entry

    #print liq_arr_list

    for i in range(0, num_months_CONST):
        liq_per_month.append([item[i] for item in liq_arr_list])

    liq_per_month.pop(0)  #pop empty first entry
    liq_per_month.pop(0)  #pop list of zeros

    #perform equation (3) to get average liquidity per month
    for item in liq_per_month:
        num_bonds = sum([1 for x in item if x != 0]) #exclude no liquidity months in sum
        liq_month_list = list(((sum(item) / num_bonds))
                            for item in liq_per_month)

    #print len(liq_month_list), '\n', len(date_arr), '\n', liq_month_list
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

    df['residual_term'] = df['residual_term'] * 100

    return df

def Plot_Liquidity(df, col_name):
    # plot liquidity vs date for each individual bond
    plt.plot(df.index.values, df[col_name])   #possibly df.index.tolist()????
    plt.show()