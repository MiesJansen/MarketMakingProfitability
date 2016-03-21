import pandas as pd
import numpy as np
import matplotlib.pyplot as plt

import MMP_config as cfg
import Display_Graphs as dg

month_list = pd.date_range(cfg.dt_start, cfg.dt_end, freq = 'M')
num_months_CONST = len(month_list)

month_keys = dict(zip((''.join([str(dt.month), str(dt.year)]) for dt in month_list),\
                      range(num_months_CONST)))

def Monthly_Volume_Graph(df_list_daily):
    #concatenate all bonds into one dataframe
    df_month_all = pd.concat(df_list_daily)

    #sum volumes for each month over all bonds
    df_month_final = df_month_all.resample('M', how={'cusip_id': 'last',\
                                         'trd_exctn_dt': 'last',\
                                         'entrd_vol_qt': np.sum,\
                                         'yld_pt': 'last'}, label='right')

    #plot month dates vs. volume amounts
    plt.plot(df_month_final.index.values, df_month_final['entrd_vol_qt'])
    plt.ylabel('Volume')
    plt.title('Volume Per Month')
    plt.savefig(cfg.DATA_PATH + cfg.CLEAN_DATA_FILE + '_monthly_volume.png')
    plt.close()

    df = pd.DataFrame({'Date': month_list, 'Volume': vol_arr})
    df.to_csv(cfg.DATA_PATH + cfg.CLEAN_DATA_FILE + '_monthly_volume.csv')

def Monthly_Total_Bond_Graph(month_list, num_bond_list):
    plt.plot(month_list, num_bond_list)
    plt.ylabel('Number of bonds')
    plt.title('Number of Bonds Per Month')
    plt.savefig(cfg.DATA_PATH + cfg.CLEAN_DATA_FILE + '_monthly_total_bonds.png')
    plt.close()

    df = pd.DataFrame({'Date': month_list, 'total Bonds': num_bond_list})
    df.to_csv(cfg.DATA_PATH + cfg.CLEAN_DATA_FILE + '_monthly_total_bonds.csv')
    