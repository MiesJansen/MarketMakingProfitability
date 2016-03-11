import pandas as pd
import numpy as np
import statsmodels.api as sm
from patsy import dmatrices

def Calculate_First_Proxy(df):
    #price = rptd_pr
    #yield = yld_pt
    #volume = entrd_vol_qt
    #yield sign = yld_sign_cd
    #date = trd_exctn_dt

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
       
    res_summary_list = []   #stores regression outputs
    list_of_dates = []         #stores datetime objects
    liquidity_factor_list = []

    # Group dataframe on index by month and year
    for date, df_group in df.groupby(pd.TimeGrouper("M")):
        #run linear regression using equation (2) from pdf 
        y,X = dmatrices('rptd_pr_1 ~ rptd_pr + volume_and_sign', data=df_group, return_type='dataframe')
        mod = sm.OLS(y,X)
        res = mod.fit()
        #store regression for ouput for each month
        res_summary_list.append([date, res])
        list_of_dates.append(date)
        liquidity_factor_list.append(res.params[2])

    #print regression output summary for each month
    '''for date, res in res_summary_list:
        print date
        print res.params[2]
        #print (res.summary())'''

    #dates = matplotlib.dates.date2num(list_of_dates)
    plt.plot(list_of_dates, liquidity_factor_list)
    plt.show()
