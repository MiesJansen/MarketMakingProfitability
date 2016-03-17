import pandas as pd
import numpy as np
import statsmodels.api as sm
from patsy import dmatrices
import matplotlib
import matplotlib.pyplot as plt
import copy

import MMP_config as cfg

day_list = pd.date_range(cfg.dt_start, cfg.dt_end, freq = 'D')
day_keys = dict(zip((''.join([str(dt.day), str(dt.month), str(dt.year)]) \
	for dt in day_list), range(1462)))
num_months_CONST = len(day_keys)

def Group_Daily(orig_df_list):
	'''Sum volume traded and get mean of yield for all trades within a day.
	   Assign them to the same named columns.
	   'yld_pt' = avg yield for day
	   'entrd_vol_qt' = sum of all volumes traded over day
	'''
	df_list = Filter_Columns(orig_df_list)
	df_day_list = []	#per bond
	df_new_list = []	#all bonds


	for df in df_list:
		for date, df_group in df.groupby(pd.TimeGrouper("D")):
			df = pd.DataFrame(df_group)

			#if no trades on a day, skip the rest of the for loop
			if df.empty:
				continue

			#average yield over trades for day
			yield_mean = df['yld_pt'].mean()
			#sum volumes traded over day
			volume_sum = df['entrd_vol_qt'].sum()

			#get last row of trades for day to get closing price
			df_new = df.tail(1)

			#assign values to already existing columns
			df_new.loc[date,'entrd_vol_qt'] = volume_sum
			df_new.loc[date,'yld_pt'] = yield_mean

			df_day_list.append(df_new)

		df_new_list.append(pd.concat(df_day_list))
		df_day_list = []

	return df_new_list

def Filter_Columns(orig_df_list):
	df_list = []

	for df in orig_df_list:
		df['trd_exctn_dt_idx'] = pd.to_datetime(df['trd_exctn_dt'], format='%Y%m%d')
		# set DateTime series as index od dataframe for regression above
		df = df.set_index('trd_exctn_dt_idx')

		df['yld_sign_cd'] = np.where(df['yld_sign_cd'] == '-', -1, 1)
   		df['yld_pt'] = df['yld_sign_cd'] * df['yld_pt']

   		if df.shape[0] > 0:
			df_list.append(df)

	return df_list












