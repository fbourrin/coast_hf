
print("\nINITIALIZING ...\n")

import sys

# add custom librairies to python PATH
libpaths = ["readers/","tools/"]
for libpath in libpaths:
	sys.path.append(libpath)

import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
import os

import read_ctd as ctd
import file_manager as fm
import tools as tl
from size import A4_paysage, A4_portait, cm

import config as conf # load configuration from the configuration file

# =============================================================================
# SOME CONFIG
# =============================================================================

root = os.getcwd()

path_manual_filter = conf.path_manual_filter

#%% ===========================================================================
# LOAD DATA
# =============================================================================

print("\nSTART LOADING DATA ...\n")

data_POEM_HF = ctd.ctds(*conf.paths)
# create a list of columns names without mdates and datetime
datetime_col_name=conf.datetime_col_name
#keys = [key for key in list(data_POEM_HF.keys()) if ("mdates" not in key) and (datetime_col_name not in key)]
keys = conf.column_names

if os.path.exists(path_manual_filter):
    f_manual = pd.read_csv(path_manual_filter)
    for key in keys:
        if key in list(f_manual.columns):
            pass
        else :
            print(f"\n[ERROR] the columns '{key}' is missing in the manual filter file.\nThe manual validation is probably not complete yet. Please refer to the documentation.\n\nQuitting ...")
            sys.exit()
else :
	print("\n[ERROR] Can't find the manual filter file. Maybe it's doesn't exist yet. Please refer to the documentation.\n\nQuitting ...")
	sys.exit()

print("\nFINISHED LOADING DATA\n")

print("RUN ...")
# %%=============================================================================
# BASIC TESTS : Static (impossible values test), Slope and Spike
# =============================================================================

print("\t + running basic tests")

# create 3 dataframes shifted of -1,0 and +1 time wise
x1 = data_POEM_HF[keys] # x_{i}
x0 = data_POEM_HF[keys].shift(1) # x_{i-1}
x2 = data_POEM_HF[keys].shift(-1) # x_{i+1}

# thresholds for static filter in order : (waring : will create a bug if the order of columns in the input is not right)
# temperature_degc,salinity,fluorescence_rfu,turbidity_ntu,oxygen_mgl
staticmin = conf.th_static_min
staticmax = conf.th_static_max

#compute slope (it's an increase actually, not a slope as we don't involve time)
sl = ((x2 - x0).abs())/2
#compute spike
sp = ((x1 - (x2 + x0)/2).abs() - ((x2 - x0).abs())/2).abs()

# thresholds for slope and spike logical test (loaded from config file)
# conf.th_sl
# conf.th.sp

# get a filter for the null values
f_null = data_POEM_HF[keys].isnull()
# spread the null filter on both side for graphical purpose
f_filternull = f_null.shift(-1) | f_null | f_null.shift(1)

#test impossible values : "ge" means "greater than of equal" and "le" means "less than or equal" 
f_static = data_POEM_HF[keys].ge(staticmin) & data_POEM_HF[keys].le(staticmax)

#test slope and spike
f_sl = sl.lt(conf.th_sl)
f_sp = sp.lt(conf.th_sp)


# =============================================================================
# ADAPTATIVE TEST
# =============================================================================

print("\t + running adaptative test")

# define the rolling window used, here 288 as the number of sample per day
window = conf.rolling_window

# interpolate missing values with last non null value,
# rolling windows doesn't like missing value,
# it's just to compute the adaptative test
interp = data_POEM_HF[keys].interpolate()

# rolling centered mean
mean = interp.rolling(window,center=True,min_periods=1).mean()

# get the HF part of the signal, substracting a rolling mean kinda does that
hf = interp - mean

# rolling standard deviation on the HF part of the signal
std = hf.rolling(window,center=True,min_periods=1).std()

# "threshold" for the adaptative test, it's a moving threshold
offset = std*conf.threshold_factor

# compute adaptative test : see documentation
f_sk = (hf > -offset) & (hf < +offset) | (hf.abs() < hf.std()*conf.threshold_factor)

