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

from sympy import *
__VERSION__ = "2.2"
__DATE__ = "2/Nov/2022"


# # Carbon Calculations
#
# Various calculations related to the Carbon whitepaper.

def isolate(eqn, var,ix=0):
    "isolates the variable var in the equation eqn and returns result as equation"
    return Eq(var, solve(eqn, var)[ix])


# ## Core Formulas

x,x0,xint,dx,Dx = symbols("x x_0 x_{int} dx \Delta{x}")
y,y0,yint,dy,Dy = symbols("y y_0 y_{int} dy \Delta{y}")
P,Pmarg,Px,Py,Q,Gam,w = symbols("P_0 P_{marg} P_x P_y Q \Gamma w")                                            

# This is the **Pool Invariant Equation** in its canonic **risk asset** form using $P, x_0, \Gamma$

PIE = Eq(
    y,
    x0*P*(x*(Gam - 1) - x0*(Gam - 2))/(Gam*x - x0*(Gam - 1))
)
PIE

PINE = PIE.subs(x0, y0/P).simplify()
PINE

# This is the **Q-form** of the **Pool Invariant Equation**

PIQE = Eq(
    Q,
    x*y / ( (x-xint)*(y-yint) )
)
PIQE

_m = (x-xint)*(y-yint)
PIQ2E = Eq(PIQE.lhs*_m, PIQE.rhs*_m)
PIQ2E

# This is the **Definition Equations** for $Q$ in terms of $\Gamma$ and its inverse

QGDE = Eq(Q,(1-Gam)**2)
QGDE

GQE = isolate(QGDE, Gam)
GQE

# This is a useful identity between a certain expression of $\Gamma$ and a certain expression of $Q$.

GFQE = Eq((2-Gam)/(1-Gam),(1+1/sqrt(Q)))
GFQE

(GFQE.lhs-GFQE.rhs).subs(Gam, 1-sqrt(Q)).simplify()

# ## Other Parametrizations

# Those are the **Definition Equations** for $x_{int}, y_{int}, P_x, P_y$

XiDE = Eq(xint, x0*(2-Gam)/(1-Gam))
XiDE

XiQE = XiDE.subs(GFQE.lhs, GFQE.rhs)
XiQE

YiDE = Eq(yint, y0*(2-Gam)/(1-Gam))
YiDE

YiQE = YiDE.subs(GFQE.lhs, GFQE.rhs)
YiQE

PxDE = Eq(Px, P*Q)
PxDE

PyDE = Eq(Py, P/Q)
PyDE

# Here are a few other important relationships. Firstly, $P_0$ is the ratio the reference coordinates

PXYE = Eq(P, y0/x0)
PXYE

# and more importantly also of the intercepts

PXYiE = Eq(P, yint/xint)
PXYiE

# $Q$ is related to the ratio of the intercept prices

QPE = Eq(Q, sqrt(Py/Px))
QPE

# In fact, if we define $w$ as the (percentage) **range width**

WDE = Eq(w, QPE.rhs**2)
WDE

# then that width is simply Q squared

WE = Eq(w, QPE.lhs**2)
WE

# Also the reference price is the geometric average of the intercept prices

PPE = Eq(P,sqrt(Px*Py))
PPE

# Below formulas are important for actually setting ranges for unidirectional trading where the parameters we have are the amount of risk asset $x_{int}$ as well as the two ends of the range $P_x, P_y$. Our goal is to solve for the parameterset $Q, x_{int}, y_{int}$ that allows us to use the invariant equation `PIQE`. $x_{int}$ is already known, and $Q$ we can get from `QPE`, so what is left is to calculate $y_{int}$.
#
# We first recall a number of definitions

QPE

PPE

PXYiE

# and now make a number of new ones

YiPE = Eq(yint, solve(PXYiE, yint)[0].subs(P, PPE.rhs))
YiPE

XiPE = Eq(xint, solve(YiPE, xint)[0])
XiPE

