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

from carbon.helpers import PathGenerator
from carbon.helpers.pdread import *
from math import sin, cos, pi
import os
from math import sqrt, exp, log
from datetime import timedelta as _timedelta, datetime as _datetime
import numpy as np
import pandas as pd
from matplotlib import pyplot as plt
plt.style.use('seaborn-dark')
plt.rcParams['figure.figsize'] = [8,4]

# # Generate Data
# ## Generate big random path samples

FILENAME = lambda sig, mu: f"RAN-{int(sig*100):05d}-{int(mu*100):04d}-NEW"
FILENAME(sig=0.2, mu=0)

FILENAME = None    # comment out to generate paths

if not FILENAME is None:
    print("Generating paths")
    for sig in (0.05, 0.1, 0.2, 0.5, 0.75, 1):
        df = PathGenerator(sig=sig).pathdf(1000)
        df.to_csv(FILENAME(sig=sig, mu=0)+".csv.gz", index=False, compression="gzip")
        #df.to_csv(FILENAME(sig=sig, mu=0)+".csv", index=False)
        df.to_pickle(FILENAME(sig=sig, mu=0)+".pickle")
else:
    print("Not generating paths")

# !ls *.pickle

# !ls *.csv.gz

# !ls *.csv

# ## Generate single random path repo

FILENAME2 = lambda mu: f"RAN-SIGMU"
FILENAME2 = None

dfs = {
    (sig,mu): PathGenerator(sig=sig, mu=mu).pathdf(10)
    for mu in [0,0.05,0.2]
    for sig in (0.01, 0.05, 0.25, 0.5, 0.75, 1)
}
df_aggr = pd.concat(dfs.values(), axis=1)
#df.to_csv(FILENAME(sig=sig, mu=0)+".csv.gz", index=False, compression="gzip")
#df.to_csv(FILENAME(sig=sig, mu=0)+".csv", index=False)
if not FILENAME2 is None:
    df_aggr.to_pickle(FILENAME2()+".pickle")
df_aggr

[ df_aggr.columns[i*10] for i in range(6) ]

[ df_aggr.columns[i*10+60] for i in range(6) ]

[ df_aggr.columns[i*10+61] for i in range(6) ]

# !ls

# +
# #!rm RAN-AGGR.pickle

# +
# fns = [fn for fn in os.listdir() if fn[:3]=="RAN"]
# fns = ['RAN-005-00.pickle',
#  'RAN-010-00.pickle',
#  'RAN-100-00.pickle',
#  'RAN-075-00.pickle',
#  'RAN-020-00.pickle',
#  'RAN-050-00.pickle']
# # for fn in fns:
# #     df = pd.read_pickle(fn)
# #     del df["time"]
# #     df = df.set_index("datetime")
# #     df.to_pickle(fn)
# pd.read_pickle(fns[2])
# -

# ## Generate Sin, Cos paths

PathGenerator.DEFAULTS

# +
start_dt=pd.Timestamp("2020-01-01")
end_dt=pd.Timestamp("2021-01-01")
nsteps = 200
delt = (end_dt-start_dt)/nsteps
x = lambda n: 2*pi*n/nsteps
t = lambda n: start_dt + delt*n
p = lambda i, f: 75+50*cos((f+1)*x(i))
assert x(nsteps) == 2*pi
assert t(nsteps) == end_dt


ix = 10
time = np.array([t(i) for i in range(nsteps+1)])

dfs = [
    pd.DataFrame(
        np.array([p(i,ix) for i in range(nsteps+1)]), 
        index=time, 
        columns=[f"p-a-{ix:02d}"]
    )
for ix in range(10)
]
df_aggr = pd.concat(dfs, axis=1)
df_aggr.to_pickle("COS.pickle")
plt.plot(dfs[0])
# -

p(100,5)

# !ls

# ## Data retrieval examples

fn = "COS.pickle"

pdcols(fn)

ser=pdread(fn, "p-a-01")
ser

plt.plot(ser)

ser = pdread(fn, 0)
ser

ser.index[0]

pd.Timedelta(days=1)


