from json import loads
from json import dumps

from copy import deepcopy

from benchmark import impl
from benchmark import spec
from benchmark import assertAlmostEqual

def format(val):
    return '{:.12f}'.format(val).rstrip('0').rstrip('.')

def execute(test, module):
    directions = [int(strategy['orders'][0]['token'] == test['targetToken']) for strategy in test['strategies']]
    strategies = [[module.Order(order) for order in strategy['orders']] for strategy in test['strategies']]
    tradeFunc = [module.tradeBySourceAmount, module.tradeByTargetAmount][test['tradeByTargetAmount']]

    for tradeActions in test['tradeActions']:
        strategyId = int(tradeActions['strategyId']) - 1
        tokenAmount = module.Amount(tradeActions['amount'])
        sourceIndex = directions[strategyId]
        targetIndex = 1 - sourceIndex
        sourceOrder = strategies[strategyId][sourceIndex]
        targetOrder = strategies[strategyId][targetIndex]
        sourceAmount, targetAmount = tradeFunc(tokenAmount, targetOrder)
        sourceOrder.y += sourceAmount
        targetOrder.y -= targetAmount
        if sourceOrder.z < sourceOrder.y:
            sourceOrder.z = sourceOrder.y

    for dstStrategy, srcStrategy in zip(test['strategies'], strategies):
        for dstOrder, srcOrder in zip(dstStrategy['orders'], srcStrategy):
            dstOrder['expected'] = {key: format(val) for key, val in dict(srcOrder).items()}

def verify(implTest, specTest, maxError):
    for implStrategy, specStrategy in zip(implTest['strategies'], specTest['strategies']):
        for implOrder, specOrder in zip(implStrategy['orders'], specStrategy['orders']):
            for key in maxError:
                assertAlmostEqual(implOrder['expected'][key], specOrder['expected'][key], maxError[key])

def generate(fileName, module):
    file = open(f'{fileName}.json', 'r')
    tests = loads(file.read())
    file.close()

    for test in tests:
        execute(test, module)

    file = open(f'{fileName}.{module.__name__}.json', 'w')
    file.write(dumps(tests, indent=2))
    file.close()

    return tests

def run(fileName, maxError):
    implTests = generate(fileName, impl)
    specTests = generate(fileName, spec)

    for implTest, specTest in zip(implTests, specTests):
        verify(implTest, specTest, maxError)

blocks = [
    {
        'fileName': 'resources/benchmark/ArbitraryTrade',
        'maxError': {
            'liquidity'    : '0.0000046064',
            'lowestRate'   : '0.0000000007',
            'highestRate'  : '0.0000000007',
            'marginalRate' : '0.0000015278',
        }
    }
]

for block in blocks:
    run(block['fileName'], block['maxError'])
