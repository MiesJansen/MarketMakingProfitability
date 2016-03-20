import pandas as pd
import numpy as np
import statsmodels.api as sm
from patsy import dmatrices
import matplotlib.pyplot as plt
import random

import MMP_config as cfg
import Display_Graphs as dg

# month name string -> integer index mapping
month_list = pd.date_range(cfg.dt_start, cfg.dt_end, freq = 'M')
num_months_CONST = len(month_list)

month_keys = dict(zip((''.join([str(dt.month), str(dt.year)]) for dt in month_list),\
                      range(num_months_CONST)))

def Test_Liquidity(df_list):
	df_betas = pd.read_csv(cfg.DATA_PATH + cfg.CLEAN_DATA_FILE + '_Betas.csv')
	df_corp_index = pd.read_csv(cfg.DATA_PATH + cfg.BOND_IDX_FILE + '.csv')
	df_corp_index['date'] = pd.to_datetime(df_corp_index['date'],\
		                                        format='%m/%d/%Y')
	df_corp_index.set_index('date', inplace=True)

	df_corp_index_1 = pd.DataFrame()
	df_corp_index_1 = df_corp_index.resample('M', \
						how={'yield': 'last'}, label='left')

	columns = ['Date', 'MKT', 'SMB', 'HML', 'DEF', 'TERM', 'RF']
	df_ff_params = pd.read_csv(cfg.DATA_PATH + cfg.FF_DATA_FILE + ".csv",\
							usecols = columns, index_col = False,
							low_memory = False) # To silent warnings

	#convert date of fama-french to end of month
	df_ff_params['Date'] = pd.to_datetime(df_ff_params['Date'],\
		                                        format='%Y%m')
	df_ff_params.set_index('Date', inplace=True)
	df_ff_params.index = df_ff_params.index.to_period('M').to_timestamp('M')

	# Random list of integer index values of subset of all cusip ids
	num_bond_limit = max((len(df_list) / 4), 5)
	rand_list = random.sample(xrange(0, len(df_list)), num_bond_limit)

	df_daily = []
	df_daily_list = []
	for i in rand_list:
		df_daily = df_list[i].resample('M', how={ \
						'cusip_id': 'last',\
                        'trd_exctn_dt': 'last',\
                        'entrd_vol_qt': np.sum,\
                        'yld_pt': 'last'}, label='left')
		df_daily_list.append(df_daily)

	df_diff_list = []
	df_diff = []
	# Calculate difference between ri and rf
	# Append beta values & farma french values for each bond & month
	for df in df_daily_list:
		df_diff = df.join(df_corp_index_1)
		df_diff = df_diff.drop(['trd_exctn_dt','entrd_vol_qt'], axis=1)
		# 'yld_pt' = bond return | 'yield' = corp bond index return
		df_diff['return_diff'] = df_diff['yld_pt'] - df_diff['yield']
		# add beta values & set index to datetime from df_diff
		df_diff = pd.merge(df_diff, df_betas, left_on='cusip_id', 
						right_on='cusip_id').set_index(df_diff.index)
		#join with fama-french factors on date index
		df_diff_1 = df_diff.join(df_ff_params, lsuffix="_m", rsuffix='_b')
		#drop any rows where dates in df_diff do not appear in fama-french
		df_diff_1 = df_diff_1[pd.notnull(df_diff_1['MKT_b'])]
		df_diff_list.append(df_diff_1)






	