# This is the **Swap Equation** derived from it, describing an actual transaction

SE = Eq(
    - Dy,
    P*x0**2*Dx/((Gam*(x - x0) + x0)*(Gam*(x - x0 + Dx) + x0))
)
SE

# This is the **Marginal Swap Equation** describing an infinitesimal transaction, rearranged with $dx$ on the LHS 

MSE = Eq(
    -dy/dx,
    P*x0**2/(Gam*(x - x0) + x0)**2
)
MSE

# This is the **Marginal Price Equation** which is the same as the Marginal Swap Equation, just recognising that $-\frac{dy}{dx}=P_{marg}%$

MPE = Eq(Pmarg, MSE.rhs)
MPE

# This is the **Reverse Marginal Price Equation** with $y,y_0$ instead of $x,x_0$, but with the price parameters unchanged

MPERev0 = MPE.subs(Pmarg, 1/Pmarg).subs(P,1/P).subs(x0,y0).subs(x,y)
MPERev0

# The is again the **Reverse Marginal Price Equation** but inversed to isolate $P_{marg}$

MPERev = Eq(Pmarg, 1/MPERev0.rhs)
MPERev

# Now we reparameterize the MPE as a function of $Q, x_{int}$ and of $Q, y_{int}$

MPQXiE = MPE.subs(GQE.lhs,GQE.rhs).subs(x0, solve(XiQE, x0)[0]).simplify()
MPQXiE

MPQYiE = MPERev.subs(GQE.lhs,GQE.rhs).subs(y0, solve(YiQE, y0)[0]).simplify()
MPQYiE

# ### Rho and r parametrizations

r, rho =symbols("r \\rho") 
RXE = Eq(x0, r*x)
RXIE = Eq(x, rho*x0)
RXE

RXIE

MPRE = MPE.subs(RXE.lhs, RXE.rhs).simplify()
MPRE

MPRIE = MPE.subs(RXIE.lhs, RXIE.rhs).simplify()
MPRIE

# For completeness, here also the invariant and swap equations using $r,\rho$

PIRE = PIE.subs(RXE.lhs, RXE.rhs).simplify()
PIRE

PIRIE = PIE.subs(RXIE.lhs, RXIE.rhs).simplify()
PIRIE

SRE = SE.subs(RXE.lhs, RXE.rhs).simplify()
SRE

SRIE = Eq(SE.lhs, P*Dx*x0 / ((Gam*(rho-1)+1)*(Gam*(Dx+x0*(rho-1))+x0)))
SRIE

(SRIE.rhs - SE.rhs.subs(RXIE.lhs, RXIE.rhs)).simplify()

# ### Adjusting active ranges
#
# As a reminder, and _inactive_ range is a range where the current market price is outside the range, and an _active_ range is one where it is inside. Active ranges split into _active active_ and _inactive active_ ranges. In the former, the market price equals the marginal price of the curve, in the latter the marginal price is somewhat off (in the direction where the marginal price shown in the direction of the AMM is _worse_ than that of the market, so it won't trade.
#
# An active active AMM whose curve is to be readjusted to remain active active has only one remaining degree of freedom -- one can choose either width or mid price, but not both. One can of course change the parameters such that it turns inactive active, in which case the parameters space is two dimensional (width and mid-price), but there is a non-trivial boundary condition to be taken into account because one is starting from the boundary. When adjusting an inactive inactive range, the space is locally fully 2-dimensional, but at one point the boundary must be taken into account.
#
# In a first step, we express our marginal price as a function of $P_0=\sqrt{P_xP_y}$ and $w=P_y/P_x$

MPWYiE = MPQYiE.subs(Q, -solve(WE, Q)[0])
MPWYiE

# We then express $P_0$ as a function of $w$ (and the other paramters), defining the 1-dimensional curve in $P_0, w$ space that any active active reparamterization must fulfil. 

