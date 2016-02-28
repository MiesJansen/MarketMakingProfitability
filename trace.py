import pandas as pd
import numpy as np

#page 12-13
def Initial_deletes(df):
	#delete items without cusip_id
	df = df[df['cusip_id'] != '']
	#delete cancellations(X) and corrections(C); 
	#keep trade(T) and replacement/correction(R)
	df = df[df['trc_st'].isin(["T", "R"])]
	#remove reversals (Y) ----->>>>> Tom not included in your notes 
	df = df[df['trc_st'] != 'Y']

	return df


if __name__ == "__main__":
	#df = DataFrame from pandas library
	df = pd.read_csv('C:\\Users\\Alex\\Desktop\\Industry Project\\trace_data.csv', sep=',')
	
	print (df.shape)
	print
	#for col in df.columns:
	#	print (col)

	df = Initial_deletes(df)

	print (df.shape)