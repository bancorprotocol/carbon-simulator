from benchmark import alphaxutils
from decimal import Decimal

tradeBySourceAmount = alphaxutils.tradeBySourceAmount
tradeByTargetAmount = alphaxutils.tradeByTargetAmount
AlphaRouter = alphaxutils.AlphaRouter
goalseek = alphaxutils.goalseek
get_geoprice = alphaxutils.get_geoprice

def mpr_matchBySource(inputAmount, orders, threshold_orders, support_partial):
    indexes = list(range(len(orders)))   
    hypothetical_output_amts = {i: tradeBySourceAmount(amount=inputAmount, order=orders[i]) for i in indexes}
    ordered_amts = {j: hypothetical_output_amts[j] for j in sorted(
        indexes, key=lambda i: hypothetical_output_amts[i], reverse=True
    )}  
    amounts = []
    effective_prices = []
    available_values = {}
    for k, v in ordered_amts.items():
        if v > orders[k].y:
            price = get_geoprice(k, orders)
            amount = orders[k].y
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

    # if inputAmount == total_subset_liquidity:
    #         rl1 = [o.y for o in order_subset]
    #         rl2 = [o.dxfromdy_f(o.y) for o in order_subset]
    if inputAmount > total_subset_liquidity:
        if support_partial:
            print(f'** Partial Match ({total_subset_liquidity/inputAmount*100:0.5f}%) **')
            inputAmount = total_subset_liquidity
            rl1 = [int(o.y) for o in order_subset]
            rl2 = [int(o.dxfromdy_f(o.y)) for o in order_subset]
        else:
            print('Insufficient Liquidity with threshold orders')
            return(None)
    else:
        dy_f = lambda p: sum(o.dyfromp_f(p,byTarget=False) for o in order_subset)
        dx_f = lambda p: sum(o.dxfromdy_f(o.dyfromp_f(p,byTarget=False)) for o in order_subset)
        p_goal = goalseek(lambda p: dx_f(p)-inputAmount, Decimal('1e-20'), Decimal('1e48'))
        rl1 = [int(o.dyfromp_f(p_goal,byTarget=False)) for o in order_subset]
        rl2 = [int(o.dxfromdy_f(o.dyfromp_f(p_goal,byTarget=False))) for o in order_subset]

    actions = {top_n_threshold_orders[i]:{"dx_specified":rl2[i],"dy":rl1[i]} for i in range(len(top_n_threshold_orders))}
    sorted_actions = dict(sorted(actions.items()))
    # print("dx_specified", sum(rl2))
    # assertAlmostEqual(inputAmount, sum(rl2), Decimal('1E-6'))
    # print("\n**Match by Target**") 
    # print('inputAmount', inputAmount)
    # print('total_subset_liquidity', total_subset_liquidity)
    # print('total_input',sum(rl2))
    # print('total_output', sum(rl1))
    # print('effective_price', sum(rl1) / sum(rl2))
    # print('1/effective_price', sum(rl2) / sum(rl1))
    # print("\n**Actions**")
    return(sorted_actions)

def mpr_matchByTarget(inputAmount, orders, threshold_orders, support_partial):
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
            rl1 = [int(o.y) for o in order_subset]
            rl2 = [int(o.dxfromdy_f(o.y)) for o in order_subset]
    elif inputAmount > total_subset_liquidity:
        if support_partial:
            print(f'** Partial Match ({total_subset_liquidity/inputAmount*100:0.5f}%) **')
            inputAmount = total_subset_liquidity
            rl1 = [int(o.y) for o in order_subset]
            rl2 = [int(o.dxfromdy_f(o.y)) for o in order_subset]
        else:
            print('Insufficient Liquidity with threshold orders')
            return(None)
    else:
        dy_f = lambda p: sum(o.dyfromp_f(p,byTarget=True) for o in order_subset)
        dx_f = lambda p: sum(o.dxfromdy_f(o.dyfromp_f(p,byTarget=True)) for o in order_subset)
        p_goal = goalseek(lambda p: dy_f(p)-inputAmount, Decimal('1e-20'), Decimal('1e48'))
        rl1 = [int(o.dyfromp_f(p_goal,byTarget=True)) for o in order_subset]
        rl2 = [int(o.dxfromdy_f(o.dyfromp_f(p_goal,byTarget=True))) for o in order_subset]
        # if sum(rl1) > inputAmount:
        #     print('** ISSUE **')
        #     a_zero = [order for order in order_subset if order.A==0]
        #     a_nonzero = [order for order in order_subset if order.A!=0]
        #     pmargs = [o.pmarg for o in a_zero]
        #     print(len(pmargs), len(set(pmargs)))
        #     sorted_set_pmargs = sorted(list(set(pmargs)), reverse=True)
        #     print(sorted_set_pmargs)
        #     # print(a_nonzero)

        #     if len(a_nonzero)>0:
        #         for pmarg in pmargs:
        #             print(sum(o.dyfromp_f(pmarg) for o in a_nonzero))
        #             if inputAmount <= sum(o.dyfromp_f(pmarg) for o in a_nonzero):
        #                 newInputAmount = inputAmount - sum(o.dyfromp_f(pmarg) for o in a_nonzero)
                        

                # unsatisfied = True
                # # while unsatisfied:
                # dy_f = lambda p: sum(o.dyfromp_f(p) for o in a_nonzero)
                # dx_f = lambda p: sum(o.dxfromdy_f(o.dyfromp_f(p)) for o in a_nonzero)
                # p_goal = goalseek(lambda p: dy_f(p)-inputAmount, Decimal('0.000000001'), Decimal('1000000000'))
                # rl1_other = [o.dyfromp_f(p_goal) for o in a_nonzero]
                # rl2_other = [o.dxfromdy_f(o.dyfromp_f(p_goal)) for o in a_nonzero]
                # if sum(rl1_other) == inputAmount:
                #     print('Success')
                #     print("p_goal", p_goal)
                # else:
                #     print('More to go')







    actions = {top_n_threshold_orders[i]:{"dy_specified":rl1[i],"dx":rl2[i]} for i in range(len(top_n_threshold_orders))}
    sorted_actions = dict(sorted(actions.items()))
    # print("dy_specified", sum(rl1))
    # assertAlmostEqual(inputAmount, sum(rl1), Decimal('1E-6'))
    # print("\n**Match by Source**")  
    # print('inputAmount', inputAmount)
    # print('total_subset_liquidity', total_subset_liquidity)
    # print('total_input',sum(rl1))
    # print('total_output', sum(rl2))
    # print('effective_price', sum(rl1) / sum(rl2))
    # print('1/effective_price', sum(rl2) / sum(rl1))
    # print("\n**Actions**")
    return(sorted_actions)

# mpr_matchBySource(inputAmount, orders, threshold_orders, support_partial)
# mpr_matchByTarget(inputAmount, orders, threshold_orders, support_partial)

