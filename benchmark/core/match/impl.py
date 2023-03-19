from functools import cmp_to_key
from core.trade.impl import tradeBySourceAmount, tradeByTargetAmount, encodeOrder

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

def rateBySourceAmount(sourceAmount, order):
    input1 = sourceAmount
    output1 = tradeBySourceAmount(input1, order)
    if output1 > order['y']:
        input2 = tradeByTargetAmount(order['y'], order)
        output2 = tradeBySourceAmount(input2, order)
        if output2 > order['y']:
            input3 = input2 - 1
            output3 = tradeBySourceAmount(input3, order)
            return Rate(input3, output3)
        return Rate(input2, output2)
    return Rate(input1, output1)

def rateByTargetAmount(targetAmount, order):
    input = min(targetAmount, order['y'])
    output = tradeByTargetAmount(input, order)
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

def sortedQuotes(amount, orders, func, cmp):
    quotes = [Quote(id, func(amount, orders[id])) for id in orders]
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
def matchFunc(amount, orders, filter, func, cmp):
    actions = []

    for quote in sortedQuotes(amount, orders, func, cmp):
        if amount > quote.rate.input:
            if filter(quote.rate):
                actions.append(Action(quote.id, quote.rate.input, quote.rate.output))
                amount -= quote.rate.input
        elif amount == quote.rate.input:
            if filter(quote.rate):
                actions.append(Action(quote.id, quote.rate.input, quote.rate.output))
            break
        else: # amount < quote.rate.input
            quote.rate = Rate(amount, func(amount, orders[quote.id]).output)
            if filter(quote.rate):
                actions.append(Action(quote.id, quote.rate.input, quote.rate.output))
            break

    return actions

def matchBySourceAmount(amount, orders, filter):
    return matchFunc(amount, orders, filter, rateBySourceAmount, cmpMin)

def matchByTargetAmount(amount, orders, filter):
    return matchFunc(amount, orders, filter, rateByTargetAmount, cmpMax)

def execute(method, amount, orders, filter = lambda rate : rate.input > 0 and rate.output > 0):
    return globals()[method](int(amount), {id: encodeOrder(orders[id]) for id in range(len(orders))}, filter)
