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
from carbon.helpers.soltest import SolTestBase
from carbon.helpers.floatint import *
print("{0.__name__} v{0.__VERSION__} ({0.__DATE__})".format(SolTestBase))
print("{0.__name__} v{0.__VERSION__} ({0.__DATE__})".format(CarbonFloatInt32))
print("{0.__name__} v{0.__VERSION__} ({0.__DATE__})".format(CarbonOrderUI))
print("{0.__name__} v{0.__VERSION__} ({0.__DATE__})".format(P))
from math import log2, floor, ceil, sqrt
print_version(require="2.3.3")

# # Solidity Curve Testing (NBTest058)
#
# ---
#
# **NOTE: THIS NOTEBOOK DOES NOT CURRENTLY CONTAIN ANY AUTOMATED TESTS**
#
# ---
#
#
# we consider by source and by target **from the point of view of the TRADER**, therefore _by source_ fixes _dx_ and calculates _dy_ and vice versa.
#
# **dx from dy ("by target")**
#
# $$
# \Delta x \,(\Delta y) = \frac{\Delta y z^2}{(Ay+Bz)(Ay+Bz-A\Delta y)} =_{A=0} \frac{\Delta y} {B^2}
# $$
#
#
#
# **dy from dx ("by source")**
#
# $$
# \Delta y \,(\Delta x) = \frac{\Delta x(Ay+Bz)^2}{A\Delta x(Ay+Bz)+z^2} =_{A=0} \frac{\Delta x(Bz)^2}{z^2} = \Delta x B^2
# $$
#
# [doc][doc]
#
#
# [doc]:https://docs.google.com/document/d/1x4ZbbS3nIRSJ0ojaOrcBhOc-_eOTga6BajDjK45o7u4/edit

# ### Setting up the common code

