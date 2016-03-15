# Some universal constants for the entire project

# A directory for holding raw/processed data
# DO NOT push any data file to Github
DATA_PATH = './data/'
OUTPUT_PATH = './data/output/'

# Whether to process raw data or read existing clean data directly
readRaw = False

# Name of the datafile
RAW_DATA_NAMES = ['List0', 'List1', 'List2', 'List3', 'List4']
CLEAN_DATA_FILE = 'list_clean'

# Start and end day of data
dt_start = '20100401'
dt_end = '20140331'

# Indicator of whether output individual clean bond data to .csv
doOutput = False

# Number of subsections dataframe (because TRACE encourage to keep data
#  smaller than 2GB)
NUM_SUB_DF = 5