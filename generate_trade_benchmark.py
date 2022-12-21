from carbon import CarbonSimulatorUI
from json import loads, dumps
import pandas as pd

from decimal import Decimal
from decimal import getcontext
from decimal import ROUND_HALF_DOWN

getcontext().prec = 50
getcontext().rounding = ROUND_HALF_DOWN

pd.set_option('display.float_format', lambda x: '%.5f' % x)

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

        simulator = CarbonSimulatorUI(pair=sourceToken+'/'+targetToken, matching_method='manual', raiseonerror=True)

        for strategy in test['strategies']:
            sourceOrder = [order for order in strategy if order['token'] == sourceToken][0]
            targetOrder = [order for order in strategy if order['token'] == targetToken][0]
            simulator.add_strategy(
                tkn            = targetToken,
                amt_sell       = Decimal(targetOrder['liquidity']),
                psell_start    = Decimal(targetOrder['highestRate']),
                psell_end      = Decimal(targetOrder['lowestRate']),
                psell_marginal = Decimal(targetOrder['marginalRate']),
                amt_buy        = Decimal(sourceOrder['liquidity']),
                pbuy_start     = Decimal(sourceOrder['highestRate']) ** -1,
                pbuy_end       = Decimal(sourceOrder['lowestRate']) ** -1,
                pbuy_marginal  = Decimal(sourceOrder['marginalRate']) ** -1,
            )

        trader_func = simulator.trader_sells if tradeBySourceAmount else simulator.trader_buys
        use_routes = [(int(tradeAction['strategyId']) - 1, Decimal(tradeAction['tokenAmount'])) for tradeAction in test['tradeActions']]
        trader_func(targetToken, sum(tradeAction[1] for tradeAction in use_routes), use_routes=use_routes)

        orders = simulator.state()['orders']
        print(orders['y'], orders['p_marg'])

run('tradeBySourceAmount', True)
run('tradeByTargetAmount', False)
