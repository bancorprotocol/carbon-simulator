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
    input = sourceAmount
    output = tradeBySourceAmount(input, order)
    if output > order['y']:
        input = tradeByTargetAmount(order['y'], order)
        output = tradeBySourceAmount(input, order)
        while output > order['y']:
            input = input - 1
            output = tradeBySourceAmount(input, order)
    return Rate(input, output)

def rateByTargetAmount(targetAmount, order):
    input = min(targetAmount, order['y'])
    output = tradeByTargetAmount(input, order)
    return Rate(input, output)

def sortByMinRate(q1, q2):
    lhs = q1.rate.output * q2.rate.input
    rhs = q2.rate.output * q1.rate.input
    lt = lhs < rhs
    gt = lhs > rhs
    eq = not lt and not gt
    is_lt = lt or (eq and q1.rate.output < q2.rate.output)
    is_gt = gt or (eq and q1.rate.output > q2.rate.output)
    return is_lt - is_gt

def sortByMaxRate(q1, q2):
    return sortByMinRate(q2, q1)

'''
 * Sort the orders from best rate to worst rate:
 * - Compute the rate of an order:
 *   - Let `x` denote the maximum tradable amount not larger than `n`
 *   - Let `y` denote the output amount of trading `x`
 *   - The rate is determined as `y / x`
 * - Compute the rates of two orders:
 *   - If the rates are different, then the one with a better value prevails
 *   - If the rates are identical, then the one with a better value of `y` prevails
'''
def sortedQuotes(amount, orders, trade, sort):
    return sorted([Quote(id, trade(amount, orders[id])) for id in orders], key=cmp_to_key(sort))

'''
 * Compute a list of {order id, trade amount} tuples:
 * - Let `n` denote the initial input amount
 * - Iterate the orders from best rate to worst rate:
 *   - Let `m` denote the maximum tradable amount not larger than `n`
 *   - Add the id of the order along with `m` to the output matching
 *   - Subtract `m` from `n` and repeat the process until `n` is zero
'''
def matchBy(amount, orders, filter, trade, sort):
    actions = []

    for quote in sortedQuotes(amount, orders, trade, sort):
        input = min(quote.rate.input, amount)
        output = trade(input, orders[quote.id]).output
        if filter(Rate(input, output)):
            actions.append(Action(quote.id, input, output))
            amount -= input
            if amount == 0:
                break

    return actions

def matchBySourceAmount(amount, orders, filter):
    return matchBy(amount, orders, filter, rateBySourceAmount, sortByMinRate)

def matchByTargetAmount(amount, orders, filter):
    return matchBy(amount, orders, filter, rateByTargetAmount, sortByMaxRate)

def execute(method, amount, orders, filter = lambda rate : rate.input > 0 and rate.output > 0):
    return globals()[method](int(amount), {id: encodeOrder(orders[id]) for id in range(len(orders))}, filter)
