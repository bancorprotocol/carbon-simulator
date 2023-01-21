# -*- coding: utf-8 -*-
# ---
# jupyter:
#   jupytext:
#     formats: ipynb,py:light
#     text_representation:
#       extension: .py
#       format_name: light
#       format_version: '1.5'
#       jupytext_version: 1.13.1
#   kernelspec:
#     display_name: Python 3
#     language: python
#     name: python3
# ---

from math import sqrt, exp, log
from datetime import timedelta as _timedelta, datetime as _datetime
import numpy as np
import pandas as pd
from matplotlib import pyplot as plt
from os.path import join as j
import os
plt.style.use('seaborn-dark')
plt.rcParams['figure.figsize'] = [8,4]

# # Create Path Charts and Display

fn = "RANPTH-05000-0000.pickle"
fn0 = fn.split(".")[0]

# !ls *.pickle

# ## Setup

OUTPATH = "charts"
OUTPATH = None
if OUTPATH:
    pass
    # !rm {OUTPATH}/*.png


# !ls charts

# ## Code

# ### Data retrieval code

# +
def dfread(fn):
    """reads dataframe from file and asserts format"""
    
    if fn[-7:] == ".pickle":
        df = pd.read_pickle(fn)
    else:
        df = pd.read_csv(fn)
    assert df.columns[0] == "time"
    assert df.columns[1] == "datetime"
    return df
    
def pdread(fn, datacol=None, indexcol=None):
    """
    reads a dataframe and returns a single column with index
    
    :fn:        the (full) filename
    :datacol:   name or index of the data col; None returns frame
    :indexcol:  name of the index col (default: "datetime")
    :returns:   pandas series
    """
    if indexcol is None: indexcol = "datetime"

    df = dfread(fn)
    df = df.set_index(indexcol)
    if datacol is None:
        return df.iloc[:, 1:]
    elif isinstance(datacol, str):
        return df[datacol]
    elif isinstance(datacol, int):
        return df.iloc[:, datacol+1]
    else:
        raise ValueError("datacol must be None, str or int", datacol)

def pdcols(fn):
    """
    reads a dataframe and returns a single column with index
    
    :fn:        the (full) filename
    :returns:   the column names (excluding the first two)
    """
    return dfread(fn).columns[2:]

def pathtime(path):
    """returns the time (in years) covered by the series `path`"""
    (path.index[-1]-path.index[0])/pd.Timedelta(days=1)/365.25


# -

# ## Plot data

cols = pdcols(fn)

for col in cols[:100] if OUTPATH else cols[:10]:
    ser = pdread(fn, col)
    plt.title(f"{fn0} [{col}]")
    plt.plot(ser)
    plt.xlabel("date")
    plt.ylabel("spot price")
    plt.grid()
    if OUTPATH:
        savefn = f"{fn0}-{col}.png"
        print(f"saving as {savefn}")
        plt.savefig(j(OUTPATH, savefn))
    plt.show()
    

if OUTPATH:
    # !ls {OUTPATH}/*.png

if OUTPATH:
    from fls import fsave
    filelist = os.listdir(OUTPATH)
    filelist = [fn for fn in filelist if fn[-4:]==".png"]
    markdown = "\n\n".join(f"![]({OUTPATH}/{fn})" for fn in filelist)
    fsave(markdown, "_charts.md", OUTPATH)
    # !pandoc {OUTPATH}/_charts.md -o {OUTPATH}/_charts.docx


