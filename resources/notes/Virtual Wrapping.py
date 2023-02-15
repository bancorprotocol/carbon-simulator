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

# # Addressing precision issues using virtual token wrapping

# bla

# ## Code

i = lambda n: int(floor(n))

# ## Examples
#
# The examples below show that in pairs with either greatly differing decimals, greatly differing prices, or a combination of both, a lot of the calculation accurary is spurious as the value of one wei of the one token is a massive multiple (powers of ten massive) of one wei of that other. Therefore, if we denominate calculations in the lower valued token-wei we will carry too many digits. In the extreme case of BTC/SHIB for example those deadweight decimals carried correspond to a range of $10^{20}$ or 66 bits.

log2(10**20)

# ### Generic TKN (18 decimals) against USDC (6 decimals)
#
# The first example is a generic 18 decimals token trading around unity with USDC. We see that that wei price is 1e-12 USDC wei per TKN wei. However, by definition, wei numbers (where wei's represent the smallest fraction of a token) must be integers. Therefor the smalles unit that can be traded in this pair is 1 USDC-wei = 1e-6 USDC against 1e-12 TKN wei.

# +
tknb, tknq = "TKN", "USDC"
decb, decq = 18, 6
price = 1
price_wei = price * 10**decq / 10**decb
price_convention = f"{tknq} per {tknb}"
price_convention_wei = f"{tknq}-wei per {tknb}-wei"

print(f"""
tknb        = {tknb} ({decb} decimals)
tknq        = {tknq} ({decq} decimals)
price       = {price} {price_convention}
price (wei) = {price_wei} {price_convention_wei}
""".strip())
# -

# The next example is two tokens with the same decimality of 18, but with greatly differing prices. In this case we assume a price ratio of 1e-9, corresponding to ETH at 10,000 USD and SHIB at 1e-5 USD. Again, the smallest possible trade that allows for an integer ETH-wei is 1e9 SHIB.

# +
tknb, tknq = "SHIB", "ETH"
decb, decq = 18, 18
price = 1e-4*1e-5
price_wei = price * 10**decq / 10**decb
price_convention = f"{tknq} per {tknb}"
price_convention_wei = f"{tknq}-wei per {tknb}-wei"

print(f"""
tknb        = {tknb} ({decb} decimals)
tknq        = {tknq} ({decq} decimals)
price       = {price} {price_convention}
price (wei) = {price_wei} {price_convention_wei}
""".strip())
# -

# Finally we combine those two: WBTC (8 decimals; assumed trading at 1e5=100,000 USD) versus SHIB (18 decimals; assumed trading at 1e-5USD). Here the smallest possible trade unit is 1e20 SHIB

# +
tknb, tknq = "SHIB", "WBTC"
decb, decq = 18, 8
price = 1e-5*1e-5
price_wei = price * 10**decq / 10**decb
price_convention = f"{tknq} per {tknb}"
price_convention_wei = f"{tknq}-wei per {tknb}-wei"

print(f"""
tknb        = {tknb} ({decb} decimals)
tknq        = {tknq} ({decq} decimals)
price       = {price} {price_convention}
price (wei) = {price_wei} {price_convention_wei}
""".strip())
# -

# ## Calculating trade formulas using integer arithmetic
#
# The key to calculating the trade formulas -- ie to calculate how many token weis of one asset to exchange for the other asset -- is the _scaling factor_ we apply to the floating point numbers, therefore effectively converting them into integer numbers with an implied floating point. 
#
# For reasons of computational efficiency, in practice we will usually choose a scaling factor as a power of 2, and our integer limit will be $2^{256} ~ 10^{77}$. For the purpose of this discussion we will choose a scaling factor that is a power of 10 instead, and we will assume 80 decimal integer limit, ie $10^{80}$

log10(2**256), log10(2**128)

# In order to understand how the scaling factor works, we assume a trade formula of $\Delta y = B^2\Delta x$ (ie the $A=0$ case of the Carbon trade formulas. Furthermore we assume the price is 2 x per y, therefore $B=\sqrt{5}$. We want to know, how many y-wei we will get for 1m x-wei. The theoretical value of course is 5m. However, as shown below, the results of integer calculations with a different scaling factor $\lambda$ can vary dramatically:
#
# - at $\lambda=0$ (ie no scaling) we get $\Delta y = 4m$, ie an effective price of 4 instead of 5
# - at $\lambda=1$ our price improves already improves to 4.84
# - however, only at $\lambda = 16$ we achieve the result that is correct at wei-level
#
# The increased precision comes at a steep cost however. We also show `maxn = int(B*ONE)**2 * dx` which is the maximum number used in this particular calculation. It becomes quick very quickly -- at $\lambda = 16$ for example, `maxn` already has 39 digits. For this particular calculation our _256 bit_ aka $10^{80}$ is still sufficient. However, $2^{128}\simeq 39$, so for 128 bit the factor of $\lambda=16$ is already borderline for this calculation.

dx = 1e6
B  = sqrt(5)
for lam in range(21):
    ONE = 10**lam
    dy = int( int(B*ONE)**2 * dx/ONE**2 )
    maxn = int(B*ONE)**2 * dx
    digs = ceil(log10(maxn))
    print(f"lam = {lam:2} ==> dy = {dy} [maxn = {int(maxn):50}; {digs:2} digits]")

# In the example above we've had prices of unity order or magnitude, and we obtained relatively decent convergence from about $\lambda = 3$ with a maximum term reaching 13 digits. We have reached full convergence from $\lambda = 16$ at a calculation length of 40 decimal digits.
#
# Now we are looking at what happens if we we look at different price ranges. Clearly, large values of B do not pose an issue as they already generate a significant number of significant digits in the integer space even without use of a scaling factor. The issue lies on the other side: 

dx = 2e20
B  = sqrt(2e-10)
for lam in range(21):
    ONE = 10**lam
    dy = int( int(B*ONE)**2 * dx/ONE**2 )
    maxn = int(B*ONE)**2 * dx
    digs = ceil(log10(maxn if maxn > 0 else 1))
    print(f"lam = {lam:2} ==> dy = {dy} [maxn = {int(maxn):50}; {digs:2} digits]")

# +
## Virtual wrapping


