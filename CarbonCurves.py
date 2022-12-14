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

from carbon import CarbonSimulatorUI, CarbonOrderUI, P, __version__, __date__
from math import sqrt
import numpy as np
from matplotlib import pyplot as plt
print(f"Carbon v{__version__} ({__date__})")
print("{0.__name__} v{0.__VERSION__} ({0.__DATE__})".format(CarbonOrderUI))

# # Carbon Curves

# ## The CarbonOrderUI object

# This curve `order1` is selling ETH for USDC, starting at 2000 USDC per ETH and ending at 3000. The curve has a capacity of 10 ETH (5 ETH for `order1b`), and it also is currently loaded with 10 ETH. The curve `order2` is selling USDC, starting at 1000 USDC per ETH and ending at 750. Capacity and loading is 20,000 USDC.

order1 = CarbonOrderUI.from_prices("ETH/USDC", "ETH", 2000, 3000, 10, 10)
order1b = CarbonOrderUI.from_prices("ETH/USDC", "ETH", 2000, 3000, 10, 5)
order2 = CarbonOrderUI.from_prices("ETH/USDC", "USDC", 1000, 750, 20000, 20000)

# ## Simple numeric properties

# The prices are retrievable under a number of names: `p_start` and `p_end` to indicate the beginning and the end of the range, `px` and `py` to indicate the axis intersect to which they corresponds, and `pa` and `pb` simply in alphabetical order. 

order1.p_start, order1.p_end, order1b.p_start, order1b.p_end, order2.p_start, order2.p_end

order1.py, order1.px, order1b.py, order1b.px, order2.py, order2.px

order1.pa, order1.pb, order1b.pa, order1b.pb, order2.pa, order2.pb

# The y-intercept `yint` correspond to the capacity of the curves, the y-value `y` to the current loading of the curve; those are expressed in `tkn`, also known as `tkny`. The x-intercept is the corresponding capacity in the other token `tknx`

order1.yint, order1b.yint, order2.yint

order1.y, order1b.y, order2.y

order1.tkny, order1b.tkny, order2.tkny

order1.xint, order1b.xint, order2.xint

order1.tknx, order1b.tknx, order2.tknx

# The ratio `yint/xint` or `yint/xint` equals `p0` which is also the geometric average of the prices of the range; `p0` is always extressed in the quuote conventions of the pair.

order1.p0, order1b.p0, order2.p0

sqrt(order1.px*order1.py), sqrt(order1b.px*order1b.py), sqrt(order2.px*order2.py)

order1.xint/order1.yint, order1b.xint/order1b.yint, order2.yint/order2.xint

# The current marginal price of the order is indicated by `p_marg`. If `y==yint` then `p_marg==p_start`, if `y==0` then `p_marg==p_end` and for `y` in between (as in `order1b`) it is in between.

order1.p_marg, order1b.p_marg, order2.p_marg

# ## Functions


ETHr = np.linspace(0,order1.yint)
ETHr2 = np.linspace(0,order1b.y)
USDCr = np.linspace(0,order2.yint)

# We first plot the invariant curves. We see that `order1` and `order1b` have the same curve, but `order2` is different, and the axis are reversed.

plt.plot([order1.xfromy_f(y) for y in ETHr], ETHr, label="order1 (y=10)", color="red")
plt.plot([order1b.xfromy_f(y) for y in ETHr], ETHr, label="order1b (y=5)", color="blue", linestyle="dotted")
plt.title("Full invariant curve")
plt.ylabel("y [ETH]")
plt.xlabel("x [USDC]")
plt.legend()

plt.plot([order2.xfromy_f(y) for y in USDCr], USDCr, label="order2 (y=20k)", color="lawngreen")
plt.title("Full invariant curve")
plt.ylabel("y [USDC]")
plt.xlabel("x [ETH]")
plt.legend()

# The _active_ curve is the part of the curve that is reachable, ie below the current value of `y`. Initially we have `y==yint` so the full curve is active. But as we see in `order1b`, if `y<yint` the active part of the curve is smaller than the full curve.

plt.plot([order1b.xfromy_f(y) for y in ETHr], ETHr, label="full curve", color="blue", linestyle="dotted")
plt.plot([order1b.xfromy_f(y) for y in ETHr2], ETHr2, label="active curve", color="blue")
plt.title("Active vs full invariant curve, order 1b")
plt.ylabel("y [ETH]")
plt.xlabel("x [USDC]")
plt.legend()

