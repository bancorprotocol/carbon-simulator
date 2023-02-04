# -*- coding: utf-8 -*-
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

from math import *
import numpy as np
from matplotlib import pyplot as plt
# plt.rcParams['figure.figsize'] = [12,6]
# plt.style.use('seaborn-dark')

# # Carbon price resolution

# ## Theory

# In carbon we specify prices $P$ using the parameter $B$ with
#
# $$
# B = \sqrt{P}
# $$
#
# $B$ is stored as a 64-bit integer, divided by $2^{32}$, which is $4.3$bn or $10^{10}$

2**32, log10(2**32)

# We are ultimately interested in the precision $\Delta P/P$. We start with
#
# $$
# \Delta B = 2^{-32} \simeq 10^{-10}
# $$
#
# and therefore 
#
# $$
# \frac{\Delta B}B = \frac{2^{-32}}B \simeq \frac{10^{-10}}B
# $$
#
# Moreover easy calculation using $\Delta P= (B+\Delta B)^2-B^2$ yields
#
# $$
# \frac{\Delta P}P = \frac{2\cdot 2^{-32}}{\sqrt P} \simeq \frac{2\cdot 10^{-10}}{\sqrt P}
# $$

# ## Charts

# + tags=[]
p_r = np.array([10**x for x in np.linspace(-25,10,100)])
delp_p_r =  np.array([2**-31/sqrt(p) for p in p_r])
# -

gs, ys, rs, e = 10**(-15), 10**(-4), 10**(-2), 10**15
plt.plot(p_r, delp_p_r)
plt.fill_between(p_r, rs, e, color="red", alpha=0.1)
plt.fill_between(p_r, ys, rs, color="yellow", alpha=0.1)
plt.fill_between(p_r, gs, ys, color="green", alpha=0.1)
plt.xscale("log")
plt.xlabel("price [log scale, adjusted for decimality]")
plt.yscale("log")
plt.ylabel("precision Delta P / P [log scale]")
plt.title("precision plot using decimality adjusted prices")
plt.ylim(10**(-14), 10**3)
plt.grid()

# + tags=[]
p_r2 = np.array([10**x for x in np.linspace(-5,5,100)])
delp_p_18_r =  np.array([2**-31/sqrt(p*10**(-18+6)) for p in p_r])
delp_p_24_r =  np.array([2**-31/sqrt(p*10**(-24+6)) for p in p_r])
# -

gs, ys, rs, e = 10**(-12), 10**(-4), 10**(-2), 10**10
plt.plot(p_r2, delp_p_18_r, label="18 vs 6 decimals")
plt.plot(p_r2, delp_p_24_r, label="24 vs 6 decimals")
plt.fill_between(p_r2, rs, e, color="red", alpha=0.1)
plt.fill_between(p_r2, ys, rs, color="yellow", alpha=0.1)
plt.fill_between(p_r2, gs, ys, color="green", alpha=0.1)
plt.xscale("log")
plt.xlabel("raw price [log scale]")
plt.yscale("log")
plt.ylabel("precision Delta P / P [log scale]")
plt.title("precision plot using raw prices")
plt.ylim(10**(-9), 10**9)
plt.legend()
plt.grid()
plt.savefig("precision.png")

# ## Tables

# ### First prices

dhi, dlo, bminexp = 18, 6, 32
bmin =  2**(-bminexp)
first_prices = [(i, (bmin*i)**2 * 10**(dhi-dlo)) for i in range(1,100)]
increments = [(b[0],b[1]/a[1]-1) for a,b in tuple(zip(first_prices, first_prices[1:]))]
print(f"  First prices at {dhi} vs {dlo} dec [diff {dhi-dlo}]")
print("-----------------------------------------")
print("  #       Price         (log)   %Chg next")
print("-----------------------------------------")
for p,i in tuple(zip(first_prices, increments))[:25]:
    print(f"{p[0]:3}:  {p[1]:14.10f}    ({abs(log10(p[1])):2.1f})     {i[1]*100:5.1f}%")

