import os
from six.moves import input as raw_input
import logging
print = logging.info

root = "/home/karnaphorion/2021/Univ/Stage/CoastHF/pylab"

def file_selector(path):
    # get list files
    path = rp2ap(path)
    rmkdir(path)
    l_dir = os.listdir(path)
    short_files = []
    full_files = []
    for e_dir in l_dir:
        tmp = os.path.join(path,e_dir)
        if os.path.isfile(tmp):
            short_files.append(e_dir)
            full_files.append(tmp)
    if len(short_files)>=0 and raw_input("Select existing file (y/n) : ")=='y':
        # build display
        s="Which file to choose (y/n) :\n"
        for i,e in enumerate(short_files):
            s+=f"{i}>\t{e}\n"
        s+=" : "
        index = int(raw_input(s))
        fres = full_files[index]
    else :
        fname = raw_input("New file name : ")
        fres = os.path.join(path,fname)
    print(fres)
    return fres
    
def rp2ap(relative_path):
    current = os.getcwd()
    res = os.path.join(current,relative_path)
    return res

def rmkdir(relative_path):
    path = rp2ap(relative_path)
    if not os.path.exists(path):
        os.mkdir(path)
        print(f"mkdir {path}")
        
def to_fname(s,ext=".png"):
    res = ""
    for c in s:
        if c.isalnum():
            res += c
        else:
            res += "_"
    res += ext
    return res

def build_path(*args,ext=".png"):
    """
    Build path of a new file waiting to be saved and create all the missing
    folder along the way 
    
    Parameters
    ----------
    *args : str
        folder, subfolder, and a string to be transform into a filename.
    ext : TYPE, optional
        the file extension. The default is ".png".

    Returns
    -------
    str
        return the full path with the filname, can be used to build the matplotlib figures filenames.

    """
    tmppath = os.getcwd()
    for arg in args[:-1]:
        print(arg)
        tmppath = os.path.join(tmppath,arg)
        if not os.path.exists(tmppath):
            os.mkdir(tmppath)
            print(f"mkdir {tmppath}")
    return f"{os.path.join(tmppath,to_fname(args[-1],ext=ext))}"
        

if __name__ == '__main__':
    # folder = "filter_save"
    # current = os.getcwd()
    # path = os.path.join(current,folder)
    # fname = file_selector(path)
    # print(fname)
    fname = build_path("root","sub","sub","fname",ext=".png")
    print(fname)
