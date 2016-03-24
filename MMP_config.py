# Some universal constants for the entire project

# PreProcessing/Cleaning data
#---------------------------------------------
# A directory for holding raw/processed data
# DO NOT push any data file to Github
DATA_PATH = './data/'
OUTPUT_PATH = './data/output/'

# Read aggreated daily data instead of precessing
readDaily = False

# Only when readDaily = False
# Whether to process raw data or read existing clean data directly
readRaw = True

CLEAN_DATA_FILE = 'list_clean_IG' #'list_clean_HY'

# Only use when readRaw = True
# Name of the datafile
RAW_DATA_NAMES = ['IG_raw']#['HY_raw']
doOutput = False    # Whether output individual clean bond data to .csv

# Calculating proxies
#-----------------------------------------------
# Start and end day of data
dt_start = '20100401'
dt_end = '20140331'

BOND_IDX_FILE = 'BofA_Corporate_Bond_Index'

# Fama French data
#-----------------------------------------------
FF_DATA_FILE = 'FF_monthly_data'

# Generating list of cusip id's
#------------------------------------------------
# Number of subsections dataframe (because TRACE encourage to keep data
#  smaller than 2GB)
NUM_SUB_DF = 2

# Output file of unique cusip ids
CUSIP_LIST = "cusip_id_list"

# Name for market segments
RATING_SEGS = ['IG', 'HY']
INDUSTRY_SEGS = ['AGRICULTURE', 'MINING', 'CONSTRUCTION', 'MANUFACTURING',
                 'UTILITIES', 'WHOLESALE', 'RETAIL', 'FINANCE', 'SERVICES',
                 'ADMINISTRATION']