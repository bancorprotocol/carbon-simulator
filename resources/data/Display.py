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
from carbon.helpers.pdread import *
plt.style.use('seaborn-dark')
plt.rcParams['figure.figsize'] = [8,4]

# # Create Path Charts and Display

fn = "RAN-050-00.pickle"
fn0 = fn.split(".")[0]

# !ls *.pickle

# ## Setup

OUTPATH = "charts"
OUTPATH = None
if OUTPATH:
    pass
    # !rm {OUTPATH}/*.png

# !ls charts

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


