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

from carbon import CarbonSimulatorUI, analytics as al, __version__, __date__
from carbon.simulators.sim_analytics import Analytics as A
print(f"Carbon v{__version__} ({__date__})")
print(f"Analytic v{al.__version__} ({al.__date__})")
print("{0.__name__} v{0.__VERSION__} ({0.__DATE__})".format(CarbonSimulatorUI))

# # Carbon Simulation - Test 32

# ## Basic arithmetic functions

v1 = al.vec([1,2,3])
v2 = al.vec([3,4,5])
v3 = al.vec([3,4,None])
v1, v2, v3

-v1, v1+v2, v1-v2, v1*v2, v1/v2

assert list(-v1) == [-1, -2, -3]
assert list(v1+v2) == [4, 6, 8]
assert list(v1-v2) == [-2, -2, -2]
assert list(v1*v2) == [3, 8, 15]
assert list(v1/v2) == [0.3333333333333333, 0.5, 0.6]

# checking that NaN are handled gracefully

-v3, v1+v3, v1-v3, v1*v3, v1/v3

assert list(-v3)[:2] == [-3.0, -4.0]
assert list(v1+v3)[:2] == [4.0, 6.0]
assert list(v1-v3)[:2] == [-2.0, -2.0]
assert list(v1*v3)[:2] == [3.0, 8.0]
assert list(v1/v3)[:2] == [0.3333333333333333, 0.5]

al.vecdot(v1,v2)

al.vecdot(v1,v3)

ts = al.vec(range(20))

ts

len(ts)

tsd = al.diff(ts)
tsd

len(tsd)


# ## Advanced functions

help(al.linspace)

help(A.linspace)

vec = al.linspace0(100,5)
assert list(vec) == [0.0001, 20.0, 40.0, 60.0, 80.0, 99.99900000000001]
assert len(vec) == 6
vec

help(al.midpoints)

help(A.midpoints)

vec2 = al.midpoints(vec)
assert list(vec) == [0.0001, 20.0, 40.0, 60.0, 80.0, 99.99900000000001]
assert len(vec2) == 5
vec2

help(al.diff)

help(A.diff)

vecd = al.diff(vec)
assert list(vecd) == [19.9999, 20.0, 20.0, 20.0, 19.99900000000001]
assert len(vecd) == 5
vecd


