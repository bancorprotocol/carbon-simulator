"""
Carbon helper module - standard Carbon imports for sims

USAGE

    from carbon.helper.stdimports import *

This will print version numbers of key Carbon modules
"""
__VERSION__ = "1.1"
__DATE__ = "25/01/2023"

from math import sqrt, exp, log
import numpy as np
import pandas as pd
from matplotlib import pyplot as plt
import os

print("[stdimports] imported np, pd, plt, os, sqrt, exp, log")

from .. import CarbonSimulatorUI, CarbonOrderUI, analytics as cal, P, __version__, __date__
from .version import require_version
from . import print_version, plt_style

def iseq(arg0, *args, eps=1e-6):
    """checks whether all arguments are equal to arg0, within tolerance eps if numeric"""
    if not args:
        raise ValueError("Must provide at least one arg", args)
    try:
        arg0+1
        isnumeric = True
    except:
        isnumeric = False
    #if isinstance(arg0, int) or isinstance(arg0, float):
    if isnumeric:
        # numeric testing
        if arg0 == 0:
            for arg in args:
                if abs(arg) > eps: 
                    return False
                return True
        for arg in args:
            if abs(arg/arg0-1) > eps:
                return False
            return True
    else:
        for arg in args:
            if not arg == arg0:
                return False
        return True

def raises(func, *args, **kwargs):
    """
    returns exception message if func(*args, **kwargs) raises, else False

    USAGE

        assert raises(func, 1, 3, three=3), "func(1, 2, three=3) should raise"
    """
    try:
        func(*args, **kwargs)
        return False
    except Exception as e:
        return str(e)