dhi, dlo, bminexp = 24, 6, 32
bmin =  2**(-bminexp)
first_prices = [(i, (bmin*i)**2 * 10**(dhi-dlo)) for i in range(1,100)]
increments = [(b[0],b[1]/a[1]-1) for a,b in tuple(zip(first_prices, first_prices[1:]))]
print(f"  First prices at {dhi} vs {dlo} dec [diff {dhi-dlo}]")
print("-----------------------------------------")
print("  #       Price         (log)   %Chg next")
print("-----------------------------------------")
for p,i in tuple(zip(first_prices, increments))[:25]:
    print(f"{p[0]:3}:  {p[1]:14.10f}    ({abs(log10(p[1])):2.1f})     {i[1]*100:5.1f}%")

# ### Last prices

dhi, dlo = 18,6
first_prices = [(i, (2**32-bmin*i)**2 * 10**(dhi-dlo)) for i in range(1,100)]
increments = [(b[0],b[1]/a[1]-1) for a,b in tuple(zip(first_prices, first_prices[1:]))]
print(f"  Last prices at {dhi} vs {dlo} dec [diff {dhi-dlo}]")
print("-----------------------------------------")
print("  #    Price     (log)     %Chg next")
print("-----------------------------------------")
for p,i in tuple(zip(first_prices, increments))[:25]:
    print(f"{p[0]:3}:  {p[1]:6.1e}    ({abs(log10(p[1])):2.1f})    {i[1]*100:5.10f}%")

# ### Different bmin

dhi, dlo, bminexp = 18, 6, 40
bmin =  2**(-bminexp)
first_prices = [(i, (bmin*i)**2 * 10**(dhi-dlo)) for i in range(1,1000)]
increments = [(b[0],b[1]/a[1]-1) for a,b in tuple(zip(first_prices, first_prices[1:]))]
print(f"  First prices @ {dhi} vs {dlo} decs [{dhi-dlo}]; bexp={bminexp}")
print("---------------------------------------------------")
print("  #              Price            (log)   %chg next")
print("---------------------------------------------------")
for p,i in tuple(zip(first_prices, increments))[:25]:
    print(f"{p[0]:3}: {p[1]:25.20f}    ({abs(log10(p[1])):4.1f})   {i[1]*100:5.1f}%")

# ## Increment plot

cumincr = np.cumprod(1+np.array(tuple(zip(*increments))[1]))
plt.plot(*zip(*increments))
plt.ylim(0,0.05)
plt.xlabel("index of first price points (1,2,3...)")
plt.ylabel("pc chg (=p(i+1)/p(i)-1; 0.05=5%)")
plt.grid()

# ## Liquidity ranges
#
# Liquidity in storage is $2^{128}$, which is about $10^{38}$. A token with 18 decimals still have a range of $10^{20}$, and one with 24 decimals $10^{14}$

2**128, log10(2**128)

# Assume we take $16$ bits off then we get $2^{112}$, which is about $10^{33}$. A token with 18 decimals still have a range of $10^{15}$, and one with 24 decimals $10^{9}$

2**112, log10(2**112)

# ## Width vs position

phi = 0.05
def rg(al):
    return np.linspace(0,1,2**al+1)
def ccr(cr, wr):
    return np.array([[c-phi*w, c+phi*w] for c in cr for w in wr])


rg(0)

data = ccr(rg(0), rg(2))

h0, a0, b0 = 0, 1, 0
dhmax = 5
for dh in range(dhmax+1):

h0, a0, b0 = 0, 2, 3
dhmax = 4
for dh in range(dhmax//2):
    data = ccr(rg(a0+h0+dh), rg(b0+h0+dhmax-dh))
    for rr in data:
        plt.fill_between(rr, h0+dh, h0+dh+1, color="red", alpha=0.01)

h0, a0, b0 = 0, 1, 0
dhmax = 5
for dh in range(dhmax+1):
    x = c(rg(a0+h0+dh), rg(b0+h0+dhmax-dh))
    y = [dh]*len(x)
    plt.scatter(x,y, color="red", s=1000, alpha=0.01)




