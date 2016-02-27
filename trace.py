import pandas as pd

df = pd.read_csv('C:\\Users\\Alex\\Desktop\\Industry Project\\trace_data.csv', sep=',')

for col in df.columns:
	print (col)