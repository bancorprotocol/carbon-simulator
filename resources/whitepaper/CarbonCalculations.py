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

from sympyx import *
__VERSION__ = "4.1"
__DATE__ = "14/Dec/2022"

# # Carbon Calculations
#
# Various calculations related to the Carbon whitepaper.

# ## Core Formulas

x,x0,xint,dx,Dx = symbols("x x_0 x_{int} dx \Delta{x}")
y,y0,yint,dy,Dy = symbols("y y_0 y_{int} dy \Delta{y}")
P,Pmarg,Px,Py,Q,Gam,w,B,S = symbols("P_0 P_{marg} P_x P_y Q \Gamma w B S")
Pa = Py
Pb = Px
xasym, yasym, kappa, k = symbols("x_{asym} y_{asym} \kappa k")
P0=P

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
QDE = QGDE
QGDE

GQE = QGDE.isolate(Gam)
GQE

# Those are useful identities between a certain expression of $\Gamma$ and certain expressions of $Q$ and vice versa

GFQE = Eq((2-Gam)/(1-Gam),(1+1/sqrt(Q)))
GFQE

(GFQE.lhs-GFQE.rhs).subs(Gam, GQE.rhs).simplify()

# For the below, note that $Q=\sqrt[4]{w}$, ie the fourth root of the width of the range

GFQ2E = Eq((Gam-1)/Gam, ((Gam-1)/Gam).subs(Gam, GQE.rhs).simplify())
GFQ2E

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
P0DE = PXYE
PXYE

# and more importantly also of the intercepts

PXYiE = Eq(P, yint/xint)
PXYiE

# $Q$ is related to the ratio of the intercept prices (smaller value in numerator)

QPE = Eq(Q, sqrt(Px/Py))
QPE

# In fact, if we define $w>1$ as the (percentage) **range width** (bigger value in numerator)

WDE = Eq(w, 1/QPE.rhs**2)
WDE

# then that width is simply the inverse Q squared

WE = Eq(w, 1/QPE.lhs**2)
WE

WE.lhs.subs(w, WDE.rhs)-WE.rhs.subs(Q, QPE.rhs)

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

# ### Asymptotic form of the invariant equation and scaling

# The invariant equation is a hyperbola with the asymptotes $x_{asym}, y_{asym}$. Note that in the formulas below for $0<\Gamma<1$ we find that $1-1/\Gamma<0$, meaning the asymptotes are negative values

PIA1E = Eq( (x-xasym)*(y-yasym),kappa)
PIA1E

XADE = Eq(xasym, x0*(1-1/Gam))
XADE

YADE = Eq(yasym, y0*(1-1/Gam))
YADE

YAXDE = Eq(yasym, (y0*(1-1/Gam)).subs(y0, P0*x0))
YAXDE

# In the above invariant equation we can substitute the above definitions of the quantities, and we substitute $y$ from the original pool invariant equation. This allows us to compute $\kappa$

KPDE = PIA1E.subs(xasym, XADE.rhs).subs(yasym, YAXDE.rhs).subs(y, PIE.rhs).simplify()
KPDE

# We remind ourselves that $P_0x_0^2=x_0y_0$ which yields the equation below. 

KPYDE = Eq(KPDE.lhs,KPDE.rhs.subs(P0, y0/x0).simplify())
KPYDE

# This is important, because we remember that the constant-product equation can be written as $xy=k=x_0y_0$. We also remind ourselves that $\sqrt k$ is financially meaningful, and therefore $1/\Gamma$ can be interpreted as pool leverage factor.

PLE = Eq(kappa, k/Gam**2)
PLE

# The scaling factor $1/\Gamma$ can be written as function of the pool width $P_y/P_x$ as

GSE = Eq(sqrt(kappa)/sqrt(k), (1/Gam).subs(Gam, GQE.rhs).subs(Q, QPE.rhs))
GSE

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

# ### B,S parameterization
#
# The B,S parameterization is not particular intuitive, but the formulas are well suited for implementation

BDE = Eq(B,sqrt(Pb))
BDE

SDE = Eq(S,sqrt(Pa)-sqrt(Pb))
SDE

PxDE

PyDE

BDE.s(PxDE)

SDE.s(PxDE).s(PyDE)

BSPIE = Eq(y*(x*(B*S + S**2) + yint), yint*(yint - x*(B*S + B**2)))
BSPIE

# +
#BSPIYE = BSPIE.isolate(y)
#BSPIYE
# -

BSPIYE = Eq(y, solve(BSPIE, y)[0])
BSPIYE

# +
#BSPIXE = BSPIE.isolate(x)
#BSPIXE
# -

BSPIXE = Eq(x, solve(BSPIE, x)[0])
BSPIXE

_eqn1 = Eq(dy/dx, (diff(BSPIYE.rhs,x).simplify()))
_eqn1

_eqn2 = factor(simplify(_eqn1.subs(x, BSPIXE.rhs)))
_eqn2

# The **marginal price equation** (where $P_{marg} = -dy/dx$) then becomes

MPBSE = Eq(Pmarg, (B+S*y/yint)**2)
MPBSE