# %%=============================================================================
# COMPUTE QUALITY CODES
# =============================================================================

print("\t + compute quality codes")

# init
df_good=pd.DataFrame() # init the dataframe (it's an instance of the DataFrame class, I think)
df_passed=pd.DataFrame() # init the dataframe (it's an instance of the DataFrame class, I think)
df_good[datetime_col_name] = data_POEM_HF[datetime_col_name] # init the size (it's ugly but it's working)
df_passed[datetime_col_name] = data_POEM_HF[datetime_col_name] # init the size (it's ugly but it's working)
df_good[keys]=True # fill the entire dataframe with True
df_passed[keys]=0 # fill the entire dataframe with 0


# list of filters
filters = [~f_null,f_static,f_sl,f_sp,f_sk,f_manual]

# for each filters in the list
for tmp_fil in filters:
    # df_good contains boolean marking the data good or bad
    # each filters is applied one after the other 
    # each cycle df_good contains a smaller amount of data marked as good
    # in the end, only the data that will be qualified as good remains
    df_good[keys] = df_good[keys] & tmp_fil[keys]
    # for each cycle df_good is added to df_passed 
    # in the end the highest score in df_passed marks a good data, the lowest
    # marks null data, and everything in between is marked accordingly
    df_passed[keys] = df_passed[keys] + df_good[keys]

# 0    No quality control (QC) was performed.
# 1    QC was performed: good data
# 2    QC was performed: probably good data
# 3    QC was performed: probably bad data
# 4    QC was performed: bad data
# 5    The value was changed as a result of QC
# 7    Nominal value
# 8    Interpolated value
# 9   The value is missing

filter2qc = {
    0 : 9, # nan
    1 : 4, # f_null
    2 : 4, # f_static
    3 : 4, # f_sl
    4 : 3, # f_sp
    5 : 3, # f_sk
    6 : 1, # f_manual
    }

qc_codes = df_passed.replace(filter2qc)

# %%=============================================================================
# BUILD AND SAVE FILE WITH QC
# =============================================================================

print("\t + build and save file with QC")

columns = ["datetime"]+keys 
out = data_POEM_HF[columns]
for key in keys:
    out[f"qc_{key}"]=qc_codes[key].copy()
    
rename = {
    "datetime" : "utc_datetime"
    }

out.rename(columns=rename,inplace=True)
out.utc_datetime = out.utc_datetime.dt.strftime("%Y-%m-%dT%H:%M:%SZ")

fname = fm.build_path(root,"_build","POEM_qc",ext=".csv")
out.to_csv(fname,index=False)

print(f"\nFILE WITH QC SAVED!\nAt : {fname}")

# %%=============================================================================
# MAKE GRAPHS
# =============================================================================

print(f"\nBUILDING GRAPHS ...\n")

#
# graph 1 : display qc as color on RAW data
#

def qc2c(qc):
    d_qc2c = {
        9 : "tab:grey",
        4 : "tab:red",
        3 : "tab:orange",
        1 : "tab:green"
        }
    return d_qc2c[qc]


fig, ax = plt.subplots(len(keys),1,sharex=True)
fig.set_size_inches(*A4_paysage)

for i,key in enumerate(keys):
    col_qc = f"qc_{key}"
    qcs = list(out[col_qc].unique())
    for qc in qcs:
        ax[i].plot(data_POEM_HF.mdates,out[key].where(out[col_qc]==qc),c=qc2c(qc),label=f"qc = {qc}")
    
    ax[i].legend()
    ax[i].xaxis.set_major_formatter(mdates.DateFormatter('%Y-%m-%d %H:%M'))
    ax[i].set_ylabel(f"{tl.col2shortname(key)}")
    ax[i].grid(True)
    ax[i].xaxis.set_major_locator(mdates.MonthLocator())
    ax[i].legend(loc=1)

