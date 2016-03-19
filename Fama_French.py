import numpy as np
import pandas as pd
import statsmodels.api as sm
from patsy import dmatrices

import MMP_config as cfg

def FamaFrenchReg(df_list, df_liq):
    # Calculate market parameters needed by Fama French Model
    #----------------------------------------------
    # Include:
    #  1. Basic parameters for Fama French 3-factor model
    #  2. DEF and TERM (calculated in Excel by investment bond portfolio yield,
    #      10-year government bond yield, and 1 month T-bill yield
    columns = ['Date', 'MKT', 'SMB', 'HML', 'DEF', 'TERM', 'RF']
    df_ff_params = pd.read_csv(cfg.DATA_PATH + cfg.FF_DATA_FILE + ".csv",\
                               usecols = columns, index_col = False,
                               low_memory = False) # To silent warnings
    
    df_ff_params['Date'] = df_ff_params['Date'].apply(str)
    
    # Add liquidity term
    df_liq = pd.DataFrame(df_liq)
    df_liq['Date'] = df_liq.index.astype(str)
    df_liq['Date'] = pd.Series(df_liq['Date'].str[:4]) + \
        pd.Series(df_liq['Date'].str[5:7])
    df_ff_params = pd.merge(left = df_ff_params, right = df_liq,
                            on = ['Date'], how = 'inner')
    
    # Reformat
    df_ff_params = df_ff_params.rename(columns={'residual_term': 'L'})
    
    # Aggregate monthly yield for each bond
    #---------------------------------------------
    df_yld_list = []
    for df in df_list:
	df_list_monthly = []
	for date, df_group in df.groupby(pd.TimeGrouper("M")):
	    df_month = pd.DataFrame(df_group)
	    if df_month.empty:
		continue
	    
	    # Take END OF THE MONTH yield as monthly yield, other possible
	    #  monthly yield is AVERAGE, or BEGINNING OF THE MONTH
	    df_month_yld = df_month.tail(1)
	    df_list_monthly.append(df_month_yld)
	
	# Combine monthly data with Fama French parameters,
	#  and add to a list for every bond
	df_month_yld = pd.concat(df_list_monthly)
	df_month_yld['trd_exctn_dt'] = \
            df_month_yld['trd_exctn_dt'].astype(str).str[0:6]	
	df_month_yld = pd.merge(left = df_month_yld, right = df_ff_params,
	                        left_on = ['trd_exctn_dt'], right_on = ['Date'],
	                        how = 'inner')
	if df_month_yld.shape[0] > 0:
	    df_yld_list.append(df_month_yld)

    ## FIX normalize data before running regression!!!
    ## Keep in mind the method needed to be documented, because the same
    ##   normalization needed for calculating excess yield with the model
    
    #run linear regression using equation (9) from pdf for each bond
    #-----------------------------------------------------
    df_list_Beta = []
    headers = ['cusip_id', 'intercept', 'MKT', 'SMB', 'HML', 'DEF', 'TERM', 'L']
    for df in df_yld_list:
	df['e_return'] = df['yld_pt'] - df['RF']
	y,X = dmatrices('e_return ~ MKT + SMB + HML + DEF + TERM + L',\
	                data = df, return_type = 'dataframe')
	mod = sm.OLS(y,X)
	res = mod.fit()
	
	# Add cusip id and all regression results to a list
	beta_list = [df.get_value(df.index[0], 'cusip_id')]
	beta_list += list(res.params[:7])
	
	df_list_Beta.append(beta_list)
	
    df_Beta = pd.DataFrame(df_list_Beta, columns = headers)
    df_Beta.to_csv(cfg.DATA_PATH + cfg.CLEAN_DATA_FILE + "_Betas.csv",
                   index = False)
