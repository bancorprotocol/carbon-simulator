from .fls import fload, fsave
from .params import Params
from .pdread import pdread, pathtime, pathtime_yrs, pathtime_days, pdcols, j
from .sharedvar import SharedVar
from .strategy import strategy
from .version import require_version
from .helpers import listdir
#from .simulation import run_sim, plot_sim

from .. import (
    CarbonSimulatorUI as _CarbonSimulatorUI, 
    CarbonOrderUI as _CarbonOrderUI, 
    __version__, 
    __date__,
)

def print_version(require=None, all=True):
    """
    prints Carbon version numbers; calls require_version(require) if not require is None
    """
    print(f"Carbon v{__version__} ({__date__})")
    if all:
        print( "{0.__name__} v{0.__VERSION__} ({0.__DATE__})".format(_CarbonSimulatorUI))
        print( "{0.__name__} v{0.__VERSION__} ({0.__DATE__})".format(_CarbonOrderUI))

    if not require is None:
        require_version(require)



