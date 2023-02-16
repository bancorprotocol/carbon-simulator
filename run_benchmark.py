from json import loads, dumps
from benchmark import impl, spec, assertAlmostEqual

def run(fileName, maxAbsErr, maxRelErr):
    file = open(f'{fileName}.json', 'r')
    tests = loads(file.read())
    file.close()

    for test in tests:
        implReturn = impl.trade(test)
        specReturn = spec.trade(test)
        assertAlmostEqual(implReturn, specReturn, maxAbsErr, maxRelErr)
        test['implReturn'] = str(implReturn)
        test['specReturn'] = '{:.12f}'.format(specReturn).rstrip('0').rstrip('.')

    file = open(f'{fileName}.json', 'w')
    file.write(dumps(tests, indent=2))
    file.close()

    return tests

run('resources/benchmark/ArbitraryTrade'   , '1', '0')
run('resources/benchmark/ConstantRateTrade', '2', '0.0000000005')
run('resources/benchmark/EthUsdcTrade'     , '0', '0.0000000008')
