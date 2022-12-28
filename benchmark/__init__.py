from decimal import Decimal
from decimal import getcontext
from decimal import ROUND_HALF_DOWN

getcontext().prec = 50
getcontext().rounding = ROUND_HALF_DOWN

def assertAlmostEqual(actual, expected, maxError):
    actual, expected, maxError = [Decimal(x) for x in [actual, expected, maxError]]
    if actual != expected:
        error = abs(actual - expected) / expected
        assert error <= maxError, 'error = {:f}'.format(error)
