from decimal import Decimal
from decimal import getcontext
from decimal import ROUND_HALF_DOWN

getcontext().prec = 50
getcontext().rounding = ROUND_HALF_DOWN
