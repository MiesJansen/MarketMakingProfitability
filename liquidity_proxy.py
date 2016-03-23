import pandas as pd
import numpy as np
import statsmodels.api as sm
from patsy import dmatrices
import matplotlib.pyplot as plt

import MMP_config as cfg
import Display_Graphs as dg

# month name string -> integer index mapping
month_list = pd.date_range(cfg.dt_start, cfg.dt_end, freq = 'M')
num_months_CONST = len(month_list)

month_keys = dict(zip((''.join([str(dt.month), str(dt.year)]) for dt in month_list),\
                      range(num_months_CONST)))


def Calculate_First_Proxy(orig_df_list):
    df_list = []
    # import corporate bond yield index 
    df_index_values = pd.read_csv(cfg.DATA_PATH + cfg.BOND_IDX_FILE + '.csv')
    
    ## FIX this can be combined into the next loop to reduce for loop overheads
    for df in orig_df_list:
        if df.shape[0] > 0:
            #apply func to each df in list of dfs, append to list if not 0 length
            df_list.append(Calculate_Excess_Return(df, df_index_values))

    #list of lists of liq coeff per bond
    liq_arr_list = []
    liq_per_month = []
    
    #print 'df_list size: ', len(df_list)
    for df in df_list:
        if df.empty:
            continue
        
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
                y,X = dmatrices('excess_return_1 ~ yld_pt + volume_and_sign', 
                                data=df_group, return_type='dataframe')
                #print date, X.shape
                mod = sm.OLS(y,X)
                res = mod.fit()

                #set specific months with liquidity factors
                #res.params(2) = liquidity coefficient
                liq_arr[month_key] = res.params[2]

        liq_arr_list.append(liq_arr)    #store all liq coeff for each month per bond

    #print liq_arr_list
    num_bond_list = []
    
    #separate liquidity per bond into monthly liquidity over all bonds
    for i in range(num_months_CONST):
        liq_per_month.append([item[i] for item in liq_arr_list])
        
    

    #perform equation (3) to get average liquidity per month
    for item in liq_per_month:
        # exclude month with no data
        num_bonds = sum([1 for x in item if not np.isnan(x)]) 
        liq_month_list = list(((np.nansum(item) / num_bonds))
                              for item in liq_per_month)
        num_bond_list.append(num_bonds)

    # Graph and output to a file the total volume per month 
    dg.Monthly_Total_Bond_Graph(month_list, num_bond_list)

    #print len(liq_month_list), '\n', liq_month_list
    df = Run_Regression(liq_month_list)

    return df

def Calculate_Excess_Return(df, df_index_values):
    # format corporate bond INDEX date
    df_index_values['date'] = pd.to_datetime(df_index_values['date'], 
                                             format="%m/%d/%Y")
    df_index_values['date_1'] = df_index_values['date']
    df_index_values = df_index_values.set_index(
                    pd.DatetimeIndex(df_index_values['date']))

    df['trd_exctn_dt_idx_1'] = df.index

    #difference between individual bond percentage yield & corporate bond index % yield
    df = pd.merge(df, df_index_values, how='inner', left_on='trd_exctn_dt_idx_1', 
                  right_on='date_1', left_index=True, suffixes=('_x', '_y'))

    if df.shape[0] > 0:
        #difference between individual bond percentage yield & corporate bond index % yield
        df['excess_return'] = df['yld_pt'] - df['yield']
        #excess return for r_e_j+1
        df['excess_return_1'] = df['excess_return'].shift(-1)
        df = df.drop(df.index[-1], inplace = False)
        
        df['excess_return_sign'] = np.where(df['excess_return'] >= 0, 1, -1)
        df['volume_and_sign'] = df['excess_return_sign'] * df['entrd_vol_qt']

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

    #calculate thre residual term --> FINAL liquidity term
    df['residual_term'] = df['liq_delta_1'] - df['liq_proxy_values']

    df['residual_term'] = df['residual_term'] * 10000

    return df

def Plot_Liquidity(df, col_name):
    # plot liquidity vs date for each individual bond
    plt.plot(df.index.values, df[col_name])   #possibly df.index.tolist()????
    plt.ylabel('Liquidity L_t')
    plt.title('Pastor-Stambaugh liquidity measure')
    plt.ylim((-2, 2))
    
    plt.savefig(cfg.DATA_PATH + cfg.CLEAN_DATA_FILE + '_liquidity.png')
    plt.close()
    