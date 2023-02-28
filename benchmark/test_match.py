from util import read, write
from core.match import impl

def run(fileName):
    tests = read(__file__, fileName)

    for test in tests:
        actions = impl.execute(test['method'], test['amount'], test['orders'])

        formatString = '- order {{:>{}}}: input = {{:>{}}}, output = {{:>{}}}'.format(
            max([len(str(action.id)) for action in actions]),
            max([len(str(action.input)) for action in actions]),
            max([len(str(action.output)) for action in actions]),
        )

        print(fileName.split('/')[-1], test['method'], test['amount'] + ':')
        for action in actions:
            print(formatString.format(action.id, action.input, action.output))

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
