"""
wrapper UI class for the Carbon simulation

(c) Copyright Bprotocol foundation 2022. 
Licensed under MIT
"""
__version__ = "1.0"
__date__ = "21/Nov/2022"

import itertools
from typing import Callable, Any, Tuple, Dict, List

from tabulate import tabulate

from ..order import Order
from ..pair import CarbonPair
from ..carbon_order_ui import CarbonOrderUI
from ..routers import ExactRouterX0Y0N, AlphaRouter
from decimal import Decimal
import pandas as pd
import numpy as np


class CarbonSimulatorUI:
    """
    Providing the user interface for the Carbon simulation

    :verbose:           if True (default), the simulation logger. infos out info along the way
    :pair:              if given, Simulation methods uses this pair as default; other pairs
                        can still be used, but need to be explicitly mentioned
    :raiseonerror:      if False (default), errors are caught and returned to the result dict
    :matching_method:   if "exact" (default), the exact matching algorithm is used; otherwise the "fast" algorithm
    :decimals:          the number of decimals to which the output is rounded
    """

    def __init__(
        self,
        verbose: bool = False,
        pair: Any = None,
        raiseonerror: bool = False,
        decimals: int = 6,
        matching_method: str = "exact",
    ):
        self._pos_id = itertools.count()
        self.verbose = verbose
        self.debug = False  # setting this to True enables debug output

        if isinstance(pair, CarbonPair):
            #print("[__init__] CarbonPair provided", pair)
            self.pair = pair.pair_iso
            self._carbon_pair = pair
        else:
            self.pair = pair
            self._carbon_pair = None

        self.raiseonerror = raiseonerror
        self.numtrades = 0
        self.decimals = decimals
        self.matcher = (
            AlphaRouter(verbose=False) if matching_method == 'alpha' 
            else ExactRouterX0Y0N(verbose=False)
        )        
        self.orders = {}
        self.vault = {}
        self.trades = {}

        if self.verbose:
            print(
                f"[__init__] pair={pair}, verbose={verbose}, raiseonerror={raiseonerror}"
            )

    @property
    def default_basetoken(self):
        """
        returns the default base token of the sim (only if initialised with CarbonPair)
        """
        return self._carbon_pair.tknb if self._carbon_pair else None
    tknb = default_basetoken

    @property
    def default_quotetoken(self):
        """
        returns the default quote token of the sim (only if initialised with CarbonPair)
        """
        return self._carbon_pair.tknq if self._carbon_pair else None
    tknq = default_quotetoken

    def get_carbon_pair(self, pair: str=None, tkn: str=None) -> Tuple[CarbonPair, str]:
        """
        helper functon determining the pair from function params and class defaults

        :pair:      a string determining the pair, or CarbonPair (which is simply returned)
        :tkn:       one token that is part of the pair
        :returns:   CarbonPairStatic object, or raises
        """
        if isinstance(pair, CarbonPair):
            return pair

        if pair is None:
            if self._carbon_pair:
                # no pair is given here, we have a carbon pair in the defaults -> that's it
                return self._carbon_pair
            pair = self.pair

        if pair is None:
            raise ValueError(
                "Trading pair must be provided either in function call or in simulation defaults"
            )
        return CarbonPair.from_isopair_and_tkn(pair, tkn)

    @property
    def carbon_pair(self):
        """return the default CarbonPair associated with this object, or None"""
        try:
            cp = self.get_carbon_pair()
            return cp
        except:
            return None

    def price_convention(self, pair, tkn):
        """
        gets the price convention associated with `pair`

        :pair:      a string describing the pair (eg, "ETHUSDC")
        :tkn:       any constituent token of pair; required to split the pair into its
                    token parts; no other semantic meaning
        :returns:   a string describing the price convention (eg "USDC per ETH")
        """
        carbon_pair = self.get_carbon_pair(pair, tkn)
        return carbon_pair.price_convention

    def _add_pos(
        self,
        tkn: str,
        amt: Any,
        p_lo: Any,
        p_hi: Any,
        carbon_pair: CarbonPair,
        id1: int = None,
        id2: int = None,
    ) -> int:
        """
        PRIVATE - adds a position for sale of tkn

        :tkn:           the token that is being added to the position, eg "ETH"; it is the token being sold*
        :amt:           the amount of `tkn` that is added to the position
        :p_lo:          the lower end of the range, quoted with `tkn` as numeraire
        :p_hi:          ditto upper
        :carbon_pair:   the token pair a CarbonPair object
        :id1/2:         the order ids of the two orders that make up the position; if not given, they are generated
        :returns:       the id of the order added
        """

        # create order tracking ids
        if id1 is None:
            id1 = self._posid
        if id2 is None:
            id2 = id1

        # rearrange p_lo, p_hi if need be
        if not p_lo <= p_hi:
            pp = p_lo
            p_lo = p_hi
            p_hi = pp
            print("WARNING: swapped start and end of the range")

        # enter order
        order_params = {
            "tkn": tkn,                             # the token being sold
            "y_int": amt,                           # the capacity of the curve
            "_y": amt,                              # the initial holding is of the curve (in `tkn`)
            "p_low": p_lo,                          # the lower end of the range (`tkn` numeraire); also p_b
            "p_high": p_hi,                         # the upper end of the range (`tkn` numeraire); also p_a
            "pair_name": carbon_pair.pair_iso,      # the iso name of the pair
            "pair": carbon_pair,                    # the CarbonPair object
            "id": id1,                              # the id of the new curve generated
            "linked_to_id": id2,                    # the id to which this curve is linked (=id if single curve)
        }

        self.orders[id1] = Order(**order_params)
        return id1

    def add_sellorder(
        self, tkn: str, amt: Any, p_start: Any, p_end: Any, pair: str = None
    ) -> Dict[str, Any]:
        """
        adds a sell order for tkn

        :tkn:           the token that is being added to the position, eg "ETH"; it is the token being sold*
        :amt:           the amount of `tkn` that is added to the position
        :p_start:       the start* of the range, quoted in the currency of the pair
        :p_end:         ditto end*
        :pair:          the token pair to which the position corresponds, eg "ETHUSD"*

        *p_start, p_end are interchangeable, the code deals with sorting them correctly,
        albeit with a warning message if they were in the wrong order
        """
        try:

            # validate tkn, pair and get CarbonPair object (raises if tkn not part of pair)
            carbon_pair = self.get_carbon_pair(pair, tkn)

            # create order tracking ids
            id1 = self._posid

            # convert the prices from the pair numeraire to the curve numeraire
            p_start_c = carbon_pair.convert_price(p_start, tkn)
            p_end_c = carbon_pair.convert_price(p_end, tkn)

            # ugly hack, but somehow we need to switch lo and hi to have the
            # boundary closer to the money always first
            order_id = self._add_pos(
                tkn, amt, p_end_c, p_start_c, carbon_pair, id1, id1
            )

            if self.verbose:
                print(
                    f"[add_sgl_pos] added position: tkn={tkn}, amt={amt}, p_start={p_start}, p_end={p_end}, "
                    f"pair={carbon_pair.pair_iso}"
                )

            orders = self._to_pandas(self.orders[order_id], decimals=self.decimals)
            orderuis = {order_id: CarbonOrderUI.from_order(self.orders[order_id])}

        except Exception as e:
            if self.raiseonerror:
                raise
            return {"success": False, "error": str(e), "exception": e}
        return {"success": True, "orders": orders, "orderuis": orderuis}
    add_sgl_pos = add_sellorder
    add_order = add_sellorder

    def add_strategy(
        self,
        tkn: str,
        amt_sell: Any,
        psell_start: Any,
        psell_end: Any,
        amt_buy: Any,
        pbuy_start: Any,
        pbuy_end: Any,
        pair: str = None,
    ) -> Dict[str, Any]:
        """
        adds two linked orders (one buy, one sell; aka a "strategy")

        :tkn:           the token that is sold in the range psell_start/_end, eg "ETH"*
        :amt_sell:      the amount of `tkn` that is available for sale in range psell_start/psell_end
        :psell_start:   start of the sell `tkn` range*, quoted in the price convention of `pair`
        :psell_end:     ditto end
        :amt_buy:       the amount of the other token that is available for selling against tkn in range pbuy_start
        :pbuy_start:    start of the of the buy `tkn` range*, quoted in the price convention of `pair`
        :pbuy_end:      ditto end
        :pair:          the token pair to which the strategy corresponds, eg "ETHUSD"

        *px_start, px_end are interchangeable, the code deals with sorting them, albeit issuing a warning
        message if they are in the wrong order; sell and buy is seen from the perspective of the AMM, which
        is the same as that of the strategy (liquidity) provider
        """
        try:

            # validate tkn, pair and get CarbonPair object (raises if tkn not part of pair)
            carbon_pair = self.get_carbon_pair(pair, tkn)
            tkn2 = carbon_pair.other(tkn)

            # create order tracking ids
            id1 = self._posid
            id2 = self._posid

            # convert the prices from the pair numeraire to the curve numeraire
            psell_start_c = carbon_pair.convert_price(psell_start, tkn)
            psell_end_c = carbon_pair.convert_price(psell_end, tkn)
            pbuy_start_c = carbon_pair.convert_price(pbuy_start, tkn2)
            pbuy_end_c = carbon_pair.convert_price(pbuy_end, tkn2)

            # ugly hack but the 1/2 range boundaries are in the wrong order
            # we want the closer boundary first
            self._add_pos(
                tkn, amt_sell, psell_end_c, psell_start_c, carbon_pair, id1, id2
            )
            self._add_pos(
                tkn2, amt_buy, pbuy_end_c, pbuy_start_c, carbon_pair, id2, id1
            )

            if self.verbose:
                print(
                    f"[add_linked_pos] added tkn={tkn}, amt_sell={amt_sell}, psell_start={psell_start}, "
                    f"psell_end={psell_end}, amt_buy={amt_buy}, pbuy_start={pbuy_start}, pbuy_end={pbuy_end}, "
                    f"pair={carbon_pair.pair_iso}"
                )

            orders = pd.concat(
                [
                    self._to_pandas(o, decimals=self.decimals)
                    for o in [self.orders[id1], self.orders[id2]]
                ]
            )
            orderuis = {
                id1: CarbonOrderUI.from_order(self.orders[id1]),
                id2: CarbonOrderUI.from_order(self.orders[id2]),
            }

        except Exception as e:
            if self.raiseonerror:
                raise
            return {"success": False, "error": str(e), "exception": e}
        return {"success": True, "orders": orders, "orderuis": orderuis}
    add_linked_pos = add_strategy

    def delete_order(self, position_id):
        """
        deletes a positon / order or strategy

        :position_id:   the index of (one of) the orders to be deleted; this order, and all
                        orders linked to it will be removed
        :returns:       the orders removed as list, [] if not found
        """

        try:
            order = self.orders[position_id]
        except KeyError as e:
            if self.verbose:
                print(f"Position {position_id} does not exist: {e}")
            return []

        linked_position_id = order.linked_to_id
        if linked_position_id == position_id:
            linked_position_id = None

        pair = order.pair

        del self.orders[position_id]

        if linked_position_id:
            del self.orders[linked_position_id]

        if self.verbose:
            str2 = (
                f"and linked position {linked_position_id}"
                if linked_position_id
                else ""
            )
            print(f"Deleted position {position_id} {str2}[{pair}]")

        return (
            [position_id, linked_position_id] if linked_position_id else [position_id]
        )
    delete_pos = delete_order
    delete_strategy = delete_order

    def _trade(
        self,
        tkn: str,
        amt: Any,
        carbon_pair: CarbonPair,
        trade_action: Callable = None,
        trade_description: str = None,
        execute: bool = True,
        limit_price: Any = None,
        inpair: bool = True,
        use_positions: List[int] = None,
        threshold_orders: Any = None,
        use_positions_matchlevel: List[int] = [],

    ) -> Dict[str, Any]:
        """
        PRIVATE - executes a trade

        :tkn:                   the token that is being SOLD by the AMM, eg "ETH"*
        :amt:                   the amount to be traded*
        :carbon_pair:           the CarbonPair class of the token pair
        :trade_action:          either `match_by_target(...)` or `match_by_src(...)` method of the `self.matcher`
        :trade_description:     human-readable description of the trade, eg "amm vs trader, buy vs sell, for amt"
        :execute:               if True (default), the trade is executed; otherwise only routing is shown
        :limit_price:           the limit price of the order (this price or better from point of view
                                of the trader, not the AMM!), quoted in convention of the pair
        :inpair:                if True, only match within pair; if False (default), route through all available pairs
        :use_positions:         the positions to use for the trade (default: all positions)
        :threshold_orders:      the maximum number of order to be routed through using the alpha router

        *amt is always effectively a positive amount; however, if `trade_action` is `match_by_target` then it must
        be provided as a negative number, and if `match_by_src` as positive number
        """
        trades, orders = None, None
        try:
            decimals = self.decimals
            carbon_pair_r = carbon_pair.reverse

            if not inpair:
                raise NotImplementedError(
                    "Currently only inpair routing implemented", inpair
                )

            # parse applicable orders, indexes, and map the router ids to the simulator ids
            order_ids = [
                k
                for k in self.orders.keys()
                if self.orders[k].pair_name
                in [carbon_pair.pair_iso, carbon_pair_r.pair_iso]
                and self.orders[k].tkn == tkn
                if self.orders[k].y > 0
            ]
            use_positions = use_positions if use_positions is not None else order_ids
            applicable_orders = [v for k, v in self.orders.items() if k in order_ids and k in use_positions]
            id_map = {i: applicable_orders[i].id for i in range(len(applicable_orders))}

            if self.debug:
                print("[_trade] order_ids", order_ids)
                print("[_trade] id_map", id_map)
                print("[_trade] applicable_orders", applicable_orders)

            # set the router to only consider the applicable orders
            self.matcher.orders = applicable_orders

            # route the trade
            routes = trade_action(
                x = amt,
                threshold_orders=threshold_orders
                )

            # retrieve the final route
            final_route = routes[-1]

            #   :tkn:           the token that has been provided to the function
            #   :tkno:          the other token in the pair
            #   :tknb:          the base token of the pair
            #   :tknq:          the quote token of the pair
            tkno = carbon_pair.other(tkn)
            tknb = carbon_pair.tknb
            tknq = carbon_pair.tknq

            # :output:      the asset SOLD by the AMM, and BOUGHT by the TRADER
            #               output is a NEGATIVE number
            # :input:       the asset BOUGHT by the AMM, and SOLD by the TRADER
            #               input is a POSITIVE number
            raw_price = -final_route.total_output / final_route.total_input
            if self.debug:
                print("[_trade] final route", final_route)
                print(
                    f"[_trade] matchmethod={final_route.match_method} tkn={tkn} tkno={tkno}"
                )
                print(
                    f"[_trade] p={raw_price} num={tkn} (amm_in={final_route.total_input} "
                    f"amm_out= {final_route.total_output} mm={final_route.match_method})"
                )

            # the variable `tkn` always holds the token that goes OUT of the AMM
            # in other words: `total_output` is measured in `tkn` and `total_input` in `otkn`
            # therefore, the numeraire of raw_p = out/in is the token associated to out, `tkn`
            price_avg = carbon_pair.convert_price(raw_price, tkn)
            price_avg = round(float(price_avg), decimals)
            if self.debug:
                print("[_trade] final routes", routes)

            # we are using the function `limit_is_met` from CarbonPair; we need following inputs
            # :tkn:                 the reference token (see below)
            # :limit_price:         the limit price (execute there OR BETTER)*; this is simply the
            #                       `limit_price` parameter from the arguments
            # :buysell:             whether the person who submitted the order (here: the trader)
            #                       BUYs or SELLs (see below)
            # :currrent_price:      the price at which the transaction can be executed*; this is the
            #                        `price_avg` we've just calculated
            # *in units of the pair
            #
            # It is important to understand the following symmetry: a limit BUY order for ETH
            # at 2000 USDC per ETH is the same as a limit SELL order for USDC at 2000. We have
            # seen above that `tkn` is always the token going OUT of the AMM, therefore the
            # trader who placed the limit order BUYs it. Therefore we have
            # - `tkn`[limit_is_met] = `tkn`[function argument], and
            # - `buysell = BUY`

            if limit_price is not None:
                limitfail = not carbon_pair.limit_is_met(
                    tkn, limit_price, carbon_pair.BUY, price_avg
                )
                if limitfail:
                    execute = False
            else:
                limitfail = None

            price_at = []
            for route in routes:
                price_at += [route.input]
                route.input = round(float(route.input), decimals)
                route.output = round(float(route.output), decimals)
                route.total_price = round(abs(float(sum(price_at))), decimals)

            # iterate through the routes
            ct = 0
            trade_ids = []
            numtrades = self.numtrades
            for route in routes:

                # Get the mapped simulator index
                indx = id_map[route.index]
                if self.debug:
                    print("[_trade] final route.index", route.index)
                    print("[_trade] final indx", indx)

                amt1, amt2 = abs(route.output), abs(route.input)

                route_info = trade_description.replace("$", str(amt1)).replace(
                    "*", str(amt2)
                )

                if execute:
                    self.orders[indx].y -= Decimal(amt1)
                    if self.orders[indx].linked_to_id != indx:
                        self.orders[self.orders[indx].linked_to_id].y += Decimal(amt2)
                        if (
                            self.orders[self.orders[indx].linked_to_id].y
                            > self.orders[self.orders[indx].linked_to_id].y_int
                        ):
                            # if the linked order is overfilled, update the order y_int
                            self.orders[
                                self.orders[indx].linked_to_id
                            ].y_int = self.orders[self.orders[indx].linked_to_id].y

                # track the route info
                uid = f"{numtrades}.{ct}"
                trade_ids.append(uid)
                self.trades[uid] = {
                    "uid": [uid],  # =id.sub_id
                    "id": [numtrades],  # trade id
                    "subid": [ct],  # id of route withing trade (aggr=A)
                    "note": [f"route #{indx}"],  # human-readable note about this item
                    "aggr": [False],  # True iff this is the aggregate route
                    "exec": [
                        execute
                    ],  # True iff this trade has been executed (also False on limitfail)
                    "limitfail": [
                        limitfail
                    ],  # False if limit met, True if not, None if no limit
                    "amt1": [amt1],  # the amount of `tkn1` being sold by the AMM (>0)
                    "tkn1": [tkn],  # the token being SOLD by the AMM
                    "amt2": [amt2],  # the amount of `tkn2` being bought by the AMM (>0)
                    "tkn2": [tkno],  #  the token being BOUGHT by the AMM
                    "pair": [
                        carbon_pair.pair_iso
                    ],  # the isoname of the pair, indicating the quote token (eg ETHUSDC)
                    "routeix": [
                        indx
                    ],  # for routes: the index of the route; for aggr: list of routes
                    "nroutes": [
                        1
                    ],  # the number of routes across which the trade was executed
                    "price": [
                        price_avg
                    ],  # the price amt_/amt_, in the convention of the pair
                    "p_unit": [
                        f"{tknq} per {tknb}"
                    ],  # the units in which price is quote (eg USD per ETH)
                    "threshold_orders": [
                        threshold_orders
                    ], # the maximum number of order to be routed through using the alpha router
                }
                ct += 1
                if self.debug:
                    print("[_trade] routeinfo", route_info.replace("#", str(indx)))

            # Handle base token vs quote token variable swaps for the trade
            ttl_input = round(abs(routes[-1].total_input), decimals)
            ttl_output = round(abs(routes[-1].total_output), decimals)
            price_avg = f"{price_avg}"

            amt1, amt2 = ttl_output, ttl_input

            note = f"AMM sells {amt1:.0f}{tkn} buys {amt2:.0f}{tkno}"
            num_trades = len(routes)
            order_ids = [id_map[o.index] for o in routes]
            uid = f"{numtrades}"
            trade_ids.append(uid)
            self.trades[uid] = {
                "uid": [uid],  # see comments above
                "id": [self.numtrades],
                "subid": ["A"],
                "note": [note],
                "aggr": [True],
                "exec": [execute],
                "limitfail": [limitfail],
                "amt1": [amt1],
                "tkn1": [tkn],
                "amt2": [amt2],
                "tkn2": [tkno],
                "pair": [carbon_pair.pair_iso],
                "routeix": [str(order_ids)],
                "nroutes": [num_trades],
                "price": [price_avg],
                "p_unit": [f"{tknq} per {tknb}"],
                "threshold_orders": [threshold_orders],
            }

            # Get the trade info results
            if len(self.trades) > 0:
                trades = pd.concat([pd.DataFrame(self.trades[i]) for i in self.trades])
                trades = trades[trades["uid"].isin(trade_ids)]

            if self.verbose:
                print(note, f" ({num_trades} routes)")
            self.numtrades += 1

        except Exception as e:
            if self.raiseonerror:
                raise
            return {"success": False, "error": str(e), "exception": e}
        return {"success": True, "trades": trades}

    def amm_buys(
        self,
        tkn: str,
        amt: Any,
        pair: str = None,
        execute: bool = True,
        inpair: bool = True,
        limit_price: Any = None,
        threshold_orders: Any = None,
        use_positions: List[int] = None,
        use_positions_matchlevel: List[int] = [],
    ) -> Dict[str, Any]:
        """
        the AMM buys (and the trader sells) `amt` > 0 of `tkn`

        :tkn:               the token bought by the AMM and sold by the trader, eg "ETH"
        :amt:               the amount bought by the AMM and sold by the trader (must be positive)
        :pair:              the token pair to which the trade corresponds, eg "ETHUSD"
        :execute:           if True (default), the trade is executed; otherwise only routing is shown
        :inpair:            if True, only match within pair; if False (default), route through all available pairs
        :limit_price:       the limit price of the order (this price or better from point of view
                            of the trader, not the AMM!), quoted in convention of the pair
        :threshold_orders:  the maximum number of order to be routed through using the alpha router
        :use_positions: the positions to use for the trade (default: all positions)
        """

        try:

            if amt < 0:
                print(f"[amm_buys] negative amount {amt}; calling amm_sells")
                return self.amm_sells(
                    tkn = tkn,
                    amt = -amt,
                    pair = pair,
                    execute = execute,
                    inpair = inpair,
                    limit_price = limit_price,
                    threshold_orders = threshold_orders,
                    )

            # get the token `tkn`, the other token `tkno` and the CarbonPair object
            tkn, tkno, carbon_pair = self._get_tkn_and_validate(tkn, pair)
            self._assert_position_is_valid(tkno, carbon_pair)

            return self._trade(
                tkn=tkno,
                amt=Decimal(str(amt)),
                carbon_pair=carbon_pair,
                trade_action=self.matcher.match_by_src,
                trade_description=f"trader buys $ {tkno} sells * {tkn} | AMM sells $ {tkno} buys * {tkn} via "
                f"order #",
                execute=execute,
                limit_price=limit_price,
                inpair=inpair,
                threshold_orders=threshold_orders,
                use_positions=use_positions,
                use_positions_matchlevel=use_positions_matchlevel,
            )
        except Exception as e:
            if self.raiseonerror:
                raise
            return {"success": False, "error": str(e), "exception": e}
    trader_sells = amm_buys

    def amm_sells(
        self,
        tkn: str,
        amt: Any,
        pair: str = None,
        execute: bool = True,
        inpair: bool = True,
        limit_price: Any = None,
        threshold_orders: Any = None,
        use_positions: List[int] = None,
        use_positions_matchlevel: List[int] = [],
    ) -> Dict[str, Any]:
        """
        the AMM sells (and the trader buys) `amt` > 0 of `tkn`

        :tkn:               the token sold by the AMM and bought by the trader, eg "ETH"
        :amt:               the amount sold by the AMM and bought by the trader (must be positive)
        :pair:              the token pair to which the trade corresponds, eg "ETHUSD"
        :execute:           if True (default), the trade is executed; otherwise only routing is shown
        :inpair:            if True, only match within pair; if False (default), route through all available pairs
        :limit_price:       the limit price of the order (this price or better from point of view
                            of the trader, not the AMM!), quoted in convention of the pair
        :threshold_orders:  the maximum number of order to be routed through using the alpha router 
        :use_positions: the positions to use for the trade (default: all positions)
        """
        try:

            if amt < 0:
                print(f"[amm_sells] negative amount {amt}; calling amm_buys")
                return self.amm_buys(
                    tkn = tkn,
                    amt = -amt,
                    pair = pair,
                    execute = execute,
                    inpair = inpair,
                    limit_price = limit_price,
                    threshold_orders = threshold_orders,
                    )

            # get the token `tkn`, the other token `tkno` and the CarbonPair object
            tkn, tkno, carbon_pair = self._get_tkn_and_validate(tkn, pair)
            self._assert_position_is_valid(tkn, carbon_pair)

            return self._trade(
                tkn=tkn,
                amt=-Decimal(str(amt)),
                carbon_pair=carbon_pair,
                trade_action=self.matcher.match_by_target,
                trade_description=f"trader buys $ {tkno} sells * {tkn} | AMM sells $ {tkn} buys * {tkno} via "
                f"order #",
                execute=execute,
                limit_price=limit_price,
                inpair=inpair,
                threshold_orders=threshold_orders,
                use_positions=use_positions,
                use_positions_matchlevel=use_positions_matchlevel,

            )

        except Exception as e:
            if self.raiseonerror:
                raise
            return {"success": False, "error": str(e), "exception": e}
    trader_buys = amm_sells

    @staticmethod
    def _to_pandas(order: Order, decimals: int = 6) -> pd.DataFrame:
        """
        Exports Order values for inspection...
        """
        #print("[_to_pandas]", order.pair)

        orderui = CarbonOrderUI.from_order(order)
        #print("[_to_pandas]", orderui)
        dic = {
            "id": order.id,
            "pair": order.pair_name,
            "tkn": order.tkn,
            #"y_int": round(order.y_int, decimals),
            #"y": round(order.y, decimals),
            "y_int": float(order.y_int),
            "y": float(order.y),
            "y_unit": order.tkn,
            #"p_start": round(order.pair.convert_price(order.p_high, order.tkn), decimals),
            #"p_end": round(order.pair.convert_price(order.p_low, order.tkn), decimals),
            "p_start": float(order.pair.convert_price(order.p_high, order.tkn)),
            "p_end": float(order.pair.convert_price(order.p_low, order.tkn)),
            "p_marg": orderui.p_marg,
            "p_unit": order.pair.price_convention,
            "lid": order.linked_to_id,
        }
        return pd.DataFrame(dic, index=[order.id])

    def state(self, pair: str = None, inclhistory: bool = True) -> Dict[str, Any]:
        """
        returns a state record, describing the current state of the system

        :pair:          if None (default), the entire state of the system is provided; if it is set to a specific
                        value, only state corresponding to this specific `pair` is provided
        :inclhistory:   if True (default), also provide history, in particular trade history If False, no trades
                        are provided
        :returns:       a dict with the current state of the system where the values are pandas dataframes
        """
        try:

            if len(self.orders) > 0:
                if pair is not None:
                    if type(pair) is str:
                        pair = [pair]
                    applicable_orders = [
                        order
                        for order in self.orders.values()
                        if order.pair_name in pair
                    ]
                else:
                    applicable_orders = [order for order in self.orders.values()]
                orders = pd.concat(
                    [
                        self._to_pandas(o, decimals=self.decimals)
                        for o in applicable_orders
                    ]
                )
                orderuis = {o.id: CarbonOrderUI.from_order(o) for o in applicable_orders}
        
            else:
                orders = pd.DataFrame({})
                orderuis = dict()

            if len(self.trades) > 0:
                trades = pd.concat([pd.DataFrame(self.trades[i]) for i in self.trades])
            else:
                trades = pd.DataFrame({})

            if self.verbose and False:
                print("[state.orders]")
                print(
                    tabulate(orders, headers=list(orders.columns), tablefmt="pretty"),
                )
                print("\n\n[state.trades]")
                print(
                    tabulate(trades, headers=list(trades.columns), tablefmt="pretty"),
                )
            return {
                "orders": orders,
                "orderuis": orderuis,
                "trades": trades if inclhistory else False,
            }

        except Exception as e:
            if self.raiseonerror:
                raise
            return {"success": False, "error": str(e), "exception": e}

    ASDICT = "asdict"
    ASDF = "asdf"
    def liquidity(self, format=ASDICT):
        """
        returns the aggregate liquidity positions by pair and token, in units of the respective token(!)

        :asdf:      if True, returns the results as dataframe, otherwise as dict

        NOTE: if you pairs are provided in both directions (eg ETHUSDC and USDCETH), which is bad
        practice in any case, then those liquidity positions are not aggregated and the result
        must be corrected manually
        """
        try:
            df = pd.pivot_table(
                self.state()["orders"], 
                values=["y"], 
                index=["pair", "tkn"], 
                aggfunc=np.sum
            )
        except KeyError:
            return None 

        if format == self.ASDF:
            return df
        dct = df.to_dict(orient='dict')["y"] # yields {("ETHUSDC", ETH): ...}
        pairs = set(k[0] for k in dct)  # yields {"ETHUSDC", "ETHDAI", ...}
        result = {p:{k[1]:v for k,v in dct.items() if k[0]==p} for p in pairs} # yields {"ETHUSDC": {"ETH": ..., "USDC": ...}, ...}
        if format == self.ASDICT:
            return result
        raise ValueError(f"Unknown format {format}")

    @property
    def _posid(self) -> int:
        """
        PRIVATE - auto-incrementing position id
        """
        return next(self._pos_id)

    def _get_tkn_and_validate(self, tkn: str, pair: str) -> Tuple[str, Any, CarbonPair]:
        """
        PRIVATE - handles trade tkn, pair validations
        """
        carbon_pair = self.get_carbon_pair(pair, tkn)
        return tkn, carbon_pair.other(tkn), carbon_pair

    def _assert_tkn_is_in_positions(self, tkn: str):
        """
        PRIVATE - checks if tkn has any liquid (=non-empty) positions (raises if not)
        """
        if tkn not in {o.tkn for o in self.orders.values() if o.y > 0}:
            raise ValueError(f"token {tkn} has no non-empty liquidity positions")

    def _assert_pair_is_in_positions(self, carbon_pair: CarbonPair):
        """
        PRIVATE - checks if pair has any liquid positions (raises if not)
        """
        orders = {o.pair_name for o in self.orders.values() if o.y > 0}
        if (
            carbon_pair.pair_iso not in orders
            and carbon_pair.reverse.pair_iso not in orders
        ):
            raise ValueError(f"valid liquidity positions for {carbon_pair.pair_iso}")

    def _assert_position_is_valid(self, tkn: str, carbon_pair: CarbonPair):
        """
        PRIVATE - checks if tkn + pair exist and are valid (raises if not)
        """
        self._assert_tkn_is_in_positions(tkn)
        self._assert_pair_is_in_positions(carbon_pair)

    @property
    def numpos(self) -> int:
        """number of positions"""
        return len(self.orders)

    def __repr__(self):
        pair = self._carbon_pair if self._carbon_pair else self.pair
        return f"{self.__class__.__name__}(<{self.numpos} orders, {self.numtrades} trades>, pair='{pair}')"

