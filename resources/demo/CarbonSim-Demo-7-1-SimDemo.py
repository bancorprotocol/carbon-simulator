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
from math import sqrt, exp, log
import numpy as np
from matplotlib import pyplot as plt
plt.style.use('seaborn-dark')
plt.rcParams['figure.figsize'] = [8,4]
print(f"Carbon v{__version__} ({__date__})")
print("{0.__name__} v{0.__VERSION__} ({0.__DATE__})".format(CarbonSimulatorUI))
print("{0.__name__} v{0.__VERSION__} ({0.__DATE__})".format(CarbonOrderUI))

# # Carbon Simulation - Demo 7-1 (Sim Demo)

# ## Setup

# +
# HTML("""
# <style>
# #notebook-container {background-color: #abc}
# </style>
# """)

# +
# style_list = ['default', 'classic'] + sorted(
#     style for style in plt.style.available
#     if style != 'classic' and not style.startswith('_'))
# style_list
# -

# #### Define parameters

# +
# spot process
pair = "ETH/USDC"
vol = 0.5
time = 1
mu = 0
steps = 100

# range
spot0      = 1500
w0         = 0.05
w1         = 2*w0
amt_usdc   = 1000
amt_eth    = 1
# -

# derived numbers
p_buy_a = spot0*(1-w0)
p_buy_b = spot0*(1-w0)*(1-w1)
p_sell_a = spot0*(1+w0)
p_sell_b = spot0*(1+w0)*(1+w1)
print(f"ETH -- BID {p_buy_b:.1f}-{p_buy_a:.1f}, SPOT {spot0:.1f}, ASK {p_sell_a:.1f}-{p_sell_b:.1f}")

# ### Calculate derived parameters and set up objects

dt = time/steps
time_r = np.array([i*dt for i in range(steps+1)])
sqrt_dt = sqrt(dt)
mudt = mu*dt
vol_sqrt_dt = vol*sqrt_dt
half_sig2_dt = 0.5*vol*vol*dt
print(sqrt_dt, mudt, vol_sqrt_dt)

Sim = CarbonSimulatorUI(pair="ETH/USDC")
Sim.add_strategy("ETH", amt_eth, p_sell_a, p_sell_b, amt_usdc, p_buy_a, p_buy_b)
Sim.state()["orders"]

# ### Generate path

rng = np.random.default_rng()
increments = rng.lognormal(mean=mudt-half_sig2_dt, sigma=vol_sqrt_dt, size=steps)
#multipliers = np.insert(np.cumprod(increments), 0, 1) 
#path = spot0 * multipliers
path = np.cumprod(np.insert(increments, 0, spot0))
plt.plot(time_r, path)
plt.fill_between(time_r, p_buy_a, p_buy_b, color="green", alpha=0.1)
plt.fill_between(time_r, p_sell_a, p_sell_b, color="red", alpha=0.1)
plt.grid()
print(f"buy ETH {p_buy_a:.1f}-{p_buy_b:.1f}, sell ETH {p_sell_a:.1f}-{p_sell_b:.1f}")

# ## Simulation using `dyfromp_f`

# +
Sim = CarbonSimulatorUI(pair="ETH/USDC", verbose=False)
Sim.add_strategy("ETH", amt_eth, p_sell_a, p_sell_b, amt_usdc, p_buy_a, p_buy_b)
print(f"buy ETH {p_buy_a:.1f}-{p_buy_b:.1f}, sell ETH {p_sell_a:.1f}-{p_sell_b:.1f}")
print("-"*20)
printdots = True
#Sim.state()["orders"]
for t, spot, ix in zip(time_r, path, range(len(path))):
    
    orderuis = Sim.state()["orderuis"]
    orders_sell_eth = {k:v for k,v in orderuis.items() if v.tkn=="ETH"}
    dy_f_sell_eth = lambda p: sum(o.dyfromp_f(p) for o in orders_sell_eth.values())
    sell_eth  = dy_f_sell_eth(spot)
    
    orders_sell_usdc = {k:v for k,v in orderuis.items() if v.tkn=="USDC"}
    dy_f_sell_usdc = lambda p: sum(o.dyfromp_f(p) for o in orders_sell_usdc.values())
    sell_usdc = dy_f_sell_usdc(spot)
    
    if sell_eth > 0.0001:
        r = Sim.amm_sells("ETH", sell_eth, support_partial=True)
        failed = "" if r['success'] else "FAILED"
        print(f"ix={ix:4.0f}, spot={spot:0.1f}: sell {sell_eth:10.2f} ETH {failed}")
        printdots = True
    elif sell_usdc > 0.001:
        r = Sim.amm_sells("USDC", sell_usdc, support_partial=True)
        failed = "" if r['success'] else "FAILED"
        print(f"ix={ix:4.0f}, spot={spot:0.1f}: sell {sell_usdc:10.2f} USDC {failed}")
        printdots = True
    else:
        if printdots:
            print("...")
        printdots = False
        #print(f"ix={ix:4.0f}, spot={spot:0.1f}: ---")

