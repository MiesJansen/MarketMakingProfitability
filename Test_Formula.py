import pandas as pd
import numpy as np
import statsmodels.api as sm
from patsy import dmatrices
import matplotlib.pyplot as plt
import random
from scipy import stats

import MMP_config as cfg
import Display_Graphs as dg

def Test_Liquidity(df_list, df_liq_prox):
	# Beta values
	df_betas = pd.read_csv(cfg.DATA_PATH + cfg.CLEAN_DATA_FILE + '_Betas.csv')

	# Fama-French factors
	df_ff_params = Format_Fama_French()

	# Random list of integer index values of subset of all cusip ids
	df_daily_list = Get_Rand_Bond_List(df_list)

	df_list = []
	# Calculate difference between ri and rf
	# Append beta values, farma french, & Lt for each bond & month
	for df in df_daily_list:
		# Add liquidity factors and fama-french factors to single df
		df = Join_Inputs(df, df_betas, df_ff_params, df_liq_prox)

		# Calculate expected & actual returns, & their difference
		df = Calculate_Returns(df)

		# Drop duplicates & remove unnecessary columns
		df = Clean_Df(df)

		df_list.append(df)

	final_df = pd.concat(df_list)

	# Graph actual (TRACE) vs. expected (F.F.) return
	dg.Return_Vs_Graph(final_df)

	Write_Results(final_df)
	Get_Summary_Stats(final_df)

def Format_Fama_French():
	# Fama-French factors
	columns = ['Date', 'MKT', 'SMB', 'HML', 'DEF', 'TERM', 'RF']
	df_ff_params = pd.read_csv(cfg.DATA_PATH + cfg.FF_DATA_FILE + ".csv",
	                           usecols = columns, index_col = False,
	                           low_memory = False) # To silent warnings

	#convert date of fama-french to end of month
	df_ff_params['Date'] = pd.to_datetime(df_ff_params['Date'],
	                                      format='%Y%m')
	df_ff_params.set_index('Date', inplace=True)
	df_ff_params.index = df_ff_params.index.to_period('M').to_timestamp('M')

	return df_ff_params

def Get_Rand_Bond_List(df_list):
	num_bond_limit = max((len(df_list) / 4), 5)
	rand_list = random.sample(xrange(0, len(df_list)), num_bond_limit)

	df_daily = []
	df_daily_list = []
	for i in rand_list:
		df_daily = df_list[i].resample('M', how={'cusip_id': 'last',
		                                         'trd_exctn_dt': 'last',
		                                         'entrd_vol_qt': np.sum,
		                                         'yld_pt': 'last'}, label='left')
		df_daily_list.append(df_daily)

	return df_daily_list

def Join_Inputs(df, df_betas, df_ff_params, df_liq_prox):
	# add beta values & set index to datetime from df_diff
	df = pd.merge(df, df_betas, left_on='cusip_id', 
	              right_on='cusip_id', left_index=True)

	df['trd_exctn_dt_idx'] = pd.to_datetime(df['trd_exctn_dt'],\
                                        format='%Y%m%d')
	df.set_index('trd_exctn_dt_idx', inplace=True)
		
	# Join with fama-french factors on date index
	df_join_ff = df.join(df_ff_params, lsuffix="_m", rsuffix='_b')
	# Drop any rows where dates in df_diff do not appear in fama-french
	df_join_ff = df_join_ff[pd.notnull(df_join_ff['MKT_b'])]

	# Combine liquidity factor L_t
	df_liq_prox_values = df_liq_prox['residual_term']
	df_join_liq = df_join_ff.join(df_liq_prox_values)
	df_join_liq = df_join_liq[pd.notnull(df_join_liq['residual_term'])]

	return df_join_liq
	
def Calculate_Returns(df):
	#Calculate actual return of each bond 
	df['act_ret_diff'] = df['yld_pt'] - df['RF']

	#Calculate expected return for each bond using fama-french factors
	df['expec_ret_diff'] = \
			(df['intercept'] + \
			 df['MKT_b'] * df['MKT_m'] + \
			 df['SMB_b'] * df['SMB_m'] + \
			 df['HML_b'] * df['HML_m'] + \
			 df['DEF_b'] * df['DEF_m'] + \
			 df['TERM_b'] * df['TERM_m'] + \
			 df['L'] * df['residual_term'])

	#Calculate diff b/w actual and expected return
	df['return_delta'] = df['act_ret_diff'] - df['expec_ret_diff']

	return df

def Clean_Df(df):
	#drop any duplicates from random list
	df.drop_duplicates(['trd_exctn_dt', 'cusip_id'])

	#drop unnneeded columns
	df = df.drop(
		['trd_exctn_dt', 'yld_pt', 'entrd_vol_qt', 'intercept', 
		 'MKT_b', 'MKT_m', 'SMB_b', 'SMB_m', 'HML_b', 'HML_m', 
		 'DEF_b', 'DEF_m', 'TERM_b', 'TERM_m', 'RF', 'L', 
		 'residual_term'],
		axis=1)

	return df

def Write_Results(df):
	df.to_csv(cfg.DATA_PATH + cfg.CLEAN_DATA_FILE + '_return_diff.csv')

	# Plot actual return (TRACE) vs. expected return (F.F.)
	plt.scatter(df['act_ret_diff'], df['expec_ret_diff'])
	plt.ylabel('Expected Return')
	plt.xlabel('Actual Return')
	plt.title('All Bonds Actual vs. Expected Return')
    
	plt.savefig(cfg.DATA_PATH + cfg.DATA_CLEAN_FILE + '_return_diff.png')
	plt.close()

def Get_Summary_Stats(df):
	slope, intercept, r_value, p_value, std_err = \
		stats.linregress(df['act_ret_diff'], df['expec_ret_diff'])

	r2_value = r_value**2

	df_stats = pd.DataFrame({'slope':[slope], 'intercept':[intercept],
		'r2_value':[r2_value], 'p_value':[p_value], 'std_err':[std_err]})

	df_stats.to_csv(cfg.DATA_PATH + cfg.CLEAN_DATA_FILE + '_summary_stats.csv', index=False)


