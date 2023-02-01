from benchmark import impl
from benchmark import alphaxutils
from decimal import Decimal
import pandas as pd

Order = alphaxutils.Order
tradeBySourceAmount = alphaxutils.tradeBySourceAmount
tradeByTargetAmount = alphaxutils.tradeByTargetAmount
AlphaRouter = alphaxutils.AlphaRouter
goalseek = alphaxutils.goalseek
assertAlmostEqual = alphaxutils.assertAlmostEqual
get_geoprice = alphaxutils.get_geoprice

threshold_orders = 6
support_partial = True

# ETH side orders
# inputAmount = Decimal('10000') # by Target = USDC amount
inputAmount = Decimal('3') # by Source = ETH amount
order_params = {
    'liquidity':Decimal('5'),
    'highestRate':Decimal('0.0005'), # 2000
    'lowestRate':Decimal('0.0004'),  # 2500
    'marginalRate':Decimal('0.0005'),
    }
order_params2 = {
    'liquidity':Decimal('4'),
    'highestRate':Decimal('0.0006'), # 1666
    'lowestRate':Decimal('0.0005'),  # 2000
    'marginalRate':Decimal('0.0006'),
    }

# USDC side orders (approx same)
# # inputAmount = Decimal('5')  # by Target = ETH amount
# inputAmount = Decimal('30000')  # by Source = USDC amount
# order_params = {
#     'liquidity':Decimal('5000'),
#     'highestRate':Decimal('2500'),
#     'lowestRate':Decimal('2000'),
#     'marginalRate':Decimal('2500'),
#     }
# order_params2 = {
#     'liquidity':Decimal('4000'),
#     'highestRate':Decimal('2000'),
#     'lowestRate':Decimal('1666'),
#     'marginalRate':Decimal('2000'),
#     }

orders = []
for i in range(5):
    orders += [Order(order_params)]
    orders += [Order(order_params2)]

def matchByTarget_selector(inputAmount, orders):
    indexes = list(range(len(orders)))   
    hypothetical_output_amts = {i: tradeBySourceAmount(x=inputAmount, order=orders[i])[1] for i in indexes}   # WTF not sure why this is bySource but it works - for input USDC as target, orders defined in ETH per USDC
    associated_liquidity = [orders[i].y for i in hypothetical_output_amts.keys()]

    amounts = []
    effective_prices = []
    available_value = []
    for k, v in hypothetical_output_amts.items():
        if v > orders[k].y:
            price = get_geoprice(k, orders)
            amount = orders[k].y
            amounts += [amount]
            effective_prices += [price]
            available_value += [amount / price]
        else:
            amounts += [v]
            price = v / inputAmount
            effective_prices += [price]
            available_value += [v / price]

    results = pd.DataFrame(
        [
            hypothetical_output_amts.keys(),
            hypothetical_output_amts.values(),
            associated_liquidity,
            amounts,
            effective_prices,
            available_value,
        ],
        index=[
            "indexes",
            "hypothetical_output_amts",
            "associated_liquidity",
            "amount",
            "effective_prices",
            "available_value",
        ],
    )
    results = results.T.copy()
    results.sort_values(
        by=["hypothetical_output_amts", 'indexes'], ascending=[False, True], inplace=True
    )

    results.fillna(0, inplace=True)
    results.reset_index(inplace=True, drop=True)

    if (not support_partial) & (results.available_value.sum() < abs(inputAmount)):
        print('Insufficient Liquidity')
        return(None)
    else:
        passed_indexes = AlphaRouter.gen_one_order_selector(results.available_value, abs(inputAmount), threshold_orders)
        top_n_threshold_orders = [results.indexes[i] for i in passed_indexes]
    order_subset = [orders[i] for i in top_n_threshold_orders]
    total_subset_liquidity = results[results.indexes.isin(top_n_threshold_orders)].available_value.sum()
    return(order_subset, total_subset_liquidity, top_n_threshold_orders)

order_subset, total_subset_liquidity, top_n_threshold_orders = matchByTarget_selector(inputAmount, orders)

def mpr_matchByTarget(inputAmount, order_subset, total_subset_liquidity, top_n_threshold_orders, support_partial):
    print("\n**Match by Target**") 
    print('inputAmount', inputAmount)
    print('total_subset_liquidity', total_subset_liquidity)
    if inputAmount == total_subset_liquidity:
            rl1 = [o.y for o in order_subset]
            rl2 = [o.dxfromdy_f(o.y) for o in order_subset]
    elif inputAmount > total_subset_liquidity:
        if support_partial:
            print(f'** Partial Match ({total_subset_liquidity/inputAmount*100:0.5f}%) **')
            inputAmount = total_subset_liquidity
            rl1 = [o.y for o in order_subset]
            rl2 = [o.dxfromdy_f(o.y) for o in order_subset]
        else:
            print('Insufficient Liquidity with threshold orders')
            return(None)
    else:
        dy_f = lambda p: sum(o.dyfromp_f(p) for o in order_subset)
        dx_f = lambda p: sum(o.dxfromdy_f(o.dyfromp_f(p)) for o in order_subset)
        p_goal = goalseek(lambda p: dx_f(p)-inputAmount, Decimal('0.000000001'), Decimal('1000000000'))
        rl1 = [o.dyfromp_f(p_goal) for o in order_subset]
        rl2 = [o.dxfromdy_f(o.dyfromp_f(p_goal)) for o in order_subset]

    actions = {top_n_threshold_orders[i]:{"input":rl2[i],"output":rl1[i]} for i in range(len(top_n_threshold_orders))}
    assertAlmostEqual(inputAmount, sum(rl2), Decimal('1E-6'))
    print('total_input',sum(rl2))
    print('total_output', sum(rl1))
    print('effective_price', sum(rl1) / sum(rl2))
    print('1/effective_price', sum(rl2) / sum(rl1))
    print("\n**Actions**")
    print(actions)

