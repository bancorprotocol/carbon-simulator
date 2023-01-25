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

def print_version(require=None, all=True):
    """
    prints Carbon version numbers; calls require_version(require) if not require is None
    """
    print(f"Carbon v{__version__} ({__date__})")
    if all:
        print( "{0.__name__} v{0.__VERSION__} ({0.__DATE__})".format(CarbonSimulatorUI))
        print( "{0.__name__} v{0.__VERSION__} ({0.__DATE__})".format(CarbonOrderUI))

    if not require is None:
        require_version(require)

def plt_style(style, alt_style):
    """
    calls plt.style.use(style) and as fallback alt_style, all wrapped in try blocks
    """
    try:
        plt.style.use(style)
    except:
        try:
            plt.style.use(alt_style)
        except:
            print("[plt_style] both styles failed", style, alt_style)