# Here we see the swap curves, ie the change in `x`, `dx` for a given change in `y`, `dy` (the chart should be read therefore in reverse: the dependent variable is on the x-axis). The first chart is for the orders selling `ETH` and we recall that the curve in `order1b` is not entirely filled, which is why it stops in the middle.

plt.plot([order1.dxfromdy_f(y, raiseonerror=False) for y in ETHr], -ETHr, label="order1 (y=10)", color="red")
plt.plot([order1b.dxfromdy_f(y, raiseonerror=False) for y in ETHr], -ETHr, label="order1b (y=5)", color="blue")
plt.title("Swap curve")
plt.ylabel("dy [ETH]")
plt.xlabel("dx [USDC]")
plt.legend()

plt.plot([order2.dxfromdy_f(y, raiseonerror=False) for y in USDCr], -USDCr, label="order2 (y=20k)", color="lawngreen")
plt.title("Swap curve")
plt.xlabel("dx [ETH]")
plt.ylabel("dy [USDC]")
plt.legend()

# In the below chart we show the marginal and effective prices for a given trade size. We have chosen `dx` as the independent variable here to keep the chart visually in line with the ones previously presented. The **marginal price** is the price (in USDC per ETH) at which the marginal unit of USDC is traded, ie _one dollar more_. The **effective price** is the average price of the entire trade, which corresponds to the average marginal price up to this point. Therefore, the effective prices curves are always flatter than the marginal price curves.
#
# The curves for selling ETH are upwards sloping, corresponding to the fact that the first units are sold for fewer dollars than the later ones. The ones for buying ETH are downwards sloping, because the first units are bought more expensively.

plt.plot(
    [order1.dxfromdy_f(dy, raiseonerror=False) for dy in ETHr], 
    [order1.p_marg_f(dy, raiseonerror=False) for dy in ETHr], 
    label="marg (1; y=10 ETH)", color="red", linestyle="solid")
plt.plot(
    [order1b.dxfromdy_f(dy, raiseonerror=False) for dy in ETHr], 
    [order1b.p_marg_f(dy, raiseonerror=False) for dy in ETHr], 
    label="marg (1b; y=5 ETH)", color="blue", linestyle="solid")
plt.plot(
    USDCr, 
    [order2.p_marg_f(dy, raiseonerror=False) for dy in USDCr], 
    label="marg(2; y=20k USDC)", color="lawngreen", linestyle="solid")
plt.plot(
    [order1.dxfromdy_f(dy, raiseonerror=False) for dy in ETHr], 
    [order1.p_eff_f(dy, raiseonerror=False) for dy in ETHr], 
    label="eff (1; y=10 ETH)", color="red", linestyle="dotted")
plt.plot(
    [order1b.dxfromdy_f(dy, raiseonerror=False) for dy in ETHr], 
    [order1b.p_eff_f(dy, raiseonerror=False) for dy in ETHr], 
    label="eff (1b; y=5 ETH)", color="blue", linestyle="dotted")
plt.plot(
    USDCr, 
    [order2.p_eff_f(dy, raiseonerror=False) for dy in USDCr], 
    label="eff (2; y=20k USDC)", color="lawngreen", linestyle="dotted")
plt.ylabel("Price [USDC per ETH]")
plt.xlabel("dx [USDC]")
plt.legend(loc="center right")

# ## Trading
#
# You can simulate trading (against a single curve) directly here. With `execute = False` the curve object itself is not changed. The command `selly` (when called with a positive `dy`) sells the y token of the curve. When called with a negative number, it buys this token. The outputs of this command are
#
#       'y_old': 10                             # the previous amount of liquidity on curve         
#       'y': 9                                  # ditto current
#       'dy': 1                                 # the liquidity change in token y (positive=SELL)
#       'yint_old': None                        # the old curve capacity
#       'y_int': 10                             # the current curve capacity
#       'expanded': False                       # whether the curve capacity has been expanded
#       'x': 2037.3867433374953                 # the implied virtual x liquidity on curve
#       'dx': 2037.3867433374958                # the liquidity change in token x (positive=BUY)
#       'tkny': 'ETH'                           # name of token y
#       'tknx': 'USDC'                          # name of token x
#       'tx': 'Sell 1 ETH buy USDC'             # the transaction as text
#       'dx/dy': 2037.3867433374958             # the ratio dx/dy (effective price)
#       'dy/dx': 0.0004908248290463863          # the ratio dy/dx (effective price; inverse quotattion)
#       'pmarg_old': 2000.0                     # the marginal price before the trade, in canonic quote direction
#       'pmarg': 2075.472370963683              # ditto after the trade
#       'p': 2037.3867433374958                 # the effective price of the trade, in canonic quote direction

