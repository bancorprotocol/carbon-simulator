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
            'highestRate': (self.A + self.B) ** 2,
            'marginalRate': ((self.y * self.A + self.z * self.B) / self.z) ** 2,
        }

class Action:
    def __init__(self, action):
        self.strategyId = int(action['strategyId']) - 1
        self.tokenAmount = Decimal(action['tokenAmount'])

class Pool:
    def __init__(self):
        self.strategies = []

    def addStrategy(self, strategy):
        self.strategies.append(strategy)

    def tradeBySourceAmount(self, sourceIndex, action):
        self.trade(sourceIndex, action, tradeBySourceAmountFunc)

    def tradeByTargetAmount(self, sourceIndex, action):
        self.trade(sourceIndex, action, tradeByTargetAmountFunc)

    def trade(self, sourceIndex, action, func):
        targetIndex = 1 - sourceIndex
        strategy = self.strategies[action.strategyId]
        sourceOrder = strategy[sourceIndex]
        targetOrder = strategy[targetIndex]
        sourceAmount, targetAmount = func(action.tokenAmount, targetOrder)
        sourceOrder.y += sourceAmount
        targetOrder.y -= targetAmount
        if sourceOrder.z < sourceOrder.y:
            sourceOrder.z = sourceOrder.y

def tradeBySourceAmountFunc(sourceAmount, targetOrder):
    x = sourceAmount
    y = targetOrder.y
    z = targetOrder.z
    A = targetOrder.A
    B = targetOrder.B
    n = x * (A * y + B * z) ** 2
    d = A * x * (A * y + B * z) + z ** 2
    return x, n / d

def tradeByTargetAmountFunc(targetAmount, targetOrder):
    x = targetAmount
    y = targetOrder.y
    z = targetOrder.z
    A = targetOrder.A
    B = targetOrder.B
    n = x * z ** 2
    d = (A * y + B * z) * (A * y + B * z - A * x)
    return n / d, x

def execute(test):
    pool = Pool()
    tradeFunc = pool.tradeByTargetAmount if test['tradeByTargetAmount'] else pool.tradeBySourceAmount

    for strategy in test['strategies']:
        pool.addStrategy([Order(order) for order in strategy])

    for action in [Action(tradeAction) for tradeAction in test['tradeActions']]:
        tradeFunc(0 if test['strategies'][action.strategyId][0]['token'] == test['sourceToken'] else 1, action)

    test['expectedResults'] = [
        [
            {
                'liquidity': '{:.12f}'.format(order['liquidity']).rstrip('0').rstrip('.'),
                'marginalRate': '{:.12f}'.format(order['marginalRate'])
            }
            for order in [order.decode() for order in strategy]
        ]
        for strategy in pool.strategies
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

run('ArbitraryTrade.json')