P0WYiE = Eq(P, solve(MPWYiE, P)[0])
P0WYiE

# Uncomment the below to obtain the closed form solution for the inverse equation $w=w(P_0)$

# +
#WP0YiE = Eq(w, solve(P0WYiE,w)[0].simplify())
#WP0YiE
# -

# For the inequality, we first note that $P_0\propto P_{marg}$. We now need to distinguish the following two cases (note that the price is always quoted as numeraire / risk asset) that ensure that the AMM either matches the market price, or it is _out of the money_, ie not willing to trade at prevailing prices.
#
# 1. **AMM sells risk asset.** If the AMM sells the risk asset it is only willing to sell it at market _or higher_, ie $P_{marg} \geq P_{market}$
#
# 1. **AMM buys risk asset.** If the AMM buys the risk asset it is only willing to buy it at market _or lower_, ie $P_{marg} \leq P_{market}$

# ## Creating the Formulas object for export
#
# The `FORMULAS` object contains all key formulas of this worksheet, and it allows to easily import and use them in other workbooks. 

try:
    from .formulalib import Formulas, __VERSION__ as _fversion, __DATE__ as _fdate
except:
    from formulalib import Formulas, __VERSION__ as _fversion, __DATE__ as _fdate
print(f"formulalib Version v{_fversion} ({_fdate})")
FORMULAS = Formulas()

# ### Core equations

FORMULAS.add(
    "PIE", PIE, 
    "Pool Invariant Equation (risk asset)", 
    "expressed as y as a function of x and parameters P, x0, Gamma", 
)

FORMULAS.add(
    "PINE", PINE, 
    "Pool Invariant Equation (numeraire)", 
    "expressed as y as a function of x and parameters P, y0, Gamma", 
)

FORMULAS.add(
    "PIQE", PIQE, 
    "Pool Invariant Equation (Q-form)", 
    "expressed as Q equals function of x,y with the intercepts as parameters", 
)

FORMULAS.add(
    "PIQ2E", PIQ2E, 
    "Pool Invariant Equation (Q-form)", 
    "expressed as Q equals function of x,y with the intercepts as parameters (alternitive form)", 
)

FORMULAS.add(
    "PIRE", PIRE, 
    "Pool Invariant Equation (r)", 
    "expressed as y as a function of r and parameters P, x0, Gamma", 
)

FORMULAS.add(
    "PIRIE", PIRIE, 
    "Pool Invariant Equation (rho)", 
    "expressed as y as a function of rho and parameters P, x0, Gamma", 
)

FORMULAS.add(
    "SE", SE, 
    "Swap Equation", 
    "expressed as minus Delta y as a function of Delta x and all other parameters and variables from the PIE", 
)

FORMULAS.add(
    "SRE", SRE, 
    "Swap Equation (r)", 
    "expressed as minus Delta y as a function of Delta x and all other parameters and variables from the PIRE", 
)

FORMULAS.add(
    "SRIE", SRIE, 
    "Swap Equation (rho)", 
    "expressed as minus Delta y as a function of Delta x and all other parameters and variables from the PIRIE", 
)

FORMULAS.add(
    "MSE", MSE, 
    "Marginal Swap Equation", 
    "the Swap Equation for Delta x -> dx; dx is brought to the LHS", 
)

FORMULAS.add(
    "MPE", MPE, 
    "Marginal Price Equation", 
    "this is the same as the Marginal Swap Equation, except that the LHS is recognized as the marginal price", 
)

FORMULAS.add(
    "MPERev", MPERev, 
    "Reverse Marginal Price Equation", 
    "Marginal price eqaution seen from the other side (ie based on y, y0)", 
)

FORMULAS.add(
    "MPQXiE", MPQXiE, 
    "Marginal Price Equation (Q,xint)", 
    "Reparametrization of the MPE as a function of $Q, x_{int}$", 
)

