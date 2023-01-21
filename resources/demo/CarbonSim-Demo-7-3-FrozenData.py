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
from carbon.helpers.pdread import *
from carbon.helpers.strategy import *
from carbon.helpers.fls import *
from carbon.helpers.simulation import run_sim, plot_sim

plt.style.use('seaborn-dark')
plt.rcParams['figure.figsize'] = [12,6]
require_version("2.3")
# -

# # Carbon Simulation - Demo 7-3 (frozen data)

# ## Setup

# ### Generated output
#
# If `OUTPATH` is `None`, output will not be saved, otherwise it will be saved to the indicated directory (use `"."` for current)

OUTPATH = "/Users/skl/Desktop/sim7-3"       # uncomment to save charts in specific location
OUTPATH = "."                               # uncomment to save charts in current directory
OUTPATH = None                              # uncomment to not save charts
if OUTPATH and OUTPATH != ".":
    # !mkdir {OUTPATH}
    # !rm {OUTPATH}/*.png
print(f"OUTPATH = {OUTPATH}")

# ### Path data
# filename determines collection, eg `RANPTH-05000-0000` is sig=50% vol and mu=0% drift; see available collections in the `ls` command below

# +
DATAID = "RANPTH-05000-0000"

DATAPATH = "../data"
DATAFN = j(DATAPATH, f"{DATAID}.pickle")
print(f"Chose data id {DATAID}")
# -

# !ls {DATAPATH}/*.pickle

# ### Strategies
#
# This is the list of strategies to be tested against the paths. The 

strats = (
    strategy.from_mwh(m=100, g=0.10, w=0.05, amt_rsk=1, amt_csh=0),
    strategy.from_mwh(m=100, g=0.20, w=0.05, amt_rsk=1, amt_csh=0),
    strategy.from_mwh(m=100, g=0.10, w=0.20, amt_rsk=1, amt_csh=0),
    strategy.from_mwh(m=100, g=0.20, w=0.20, amt_rsk=1, amt_csh=0),
)
#strats

# ## Simulation

for colnm in ["p0000", "p0001", "p0002"]:
    for ix, strat in enumerate(strats):
    
        path = pdread(DATAFN, colnm)
        simresults = run_sim(strat, path)
        plot_sim(strat, path, simresults, f"{DATAID} [{colnm}]")
        
        # save charts
        if isinstance(OUTPATH, str):
            plt.savefig(j(OUTPATH, f"{DATAID}-{colnm}-{ix}.png"))
        plt.show()


if OUTPATH:
    # !ls {OUTPATH}/*.png

if OUTPATH and OUTPATH != ".":
    filelist = os.listdir(OUTPATH)
    filelist = [fn for fn in filelist if fn[-4:]==".png"]
    markdown = "\n\n".join(f"![]({OUTPATH}/{fn})" for fn in filelist)
    fsave(markdown, "_sim-charts.md", OUTPATH)
    # !pandoc {OUTPATH}/_sim-charts.md -o {OUTPATH}/_sim-charts.docx


