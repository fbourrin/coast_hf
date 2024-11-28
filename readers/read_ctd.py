import datetime
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.dates as mdates

#utctimestamp_yyyy-mm-dd_hh:mm:ss,temperature_degc,salinity,fluorescence_rfu,turbidity_ntu,oxygen_mgl
#2020-01-01 00:00:00,13.8,36.8,0.1,2.3,6.3

fname_POEM_ctd_2020 = "data/POEM_subsurface_2020_2021/oobobsbuo_poem_ctd0med5m_2020.csv"
fname_POEM_ctd_2021 = "data/POEM_subsurface_2020_2021/oobobsbuo_poem_ctd0med5m_2021.csv"
fname_SOLA_ctd_2021 = "data/SOLA_subsurface_2021_2022/oobobsbuo_sola_ctd2med5m_2021.csv"
fname_SOLA_ctd_2022 = "data/SOLA_subsurface_2021_2022/oobobsbuo_sola_ctd2med5m_2022.csv"

def ctd(fname,add_mdates=True,nrows=None):
    dateparse = lambda X: datetime.datetime.strptime(X,'%Y-%m-%d %H:%M:%S')
    print(f"Read CTD\n{fname}")
    data = pd.read_table(fname,header=0,
                        decimal='.',
                        sep = ",",
                        usecols=[0,1,2,3,4,5],
                        names=["﻿utctimestamp","temperature_degc","salinity","fluorescence_rfu","turbidity_ntu","oxygen_mgl"],
                        parse_dates={"datetime": ["﻿utctimestamp"]},
                        date_parser=dateparse,
                        nrows=nrows
                        #delim_whitespace = True,
                        #skip_blank_lines=True
                        )
    if add_mdates :
        data.loc[:,"mdates"] = [mdates.date2num(e) for e in data.datetime]
    return data

def ctds(*fnames,add_mdates=True):
    data = ctd(fnames[0],False)
    for fname in fnames[1:]:
        data = pd.concat((data,ctd(fname,False)))
    data.reset_index(drop=True,inplace=True)
    if add_mdates :
        data.loc[:,"mdates"] = [mdates.date2num(e) for e in data.datetime]
    return data