o = Sim.state()["orders"]
#print(f"ix={ix:4.0f}, spot={spot:0.1f}: -- sim  finished --")
amt_eth_final = abs(float(o.query("tkn=='ETH'")["y"]))
amt_usdc_final = abs(float(o.query("tkn=='USDC'")["y"]))
print("-"*20)
print(f"ix={0:4.0f},  spot={path[0]:6.1f}: {amt_eth:.1f} ETH {amt_usdc:8.2f} USDC (={amt_eth*path[0]+amt_usdc:8.1f} USDC)")
print(f"ix={ix:4.0f},  spot={spot:6.1f}: {amt_eth_final:.1f} ETH {amt_usdc_final:8.2f} USDC (={amt_eth_final*spot+amt_usdc_final:8.1f} USDC)")
pass
# -
# ## Simulation using `tradeto`

# +
Sim = CarbonSimulatorUI(pair="ETH/USDC", verbose=False)
Sim.add_strategy("ETH", amt_eth, p_sell_a, p_sell_b, amt_usdc, p_buy_a, p_buy_b)
ouis = Sim.state()["orderuis"]
assert ouis[0].tkn == "ETH"
assert ouis[1].tkn == "USDC"
ethamt_r  = [ouis[0].y]
usdcamt_r = [ouis[1].y]
print(f"buy ETH {p_buy_a:.1f}-{p_buy_b:.1f}, sell ETH {p_sell_a:.1f}-{p_sell_b:.1f}")
print("-"*20)

for spot in path[1:]:
    for oui in ouis.values():
        oui.tradeto(spot)
    ethamt_r  += [ouis[0].y]
    usdcamt_r += [ouis[1].y]

amt_eth_final  = ethamt_r[-1]
amt_usdc_final = usdcamt_r[-1]
#print("-"*20)
print(f"ix={0:4.0f},  spot={path[0]:6.1f}: {amt_eth:.1f} ETH {amt_usdc:8.2f} USDC (={amt_eth*path[0]+amt_usdc:8.1f} USDC)")
print(f"ix={ix:4.0f},  spot={spot:6.1f}: {amt_eth_final:.1f} ETH {amt_usdc_final:8.2f} USDC (={amt_eth_final*spot+amt_usdc_final:8.1f} USDC)")
pass
# -

#plt.scatter(x=ethamt_r, y=usdcamt_r)
print(f"t={0:3.1f}: {ethamt_r[0]:4.1f} ETH {usdcamt_r[0]:6.0f} USDC (value {ethamt_r[0]*path[0]+usdcamt_r[0]:6.1f} USDC)")
print(f"t={1:3.1f}: {ethamt_r[-1]:4.1f} ETH {usdcamt_r[-1]:6.0f} USDC (value {ethamt_r[-1]*path[-1]+usdcamt_r[-1]:6.1f} USDC)")
plt.plot(ethamt_r, usdcamt_r, "-o")
plt.xlabel("ETH")
plt.ylabel("USDC")
plt.grid()

value_r = ethamt_r * path + usdcamt_r
fig, ax1 = plt.subplots()
ax2 = ax1.twinx()
ax1.plot(time_r, path, color="lightgrey")
ax1.fill_between(time_r, p_buy_a, p_buy_b, color="lightgreen", alpha=0.1)
ax1.fill_between(time_r, p_sell_a, p_sell_b, color="lightcoral", alpha=0.1)
ax2.plot(time_r, value_r)
plt.xlabel("time")
ax2.set_ylabel("portfolio value [USDC]")
ax1.set_ylabel("ETH price [USDC]")
print(f"t={1:3.1f}: {ethamt_r[-1]:4.1f} ETH {usdcamt_r[-1]:6.0f} USDC (value {ethamt_r[-1]*path[-1]+usdcamt_r[-1]:6.1f} USDC)")
pass


