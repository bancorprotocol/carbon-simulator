from json import loads
from json import dumps

from decimal import Decimal
from decimal import getcontext
from decimal import ROUND_HALF_DOWN

getcontext().prec = 50
getcontext().rounding = ROUND_HALF_DOWN

class Order:
    def __init__(self, order):
        liq = Decimal(int(order['liquidity']))
        min = Decimal(order['lowestRate']).sqrt()
        max = Decimal(order['highestRate']).sqrt()
        mid = Decimal(order['marginalRate']).sqrt()
        self.y = liq
        self.z = liq * (max - min) / (mid - min)
        self.A = max - min
        self.B = min
    def decode(self):
        return {
            'liquidity': self.y,
            'lowestRate': self.B ** 2,
            'highestRate': (self.B + self.A) ** 2,
            'marginalRate': (self.B + self.A * self.y / self.z) ** 2
        }

def tradeBySourceAmount(x, y, z, A, B):
    n = x * (A * y + B * z) ** 2
    d = A * x * (A * y + B * z) + z ** 2
    return x, n / d

def tradeByTargetAmount(x, y, z, A, B):
    n = x * z ** 2
    d = (A * y + B * z) * (A * y + B * z - A * x)
    return n / d, x

def execute(test):
    directions = [int(strategy[0]['token'] == test['targetToken']) for strategy in test['strategies']]
    strategies = [[Order(order) for order in strategy] for strategy in test['strategies']]
    tradeFunc = [tradeBySourceAmount, tradeByTargetAmount][test['tradeByTargetAmount']]

    for tradeActions in test['tradeActions']:
        strategyId = int(tradeActions['strategyId']) - 1
        tokenAmount = Decimal(tradeActions['tokenAmount'])
        sourceIndex = directions[strategyId]
        targetIndex = 1 - sourceIndex
        sourceOrder = strategies[strategyId][sourceIndex]
        targetOrder = strategies[strategyId][targetIndex]
        sourceAmount, targetAmount = tradeFunc(tokenAmount, targetOrder.y, targetOrder.z, targetOrder.A, targetOrder.B)
        sourceOrder.y += sourceAmount
        targetOrder.y -= targetAmount
        if sourceOrder.z < sourceOrder.y:
            sourceOrder.z = sourceOrder.y

    test['expectedResults'] = [
        [
            {
                'liquidity': '{:.12f}'.format(order['liquidity']).rstrip('0').rstrip('.'),
                'marginalRate': '{:.12f}'.format(order['marginalRate'])
            }
            for order in [order.decode() for order in strategy]
        ]
        for strategy in strategies
    ]

def run(fileName):
    file = open(fileName, 'r')
    tests = loads(file.read())
    file.close()

    for test in tests:
        execute(test)

    file = open(fileName, 'w')
    file.write(dumps(tests, indent=4))
    file.close()

run('benchmark/ArbitraryTrade.json')