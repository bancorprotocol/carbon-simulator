from functools import cmp_to_key
from benchmark.trade_impl import *

class DecodedOrder:
    def __init__(self, order: dict):
        self.liquidity = Decimal(order['liquidity'])
        self.lowestRate = Decimal(order['lowestRate'])
        self.highestRate = Decimal(order['highestRate'])
        self.marginalRate = Decimal(order['marginalRate'])

class EncodedOrder:
    def __init__(self, order: dict):
        self.y = int(order['y'])
        self.z = int(order['z'])
        self.A = int(order['A'])
        self.B = int(order['B'])

class Rate:
    def __init__(self, input, output):
        self.input = input
        self.output = output

class Quote:
    def __init__(self, id, rate):
        self.id = id
        self.rate = rate

class Action:
    def __init__(self, id, input, output):
        self.id = id
        self.input = input
        self.output = output

def encodeOrder(order: DecodedOrder) -> EncodedOrder:
    y = int(order.liquidity)
    L = int(encodeRate(order.lowestRate))
    H = int(encodeRate(order.highestRate))
    M = int(encodeRate(order.marginalRate))
    return EncodedOrder({
        'y' : y,
        'z' : y if H == M else y * (H - L) // (M - L),
        'A' : encodeFloat(H - L),
        'B' : encodeFloat(L),
    })

def decodeOrder(order: EncodedOrder) -> DecodedOrder:
    y = Decimal(order.y)
    z = Decimal(order.z)
    A = Decimal(decodeFloat(order.A))
    B = Decimal(decodeFloat(order.B))
    return DecodedOrder({
        'liquidity'    : y,
        'lowestRate'   : decodeRate(B),
        'highestRate'  : decodeRate(B + A),
        'marginalRate' : decodeRate(B + A if y == z else B + A * y / z),
    })

def getTradeTargetAmount(x, order):
    y = order.y
    z = order.z
    A = decodeFloat(order.A)
    B = decodeFloat(order.B)
    try:
        return uint128(tradeBySourceAmount(x, y, z, A, B))
    except AssertionError:
        return 0 # rate = zero / amount = zero

def getTradeSourceAmount(x, order):
    y = order.y
    z = order.z
    A = decodeFloat(order.A)
    B = decodeFloat(order.B)
    try:
        return uint128(tradeByTargetAmount(x, y, z, A, B))
    except AssertionError:
        return MAX_UINT256 # rate = amount / infinity = zero

def getRateBySourceAmount(sourceAmount, order):
    output = min(getTradeTargetAmount(sourceAmount, order), order.y)
    input = getTradeSourceAmount(output, order)
    return Rate(input, output)

def getRateByTargetAmount(targetAmount, order):
    input = min(targetAmount, order.y)
    output = getTradeSourceAmount(input, order)
    return Rate(input, output)

def cmpMin(x, y):
    lhs = x.rate.output * y.rate.input
    rhs = y.rate.output * x.rate.input
    lt = lhs < rhs
    gt = lhs > rhs
    eq = not lt and not gt
    is_lt = lt or (eq and x.rate.output < y.rate.output)
    is_gt = gt or (eq and x.rate.output > y.rate.output)
    return is_lt - is_gt

def cmpMax(x, y):
    return cmpMin(y, x)

def sortedQuotes(amount, orders, trade, cmp):
    quotes = [Quote(id, trade(amount, orders[id])) for id in orders]
    return sorted([quote for quote in quotes], key=cmp_to_key(cmp))

'''
 * Compute a list of {order id, trade amount} tuples:
 * - Let `n` denote the initial input amount
 * - Iterate the orders from best rate to worst rate:
 *   - Let `m` denote the maximum tradable amount not larger than `n`
 *   - Add the id of the order along with `m` to the output matching
 *   - If `m < n` then subtract `m` from `n` and continue, otherwise break
 *
 * Sorting the orders from best rate to worst rate:
 * - Computing the rate of an order:
 *   - Let `x` denote the maximum tradable amount not larger than `n`
 *   - Let `y` denote the output amount of trading `x`
 *   - The rate is determined as `y / x`
 * - Comparing the rates of two orders:
 *   - If the rates are different, then the one with a better value prevails
 *   - If the rates are identical, then the one with a better value of `y` prevails
'''
def match(amount, orders, filter, trade, cmp):
    actions = []

    for quote in sortedQuotes(amount, orders, trade, cmp):
        if amount > quote.rate.input:
            if filter(quote.rate):
                actions.append(Action(quote.id, quote.rate.input, quote.rate.output))
                amount -= quote.rate.input
        elif amount == quote.rate.input:
            if filter(quote.rate):
                actions.append(Action(quote.id, quote.rate.input, quote.rate.output))
            break
        else: # amount < quote.rate.input
            quote.rate = Rate(amount, trade(amount, orders[quote.id]).output)
            if filter(quote.rate):
                actions.append(Action(quote.id, quote.rate.input, quote.rate.output))
            break

    return actions

default_filter = lambda rate : rate.input > 0 and rate.output > 0

def matchBySourceAmount(amount, orders, filter = default_filter):
    return match(amount, orders, filter, getRateBySourceAmount, cmpMin)

def matchByTargetAmount(amount, orders, filter = default_filter):
    return match(amount, orders, filter, getRateByTargetAmount, cmpMax)
