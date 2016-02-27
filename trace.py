import pandas as pd
import numpy as np

#page 12-13
def Initial_deletes(df):
	#delete items without cusip_id
	df = df[df['cusip_id'] != '']
	#delete cancellations(X) and corrections(C); 
	#keep trade(T) and replacement/correction(R)
	df = df[df['trc_st'].isin(["T", "R"])]

if __name__ == "__main__":
	df = pd.read_csv('C:\\Users\\Alex\\Desktop\\Industry Project\\trace_data.csv', sep=',')
	for col in df.columns:
		print (col)

	Initial_deletes(df)