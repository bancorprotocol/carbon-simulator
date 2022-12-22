from carbon import CarbonSimulatorUI
from carbon.common import Decimal
from json import loads, dumps

def run(filename, tradeBySourceAmount):
    file = open(filename +'.json', 'r')
    tests = loads(file.read())
    file.close()

    for test in tests:
        execute(test, tradeBySourceAmount)

    #file = open(filename +'.json', 'w')
    #file.write(dumps(tests, indent = 4))
    #file.close()

def execute(test, tradeBySourceAmount):
    sourceToken = test['sourceToken']
    targetToken = test['targetToken']

    simulator = CarbonSimulatorUI(pair=sourceToken+'/'+targetToken, matching_method='fast', raiseonerror=True)

    for strategy in test['strategies']:
        sourceOrder = [order for order in strategy if order['token'] == sourceToken][0]
        targetOrder = [order for order in strategy if order['token'] == targetToken][0]
        simulator.add_strategy(
            tkn            = targetToken,
            amt_sell       = Decimal(targetOrder['liquidity'   ]),
            amt_buy        = Decimal(sourceOrder['liquidity'   ]),
            psell_start    = Decimal(targetOrder['highestRate' ]) ** +1,
            pbuy_start     = Decimal(sourceOrder['highestRate' ]) ** -1,
            psell_end      = Decimal(targetOrder['lowestRate'  ]) ** +1,
            pbuy_end       = Decimal(sourceOrder['lowestRate'  ]) ** -1,
            psell_marginal = Decimal(targetOrder['marginalRate']) ** +1,
            pbuy_marginal  = Decimal(sourceOrder['marginalRate']) ** -1,
        )

    for tradeAction in test['tradeActions']:
        strategyId = int(tradeAction['strategyId']) - 1
        tokenAmount = Decimal(tradeAction['tokenAmount'])
        if tradeBySourceAmount:
            positionId = 2 * strategyId + 1
            simulator.amm_buys(targetToken, tokenAmount, use_positions=[positionId], use_positions_matchlevel=[positionId])
        else:
            positionId = 2 * strategyId + 0
            simulator.amm_sells(targetToken, tokenAmount, use_positions=[positionId], use_positions_matchlevel=[positionId])

    orders = simulator.state()['orders']
    print(orders['y'], orders['p_marg'])

    for n in range(len(test['strategies'])):
        for k in range(2):
            orderId = {sourceToken: 1, targetToken: 0}[test['strategies'][n][k]['token']]
            test['expectedResults'][n][k]['liquidity'] = '{:.12f}'.format(orders['y'][2 * n + orderId]).rstrip('0').rstrip('.')

run('tradeBySourceAmount', True)
run('tradeByTargetAmount', False)
