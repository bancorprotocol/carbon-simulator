from util import read, write
from core.trade import impl as trade_impl
from core.match import impl as match_impl

def run(fileName):
    tests = read(__file__, fileName)

    for test in tests:
        actions = match_impl.execute(test['method'], test['amount'], test['orders'])

        print(fileName.split('/')[-1], test['method'], test['amount'] + ':')

        for type in actions:
            print('-', type + ':')

            formatString = '  - order {{:>{}}}: input = {{:>{}}}, output = {{:>{}}}'.format(
                max([len(str(action.id)) for action in actions[type]]),
                max([len(str(action.input)) for action in actions[type]]),
                max([len(str(action.output)) for action in actions[type]]),
            )

            for action in actions[type]:
                print(formatString.format(action.id, action.input, action.output))

        [method, attribute, compare_input, compare_output] = {
            'matchBySourceAmount': ['tradeBySourceAmount', 'output', int.__le__, int.__ge__],
            'matchByTargetAmount': ['tradeByTargetAmount', 'input' , int.__ge__, int.__le__],
        }   [test['method']]

        for type in actions:
            assert sum(action.input for action in actions[type]) <= int(test['amount'])
            for action in actions[type]:
                assert getattr(action, attribute) <= int(test['orders'][action.id]['liquidity'])
                assert action.output == trade_impl.execute(method, action.input, test['orders'][action.id])

        assert compare_input(
            sum(action.input for action in actions[match_impl.Best]),
            sum(action.input for action in actions[match_impl.Fast])
        )

        assert compare_output(
            sum(action.output for action in actions[match_impl.Best]),
            sum(action.output for action in actions[match_impl.Fast])
        )

        test['actions'] = {
            type: [
                {
                    'id': str(action.id),
                    'input': str(action.input),
                    'output': str(action.output),
                }
                for action in actions[type]
            ]
            for type in actions
        }

    write(__file__, fileName, tests)

run('resources/match/ArbitraryMatch')
run('resources/match/BigPoolMatch')
run('resources/match/EthUsdcMatch')
run('resources/match/SpecialMatch')
