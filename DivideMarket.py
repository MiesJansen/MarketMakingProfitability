import pandas as pd

import MMP_config as cfg

MOODY_IG = ["Aaa", "Aa1", "Aa2", "Aa3", "A1", "A2", "A3",\
			"Baa1", "Baa2", "Baa3"]

def DivideMarket(df_trace, df_datastream, sym_delim):
	# Merge trace cusip ids with datastream cusip_ids, to find the common
	#  set of cusip id to construct the corporate bond market portfolio
	df = pd.merge(df_trace, df_datastream, on = ["cusip_id"])
	
	if sym_delim is "MOODY RATING":
		df = df[df[sym_delim].str.startswith(['A', 'B', 'C'], na = False)]
	## TODO: add more specific rules for dividing the market
	
	print "After merging, number of corporate bonds =", df.shape[0]
	
	df_groups = df.groupby([sym_delim])
	IGs = []
	HYs = []
	for label, df_group in df_groups:
		if label in MOODY_IG:
			IGs.append(df_group)
		else:
			HYs.append(df_group)
	
	df_IG = pd.concat(IGs)
	df_HY = pd.concat(HYs)
	
	if not df_IG.empty:
		df_IG.to_csv(cfg.DATA_PATH + sym_delim + "_cusips_IG.csv")
	if not df_HY.empty:
		df_HY.to_csv(cfg.DATA_PATH + sym_delim + "_cusips_HY.csv")
		



df_trace = pd.read_csv(cfg.DATA_PATH + cfg.CUSIP_LIST + ".csv")
df_datastream = pd.read_csv(cfg.DATA_PATH + "bond_list_datastream.csv")

DivideMarket(df_trace, df_datastream, "MOODY_RATING")