(_eqn2.rhs+MPBSE.rhs).simplify()

# This is an important equation that determines the liquidity amount $y$ as a function of the marginal price.

YMPE = MPBSE.isolate(y)
YMPE

# Below is the **Swap Equation** (ie $\Delta y$ as a function of $\Delta x$) in B,S parameterization.

BSSE = Eq(Dy, Dx*(S*y + B*yint)**2 / (S*Dx * (S*y + B*yint) + yint**2))
BSSE

# Here is the **Reverse Swap Equation** (ie $\Delta x$ as a function of $\Delta y$)

BSRSE = Eq(Dx, Dy * yint**2 / ((S*y + B*yint) * (S*y + B*yint - S*Dy)))
BSRSE

# We check that the marginal price equation is consistent with the swap equations

((BSSE.rhs / Dx).subs(Dx,0)-MPBSE.rhs).simplify()

((BSRSE.rhs / Dy).subs(Dy,0) - 1/MPBSE.rhs).simplify()

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
FORMULAS = Formulas(version=__VERSION__,date=__DATE__)
print(f"formulalib Version v{_fversion} ({_fdate})")
print(f"FORMULAS Version v{FORMULAS.version} ({FORMULAS.date})")


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
    "Pool Invariant Equation (Q form)", 
    "expressed as Q equals function of x,y with the intercepts as parameters", 
)

FORMULAS.add(
    "PIQ2E", PIQ2E, 
    "Pool Invariant Equation (Q form)", 
    "expressed as Q equals function of x,y with the intercepts as parameters (alternitive form)", 
)

FORMULAS.add(
    "PIRE", PIRE, 
    "Pool Invariant Equation (r form)", 
    "expressed as y as a function of r and parameters P, x0, Gamma", 
)

FORMULAS.add(
    "PIRIE", PIRIE, 
    "Pool Invariant Equation (rho)", 
    "expressed as y as a function of rho and parameters P, x0, Gamma", 
)

FORMULAS.add(
    "PIA1E", PIA1E, 
    "Pool Invariant Equation (asymptotic)", 
    "expressed as hyperbola equation with asymptotes and kappa", 
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
    "PLE", PLE, 
    "Pool leverage equation", 
    "Establishes relationship between kappa, k, Gamma", 
)

FORMULAS.add(
    "KPYDE", KPYDE, 
    "Alternative definition equation for kappa", 
    "Defines kappa in terms of x0, y0, Gamma$", 
)

FORMULAS.add(
    "GSE", GSE, 
    "Gamma scaling equation", 
    "Defines the scaling factor 1/Gamma as function of the range size Py/Px", 
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

# ### B, S equations

FORMULAS.add(
    "BDE", BDE, 
    "B definition equation", 
    "This equation defines the parameter B = sqrt Px", 
)

FORMULAS.add(
    "SDE", SDE, 
    "S definition equation", 
    "This equation defines the parameter S = sqrt Py - sqrt Px", 
)

FORMULAS.add(
    "BSPIE", BSPIE, 
    "Pool Invariant Equation in B,S parameterization", 
    "This is the Pool Invariant Equation with parameters B, S, and yint", 
)

FORMULAS.add(
    "BSPIYE", BSPIYE, 
    "Pool Invariant Equation in B,S parameterization (solved for y)", 
    "This is the Pool Invariant Equation with parameters B, S, and yint (solved for y)", 
)

FORMULAS.add(
    "BSPIXE", BSPIXE, 
    "Pool Invariant Equation in B,S parameterization (solved for x)", 
    "This is the Pool Invariant Equation with parameters B, S, and yint (solved for x)", 
)

FORMULAS.add(
    "BSSE", BSSE, 
    "Swap Equation in B,S parameterization", 
    "This equation determined Delta y as a function of a non-infinitesimal Delta x", 
)

FORMULAS.add(
    "BSRSE", BSRSE, 
    "Reverse Swap Equation in B,S parameterization", 
    "This equation determined Delta x as a function of a non-infinitesimal Delta y", 
)

FORMULAS.add(
    "MPBSE", MPBSE, 
    "Marginal Price Equation in B,S", 
    "The marginal price equation using B,S parameterization", 
)

FORMULAS.add(
    "YMPE", YMPE, 
    "Marginal Price Equation solved for y", 
    "The marginal price equation using B,S parameterization, solved for y", 
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

FORMULAS.add(
    "XADE", XADE, 
    "Definition equation for xasym", 
    "Defines $x_{asym}$ in terms of x0, Gamma", 
)

FORMULAS.add(
    "YADE", YADE, 
    "Definition equation for yasym", 
    "Defines $y_{asym}$ in terms of y0, Gamma", 
)

FORMULAS.add(
    "YAXDE", YAXDE, 
    "Alternative definition equation for yasym", 
    "Defines $y_{asym}$ in terms of x0, P0, Gamma", 
)

FORMULAS.add(
    "KPDE", KPDE, 
    "Definition equation for kappa$", 
    "Defines $\kappa$ in terms of x0, P0, Gamma", 
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


