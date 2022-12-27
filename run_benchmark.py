from json import loads
from json import dumps

from copy import deepcopy

from benchmark import impl
from benchmark import spec
from benchmark import assertAlmostEqual

def execute(test, module):
    directions = [int(strategy['orders'][0]['token'] == test['targetToken']) for strategy in test['strategies']]
    strategies = [[module.Order(order) for order in strategy['orders']] for strategy in test['strategies']]
    tradeFunc = [module.tradeBySourceAmount, module.tradeByTargetAmount][test['tradeByTargetAmount']]

    for tradeActions in test['tradeActions']:
        strategyId = int(tradeActions['strategyId']) - 1
        tokenAmount = module.Amount(tradeActions['tokenAmount'])
        sourceIndex = directions[strategyId]
        targetIndex = 1 - sourceIndex
        sourceOrder = strategies[strategyId][sourceIndex]
        targetOrder = strategies[strategyId][targetIndex]
        sourceAmount, targetAmount = tradeFunc(tokenAmount, targetOrder)
        sourceOrder.y += sourceAmount
        targetOrder.y -= targetAmount
        if sourceOrder.z < sourceOrder.y:
            sourceOrder.z = sourceOrder.y
        for index, order in [[sourceIndex, dict(sourceOrder)], [targetIndex, dict(targetOrder)]]:
            for dst, src in [['newLiquidity', 'liquidity'], ['newMarginalRate', 'marginalRate']]:
                test['strategies'][strategyId]['orders'][index][dst] = '{:.12f}'.format(order[src]).rstrip('0').rstrip('.')

def verify(implTest, specTest, maxError):
    for implStrategy, specStrategy in zip(implTest['strategies'], specTest['strategies']):
        for implOrder, specOrder in zip(implStrategy['orders'], specStrategy['orders']):
            for key in maxError:
                assertAlmostEqual(implOrder[key], specOrder[key], maxError[key])

def run(fileName, maxError):
    file = open(fileName, 'r')
    data = loads(file.read())
    file.close()

    for implTest, specTest in zip(data, deepcopy(data)):
        execute(implTest, impl)
        execute(specTest, spec)
        verify(implTest, specTest, maxError)

    file = open(fileName, 'w')
    file.write(dumps(data, indent=4))
    file.close()

run('resources/benchmark/ArbitraryTrade.json', {'newLiquidity': '0.000005', 'newMarginalRate': '0.000002'})