mulDivF = lambda x, y, z: int((x * y) // z)
mulDiv  = mulDivF
mulDivC = lambda x, y, z: int((x * y + z - 1) // z)


def dy_from_dx(params, C):
    """
    calculates trade amount dx (received by AMM) from dy (sold by AMM)
    
    :params:   tuple(dx, (y,z,A,B,S))
    :C:        the check function C(num, label); must return int(num)
    :returns:  dy
    """

    dx = params[0]
    y,z,A,B,ONE = params[1]
    temp1 = C(y * A + z * B, "temp1")               
    temp2 = C(temp1 * dx / ONE, "temp2")            
    temp3 = C(temp2 * A + z * z * ONE, "temp3") 
    dy = mulDiv(temp1, temp2, temp3)
    #print(temp1, temp2, temp3, dy)
    return dy


def dx_from_dy(params, C):
    """
    calculates trade amount dy (sold by AMM) from dx (received by AMM) 
    
    :params:   tuple(dy, (y,z,A,B,S))
    :C:        the check function C(num, label); must return int(num)
    :returns:  dx
    """

    dy = params[0]
    y,z,A,B,ONE = params[1]
    temp1 = C(z * ONE, "temp1")                  
    temp2 = C(y * A + z * B, "temp2")         
    temp3 = C(temp2 - dy * A, "temp3")        
    scale = mulDiv(temp2, temp3, 2**255)+1
    temp1s = C(temp1//scale, "temp1s")
    temp2s = C(temp2//scale, "temp2s")
    dx = mulDiv(
        C(dy*temp1s, "dx*temp1s"), 
        temp1, 
        C(temp2s*temp3, "temp2s*temp3")
    )
    #print(temp1, temp2, temp3, temp1s, temp2s, dy)
    return dx


# ## DummyTest

assert True


# ## Running comparison simple examples [NOTEST]

class STB(SolTestBase):
    PRINT_LVL_DEFAULT = SolTestBase.LVL_LOG
    #PRINT_LVL_DEFAULT = SolTestBase.LVL_WARN
VERBOSE = True

# ### SHIB/BTC (Selling BTC)

PAIR = P("SHIB/BTC").sd(18,8)
price = 1e-5 * 1e-5 # SHIB per BTC
capacity = 1000 # 1000 BTC
oui = CarbonOrderUI.from_prices(PAIR, "BTC", price, price/1.05, capacity, capacity)
curve = oui.yzABS(sx=48, verbose=True)
curve

params  = (1*1e8, curve)       # dy = BTC-wei
dx = dx_from_dy( params, STB() )
dx/1e18 # 1e10 SHIB <- 1 BTC

dx2 = oui.dxfromdy_f(1)
print(f"dx={dx/1e18:0.2f} vs {dx2:0.2f} {oui.tknx}, diff={abs(dx/1e18/dx2-1)*100:0.4f}%")

params = (1e10*1e18, curve)      # dx = SHIB-wei
dy = dy_from_dx(params, STB())
dy/1e8 # 1e3 SHIB <- 1 BTC

dy2 = oui.dyfromdx_f(1e10)
print(f"dy={dy/1e8:0.4f} vs {dy2:0.4f} {oui.tkny}, diff={abs(dy/1e8/dy2-1)*100:0.4f}%")

# ### SHIB/BTC (selling SHIB)

PAIR = P("SHIB/BTC").sd(18,8)
price = 1e-5 * 1e-5 # SHIB per BTC # 1e10 USD
capacity = 1000 * 1e10 # 1000 BTC
oui = CarbonOrderUI.from_prices(PAIR, "SHIB", price, price*1.05, capacity, capacity)
curve = oui.yzABS(sx=40, verbose=True)
curve

params  = (1*1e5*1e5*1e18, curve)       # dy = SHIB-wei (1USD)
dx = dx_from_dy( params, STB() )
dx/1e8 # 1e10 SHIB = 1 BTC

dx2 = oui.dxfromdy_f(1)
print(f"dx={dx/1e8:0.6f} vs {dx2:0.6f} {oui.tknx}, diff={abs(dx/1e18/dx2-1)*100:0.4f}%")

params = (1e8, curve)      # dx = BTC-wei
dy = dy_from_dx( params, STB() )
dy/1e18/1e10 #1e10 SHIB = 1 BTC

dy2 = oui.dyfromdx_f(1)
print(f"dy={dy/1e18:0.4f} vs {dy2:0.4f} {oui.tkny}, diff={abs(dy/1e18/dy2-1)*100:0.8f}%")


# ## Running the whole tests [NOTEST]

class STB(SolTestBase):
    #PRINT_LVL_DEFAULT = SolTestBase.LVL_LOG
    #PRINT_LVL_DEFAULT = SolTestBase.LVL_WARN
    PRINT_LVL_DEFAULT = SolTestBase.LVL_ERR
VERBOSE = False

# ### Template code

# +
## SETUP Y = TKNQ, X = TKNB

# parameters
decb = 20
decq = 1
sx=48
amty, amtx = 1, 1
capacity = 1e10
width = 0.1

# set up curves y = TKNQ, x = TKNB
PAIR = P("TKNB/TKNQ").sd(decb,decq)
price = 1 # TKNQ per TKNB
capacity = 1e6 # y = 1e6 TKNQ
oui = CarbonOrderUI.from_prices(PAIR, "TKNQ", price, price/(1+width), capacity, capacity)
curve = oui.yzABS(sx=sx, verbose=VERBOSE)
#print(curve)

# dy from dx
params  = (amty*10**decq, curve)             # amty = TKNQ
dx  = dx_from_dy(params, STB()) / 10**decb    # dx   = TKNB 
dx2 = oui.dxfromdy_f(amty)
print(f"dx={dx:0.6f} vs {dx2:0.6f} {oui.tknx} ==> diff={abs(dx/dx2-1)*100:0.4f}%")

# dx from dy
params  = (amtx*10**decb, curve)             # amtx = TKNB
dy = dy_from_dx(params, STB()) / 10**decq    # dy   = TKNQ 
dy2 = oui.dyfromdx_f(amtx)
print(f"dy={dy:0.6f} vs {dy2:0.6f} {oui.tkny} ==> diff={abs(dy/dy2-1)*100:0.4f}%")
dy_from_dx(params, STB())
# -

# Note: the issues for `decb=0,1` are caused by the fact that the number of tokens expected is very small (1,10 respectively). The float amounts are $10^{-4}$ close to the expected value, but because they are below the int division rounds down, giving 1 token difference, which corresponds to 100% and 10% respectively.

28146000000*9999467920351890/281474989799959504785244160

890090000000*316223491836353792/28147498980863303799508303872

# ### Loop over decimals

# +
## SETUP Y = TKNQ, X = TKNB

# parameters
decb = 20
sx=40
amty, amtx = 1, 1
capacity = 1e12
width = 0.1

for decq in range(0,41):
    print(f"\ndecq = {decq}")

    # set up curves y = TKNQ, x = TKNB
    PAIR = P("TKNB/TKNQ").sd(decb,decq)
    price = 1 # TKNQ per TKNB
    capacity = 1e6 # y = 1e6 TKNQ
    oui = CarbonOrderUI.from_prices(PAIR, "TKNQ", price, price/(1+width), capacity, capacity)
    curve = oui.yzABS(sx=sx, verbose=VERBOSE)
    #print(curve)

    # dy from dx
    params  = (amty*10**decq, curve)             # amty = TKNQ
    dx  = dx_from_dy(params, STB()) / 10**decb    # dx   = TKNB 
    dx2 = oui.dxfromdy_f(amty)
    print(f"dx={dx:0.6f} vs {dx2:0.6f} {oui.tknx} ==> diff={abs(dx/dx2-1)*100:0.4f}%")

    # dx from dy
    params  = (amtx*10**decb, curve)             # amtx = TKNB
    dy = dy_from_dx(params, STB()) / 10**decq    # dy   = TKNQ 
    dy2 = oui.dyfromdx_f(amtx)
    print(f"dy={dy:0.6f} vs {dy2:0.6f} {oui.tkny} ==> diff={abs(dy/dy2-1)*100:0.4f}%")
# -

# ### Loop over prices (18/18)

# +
## SETUP Y = TKNQ, X = TKNB

# parameters
decb = 18
decq = decb
sx=40
amtx = 1 # TKNB
capacity = 1e6
width = 0.1

for priceexp in range(-10,10):
    price = 10**priceexp
    amty = amtx*price # TKNQ
    print(f"\nprice = {price} TKNQ per TKNB [10**{priceexp}]")

    # set up curves y = TKNQ, x = TKNB
    PAIR = P("TKNB/TKNQ").sd(decb,decq)
    #price = 1 # TKNQ per TKNB
    capacity = 1e6 # y = 1e6 TKNQ
    oui = CarbonOrderUI.from_prices(PAIR, "TKNQ", price, price/(1+width), capacity*price, capacity*price)
    curve = oui.yzABS(sx=sx, verbose=VERBOSE)
    #print(curve)

    # dy from dx
    params  = (amty*10**decq, curve)             # amty = TKNQ
    dx  = dx_from_dy(params, STB()) / 10**decb    # dx   = TKNB 
    dx2 = oui.dxfromdy_f(amty)
    print(f"dx={dx:0.6f} vs {dx2:0.6f} {oui.tknx} ==> diff={abs(dx/dx2-1)*100:0.4f}%")

    # dx from dy
    params  = (amtx*10**decb, curve)             # amtx = TKNB
    dy = dy_from_dx(params, STB()) / 10**decq    # dy   = TKNQ 
    dy2 = oui.dyfromdx_f(amtx)
    print(f"dy={dy:0.6f} vs {dy2:0.6f} {oui.tkny} ==> diff={abs(dy/dy2-1)*100:0.4f}%")
# -

# ### Loop over prices (18/6)

# +
## SETUP Y = TKNQ, X = TKNB

# parameters
decb = 18
decq = 6
sx=48
amtx = 1 # TKNB
capacity = 1e6
width = 0.1

for priceexp in range(-10,10):
    price = 10**priceexp
    amty = amtx*price # TKNQ
    print(f"\nprice = {price} TKNQ per TKNB [10**{priceexp}]")

    # set up curves y = TKNQ, x = TKNB
    PAIR = P("TKNB/TKNQ").sd(decb,decq)
    #price = 1 # TKNQ per TKNB
    capacity = 1e6 # y = 1e6 TKNQ
    oui = CarbonOrderUI.from_prices(PAIR, "TKNQ", price, price/(1+width), capacity*price, capacity*price)
    curve = oui.yzABS(sx=sx, verbose=VERBOSE)
    #print(curve)

    # dy from dx
    params  = (amty*10**decq, curve)             # amty = TKNQ
    dx  = dx_from_dy(params, STB()) / 10**decb    # dx   = TKNB 
    dx2 = oui.dxfromdy_f(amty)
    print(f"dx={dx:0.6f} vs {dx2:0.6f} {oui.tknx} ==> diff={abs(dx/dx2-1)*100:0.4f}%")

    # dx from dy
    params  = (amtx*10**decb, curve)             # amtx = TKNB
    dy = dy_from_dx(params, STB()) / 10**decq    # dy   = TKNQ 
    dy2 = oui.dyfromdx_f(amtx)
    print(f"dy={dy:0.6f} vs {dy2:0.6f} {oui.tkny} ==> diff={abs(dy/dy2-1)*100:0.4f}%")
# -


