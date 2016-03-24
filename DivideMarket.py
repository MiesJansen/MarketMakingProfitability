import pandas as pd

import MMP_config as cfg

## TODO: add more specific rules for dividing the market
MOODY_IG = ["Aaa", "Aa1", "Aa2", "Aa3", "A1", "A2", "A3",\
            "Baa1", "Baa2", "Baa3"]

def SegmentByRating(df_trace, df_datastream):
	# Merge TRACE cusip ids with datastream cusip_ids, to find the common
	#  set of cusip id to construct the corporate bond market portfolio
	df = pd.merge(df_trace, df_datastream, on = ["cusip_id"])

	# Eliminate invalid ratings
	df = df[df['MOODY_RATING'].str.startswith(tuple(['A', 'B', 'C']),
	                                          na = False)]
	#print "After merging, number of corporate bonds =", df.shape[0]
	
	df_groups = df.groupby(['MOODY_RATING'])
	IGs = []
	HYs = []
	for label, df_group in df_groups:
		if label in MOODY_IG:
			IGs.append(df_group)
		else:
			HYs.append(df_group)
	
	ddf_ratings = dict.fromkeys(cfg.RATING_SEGS)
	ddf_ratings['IG'] = pd.concat(IGs)
	ddf_ratings['HY'] = pd.concat(HYs)
	return ddf_ratings


# Segment the market by SIC ID, i.e. by industry group
def SegmentBySIC(df_trace, df_datastream):
	# Merge TRACE cusip ids with datastream cusip_ids, to find the common
	#  set of cusip id to construct the corporate bond market portfolio
	df = pd.merge(df_trace, df_datastream, on = ["cusip_id"])
	
	# Eliminate invalid SIC ID's
	df = df.dropna(subset = ['SIC'])
	df = df[(df['SIC'] >= 100) & (df['SIC'] <= 9999)]
	#print "After merging, number of corporate bonds =", df.shape[0]
	
	ddf_industry = dict.fromkeys(cfg.INDUSTRY_SEGS)
	# Agriculture, Forestry and Fishing
	ddf_industry['AGRICULTURE'] = df[df['SIC'] < 1000]
	# Mining
	ddf_industry['MINING'] = df[(df['SIC'] >= 1000) & (df['SIC'] < 1500)]
	# Construction
	ddf_industry['CONSTRUCTION'] = df[(df['SIC'] >= 1500) & (df['SIC'] < 2000)]
	# Manufacturing
	ddf_industry['MANUFACTURING'] = df[(df['SIC'] >= 2000) & (df['SIC'] < 4000)]
	# Transportation, Communications, Electric, Gas, and Sanitary Services
	ddf_industry['UTILITIES'] = df[(df['SIC'] >= 4000) & (df['SIC'] < 5000)]
	# Wholesale
	ddf_industry['WHOLESALE'] = df[(df['SIC'] >= 5000) & (df['SIC'] < 5200)]
	# Retail
	ddf_industry['RETAIL'] = df[(df['SIC'] >= 5200) & (df['SIC'] < 6000)]
	# Finance, Insurance and Real Estate
	ddf_industry['FINANCE'] = df[(df['SIC'] >= 6000) & (df['SIC'] < 7000)]
	# Services
	ddf_industry['SERVICES'] = df[(df['SIC'] >= 7000) & (df['SIC'] < 9000)]
	# Public Administration
	ddf_industry['ADMINISTRATION'] = df[df['SIC'] >= 9000]
	
	return ddf_industry
	