from util import read, write
from core.trade import impl, spec
from core import assertAlmostEqual

def run(fileName, maxAbsErr, maxRelErr):
    tests = read(__file__, fileName)

    for test in tests:
        implOutput = impl.execute(test['method'], test['amount'], test['order'])
        specOutput = spec.execute(test['method'], test['amount'], test['order'])
        assertAlmostEqual(implOutput, specOutput, maxAbsErr, maxRelErr)
        test['output']['impl'] = str(implOutput)
        test['output']['spec'] = f'{specOutput:.12f}'.rstrip('0').rstrip('.')
        print(fileName.split('/')[-1], test['output']['impl'], test['output']['spec'])

    write(__file__, fileName, tests)

run('resources/trade/ArbitraryTrade' , '2', '0')
run('resources/trade/EthUsdcTrade'   , '0', '0.0000000009')
run('resources/trade/ExtremeSrcTrade', '2', '0.0005326707')
run('resources/trade/ExtremeTrgTrade', '2', '0.0005329546')
