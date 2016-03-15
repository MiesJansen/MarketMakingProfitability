# Some universal constants for the entire project

# PreProcessing/Cleaning data
#---------------------------------------------
# A directory for holding raw/processed data
# DO NOT push any data file to Github
DATA_PATH = './data/'
OUTPUT_PATH = './data/output/'

# Whether to process raw data or read existing clean data directly
readRaw = False

# Only use when readRaw = False
doOutput = False    # Whether output individual clean bond data to .csv
CLEAN_DATA_FILE = 'list_clean'

# Only use when readRaw = True
# Name of the datafile
RAW_DATA_NAMES = ['List0', 'List1', 'List2', 'List3', 'List4']

# Calculating proxies
#-----------------------------------------------
# Start and end day of data
dt_start = '20100401'
dt_end = '20140331'

# Generating list of cusip id's
#------------------------------------------------
# Number of subsections dataframe (because TRACE encourage to keep data
#  smaller than 2GB)
NUM_SUB_DF = 5