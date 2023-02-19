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
        test['specReturn'] = f'{specReturn:.12f}'.rstrip('0').rstrip('.')

    file = open(f'{fileName}.json', 'w')
    file.write(dumps(tests, indent = 2))
    file.close()

run('resources/benchmark/ArbitraryTrade' , '2', '0')
run('resources/benchmark/EthUsdcTrade'   , '0', '0.0000000009')
run('resources/benchmark/ExtremeSrcTrade', '2', '0.0005326707')
run('resources/benchmark/ExtremeTrgTrade', '2', '0.0005329546')
