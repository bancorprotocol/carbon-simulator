from util import read, write
from core.trade import impl as trade_impl
from core.match import impl as match_impl

def run(fileName):
    tests = read(__file__, fileName)

    for test in tests:
        actions = match_impl.execute(test['method'], test['amount'], test['orders'])

        print(fileName.split('/')[-1], test['method'], test['amount'] + ':')

        formatString = '- order {{:>{}}}: input = {{:>{}}}, output = {{:>{}}}'.format(
            max([len(str(action.id)) for action in actions]),
            max([len(str(action.input)) for action in actions]),
            max([len(str(action.output)) for action in actions]),
        )

        for action in actions:
            print(formatString.format(action.id, action.input, action.output))

        [method, attribute] = {
            'matchBySourceAmount': ['tradeBySourceAmount', 'output'],
            'matchByTargetAmount': ['tradeByTargetAmount', 'input' ],
        }   [test['method']]

        assert sum(action.input for action in actions) <= int(test['amount'])
        for action in actions:
            order = test['orders'][action.id]
            assert getattr(action, attribute) <= int(order['liquidity'])
            assert action.output == trade_impl.execute(method, action.input, order)

        test['actions'] = [
            {
                'id': str(action.id),
                'input': str(action.input),
                'output': str(action.output),
            }
            for action in actions
        ]

    write(__file__, fileName, tests)

run('resources/match/ArbitraryMatch')
run('resources/match/BigPoolMatch')
run('resources/match/EthUsdcMatch')
run('resources/match/SpecialMatch')
