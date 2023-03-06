from benchmark import alphaxutils
from decimal import Decimal
from math import ceil

tradeBySourceAmount = alphaxutils.tradeBySourceAmount
tradeByTargetAmount = alphaxutils.tradeByTargetAmount
AlphaRouter = alphaxutils.AlphaRouter
goalseek = alphaxutils.goalseek
get_geoprice = alphaxutils.get_geoprice
handle_wei_discrepancy = alphaxutils.handle_wei_discrepancy

def mpr_matchBySource(inputAmount, orders, threshold_orders, support_partial):
    isPartial = False
    indexes = list(range(len(orders)))   
    hypothetical_output_amts = {i: Decimal(tradeBySourceAmount(amount=inputAmount, order=orders[i])) for i in indexes}
    ordered_amts = {j: hypothetical_output_amts[j] for j in sorted(
        indexes, key=lambda i: hypothetical_output_amts[i], reverse=True
    )}  
    amounts = []
    effective_prices = []
    available_values = {}
    for k, v in ordered_amts.items():
        if v > orders[k].y:
            price = get_geoprice(k, orders)
            amount = Decimal(orders[k].y)
            amounts += [amount]
            effective_prices += [price]
            available_values[k] = amount / price
        else:
            amounts += [v]
            price = v / inputAmount
            effective_prices += [price]
            available_values[k] = v / price

    ordered_available_values = {i:available_values[i] for i in ordered_amts.keys()}
    total_available_value = sum([v for k,v in ordered_available_values.items()])

    if (not support_partial) & (total_available_value < abs(inputAmount)):
        print('Insufficient Liquidity')
        return(None)
    else:
        passed_indexes = AlphaRouter.gen_two_order_selector(ordered_available_values.values(), abs(inputAmount), threshold_orders)
        top_n_threshold_orders = [list(ordered_available_values.keys())[i] for i in passed_indexes]
    order_subset = [orders[i] for i in top_n_threshold_orders]
    total_subset_liquidity = sum([v for k,v in ordered_available_values.items() if k in top_n_threshold_orders])

    if inputAmount > total_subset_liquidity:
        if support_partial:
            print(f'** Partial Match ({total_subset_liquidity/inputAmount*100:0.5f}%) **')
            inputAmount = total_subset_liquidity
            rl1 = [ceil(o.y) for o in order_subset]
            rl2 = [ceil(o.dxfromdy_f(o.y)) for o in order_subset]
            isPartial = True
        else:
            print('Insufficient Liquidity with threshold orders')
            return(None)
    else:
        dy_f = lambda p: sum(o.dyfromp_f(p) for o in order_subset)
        dx_f = lambda p: sum(o.dxfromdy_f(o.dyfromp_f(p)) for o in order_subset)
        p_goal = goalseek(lambda p: dx_f(p)-inputAmount, Decimal('1e-20'), Decimal('1e48'))
        rl1 = [ceil(o.dyfromp_f(p_goal)) for o in order_subset]
        rl2 = [ceil(o.dxfromdy_f(o.dyfromp_f(p_goal))) for o in order_subset]

    actions = {top_n_threshold_orders[i]:{"dx_specified":rl2[i],"dy":rl1[i]} for i in range(len(top_n_threshold_orders))}
    actions0 = {k:v for k,v in actions.items() if v['dy'] != 0}
    # print("pre", actions0)
    if not isPartial:
        resultant_dx_specified = sum([v["dx_specified"] for k,v in actions0.items()])
        over = resultant_dx_specified - inputAmount
        actions0 = handle_wei_discrepancy(actions0, orders, over, tradeByTarget=False)
    # print("post", actions0)
    sorted_actions = dict(sorted(actions0.items()))
    return(sorted_actions)

def mpr_matchByTarget(inputAmount, orders, threshold_orders, support_partial):
    isPartial = False
    indexes = list(range(len(orders)))   
    hypothetical_output_amts = {i: tradeByTargetAmount(amount=inputAmount, order=orders[i]) for i in indexes}
    ordered_amts = {j: hypothetical_output_amts[j] for j in sorted(
        indexes, key=lambda i: hypothetical_output_amts[i], reverse=False
    )}   
    max_output_amt = {i: tradeByTargetAmount(amount=orders[i].y, order=orders[i]) for i in indexes}  
    ordered_associated_liquidity = {i:orders[i].y for i in ordered_amts.keys()}
    total_liquidity = sum([v for k,v in ordered_associated_liquidity.items()])

    if (not support_partial) & (total_liquidity < abs(inputAmount)):
        print('Insufficient Liquidity')
        return(None)
    else:
        passed_indexes = AlphaRouter.gen_two_order_selector(ordered_associated_liquidity.values(), abs(inputAmount), threshold_orders)
        top_n_threshold_orders = [list(ordered_associated_liquidity.keys())[i] for i in passed_indexes]
    
    order_subset = [orders[i] for i in top_n_threshold_orders]
    total_subset_liquidity = sum(o.y for o in order_subset)
    
    if inputAmount == total_subset_liquidity:
            rl1 = [ceil(o.y) for o in order_subset]
            rl2 = [ceil(o.dxfromdy_f(o.y)) for o in order_subset]
    elif inputAmount > total_subset_liquidity:
        if support_partial:
            print(f'** Partial Match ({total_subset_liquidity/inputAmount*100:0.5f}%) **')
            inputAmount = total_subset_liquidity
            rl1 = [ceil(o.y) for o in order_subset]
            rl2 = [ceil(o.dxfromdy_f(o.y)) for o in order_subset]
            isPartial = True
        else:
            print('Insufficient Liquidity with threshold orders')
            return(None)
    else:
        dy_f = lambda p: sum(o.dyfromp_f(p) for o in order_subset)
        dx_f = lambda p: sum(o.dxfromdy_f(o.dyfromp_f(p)) for o in order_subset)
        p_goal = goalseek(lambda p: dy_f(p)-inputAmount, Decimal('1e-20'), Decimal('1e48'))
        rl1 = [ceil(o.dyfromp_f(p_goal)) for o in order_subset]
        rl2 = [ceil(o.dxfromdy_f(o.dyfromp_f(p_goal))) for o in order_subset]
    actions = {top_n_threshold_orders[i]:{"dy_specified":rl1[i],"dx":rl2[i]} for i in range(len(top_n_threshold_orders))}
    actions0 = {k:v for k,v in actions.items() if (v['dx'] != 0)}
    # print("pre", actions0)
    if not isPartial:
        resultant_dy_specified = sum([v["dy_specified"] for k,v in actions0.items()])
        over = resultant_dy_specified - inputAmount
        actions0 = handle_wei_discrepancy(actions0, orders, over, tradeByTarget=True)
    # print("post", actions0)
    sorted_actions = dict(sorted(actions0.items()))
    return(sorted_actions)
