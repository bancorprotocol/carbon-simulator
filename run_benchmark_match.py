from json import loads, dumps
from benchmark.match import impl

def run(fileName):
    file = open(f'{fileName}.json', 'r')
    tests = loads(file.read())
    file.close()

    for test in tests:
        method = getattr(impl, test['method'])
        amount = int(test['amount'])
        orders = {id: impl.encodeOrder(impl.DecodedOrder(test['orders'][id])) for id in range(len(test['orders']))}
        actions = method(amount, orders)

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

    file = open(f'{fileName}.json', 'w')
    file.write(dumps(tests, indent = 2))
    file.close()

run('resources/benchmark/ArbitraryMatch')
run('resources/benchmark/BigPoolMatch')
run('resources/benchmark/EthUsdcMatch')
