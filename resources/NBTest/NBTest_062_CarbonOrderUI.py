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

from carbon.helpers.stdimports import *
from carbon import CarbonOrderUI
print("{0.__name__} v{0.__VERSION__} ({0.__DATE__})".format(CarbonOrderUI))
print_version(require="2.3.3")

# # CarbonOrderUI (NBTest 062)
#
# We introduced new properties that allow getting more curve parameters such as $x_0$ and $x_{asym}$. The code below introduces those parameters and at the same time asserts key relationships.

# ## Selling the base token

o = CarbonOrderUI.from_prices(
    pair="ETH/USDC", 
    tkn="ETH", 
    pa=2500, 
    pb=3000, 
    yint=10, 
    y=5)
o

# ### Prices
#
# Below the different ways of accessing the prices. `pa=py=p_start` is always the beginning of the range, and `pb=px=p_end` is always the end of the range. `pmax` and `pmin` are always the higher and lower price in the quote convention of the pair, respectively. Those figures are quoted in the convention of the pair, so as we are selling the base token this is the inverse of the internal quotation $dy/dx$ which is `pa_raw` and `pb_raw`. `p0` and `p0_raw` are is the geometric average of the start and end prices in the respective quotation. `reverseq` is true if and only if the `_raw` figures are the inverse of the other figures.

print("p_start", o.p_start)
print("p_end", o.p_end)
print("p0", o.p0)
print("reverseq", o.reverseq)
print("pa_raw", o.pa_raw)
print("pb_raw", o.pb_raw)
print("p0_raw", o.p0_raw)
print("p_min", o.pmin)
print("p_max", o.pmax)
assert abs(o.p_start/2500-1)<1e-10
assert abs(o.p_end/3000-1)<1e-10
assert o.pa is o.p_start
assert o.pb is o.p_end
assert o.py is o.pa
assert o.px is o.pb
assert o.pmin == min(o.p_start, o.p_end)
assert o.pmax == max(o.p_start, o.p_end)
assert o.pa_raw == 1/o.pa if o.reverseq else o.pa
assert o.pb_raw == 1/o.pb if o.reverseq else o.pb
assert abs(o.p0/sqrt(o.pa*o.pb)-1)<1e-10
assert abs(o.p0_raw/sqrt(o.pa_raw*o.pb_raw)-1)<1e-10

# ### Curve capacity
#
# `yint` is the curve capacity in the token being sold (here: ETH), and `xint` the corresponding sale amount. `y0` and `x0` are reference parameters determining the curve, and we have `yint/xint=y0/x0=p0_raw`

print("yint", o.yint)
print("xint", o.xint)
print("y0", o.y0)
print("x0", o.x0)
assert o.yint == 10
assert abs(o.yint/o.xint/o.p0_raw-1)<1e-10
assert o.y0/o.x0 == o.p0_raw

# ### Curve convexity
#
# The curve convexity determines how different `pa` and `pb` are. There are a number of ultimately equivalent paramters that describe that
#
# - `widthpc` is the percentage width, defined as `(pa_raw-pb_raw)/p0_raw`
# - `widthr` is the width ratio, defined as `pa_raw/pb_raw >= 1`
# - `Gamma` is the curve leverage parameter between `0..1` where `0` corresponds to constant price and `1` corresponds to constant product
# - `Q` is an alternative convexity parameter also between `0..1` but the other way
#
# The relationshipt between the parameters is provided in the functions `Gamma_from_Q`
#
# $$
# \Gamma(Q) = 1 - \sqrt{Q}
# $$ 
#
# and `Q_from_Gamma` 
#
# $$
# Q(\Gamma) = (1-\Gamma)^2
# $$
#
# Also `Q=1/sqrt(widthr)` because
#
# $$
# Q = \sqrt{\frac{p_a}{p_b}}
# $$

print("widthpc", o.widthpc)
print("widthr", o.widthr)
print("Gamma", o.Gamma)
print("Q", o.Q)
assert abs(o.widthpc/((o.pa_raw-o.pb_raw)/o.p0_raw)-1)<1e-10
assert abs(o.widthr/(o.pa_raw / o.pb_raw)-1)<1e-10
assert abs(o.widthr/(o.pmax / o.pmin)-1)<1e-10
assert abs(o.Q/(sqrt(1/o.widthr))-1)<1e-10
assert abs(o.Q/o.Q_from_Gamma(o.Gamma)-1)<1e-10
assert abs(o.Gamma/o.Gamma_from_Q(o.Q)-1)<1e-10

# ### Asymptotes
#
# Here we deal with the curve asymptotes `yasym` and `xasym`. They are related to the other token figures via 
#
# $$
# \frac{x_{asym}}{x_0} = \frac{y_{asym}}{y_0} = 1-\frac 1 \Gamma
# $$
#
# We also look at the relationship between the `int`ercepts and the `0` figures which are
#
# $$
# \frac{x_{int}}{x_0} = \frac{y_{int}}{y_0} = \frac {2-\Gamma} {1-\Gamma}
# $$

print("yasym", o.yasym)
print("xasym", o.xasym)
print("yint", o.yint)
print("xint", o.xint)
print("y0", o.y0)
print("x0", o.x0)
assert abs(o.xasym/o.x0/(o.yasym/o.y0)-1)<1e-10
assert abs(o.yasym/o.y0/o.asym_over_0(o.Gamma)-1)<1e-10
assert abs(o.xasym/o.x0/o.asym_over_0(o.Gamma)-1)<1e-10
assert abs(o.xint/o.x0/(o.yint/o.y0)-1)<1e-10
assert abs(o.yint/o.y0/o.int_over_0(o.Gamma)-1)<1e-10
assert abs(o.xint/o.x0/o.int_over_0(o.Gamma)-1)<1e-10

