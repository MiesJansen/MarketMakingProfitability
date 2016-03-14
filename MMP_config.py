# Some universal constants for the entire project

# A directory for holding raw/processed data
# DO NOT push any data file to Github
DATA_PATH = './data/'
OUTPUT_PATH = './data/output/'

# Name of the datafile
DATA_NAME = 'List0'

# Indicator of whether output individual clean bond data to .csv
doOutput = True

# Number of subsections dataframe (because TRACE encourage to keep data
#  smaller than 2GB)
NUM_SUB_DF = 5