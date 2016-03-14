# Some universal constants for the entire project

# A directory for holding raw/processed data
# DO NOT push any data file to Github
DATA_PATH = './data/'
OUTPUT_PATH = './data/output/'

# Name of the datafile
DATA_NAMES = ['List0', 'List1', 'List2', 'List3', 'List4']

# Indicator of whether output individual clean bond data to .csv
doOutput = True

# Number of subsections dataframe (because TRACE encourage to keep data
#  smaller than 2GB)
NUM_SUB_DF = 5