fig.suptitle("Graph QC",y=1.02)      
fig.autofmt_xdate()
fig.tight_layout(pad=0)
fig.subplots_adjust(hspace=0)

fname = fm.build_path(root,"_build","qc_POEM",ext=".svg")
fig.savefig(fname,bbox_inches='tight')

#
# graph 2 : temporal series with triggered bad data pinpoint
#

fig, axes = plt.subplots(len(keys),1,sharex=True)
fig.set_size_inches(*A4_paysage)

for i,key in enumerate(keys):
    axes[i].plot(data_POEM_HF.mdates,data_POEM_HF[key],c=tl.color(0),zorder=-20)
    axes[i].scatter(data_POEM_HF.mdates,data_POEM_HF.where(~f_sl & ~f_filternull)[key],c="tab:red",marker="x",label="accroissement > seuil")
    axes[i].scatter(data_POEM_HF.mdates,data_POEM_HF.where(~f_sp & ~f_filternull)[key],c="tab:orange",marker="x",label="pic > seuil")
    axes[i].scatter(data_POEM_HF.mdates,data_POEM_HF.where(~f_static)[key],c="tab:purple",marker="x",label="hors plage")
    axes[i].set_ylabel(f"{tl.col2shortname(key)}")
    axes[i].grid(True)
    axes[i].xaxis.set_major_formatter(mdates.DateFormatter('%Y-%m-%d'))
    axes[i].xaxis.set_major_locator(mdates.MonthLocator())
    axes[i].legend(loc=1)

fig.autofmt_xdate()
fig.tight_layout(pad=0)
fig.subplots_adjust(hspace=0)

fname = fm.build_path(root,"_build","basic_filter_POEM",ext=".svg")
fig.savefig(fname,bbox_inches='tight')

#
# graph 3 : flagged  sk
#

fw_min = mean - offset
fw_max = mean + offset

fig, axes = plt.subplots(len(keys),1,sharex=True)
fig.set_size_inches(*A4_paysage)

for i,key in enumerate(keys):
    axes[i].plot(data_POEM_HF.mdates,data_POEM_HF[key],c=tl.color(0),label="donnée brute",zorder=0)
    axes[i].scatter(data_POEM_HF.mdates,data_POEM_HF.where(~f_sk & ~f_null)[key],c="tab:red",zorder=1,label="donnée rejetée",alpha=1,marker="x")
    axes[i].fill_between(data_POEM_HF.mdates,fw_min[key],fw_max[key],color="tab:purple",alpha=0.5,zorder=-1,label="fenetre données conservées")
    axes[i].set_ylabel(f"{tl.col2shortname(key)}")
    axes[i].grid(True)
    axes[i].xaxis.set_major_formatter(mdates.DateFormatter('%Y-%m-%d'))
    axes[i].xaxis.set_major_locator(mdates.MonthLocator())
    axes[i].legend(loc=1)

fig.autofmt_xdate()
fig.tight_layout(pad=0)
fig.subplots_adjust(hspace=0)

fname = fm.build_path(root,"_build","sk_POEM",ext=".png")
fig.savefig(fname,bbox_inches='tight')

#
# graph 4 : good bad sk
#

fig, axes = plt.subplots(len(keys),1,sharex=True)
fig.set_size_inches(*A4_paysage)

for i,key in enumerate(keys):
    axes[i].plot(data_POEM_HF.mdates,data_POEM_HF.where(f_sk)[key],c=tl.color(0),label="donnée brute",zorder=0)
    axes[i].set_ylabel(f"{tl.col2shortname(key)}")
    axes[i].grid(True)
    axes[i].xaxis.set_major_formatter(mdates.DateFormatter('%Y-%m-%d'))
    axes[i].xaxis.set_major_locator(mdates.MonthLocator())
    axes[i].legend(loc=1)

fig.autofmt_xdate()
fig.tight_layout(pad=0)
fig.subplots_adjust(hspace=0)

fname = fm.build_path(root,"_build","sk_good_POEM",ext=".svg")
fig.savefig(fname,bbox_inches='tight')

