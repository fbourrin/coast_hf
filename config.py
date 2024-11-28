import numpy as np

# =============================================================================
# DATA
# =============================================================================

# list of the paths of the data file csv (must have the same column names)
paths = ["data/POEM_subsurface_2020_2021/oobobsbuo_poem_ctd0med5m_2020.csv","data/POEM_subsurface_2020_2021/oobobsbuo_poem_ctd0med5m_2021.csv"]

# list of the column names of the parameters
column_names = ["temperature_degc","salinity","fluorescence_rfu","turbidity_ntu","oxygen_mgl"]

#datetime column name
datetime_col_name="datetime"

# path of the manual filter file
path_manual_filter = "data/manual_filter/manual_filter.csv"

# =============================================================================
# BASIC FILTERS
# =============================================================================

# threshold values (min and max) for static filter (test of the impossibles values)
th_static_min = np.array([10,20,0,0,0])
th_static_max = np.array([30,45,15,40,10])

# threshold values for slope filter
th_sl = np.array([1,3,4,6,0.3])

# threshold values for spike filter
th_sp  = np.array([1,3,4,6,0.3])

# =============================================================================
# ADAPTATIVE FILTER
# =============================================================================

# rolling window in sample size (here we got a sample every 5 minutes,
# 288 samples represent a day worth of data)
rolling_window = 288

# factor apply to the moving threshold (which is kinda based on standard deviation,
# if we suppose a normal distribution, which is not quite sure)
threshold_factor = 4
