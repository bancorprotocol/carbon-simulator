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

from carbon import CarbonSimulatorUI, CarbonOrderUI, P, __version__, __date__
from carbon.helpers import SharedVar, print_version
from math import floor, ceil, trunc
print_version(require="2.3")

# # SharedVar class in helpers (NBTest 54)

# ## Shared Var

# #### Definitions

x, x2 = SharedVar(5), SharedVar(5.1234)
x

assert repr(x)[:17] == "SharedVar(5, oid="

# #### Comparisons

assert (x==x, x==5, x<5, x>5, x<=5, x>=5, 5<x, 5>x) == (True, True, False, False, True, True, False, False)
assert (x==x, 5<=x, 5>=x) == (True, True, True)

# #### Unitary operations

assert x==+x
assert x.id != (+x).id
assert (-x).value == -5
assert x.id != (-x).id
assert (abs(-x)).value == 5
assert x.id != (abs(-x)).id
assert round(x2,2)==5.12
assert x2.id != round(x2,2).id
assert trunc(x2)==5
assert x2.id != trunc(x2).id
assert floor(x2)==5
assert x2.id != floor(x2).id
assert ceil(x2)==6
assert x2.id != ceil(x2).id

# #### Binary operations

assert x+1 == 6
assert x.id != (x+1).id
assert x-1 == 4
assert x.id != (x-1).id
assert x*2 == 10
assert x.id != (x*2).id
assert x/2 == 2.5
assert x.id != (x/2).id
assert x//2 == 2
assert x.id != (x//2).id
assert x**2 == 25
assert x.id != (x//2).id
assert x<<1 == 10
assert x.id != (x<<1).id
assert x>>1 == 2
assert x.id != (x>>1).id
assert x&3 == 1
assert x.id != (x&3).id
assert x|2 == 7
assert x.id != (x|2).id
assert x^1 == 4
assert x.id != (x^1).id

assert divmod(x,2)[0] == 2
assert divmod(x,2)[1] == 1
assert x.id != divmod(x,2)[0].id
assert x.id != divmod(x,2)[1].id

# #### Reverse binary operations

assert 1+x == 6
assert x.id != (1+x).id
assert 1-x == -4
assert x.id != (1-x).id
assert 2*x == 10
assert x.id != (2*x).id
assert 2/x == 0.4
assert x.id != (2/x).id
assert 2//x == 0
assert x.id != (2//x).id
assert 2**x == 32
assert x.id != (2**x).id
assert 1<<x == 32
assert x.id != (1<<x).id
assert 1024>>x == 32
assert x.id != (1024>>x).id
assert 3&x == 1
assert x.id != (3&x).id
assert 2|x == 7
assert x.id != (2|x).id
assert 1^x == 4
assert x.id != (1^x).id

assert divmod(16,x)[0] == 3
assert divmod(16,x)[1] == 1
assert x.id != divmod(16,x)[0].id
assert x.id != divmod(16,x)[1].id

# #### Assignment operations

y = SharedVar(100)
id0 = y.id
y+=1
y-=1
y*=10
y//=10
assert y == 100
y<<=2
y>>=1
assert y == 200
y&=199
y|=1
y^=17
assert y == 208
y /= 32
assert y == 6.5
assert y.id == id0

# #### Conversions

x = SharedVar(5.5)
assert int(x) == 5
assert str(x) == "5.5"
assert float(x) == 5.5
assert complex(x) == complex(float(x))





