import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
import matplotlib.colors as mcolors
import os
import sys
from matplotlib.colors import Normalize

import file_manager as fm

def color(index):
    colors  = list(mcolors.TABLEAU_COLORS.keys()) + list(mcolors.BASE_COLORS.keys())
    return colors[index]

def colors(ilist):
    return [color(int(i)) for i in ilist]
    
s_trad="""
oxygen_mgl:Oxygène $(mg/L)$
atmosphericpressure_mbar:Pression Atmo. $(mbar)$
airtemperature_degc:Température Air $(°C)$
windspeed_kn:Vitesse Vent $(kn)$
windirection_deg:Direction Vent $(°)$
temperature_degc:Température Eau $(°C)$
salinity:Salinité $(psu)$
fluorescence_rfu:Fluoréscence $(rfu)$
turbidity_ntu:Turbidité $(ntu)$
"""
t_trad = np.array([e.split(":") for e in s_trad.strip().split("\n")])
d_trad = {k:v for k,v in t_trad}

def col2name(val):
    if val in d_trad.keys():
        sres = f"{d_trad[val]}"
    else:
        sres = "<empty trad>"
    return sres

s_shorttrad="""
oxygen_mgl:oxy.
atmosphericpressure_mbar:pres.
airtemperature_degc:air temp.
temperature_degc:eau temp.
salinity:sal.
fluorescence_rfu:fluo.
turbidity_ntu:tur.
"""

t_shorttrad = np.array([e.split(":") for e in s_shorttrad.strip().split("\n")])
d_shorttrad = {k:v for k,v in t_shorttrad}

def col2shortname(val):
    if val in d_shorttrad.keys():
        sres = f"{d_shorttrad[val]}"
    else:
        sres = "<empty trad>"
    return sres

def timecut(data,start,end,col="datetime"):
    """
    Cut dataframe between 2 dates and returned the inside

    Parameters
    ----------
    data : pandas dataframe
        this is the dataframe to be cut
    start : str, datetime object
        cut from this date (included)
    end : str, datetime object
        cut to this date (included)
    col : str, optional
        datetime object col name in data dataframe. The default is "datetime".

    Returns
    -------
    dataframe

    """
    cut = (data[col]>=start) & (data[col]<=end)
    data = data[cut]
    return data

def addmdates(data,dtcol = "datetime"):
    data.loc[:,("mdates")] = [mdates.date2num(e) for e in data[dtcol]]
    return data
def warn(msg="My job is done, sir."):
    os.system(f"espeak '{msg}'")
    os.system(f"notify-send '{msg}'")
    
def fix_missing_date(data,col="datetime",freq=None):
    """
    Just add a row with date and nan for the value where the date is missing.
    This allow to later extract the array with a correct index

    Parameters
    ----------
    data : dataframe
        dataframe to be fixed in dates.
    col : str, optional
        Column name containing datetime object on which to perform the fixing. The default is "datetime".

    Returns
    -------
    fixeddata : datafame
        .

    """
    date0 = data[col].iloc[0]
    date1 = data[col].iloc[1]
    daten = data[col].iloc[-1]
    
    if freq == None :
        freq = date1-date0
    
    fixeddata = pd.DataFrame()
    fixeddata["datetime"] = pd.date_range(start=date0,end=daten,freq=freq)
    
    fixeddata = fixeddata.merge(data,on=col,how="outer")
    return fixeddata
    
if __name__ == '__main__' :
    station = hydro.station_Tet_Perpignan
    start = "2020-01-01"
    end = "2021-12-31"
    hydro0 = hydro.HydroSeries(station=station,start=start,end=end).data
    hydro1 = fix_missing_date(hydro0)