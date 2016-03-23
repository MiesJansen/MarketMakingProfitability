import pandas as pd

import MMP_config as cfg

## TODO: add more specific rules for dividing the market
MOODY_IG = ["Aaa", "Aa1", "Aa2", "Aa3", "A1", "A2", "A3",\
            "Baa1", "Baa2", "Baa3"]

def SegmentByRating(df_trace, df_datastream, sym_delim):
	# Merge trace cusip ids with datastream cusip_ids, to find the common
	#  set of cusip id to construct the corporate bond market portfolio
	df = pd.merge(df_trace, df_datastream, on = ["cusip_id"])

	# Eliminate invalid ratings
	df = df[df[sym_delim].str.startswith(tuple(['A', 'B', 'C']), na = False)]
	#print "After merging, number of corporate bonds =", df.shape[0]
	
	df_groups = df.groupby([sym_delim])
	IGs = []
	HYs = []
	for label, df_group in df_groups:
		if label in MOODY_IG:
			IGs.append(df_group)
		else:
			HYs.append(df_group)
	
	return pd.concat(IGs), pd.concat(HYs)
		
