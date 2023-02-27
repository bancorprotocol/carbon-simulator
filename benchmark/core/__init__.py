from decimal import Decimal
from decimal import getcontext
from decimal import ROUND_HALF_DOWN

getcontext().prec = 100
getcontext().rounding = ROUND_HALF_DOWN

def assertAlmostEqual(actual, expected, maxAbsErr, maxRelErr):
    actual, expected, maxAbsErr, maxRelErr = [Decimal(x) for x in [actual, expected, maxAbsErr, maxRelErr]]
    if actual != expected:
        absErr = abs(actual - expected)
        relErr = absErr / expected
        assert absErr <= maxAbsErr or relErr <= maxRelErr, \
            '\n- expected value = {:f}'.format(expected) + \
            '\n- actual   value = {:f}'.format(actual) + \
            '\n- absolute error = {:f}'.format(absErr) + \
            '\n- relative error = {:f}'.format(relErr)
