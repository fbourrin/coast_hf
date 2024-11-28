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
from matplotlib.colors import Normalize
from matplotlib.widgets import  Button, SpanSelector
from matplotlib.colors import ListedColormap
from time import sleep
import shutil

import read_ctd as ctd
import file_manager as fm

def notify(msg):
    try:
        os.system(f"notify-send '{msg}'")
    except:
        pass

#%%
class Selector:
    def __init__(self,x,y,s,param,visual=None):
        self.state = False
        self.x = x
        self.y = y
        self.s = s
        self.param = param
        self.visual = visual
        
        self.root = os.getcwd()
        self.fname = fm.build_path(self.root,"data","manual_filter","manual_filter",ext=".csv")
        
        # load s if it exists
        self.load()
        
        cm = (25/64)
        A4_portait = np.array([21,29.7])*cm
        A4_paysage = np.array([29.7,21])*cm
        SIZE = A4_paysage
        
        self.fig, self.ax = plt.subplots()
        self.fig.set_size_inches(*SIZE)
        self.good, = self.ax.plot(self.x,self.y.where(self.s),c="tab:green")
        self.bad, = self.ax.plot(self.x,self.y.where(~self.s),c="tab:red")
        
        if isinstance(self.visual, pd.DataFrame):
            self.ax2 = self.ax.twinx()
            keys = [e for e in visual.keys() if ("datetime" not in e) and ("mdates" not in e)]
            self.visual.index = self.visual.mdates
            self.visual = self.visual[keys]
            self.visual = (self.visual-self.visual.min())/(self.visual.max()-self.visual.min())
            self.ax2.plot(visual,zorder=-10,alpha=0.3)
            self.ax2.legend(keys)
            
        self.ax.grid(True)
        self.ax.xaxis.set_major_formatter(mdates.DateFormatter('%Y-%m-%d %H:%M'))
        self.ax.xaxis.set_major_locator(mdates.MonthLocator())
        self.fig.autofmt_xdate()
        self.fig.tight_layout(pad=0)
        
        self.ss = SpanSelector(self.ax, self.onselect, "horizontal")
        self.fig.canvas.mpl_connect('close_event', self.on_close)  
         
        self.axbadd = self.fig.add_axes([0,0.95,0.1, 0.05])
        self.badd = Button(self.axbadd, 'Add')
        self.badd.on_clicked(self.add)
        
        self.axbrem = self.fig.add_axes([0.1,0.95,0.1, 0.05])
        self.brem = Button(self.axbrem, 'Remove')
        self.brem.on_clicked(self.remove)
        
        self.axbsav = self.fig.add_axes([0.2,0.95,0.1, 0.05])
        self.bsav = Button(self.axbsav, 'Save')
        self.bsav.on_clicked(self.save)
        
    def onselect(self,*args):
        #print(args)
        d0, d1 = args
        cut = ((self.x>=d0) & (self.x<=d1))
        self.s[cut] = self.state
        self.good.set_ydata(self.y.where(self.s))
        self.bad.set_ydata(self.y.where(~self.s))
        self.fig.canvas.draw()
        
    def on_close(self,*args):
        self.backup()
    
    def add(self,*args):
        print("state set to add")
        self.state = True
        
    def remove(self,*args):
        print("state set to remove")
        self.state = False
        
    def load(self,*args):
        print("Loading if data exists ... ")
        if os.path.exists(self.fname):
            print("It exists!")
            tmp = pd.read_csv(self.fname)
            if self.param in list(tmp.keys()):
                #print(self.s)
                #print(tmp[self.param])
                self.s = tmp[self.param]
        else :
            print("It does not exists!")
            
    def backup(self,*args):
        now = pd.Timestamp.now().strftime("%Y%m%d%H%M%S")
        fbak = f"{self.fname}.{now}.bak"
        msg = f"Closing...\nBacking up just in case :\n{fbak}"
        print(msg)
        notify(msg)
        
        if os.path.exists(self.fname):
            # backup
            shutil.copyfile(self.fname,fbak)
            # load
            df_mf = pd.read_csv(self.fname)
            # modify
            df_mf[self.param] = self.s
            # save
            df_mf.to_csv(fbak,index=False)
        else :
            # create
            df_mf = pd.DataFrame()
            # save
            df_mf[self.param] = self.s
            df_mf.to_csv(fbak,index=False)
        
    def save(self,*args):
        print("Saving ...")
        now = pd.Timestamp.now().strftime("%Y%m%d%H%M%S")
        fbak = f"{self.fname}.{now}.bak"
        msg = f"Saving {self.param}\ninto {self.fname}"
        notify(msg)
        if os.path.exists(self.fname):
            print(f"File exist : {self.fname}")
            print(f"Saving param : {self.param}")
            # backup
            shutil.copyfile(self.fname,fbak)
            # load
            df_mf = pd.read_csv(self.fname)
            # modify
            df_mf[self.param] = self.s
            # save
            df_mf.to_csv(self.fname,index=False)
        else :
            print(f"File doesn't exist : {self.fname}")
            print(f"Saving param : {self.param}")
            # create
            df_mf = pd.DataFrame()
            # save
            df_mf[self.param] = self.s
            df_mf.to_csv(self.fname,index=False)
#%%
if __name__ == '__main__': 
    
    print("LOADING DATA ...\n")
    df = ctd.ctds(ctd.fname_POEM_ctd_2020,ctd.fname_POEM_ctd_2021)
    print("\nLOADING DATA FINISHED\n")
    
    keys = [e for e in df.keys() if ("datetime" not in e) and ("mdates" not in e)]
    
    # ['temperature_degc',
    #  'salinity',
    #  'fluorescence_rfu',
    #  'turbidity_ntu',
    #  'oxygen_mgl']
    
    #%%
    # select param
    dkeys = {i:e for i,e in enumerate(keys)}
    msg = "On which parameter do you want to work ?\n(enter a number and then press [ENTER])\n"
    msg += "\n".join([f"\t{i} > {e}" for i,e in enumerate(keys)])
    msg += "\n : "
    r = int(input(msg))
    if r in dkeys.keys() :
        param = dkeys[r]
        x = df.mdates
        y = df[param]
        s = pd.Series(True,index=x.index)
        sel = Selector(x, y, s, param)
    else :
        print("Wrong param, quitting ...")
    
    
    



