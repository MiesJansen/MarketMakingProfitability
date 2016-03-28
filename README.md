Python Version Used --> Python 2.7 
(Recommend installing Anaconda which has many of the following libraries preinstalled)

Python Library Dependencies 

1. pandas

2. numpy

3. matplotlib.pyplot

4. statsmodels.api

5. random

6. csv

7. tablib

8. os

9. from patsy import dmatrices

10. from scipy import stats

--------------------------------------------------------------------

Instructions to Run

1. Create main directory folder. For example "C:/Users/Project". 

2. Also create subdirectory folder "./data". For example 
   "C:/Users/Project/data". 

3. Download enhanced TRACE data from WRDS database. Included all 
   columns when downloading. Specify date format as YYMMDD.

4. Upload TRACE data file into ./data.

5. Specify all parameters in "MMP_config.py"
  
  5.1. Set "dt_start" and "dt_end" from downloaded TRACE data
  
  5.2. Set "RAW_DATA_NAMES" with an array of filenames of raw TRACE 
       data files downloaded.
  
    5.2.1. If only one file, set to an array of one value.
  
  5.3. Set "readRaw" = True. Program will read raw TRACE data files.
  
    5.3.1. If already generated the clean data file set 
		   "readRaw" = False.
  
  5.4. Set "CLEAN_DATA_FILE" with a filename. The data written will 
       be cleaned TRACE data and have all same-day trades aggregated into one daily trade.

6. Respecify parameters in "MMP_config.py" after running program 
   with raw TRACE data files.
  
  6.1 Set "readRaw" = False. Don't need to read raw 
      data file anymore because generated clean data file.
  
  6.2 Set "readDaily" = True.

  --> Note - Will now read "CLEAN_DATA_FILE" instead of 
             "RAW_DATA_NAMES".
  
  --> Note - Reading "CLEAN_DATA_FILE" much faster than 
			 reading "RAW_DATA_NAMES".

---------------------------------------------------------------------

Files Generated --> All contained in "./data"

1. "CLEAN_DATA_FILE" value = "filename_clean"

2. ["filename_clean"] + ["_Betas.csv"] 
  
  2.1. Values calculated in Fama-Fench model 

3. ["filename_clean"] + ["_return_diff.csv"]

  3.1. Actual bond return minus risk free rate 
       ("BofA_Corporate_Bond_Index")

  3.2. Expected return minues risk free rate from Fama-French model

  3.3. Difference between actual and expected return.

4. ["filename_clean"] + ["_return_diff.pdf"]

  4.1. Scatterplot of actual return vs. expected return.

5. ["filename_clean"] + ["_stats_summary.csv"]

  5.1. R^2, t test-statistic, and p value for each bond return 
       calculated in Fama-French equation.

6. ["filename_clean"] + ["_monthly_volume.csv"]

7. ["filename_clean"] + ["_monthly_volume.pdf"]

8. ["filename_clean"] + ["_monthly_total_bonds.csv"]

9. ["filename_clean"] + ["_monthly_total_bonds.pdf"]

10. ["filename_clean"] + ["_liquidity.csv"]

  10.1. Liquidity coefficient per month calculated from equation (3) 
        in 'Liquiidity risk and expected corporate bond return' paper.

11. ["filename_clean"] + ["_liquidity.pdf"]

12. ["filename_clean"] + ["_liquidity_risk.pdf"]

  12.1. Lt calculated from residual term in equation (5) in 
        'Liquiidity risk and expected corporate bond return' paper.




