from json import loads
from json import dumps

from benchmark import impl
from benchmark import spec
from benchmark import assertAlmostEqual

def format(val):
    return str(val) if type(val) is int else '{:.24f}'.format(val).rstrip('0').rstrip('.')

def execute(test, module):
    targetOrder = module.Order(test)
    tradeFunc = getattr(targetOrder, 'tradeBy' + test['tradeBy'])
    test['outputAmount'] = format(tradeFunc(test['inputAmount']))

def verify(implTest, specTest, maxAbsErr, maxRelErr):
    assertAlmostEqual(implTest['outputAmount'], specTest['outputAmount'], maxAbsErr, maxRelErr)

def generate(fileName, module, suffix):
    file = open(f'{fileName}.json', 'r')
    tests = loads(file.read())
    file.close()

    for test in tests:
        execute(test, module)

    file = open(f'{fileName}.{suffix}.json', 'w')
    file.write(dumps(tests, indent=2))
    file.close()

    return tests

def run(fileName, maxAbsErr, maxRelErr):
    implTests = generate(fileName, impl, 'impl')
    specTests = generate(fileName, spec, 'spec')

    for implTest, specTest in zip(implTests, specTests):
        verify(implTest, specTest, maxAbsErr, maxRelErr)

run('resources/benchmark/ArbitraryTrade'   , '1', '0')
run('resources/benchmark/ConstantRateTrade', '1', '0.0000000006')
run('resources/benchmark/EthUsdcTrade'     , '0', '0.0000000008')
