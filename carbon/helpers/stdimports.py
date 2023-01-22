"""
Carbon helper module - standard Carbon imports for sims

USAGE

    from carbon.helper.stdimports import *

This will print version numbers of key Carbon modules
"""
from math import sqrt, exp, log
import numpy as np
import pandas as pd
from matplotlib import pyplot as plt

from .. import CarbonSimulatorUI, CarbonOrderUI, analytics as cal, P, __version__, __date__
from .version import require_version

def print_version(require=None):
    print(f"Carbon v{__version__} ({__date__})")
    print( "{0.__name__} v{0.__VERSION__} ({0.__DATE__})".format(CarbonSimulatorUI))
    print( "{0.__name__} v{0.__VERSION__} ({0.__DATE__})".format(CarbonOrderUI))

    if not require is None:
        require_version(require)
