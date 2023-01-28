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

