"""
Carbon helper module - read time series from data frame
"""
__VERSION__ = "1.0"
__DATE__ = "23/01/2023"

import pandas as _pd

# those imports are for re-export
from os.path import join as j
import os

def dfread(fn):
    """reads dataframe from file and asserts format"""
    
    if fn[-7:] == ".pickle":
        df = _pd.read_pickle(fn)
    else:
        df = _pd.read_csv(fn)
    assert df.columns[0] == "time"
    assert df.columns[1] == "datetime"
    return df
    
def pdread(fn, datacol=None, indexcol=None, from_ts=None, from_pc=None, period_days=None, period_pc=None):
    """
    reads a dataframe and returns a single column with index
    
    :fn:            the (full) filename
    :datacol:       name or index of the data col; None returns frame
    :indexcol:      name of the index col (default: "datetime")
    :from_ts:       the start of the observation period, in a formate that can be converted
                    by pd.Timestamp(from_ts); default is beginning of series
    :from_pc:       alternative to from_ts; sets the start date as perc of full time
    :period_days:   the observation period in days (inclusive); default end of series
    :period_pc:     alternative to period_days; sets period as perc of full time
    :returns:       pandas series (or data frame if indexcol is None)
    """
    if indexcol is None: indexcol = "datetime"

    df = dfread(fn)
    df = df.set_index(indexcol)
    
    if not period_days is None and not period_pc is None:
        raise ValueError("Not both period_days and period_pc can not-None")
    if not period_pc is None:
        period_days = period_pc * (df.index[-1]-df.index[0])/_pd.Timedelta(days=1)
        #print("[pdread]", period_days)

    if not from_ts is None and not from_pc is None:
        raise ValueError("Not both from_ts and from_pc can not-None")
    if not from_pc is None:
        from_ts = df.index[0] + from_pc * (df.index[-1]-df.index[0])

    if not from_ts is None or not period_days is None:
        if from_ts is None:
            from_ts = df.index[0]
        else:
            from_ts = _pd.Timestamp(from_ts)
            if from_ts < df.index[0]:
                from_ts = df.index[0]
        if period_days is None:
            to_ts = df.index[-1]
        else:
            to_ts = from_ts + period_days * _pd.Timedelta(days=1)
        to_ts   = _pd.Timestamp(to_ts)
    else:
        from_ts = df.index[0]
        to_ts = df.index[-1]
    
    #print("[pdread]", from_ts, to_ts)
    df = df[(df.index >= from_ts) & (df.index <= to_ts)]
    
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
    """
    DEPRECATED returns the time (in years) covered by the series `path`
    
    use pathtime_yrs
    """
    return (path.index[-1]-path.index[0])/_pd.Timedelta(days=1)/365.25

def pathtime_yrs(path):
    """
    returns the time (in years) covered by the series `path`

    NOTE: conversion factor is 365.25
    """
    return pathtime_days(path)/365.25

def pathtime_days(path):
    """
    returns the time (in days) covered by the series `path`
    """
    return (path.index[-1]-path.index[0])/_pd.Timedelta(days=1)