def matchBySource_selector(inputAmount, orders):
    indexes = list(range(len(orders)))   
    hypothetical_output_amts = {i: tradeByTargetAmount(x=inputAmount, order=orders[i])[0] for i in indexes}   # WTF not sure why this is byTarget but it works
    max_output_amt = {i: tradeByTargetAmount(x=orders[i].y, order=orders[i])[0] for i in indexes}  
    ordered_associated_liquidity = {i:orders[i].y for i in hypothetical_output_amts.keys()}

    results = pd.DataFrame(
        [
            hypothetical_output_amts.keys(),
            hypothetical_output_amts.values(),
            max_output_amt.keys(),
            max_output_amt.values(),
        ],
        index=[
            "indexes",
            "hypothetical_output_amts",
            "indexes_b",
            "max_output_amt",
        ],
    )
    results = results.T.copy()
    assert(list(results.indexes) == list(results.indexes_b))

    results.sort_values(
        by=["hypothetical_output_amts", 'indexes'], ascending=[True, True], inplace=True
    )

    results2 = pd.DataFrame(
        [
            ordered_associated_liquidity.keys(),
            ordered_associated_liquidity.values(),
        ],
        index=[
            "ordered_associated_liquidity_keys",
            "ordered_associated_liquidity",
        ],
    )
    results2 = results2.T.copy()

    results = pd.merge(results, results2, how='left', left_on = 'indexes', right_on='ordered_associated_liquidity_keys')
    assert(list(results.indexes) == list(results.ordered_associated_liquidity_keys))

    results.fillna(0, inplace=True)
    results.reset_index(inplace=True, drop=True)

    if (not support_partial) & (results.ordered_associated_liquidity.sum() < abs(inputAmount)):
        print('Insufficient Liquidity')
        return(None)
    else:
        passed_indexes = AlphaRouter.gen_one_order_selector(results.ordered_associated_liquidity, abs(inputAmount), threshold_orders)
        top_n_threshold_orders = [results.indexes[i] for i in passed_indexes]
    order_subset = [orders[i] for i in top_n_threshold_orders]
    total_subset_liquidity = results[results.indexes.isin(top_n_threshold_orders)].ordered_associated_liquidity.sum()
    return(order_subset, total_subset_liquidity, top_n_threshold_orders)

order_subset, total_subset_liquidity, top_n_threshold_orders = matchBySource_selector(inputAmount, orders)

def mpr_matchBySource(inputAmount, order_subset, total_subset_liquidity, top_n_threshold_orders, support_partial):  
    print("\n**Match by Source**")  
    print('inputAmount', inputAmount)
    print('total_subset_liquidity', total_subset_liquidity)
    if inputAmount == total_subset_liquidity:
            rl1 = [o.y for o in order_subset]
            rl2 = [o.dxfromdy_f(o.y) for o in order_subset]
    elif inputAmount > total_subset_liquidity:
        if support_partial:
            print(f'** Partial Match ({total_subset_liquidity/inputAmount*100:0.5f}%) **')
            inputAmount = total_subset_liquidity
            rl1 = [o.y for o in order_subset]
            rl2 = [o.dxfromdy_f(o.y) for o in order_subset]
        else:
            print('Insufficient Liquidity with threshold orders')
            return(None)
    else:
        dy_f = lambda p: sum(o.dyfromp_f(p) for o in order_subset)
        dx_f = lambda p: sum(o.dxfromdy_f(o.dyfromp_f(p)) for o in order_subset)
        p_goal = goalseek(lambda p: dy_f(p)-inputAmount, Decimal('0.000000001'), Decimal('1000000000'))
        rl1 = [o.dyfromp_f(p_goal) for o in order_subset]
        rl2 = [o.dxfromdy_f(o.dyfromp_f(p_goal)) for o in order_subset]

    actions = {top_n_threshold_orders[i]:{"input":rl1[i],"output":rl2[i]} for i in range(len(top_n_threshold_orders))}
    assertAlmostEqual(inputAmount, sum(rl1), Decimal('1E-6'))
    print('total_input',sum(rl1))
    print('total_output', sum(rl2))
    print('effective_price', sum(rl1) / sum(rl2))
    print('1/effective_price', sum(rl2) / sum(rl1))
    print("\n**Actions**")
    print(actions)

# mpr_matchByTarget(inputAmount, order_subset, total_subset_liquidity, top_n_threshold_orders, support_partial)
mpr_matchBySource(inputAmount, order_subset, total_subset_liquidity, top_n_threshold_orders, support_partial)


