from functools import cmp_to_key
from core.trade.impl import tradeBySourceAmount, tradeByTargetAmount, encodeOrder, decodeFloat

Fast = 'Fast'
Best = 'Best'

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

def getParams(order):
    y, z, A, B = [order[k] for k in 'yzAB']
    return [y, z, decodeFloat(A), decodeFloat(B)]

def getLimit(order):
    y, z, A, B = getParams(order)
    return (y * A + z * B) // z if z > 0 else 0

def equalizeByTargetAmount(order, limit):
    y, z, A, B = getParams(order)
    return (y * A + z * (B - limit)) // A if A > 0 else y

def equalizeBySourceAmount(order, limit):
    return tradeByTargetAmount(equalizeByTargetAmount(order, limit), order)

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
    quotes = [Quote(id, trade(amount, orders[id])) for id in orders]
    return sorted([quote for quote in quotes], key=cmp_to_key(sort))

'''
 * Compute a list of {order id, trade amount} tuples:
 * - Let `n` denote the initial input amount
 * - Iterate the orders from best rate to worst rate:
 *   - Let `m` denote the maximum tradable amount not larger than `n`
 *   - Add the id of the order along with `m` to the output matching
 *   - If `m < n` then subtract `m` from `n` and continue, otherwise break
'''
def matchFast(amount, orders, quotes, filter, trade):
    actions = []

    for quote in quotes:
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

'''
 * Compute a list of {order id, trade amount} tuples:
 * - Iterate the orders from best rate to worst rate:
 *   - Calculate a trade which brings orders `0` thru `n - 1` to the rate of order `n`
 *   - If the result is larger than or equal to the requested trade amount, then stop
 * - If the result is larger than the requested trade amount:
 *   - Determine a rate `r` between the rate of order `n - 1` and the rate of order `n`
 *   - Calculate a trade which brings orders `0` thru `n - 1` to the rate `r`
 *   - If the result is equal to the requested trade amount, then stop
'''
def matchBest(amount, orders, quotes, filter, trade, equalize):
    orders = [orders[quote.id] for quote in quotes] + [{k: 0 for k in 'yzAB'}]

    for n in range(1, len(orders)):
        limit = getLimit(orders[n])
        rates = [trade(equalize(order, limit), order) for order in orders[:n]]
        total = sum(rate.input for rate in rates)
        delta = total - amount
        if delta >= 0:
            break

    if delta > 0:
        lo = limit
        hi = getLimit(orders[n - 1])
        while lo + 1 < hi:
            limit = (lo + hi) // 2
            rates = [trade(equalize(order, limit), order) for order in orders[:n]]
            total = sum(rate.input for rate in rates)
            delta = total - amount
            if delta > 0:
                lo = limit
            elif delta < 0:
                hi = limit
            else: # delta == 0
                break

    if delta > 0:
        for i in reversed(range(len(rates))):
            rate = trade(rates[i].input - delta, orders[i])
            delta += rate.input - rates[i].input
            rates[i] = rate
            if delta <= 0:
                break
    elif delta < 0:
        for i in range(len(rates)):
            rate = trade(rates[i].input - delta, orders[i])
            delta += rate.input - rates[i].input
            if delta > 0:
                break
            rates[i] = rate

    return [Action(quotes[i].id, rates[i].input, rates[i].output) for i in range(len(rates)) if filter(rates[i])]

def matchBy(amount, orders, types, filter, trade, sort, equalize):
    quotes = sortedQuotes(amount, orders, trade, sort)
    return {
        Fast: matchFast(amount, orders, quotes, filter, trade) if Fast in types else None,
        Best: matchBest(amount, orders, quotes, filter, trade, equalize) if Best in types else None,
    }

def matchBySourceAmount(amount, orders, types, filter):
    return matchBy(amount, orders, types, filter, rateBySourceAmount, sortByMinRate, equalizeBySourceAmount)

def matchByTargetAmount(amount, orders, types, filter):
    return matchBy(amount, orders, types, filter, rateByTargetAmount, sortByMaxRate, equalizeByTargetAmount)

def execute(method, amount, orders, types = [Fast, Best], filter = lambda rate : rate.input > 0 and rate.output > 0):
    return globals()[method](int(amount), {id: encodeOrder(orders[id]) for id in range(len(orders))}, types, filter)