FORMULAS.add(
    "MPQYiE", MPQYiE, 
    "Marginal Price Equation (Q,yint)", 
    "Reparametrization of the MPE as a function of $Q, y_{int}$", 
)

FORMULAS.add(
    "MPWYiE", MPWYiE, 
    "Marginal Price Equation (w,yint)", 
    "Reparametrization of the MPE as a function of $w, y_{int}$", 
)

FORMULAS.add(
    "MPWYiE", MPWYiE, 
    "Marginal Price Equation (w,yint)", 
    "Reparametrization of the MPE as a function of $w, y_{int}$", 
)

FORMULAS.add(
    "P0WYiE", P0WYiE, 
    "Constant Marginal Price Curve Equation", 
    "Establishes relationship $P_0=P_0(w)$ for which the marginal price remains const", 
)

FORMULAS.add(
    "RXE", RXE, 
    "Ratio equation (x/x0)", 
    "Defines r as the ratio x/x0", 
)

FORMULAS.add(
    "RXIE", RXIE, 
    "Inverse ratio equation (x0/x)", 
    "Defines rho as the ratio x0/x", 
)

FORMULAS.add(
    "MPRE", MPRE, 
    "Marginal Price Equation (fixed x/x0)", 
    "this is the same as the Marginal Swap Equation, except that the LHS is recognized as the marginal price; x/x0 = r is fixed", 
)

FORMULAS.add(
    "MPRIE", MPRIE, 
    "Marginal Price Equation (fixed x0/x)", 
    "this is the same as the Marginal Swap Equation, except that the LHS is recognized as the marginal price; x/x0 = r is fixed", 
)

# ### Definition equations and other relationships

FORMULAS.add(
    "QGDE", QGDE, 
    "Q Gamma Definition Equation", 
    "Gamma as a function of Q", 
)

FORMULAS.add(
    "GQE", GQE, 
    "Gamma Q Equation", 
    "Gamma as a function of Q", 
)

FORMULAS.add(
    "GFQE", GFQE, 
    "Gamma Q Formula Equation", 
    "an important relationship between functions of Gamma and Q", 
)

FORMULAS.add(
    "XiDE", XiDE, 
    "Xint Definition Equation", 
    "xint as function of x0 and Gamma", 
)

FORMULAS.add(
    "YiDE", YiDE, 
    "Yint Definition Equation", 
    "xint as function of y0 and Gamma", 
)

FORMULAS.add(
    "XiQE", XiQE, 
    "Xint Q Equation", 
    "xint as function of x0 and Q", 
)

FORMULAS.add(
    "YiQE", YiQE, 
    "Yint Q Equation", 
    "yint as function of y0 and Q", 
)

FORMULAS.add(
    "PxDE", PxDE, 
    "Px Equation", 
    "Px as function of P and Q", 
)

FORMULAS.add(
    "PyDE", PyDE, 
    "Py Equation", 
    "Py as function of P and Q", 
)

FORMULAS.add(
    "PXYE", PXYE, 
    "PXY Equation", 
    "P as a function of x0 and y0", 
)

FORMULAS.add(
    "PXYiE", PXYiE, 
    "PXYi Equation", 
    "P as a function of xint and yint", 
)

FORMULAS.add(
    "QPE", QPE, 
    "QP Equation", 
    "Q as a function of Px and Py", 
)

FORMULAS.add(
    "WDE", WDE, 
    "Range width definition equation", 
    "w as ratio Py/Px ", 
)

FORMULAS.add(
    "WE", WE, 
    "Range width equation", 
    "Py/Px as a function of Q", 
)

FORMULAS.add(
    "PPE", PPE, 
    "PP Equation", 
    "P as a function of Px and Py", 
)

FORMULAS.add(
    "XiPE", XiPE, 
    "Xint from P", 
    "xint as function of Px and Py", 
)

FORMULAS.add(
    "YiPE", XiPE, 
    "yint from P", 
    "yint as function of Px and Py", 
)
