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

# +
from carbon.helpers.stdimports import *
from carbon.helpers import j, strategy, pdread, pdcols, fsave, listdir, Params
from carbon.helpers.widgets import CheckboxManager, DropdownManager, PcSliderManager
from carbon.helpers.simulation import run_sim, plot_sim, SIM_DEFAULT_PARAMS

plt.rcParams['figure.figsize'] = [12,6]
plt_style('seaborn-v0_8-dark', 'seaborn-dark')
print_version(require="2.2.5")
# -

# # Carbon Simulation - Demo 7-3

# _[frozen_20230128][frozen]: **this** notebook on [Binder][frozen_nb] and on [github][frozen_gh];  **latest** notebook on [Binder][latest_nb] and on [github][latest_gh]_
#
# Use **Run -- Run All Cells** in the menu above to run the notebook, then adjust the simulation parameters as desired. Further resources are (1) the github repo [github:carbon-simulator-binder][repob] associated with this binder, (2) the main simulator repo [github:carbon-simulator][repo], (3) the carbon package [pypi:carbon-simulator][simpypi] and finally (4) the ["Carbon Simulator" presentation][presn]
#
# [presn]:https://github.com/bancorprotocol/carbon-simulator/blob/beta/resources/notes/202301%20Simulating%20Carbon.pdf
# [simpypi]:https://pypi.org/project/carbon-simulator/
# [repo]:https://github.com/bancorprotocol/carbon-simulator
# [repob]:https://github.com/bancorprotocol/carbon-simulator-binder
# [frozen]:https://mybinder.org/v2/gh/bancorprotocol/carbon-simulator-binder/frozen_20230128
# [frozen_nb]:https://mybinder.org/v2/gh/bancorprotocol/carbon-simulator-binder/frozen_20230128?labpath=Frozen%2FDemo7-3%2FDemo7-3.ipynb
# [frozen_gh]:https://github.com/bancorprotocol/carbon-simulator-binder/blob/frozen_20230128/Frozen/Demo7-3/Demo7-3.ipynb
# [latest_nb]:https://mybinder.org/v2/gh/bancorprotocol/carbon-simulator-binder/latest_7_3?labpath=Frozen%2FDemo7-3%2FDemo7-3.ipynb
# [latest_gh]:https://github.com/bancorprotocol/carbon-simulator-binder/blob/latest_7_3/Frozen/Demo7-3/Demo7-3.ipynb

# ## Setup

import datetime 
fname = lambda data, col, strat: f"{datetime.datetime.now().strftime('%m%d-%H%M%S')}-{data}-{col.replace('/', '')}-{strat}.png"

# ### Generated output

OUTPATH = "."                               # where to save generated charts (None to not save)
DELETE_BEFORE_SIM = True                    # if True, delete all output files before running a new Sim
print(f"OUTPATH = {OUTPATH}")

# ### Path data

# +
DATAID = "COINS-CROSS"

DATAPATH = "../data"
DATAFN = j(DATAPATH, f"{DATAID}.pickle")
print(f"DATAID = {DATAID}")
# -

# !ls {DATAPATH}/*.pickle

", ".join(pdcols(DATAFN))

COLS_INVERT = {
    "ETH/LTC"   : False,
    "ETH/OKB"   : False, 
    "DOT/MATIC" : False, 
    "BNB/AVAX"  : False
}
print(f"COLS_INVERT = {COLS_INVERT}")

# ### Simulation parameters

SIM_PARAMS = {
    'plotPrice': True,
    'plotValueCsh': False,
    'plotValueRsk': False,
    'plotValueTotal': True,
    'plotValueHODL': True,
    'plotRanges': True,
    'plotMargP': True,
    'plotBid': True,
    'plotAsk': True
}
print(f"SIM_PARAMS = {SIM_PARAMS}")

# ### Strategies 

STRATS = {
     "single":     strategy.from_mgw(m=100, g=0.01, w=0.02, amt_rsk=1, amt_csh=0),
     "multiple":   [strategy.from_mgw(m=100, g=0.25, w=0.05, amt_rsk=1, amt_csh=0),
                   strategy.from_mgw(m=100, g=0.10, w=0.03, amt_rsk=1, amt_csh=0)],  
     "univ3":      strategy.from_u3(p_lo=100, p_hi=150, start_below=True, fee_pc=0.05, tvl_csh=1000),
}
print(f"STRATS ids = {tuple(STRATS)}")

STARTPC = 0
LENPC = 1
PATH_MIN_DATE = "2022-01-01"

# ## Simulation

if DELETE_BEFORE_SIM:
    # !rm {OUTPATH}/*.png
    # !rm {OUTPATH}/_CHARTS.*

for colnm, invert in COLS_INVERT.items():
    path, pair = pdread(DATAFN, colnm, from_pc=STARTPC, period_pc=LENPC, min_dt=PATH_MIN_DATE, invert=invert, tkns=True)
    for stratid, strat in STRATS.items():
        simresults = run_sim(strat, path, shift=0)
        plot_sim(simresults, simresults, f"{DATAID}:{colnm}", Params(**SIM_PARAMS), pair=pair)
        if isinstance(OUTPATH, str):
            plt.savefig(j(OUTPATH, fname(DATAID, colnm, stratid)))
        plt.show()


if OUTPATH and False:
    print("Listing OUTPATH [uncheck box at top to disable]")
    print ("\n".join([fn[:-4] for fn in os.listdir(OUTPATH) if fn[-4:]==".png"]))

if OUTPATH:
    print("Creating consolidated docx and zip from charts [uncheck box at top to disable]")
    markdown = "\n\n".join(f"![]({OUTPATH}/{fn})" for fn in [fn for fn in os.listdir(OUTPATH) if fn[-4:]==".png"])
    fsave(markdown, "_CHARTS.md", OUTPATH, quiet=True)
    # !pandoc {OUTPATH}/_CHARTS.md -o {OUTPATH}/_CHARTS.docx
    # !zip _CHARTS.zip -qq *.png 