order1.selly(1, execute = False)

order1.selly(2, execute = False)

order1.buyx(1000, execute = False)

order1.buyx(2000, execute = False)

# With `execute = True` (default), the order object is changed

order_ = CarbonOrderUI.from_order(order1)
print(f"y={10-1-2+1.5}")
order_.selly(1)
order_.selly(2)
order_.selly(-1.5)


# ## Order book calculations

# First we create a staggered list of 10 orders. Note that all those orders are only half-filled. The corresponding marginal prices are shown in the printout.

orders = [
    CarbonOrderUI.from_prices("ETH/USDC", "ETH", 2000+50*i, 2500+50*i, 10, 5)
    for i in range(10)
]
for o in orders:
    print(f"y={o.y} pa={round(o.pa,0)} pb={round(o.pb,0)}  pmarg={round(o.p_marg,1)}")
margp = [o.p_marg for o in orders]
min(margp), max(margp)

# We are now looking at the dy released if the market moves to 2100. Those are all 0, because all positions are already beyond 2100 (as we can see above, the lowest marginal prices is about 2229)

[o.dyfromp_f(2100) for o in orders]

# If markets go all the way to 3000 -- which is above the upper end of the highest range which is at 2950 -- we see that all positions release their 5 ETH.

[o.dyfromp_f(3000) for o in orders]

# For 2300 we see that only the first two positions contribute -- they release 1.39 and 0.40 ETH respectively. The current marginal price of the 3rd position is about 2330 which is already to high, and the other ones are even higher. If the market goes to 2500, the 1st position is fully used up, and the the next 4 position partially.

[round(o.dyfromp_f(2300),2) for o in orders]

# For 2500, the first 6 positions release ETH

[round(o.dyfromp_f(2500),2) for o in orders]

# We now define `dy_f` as the aggregate ETH released from all positions defined above, and we compute the corresponding USDC inflow `dx_f` from this. In case you are not familiar with the `lamba` syntax, this is simply a short form for saying that `dy_f(p)` and `dx_f(p)` are functions of p.  

dy_f = lambda p: sum(o.dyfromp_f(p) for o in orders)

dx_f = lambda p: sum(o.dxfromdy_f(o.dyfromp_f(p)) for o in orders)

# We can then plot the ETH release (first chart) and USDC inflow (second chart) as a function of marginal price of the AMM, keeping in mind that in reasonably liquid markets the marginal price of the AMM will correspond to the market price of ETH/USDC.

pvals = np.linspace(2000, 3000)
dyvals = [dy_f(p) for p in pvals]
dxvals = [dx_f(p) for p in pvals]

# The chart below looks at (ETH) outflows vs (USDC) inflows. Unsurprisingly it is monotonically increasing. It also looks mostly linear but this is an illusion as the prices change along the way as we can see in the marginal and effective price charts below.

plt.plot(dyvals, dxvals)
plt.title("Inflows vs outflows")
plt.ylabel("Aggregate USDC inflow")
plt.xlabel("Aggregate ETH release")

plt.plot(dyvals, pvals)
plt.title("Marginal price chart")
plt.ylabel("Marginal price (USDC per ETH)")
plt.xlabel("Aggregate ETH release")

plt.plot(dyvals, [dx/dy if dy>0 else None for dx,dy in zip(dxvals, dyvals)])
plt.title("Effective price chart")
plt.xlabel("Aggregate ETH release")
plt.ylabel("Effective price (USDC per ETH)")

plt.plot(pvals, dyvals)
plt.title("Price reaction chart")
plt.xlabel("Marginal price (USDC per ETH)")
plt.ylabel("Aggregate ETH release")

plt.plot(pvals, dxvals)
plt.title("USDC inflow vs market price")
plt.xlabel("Marginal price (USDC per ETH)")
plt.ylabel("Aggregate USDC inflow")

plt.plot(pvals, [dx/dy if dy>0 else None for dx,dy in zip(dxvals, dyvals)])
plt.xlabel("Marginal price (USDC per ETH)")
plt.ylabel("Effective price (USDC per ETH)")