# ### Kappa and the invariant function
#
# A very elegant way to express the invariant function is 
#
# $$
# (x-x_{asym})(y-y_{asym}) = \kappa = \frac{x_0y_0}{\Gamma^2}
# $$
#
# or in way that scales better as
#
# $$
# \sqrt{(x-x_{asym})(y-y_{asym})} = \bar\kappa = \frac{\sqrt{x_0y_0}}{\Gamma}
# $$
#

print("y0", o.y0)
print("x0", o.x0)
print("Gamma", o.Gamma)
print("leverage_fctr", o.leverage_fctr)
print("kappa", o.kappa)
print("kappa_bar", o.kappa_bar)
assert o.leverage_fctr == 1/o.Gamma
assert abs(o.kappa/(o.x0*o.y0/o.Gamma**2)-1)<1e-10
assert abs(o.kappa_bar/(sqrt(o.x0*o.y0)/o.Gamma)-1)<1e-10

# Here we are checking the invariant function against the expression above. We are comparing both against `xfromy_f` and `yfromx_f` where we recall that `y` is the token being sold and `x` the token being bought by the AMM.

for y in [0.1,1,3,5,7,9,9.99]:
    x = o.xfromy_f(y)
    f2 = (x-o.xasym)*(y-o.yasym)
    f = sqrt(f2)
    print(f"y={y} ->", x, f, o.kappa_bar, f2, o.kappa)
    assert abs(f/o.kappa_bar-1) < 1e-10
    assert abs(f2/o.kappa-1) < 1e-10

# ## Selling the quote token

o = CarbonOrderUI.from_prices(
    pair="ETH/USDC", 
    tkn="USDC", 
    pa=1500, 
    pb=1000, 
    yint=3000, 
    y=1500)
o

# ### Prices

print("p_start", o.p_start)
print("p_end", o.p_end)
print("p0", o.p0)
print("reverseq", o.reverseq)
print("pa_raw", o.pa_raw)
print("pb_raw", o.pb_raw)
print("p0_raw", o.p0_raw)
print("p_min", o.pmin)
print("p_max", o.pmax)
assert abs(o.p_start/1500-1)<1e-10
assert abs(o.p_end/1000-1)<1e-10
assert o.pa is o.p_start
assert o.pb is o.p_end
assert o.py is o.pa
assert o.px is o.pb
assert o.pmin == min(o.p_start, o.p_end)
assert o.pmax == max(o.p_start, o.p_end)
assert o.pa_raw == 1/o.pa if o.reverseq else o.pa
assert o.pb_raw == 1/o.pb if o.reverseq else o.pb
assert abs(o.p0/sqrt(o.pa*o.pb)-1)<1e-10
assert abs(o.p0_raw/sqrt(o.pa_raw*o.pb_raw)-1)<1e-10

# ### Curve capacity
#

print("yint", o.yint)
print("xint", o.xint)
print("y0", o.y0)
print("x0", o.x0)
assert o.yint == 3000
assert abs(o.yint/o.xint/o.p0_raw-1)<1e-10
assert o.y0/o.x0 == o.p0_raw

# ### Curve convexity

print("widthpc", o.widthpc)
print("widthr", o.widthr)
print("Gamma", o.Gamma)
print("Q", o.Q)
assert abs(o.widthpc/((o.pa_raw-o.pb_raw)/o.p0_raw)-1)<1e-10
assert abs(o.widthr/(o.pa_raw / o.pb_raw)-1)<1e-10
assert abs(o.widthr/(o.pmax / o.pmin)-1)<1e-10
assert abs(o.Q/(sqrt(1/o.widthr))-1)<1e-10
assert abs(o.Q/o.Q_from_Gamma(o.Gamma)-1)<1e-10
assert abs(o.Gamma/o.Gamma_from_Q(o.Q)-1)<1e-10

# ### Asymptotes

print("yasym", o.yasym)
print("xasym", o.xasym)
print("yint", o.yint)
print("xint", o.xint)
print("y0", o.y0)
print("x0", o.x0)
assert abs(o.xasym/o.x0/(o.yasym/o.y0)-1)<1e-10
assert abs(o.yasym/o.y0/o.asym_over_0(o.Gamma)-1)<1e-10
assert abs(o.xasym/o.x0/o.asym_over_0(o.Gamma)-1)<1e-10
assert abs(o.xint/o.x0/(o.yint/o.y0)-1)<1e-10
assert abs(o.yint/o.y0/o.int_over_0(o.Gamma)-1)<1e-10
assert abs(o.xint/o.x0/o.int_over_0(o.Gamma)-1)<1e-10

# ### Kappa and invariant

print("y0", o.y0)
print("x0", o.x0)
print("Gamma", o.Gamma)
print("leverage_fctr", o.leverage_fctr)
print("kappa", o.kappa)
print("kappa_bar", o.kappa_bar)
assert o.leverage_fctr == 1/o.Gamma
assert abs(o.kappa/(o.x0*o.y0/o.Gamma**2)-1)<1e-10
assert abs(o.kappa_bar/(sqrt(o.x0*o.y0)/o.Gamma)-1)<1e-10

# Here we are checking the invariant function against the expression above. We are comparing both against `xfromy_f` and `yfromx_f` where we recall that `y` is the token being sold and `x` the token being bought by the AMM.

for y in [1,100,1000,1500,2500,2999]:
    x = o.xfromy_f(y)
    f2 = (x-o.xasym)*(y-o.yasym)
    f = sqrt(f2)
    print(f"y={y} ->", x, f, o.kappa_bar, f2, o.kappa)
    assert abs(f/o.kappa_bar-1) < 1e-10
    assert abs(f2/o.kappa-1) < 1e-10



