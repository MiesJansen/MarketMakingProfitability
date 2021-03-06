import pandas as pd
import numpy as np
import matplotlib.pyplot as plt

import MMP_config as cfg
import Display_Graphs as dg

def Monthly_Volume_Graph(df_list_daily):
    # Concatenate all bonds into one dataframe
    df_month_all = pd.concat(df_list_daily)

    # Sum volumes for each month over all bonds
    df_month_final = df_month_all.resample('M', how={'cusip_id': 'last',\
                                         'trd_exctn_dt': 'last',\
                                         'entrd_vol_qt': np.sum,\
                                         'yld_pt': 'last'}, label='right')

    # Plot month dates vs. volume amounts
    plt.plot(df_month_final.index.values, df_month_final['entrd_vol_qt'])
    plt.ylabel('Volume')
    plt.title('Volume Per Month')
    plt.savefig(cfg.DATA_PATH + cfg.CLEAN_DATA_FILE + '_monthly_volume.png')
    plt.close()

    df = pd.DataFrame({'Date': df_month_final.index.values, \
                       'Volume': df_month_final['entrd_vol_qt']})
    df.to_csv(cfg.DATA_PATH + cfg.CLEAN_DATA_FILE + '_monthly_volume.csv')

def Monthly_Total_Bond_Graph(month_list, num_bond_list):
    plt.plot(month_list, num_bond_list)
    plt.ylabel('Number of bonds')
    plt.title('Number of Bonds Per Month')
    plt.savefig(cfg.DATA_PATH + cfg.CLEAN_DATA_FILE + '_monthly_total_bonds.png')
    plt.close()

    df = pd.DataFrame({'Date': month_list, 'total Bonds': num_bond_list})
    df.to_csv(cfg.DATA_PATH + cfg.CLEAN_DATA_FILE + '_monthly_total_bonds.csv')
    
def Liquidity_Graphs(df):
    # plot market liquidity measure vs date
    # Note: liquidity measure has a unit of excess yield percentage per volume,
    #  so the magnitude of vertical axis is likely very small
    plt.plot(df.index.values, df['liq_month_list_1'])
    plt.ylabel('Liquidity Measure pi_t')
    plt.title('Pastor-Stambaugh liquidity measure')
    
    plt.savefig(cfg.DATA_PATH + cfg.CLEAN_DATA_FILE + '_liquidity.png')
    plt.close()
    
    # Plot market liquidity risk vs date
    plt.plot(df.index.values, df['residual_term'])
    plt.ylabel('Liquidity Risk L_t')
    plt.title('Pastor-Stambaugh liquidity risk measure')
    
    plt.savefig(cfg.DATA_PATH + cfg.CLEAN_DATA_FILE + '_liquidity_risk.png')
    plt.close()
    
def Return_Vs_Graph(df):
    df.to_csv(cfg.DATA_PATH + cfg.CLEAN_DATA_FILE + '_return_diff.csv')

    # Plot actual return (TRACE) vs. expected return (F.F.)
    plt.plot(df['act_ret_diff'], df['expec_ret_diff'])
    plt.ylabel('Expected Return')
    plt.xlabel('Actual Return')
    plt.title('All Bonds Actual vs. Expected Return')
    
    plt.savefig(cfg.DATA_PATH + cfg.CLEAN_DATA_FILE + '_return_diff.png')
    plt.close()