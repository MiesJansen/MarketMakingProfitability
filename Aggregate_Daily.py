import pandas as pd
import numpy as np

import MMP_config as cfg

day_list = pd.date_range(cfg.dt_start, cfg.dt_end, freq = 'D')
day_keys = dict(zip((''.join([str(dt.day), str(dt.month), str(dt.year)]) \
	for dt in day_list), range(len(day_list))))

def Group_Daily(df_list):
	'''Sum volume traded and get mean of yield for all trades within a day.
	   Assign them to the same named columns.
	   'yld_pt' = avg yield for day
	   'entrd_vol_qt' = sum of all volumes traded over day
	'''
	df_new_list = []	#all bonds

	for df in df_list:
		# Skip empty bond record
		if df.empty:
			continue

		df['trd_exctn_dt_idx'] = pd.to_datetime(df['trd_exctn_dt'],\
		                                        format='%Y%m%d')
		# set DateTime series as index od dataframe for regression above
		df = df.set_index('trd_exctn_dt_idx')

		df['yld_sign_cd'] = np.where(df['yld_sign_cd'] == '-', -1, 1)
		df['yld_pt'] = df['yld_sign_cd'] * df['yld_pt']

		# For each day, sum all volumnes, take the END OF DAY yield
		## FIX yield sign is temporarily needed until the excess yield
		##      is implemented in proxy
		df_daily = df.resample('D', how={'cusip_id': 'last',\
		                                 'trd_exctn_dt': 'last',\
		                                 'entrd_vol_qt': np.sum,\
		                                 'yld_sign_cd': 'last',
		                                 'yld_pt': 'last'}, label='left')
		df_daily = df_daily.dropna(how = 'any', inplace = False)

		df_new_list.append(df_daily)

	return df_new_list
