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

from carbon import CarbonSimulatorUI, CarbonOrderUI, P, __version__, __date__

print(f"[stdimports] Carbon v{__version__} ({__date__})")
print( "[stdimports] {0.__name__} v{0.__VERSION__} ({0.__DATE__})".format(CarbonSimulatorUI))
print( "[stdimports] {0.__name__} v{0.__VERSION__} ({0.__DATE__})".format(CarbonOrderUI))
