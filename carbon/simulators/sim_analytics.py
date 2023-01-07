"""
analytics classes and functions related to the simulation

All functions are included on the Analytics object, so you can import all of them as

    from sim_analytics import Analytics as A
    A.linspace(100)

Most functions are also exposed at module level, so alternatively you can do

    import sim_analytics as al
    al.linspace(100)


(c) Copyright Bprotocol foundation 2022. 
Licensed under MIT

VERSION HISTORY
- v2.0.2: chart markers
- v2.1: order book improvements (data_orderbook_chart, data_price_chart, data_tokenamount_chart)
"""
__version__ = "2.1-beta2"
__date__ = "7/Jan/2022"

import numpy as np
import pandas as pd
from collections import namedtuple
from ..pair import CarbonPair
from matplotlib import pyplot as plt
from math import isnan
    

class Analytics:
    """
    collection of analytics functions useful for Carbon simulations

    :sim:       the CarbonSimulatorUI object

    NOTE: this library relies heavily on numpy, and all vectors are in fact numpy arrays
    """
    __VERSION__ = __version__
    __DATE__    = __date__

    def __init__(self, sim=None, verbose=False):
        self.sim = sim
        self.verbose = verbose

    @staticmethod
    def midpoints(r):
        """
        calculates the midpoints: (x0, x1, x2, ...) -> (avg(x0,x1), avg(x1,x2), ...)
        """
        return Analytics.vec([0.5*(x1+x2) for x1,x2 in zip(r, r[1:])])

    @staticmethod
    def diff(vec):
        """
        calculates the differences: (x0, x1, x2, ...) -> (x1-x0, x2-x1, ...)
        """
        return Analytics.vec(np.diff(vec))
        # return np.diff(vec)

    @staticmethod
    def vec(v):
        """
        converts iterable into vector*

        *currently our vector format is np.array; however, this is NOT guaranteed and we may
        switch over to a difference vector implementation the allows for basic vector operations
        (component-wise +-*/ using the usual syntax)
        """
        return pd.Series(v)
        # return np.array(v)

    @staticmethod
    def vecdot(v1, v2):
        """implements the dot product (sumproduct)"""
        return v1.fillna(0).dot(v2.fillna(0))
        # try:
        #     return np.dot(v1, v2)
        # except TypeError:
        #     v1a = [0 if x is None else x for x in v1]
        #     v2a = [0 if x is None else x for x in v2]
        #     print(f"[vecdot] typeerror {v1} {v2}; using {v1a} {v2a}")
        #     return np.dot(v1a, v2a)
            
    EPSILON = 0.0001
    EPSILON2 = 0.00001
    @classmethod
    def linspace0(cls, xmax, nint=10, eps=None, eps2=None):
        """
        generates a linearly spaced vector of floats (0+eps, x1, x2, ... xmax*(1-eps2))

        :xmax:          maximum x to be generated
        :nint:          number of intervals, ie numper of points - 1

        The function generates nint equally space intervals (nint+1 points), starting
        from ~0 and ending at ~xmax. The intermediate points are based on the exact
        interval (0, xmax). Once the series has been generated to following adjustments
        are made for numerical stability reasons

            vec[0]  = eps
            vec[-1] = (1-eps2) * maxx
        """
        if eps is None: eps = cls.EPSILON
        if eps2 is None: eps2 = cls.EPSILON2
        vec = np.linspace(0,xmax, nint+1)
        vec[0] = eps
        vec[-1] = (1-eps2) * xmax
        return cls.vec(vec)
        # return vec

    @classmethod
    def linspace(cls, *args, **kwargs):
        """
        alias for numpy linspace, but returning a vec()
        
        eg linspace(10,20,3) -> vec([10,15,20])
        """
        return cls.vec(np.linspace(*args, **kwargs)) 

    @staticmethod
    def isnonenan(x):
        """
        returns true if None or Nan, False else
        """
        if x is None: return True
        try:
            return isnan(x)
        except:
            return False
    
    @classmethod
    def truncate(cls, s1, s2):
        """
        truncates both series to the same length, removing NaN / None from the end of the second
        
        :s1:                shortened if need be to the length of s2
        :s2:                truncated of NaN / None at the end
        :returns:           truncated (s1, s2)
        """
        s2r = cls.vec(x for x in s2 if not cls.isnonenan(x))
        s1r = s1[:len(s2r)]
        return s1r, s2r

    BID_BOOK = "amm_buys"
    BID = BID_BOOK
    ASK_BOOK = "amm_sells"
    ASK = ASK_BOOK
    OFFER_BOOK = ASK_BOOK
    OFFER = ASK_BOOK
    MAXPRICE = 1E100        # price returned if out of liquidity for amm_buys
    
    def effective_price(self, size, bidask, tkn=None, sim=None, pair=None):
        """
        returns the price at which `tkn` can be bought or sold in `size`

        :size:          the amount of tkn being bought or sold
        :bidask:        whether  to look at the bid book (AMM buys) or the ask book (AMM sells)
                        use the constants BID=BID_BOOK, ASK=ASK_BOOK
        :tkn:           the token being bought or sold (usually the base token of the pair)
                        can be omitted if the sim is provided and has been seeded with CarbonPair
        :sim:           the CarbonSimulatorUI object (from self.sim if None)
        :pair:          the corresponding pair (if none, use sim defaults)
        """
        if sim is None: sim = self.sim

        if tkn is None:
            if sim is None:
                raise ValueError("If tkn is None then sim must be provided in arguments or class defaults")
            tkn = sim.default_basetoken
            if tkn is None:
                raise ValueError(f"The sim provided does not specify a basetoken [{sim}]")

        if pair is None: 
            if sim is None:
                raise ValueError("If pair is None then sim must be provided in arguments or class defaults")
            pair = sim.pair 
        if bidask == self.BID_BOOK: 
            price_f = sim.amm_buys
            fail_value = self.MAXPRICE
        elif bidask == self.ASK_BOOK: 
            price_f = sim.amm_sells
            fail_value = 0.
        else:
            raise ValueError(f"Illegal value for bidask [{bidask}]")
        
        try:
            result = price_f(tkn, size, execute=False, pair=pair)
            price = result["trades"].iloc[-1]["price"]
            if self.verbose:
                print(f"[effective_price] trading size={size} price={price} [pair={pair}, tkn={tkn} {bidask}]")
            return float(price)
        except:
            return fail_value


    AMM_SELLS_BASETOKEN = "amm_sells_tknb"
    ASK = "amm_sells_tknb"
    AMM_BUYS_BASETOKEN = "amm_buys_tknb"
    BID = "amm_buys_tknb"
    
    def simulate_trades(self, src_size, buysell, sim=None, carbon_pair=None):
        """
        returns amount against which `tkn` can be traded (bought or sold) or sold in `src_size`

        :src_size:          the amount of the source tkn being sold or bought (always positive!)
        :buysell:           either AMM_SELLS_BASETOKEN or AMM_BUYS_BASETOKEN
        :sim:               the CarbonSimulatorUI object (from self.sim if None)
        :carbon_pair:       the corresponding pair as CarbonPair object (if none, use sim defaults)
        """
        if sim is None: sim = self.sim
        if carbon_pair is None:
            if self.sim is None:
                raise ValueError("The `sim` object must be provided and have a default carbon pair if `carbon_pair` is not given.")
            sim = self.sim
            if sim.carbon_pair is None:
                raise ValueError("The `sim` object must have a default carbon pair if `carbon_pair` is not given.")
            carbon_pair = sim.carbon_pair
        if not isinstance(carbon_pair, CarbonPair):
            raise ValueError("The `carbon_pair` provided is not a CarbonPair instance", carbon_pair)

        pair = carbon_pair.slashpair
        tkn = carbon_pair.tknb
        if buysell == self.AMM_SELLS_BASETOKEN:
            func = sim.amm_sells
            fail_value = None
            ix = "amt2"
        elif buysell == self.AMM_BUYS_BASETOKEN:
            func = sim.amm_buys
            fail_value = None
            ix = "amt1"
        else:
            raise ValueError(f"Unknonwn buysell {buysell}")
        try:
            result = func(tkn, src_size, execute=False, pair=pair)
            trg_size = result["trades"].iloc[-1][ix]
            result = trg_size
        except:
            result = fail_value
        if self.verbose:
            print(f"[simulate_trades] trading src={src_size} trg={result} [pair={pair}, tknb={tkn} {buysell}]")
        return result
            
    def __repr__(self):
        return f"{self.__class__.__name__}(sim={self.sim})"

orders_nt = namedtuple("orders_nt", 'tkn, amt, p_start, p_end')
midpoints = Analytics.midpoints
linspace0 = Analytics.linspace0
linspace = Analytics.linspace
diff = Analytics.diff
vec = Analytics.vec
vecdot = Analytics.vecdot
truncate = Analytics.truncate
isnonenan = Analytics.isnonenan

class OrderBook():
    """
    this class represents a (numerical) order book
    
    :src_amounts:       a vector of trade sizes (`src_tkn`; always positive)
    :trg_amounts:       a vector of tokens received in those trades (`trg_tkn`; alwaus positive)
    :src_tkn:           the name of the source token (ie the one appearing on the x-axis driving the deal)
    :trg_tkn:           ditto target token (ie the other one, the one that is reacting)



    The OrderBook class in particular prepares the data to draw a number
    of charts, eg with the matplotlib command

        plt.plot(x, y)

    Below we indicate which properties provide the data for which chart
    (we assume the OrderBook object is called `ob`)

    - Token Amount chart: plots the amount of token in vs out
        :x:     ob.src_amounts
        :y:     ob.trg_amounts

    - Price chart: plots the effective (1) and marginal (2) prices vs out amount
        :x1:    ob.src_amounts
        :y1:    ob.prices
        :x2:    ob.midpoints(ob.src_amounts)
        :y2:    ob.marg_prices

    - Order Book chart: plots the order book (marginal liquidity vs price)
        :x:     ob.ob_liquidity
        :y:     ob.ob_prices

    - Liquidity Depth chart: plots liquidity depth (cumulative order book)
        :x:
        :y:

    """
    __VERSION__ = __version__
    __DATE__    = __date__
    
    ASK = "ASK_amm_sells_src_tkn"
    BID = "BID_amm_buys_src_tkn"
    def __init__(self, src_amounts, trg_amounts, src_tkn="SRC", trg_tkn="TRG", bidask=ASK):
        src_amounts, trg_amounts = Analytics.truncate(src_amounts, trg_amounts)
        self.src_amounts = Analytics.vec(src_amounts)
        self.trg_amounts = Analytics.vec(trg_amounts)
        self.src_tkn = src_tkn
        self.trg_tkn = trg_tkn
        self.bidask = bidask
        if bidask == self.ASK:
            self.reverse_book = False
        elif bidask == self.BID:
            self.reverse_book = True
        else:
            raise ValueError(f"illegal value for bidask {bidask}")

    @property
    def base_tkn(self):
        """returns the base token (=self.src_tkn)"""
        return self.src_tkn

    @property
    def quote_tkn(self):
        """returns the quote token (=self.trg_tkn)"""
        return self.trg_tkn

    def explain(self):
        """
        human-readable explanation 
        """
        ba    = 'ASK' if self.bidask==self.ASK else 'BID'
        msg0  = f"This is the {ba} book."
        msg1  = f"Source token = {self.src_tkn}, target token = {self.trg_tkn}."
        bs    = "sells" if self.bidask == self.ASK else "buys"
        msg2  = f"AMM {bs} {self.src_tkn} for {self.trg_tkn}."
        msg3  = f"Base token = {self.base_tkn}, quote token = {self.quote_tkn}."
        msg3b = f"Prices are quoted in {self.prices_u}."
        msg4  = f"Order book amounts are quoted in {self.ob_liquidity_u}."
        return "\n".join([msg0, msg1, msg2, msg3, msg3b, msg4])

    @property
    def src_token_outin(self):
        """'out' if source token goes out, 'in' otherwise"""
        return "in" if self.reverse_book else "out"

    @property
    def trg_token_outin(self):
        """'out' if target token goes out, 'in' otherwise"""
        return "out" if self.reverse_book else "in"

    @property
    def amm_buysell_src(self):
        """'sells' if AMM sells source token, 'buys' otherwise"""
        return "buys" if self.reverse_book else "sells"

    @property
    def amm_buysell_trg(self):
        """'sells' if AMM sells target token, 'buys' otherwise"""
        return "sells" if self.reverse_book else "buys"

    @property
    def amm_bidask(self):
        """'ask' if AMM sells target token, 'bid' otherwise"""
        return "bid" if self.reverse_book else "ask"

    @property
    def marg_trg_amounts(self):
        """
        the marginal in amounts (amt1-amt0, amt2-amt1, ...)
        """
        return Analytics.diff(self.trg_amounts)

    @property
    def marg_src_amounts(self):
        """
        the marginal out amounts (amt1-amt0, amt2-amt1, ...)
        """
        return Analytics.diff(self.src_amounts)

    @property
    def prices(self):
        """
        returns the effective prices (trg_amounts / src_amounts)
        """
        return self.trg_amounts / self.src_amounts
    
    def pricesr(self, reverse=True):
        """
        returns the reverse effective prices (1/prices) if reverse True (default), otherwise prices
        """
        return 1/self.prices if reverse else self.prices
    
    @property
    def marg_prices(self):
        """
        returns the reverse marginal prices (marg_src_amounts / marg_trg_amounts)
        """
        return self.marg_trg_amounts / self.marg_src_amounts 
    
    def marg_pricesr(self, reverse=True):
        """
        returns the reverse effective prices (1/marg_prices) if reverse True (default), otherwise marg_prices
        """
        return 1/self.marg_prices if reverse else self.marg_prices
    
    @property
    def prices_u(self):
        """
        unit of `prices`, `marg_prices`, etc
        """
        return f"{self.quote_tkn} per {self.base_tkn}"
    marg_prices_u = prices_u

    def pricesr_u(self, reverse=True):
        """
        unit of `pricesr`, `marg_pricesr`, etc
        """
        return f"{self.src_tkn} per {self.trg_tkn}" if reverse else self.prices_u
    marg_pricesr_u = pricesr_u
    
    @property
    def ob_liquidity(self):
        """
        returns the order book liquidity at the price points corresponding to `ob_prices`
        """
        return self.midpoints(self.marg_trg_amounts) / self.dmarg_prices

    @property
    def dmarg_prices(self):
        """
        returns the differences of marginal prices (dp1-dp0, dp2-dp1, ...)

        Note: the dot product `Analytics.vecdot(dmarg_prices, ob_liquidity)`, which corresponds
        to the area under the curve, is approximately the entire liquidity in the curve, 
        ie the same as `max(trg_amounts)`
        """
        result = Analytics.diff(self.marg_prices)
        if self.reverse_book:
            result = - result
        return result
    
    @property
    def ob_liquidity_u(self):
        """
        returns the units of ob_liquidity
        """
        return f"{self.trg_tkn}"

    @property
    def ob_prices(self):
        """
        returns the prices corresponding to the order book liquidity in `ob_liquidity`
        """
        return self.midpoints(self.marg_prices)
    ob_prices_u = prices_u

    @staticmethod
    def reverse(vec):
        """
        returns inverse of vec = (x0, x1, ..) -> (1/x0, 1/x1, ...)
        """
        return 1/vec
    inverse = reverse

    @staticmethod
    def midpoints(vec):
        """
        alias for Analytics.midpoints
        """
        return Analytics.midpoints(vec)
    mp = midpoints

    @staticmethod
    def calc_liquidity_approx(orderuis, prices, pair, reverse=True, purgezero=True):
        """
        calculates the approximate liquidity of all positions
        
        :orderuis:      the dict returned by Sim.state()["orderuis"]
                        
        :prices:        the price range over which to calculate the liquidity
                        eg al.linspace(500,3000,100)
        :pair:          the pair (CarbonPair object) for which to calculate the liquidity
                        eg CarbonPair(tknb="ETH", tknq="USDC"); note that the curve 
                        price convention MUST be the same as the one in orderuis
        :reverse:       if True (default), calculate the liquidity in terms of quote token
                        (eg USDC); otherwise calculate it in terms of base token (eg ETH)
        :purgezero:     if True (default), replace zeroes with None
        :returns:       example {"ask":list, "bid":list, "prices":list, "pair":CarbonPair
                        "price_u":"USDC per ETH", "liqtkn_u":"USDC", "reverse": True}
        """
        if not isinstance(pair, CarbonPair):
            raise ValueError("Pair must be a CarbonPair", pair)
        
        pair_iso = pair.pair_iso
        tkn_ask = pair.tknb
        tkn_bid = pair.tknq
        print(f"[calc_liquidity_approx] pair:{pair_iso}", tkn_ask, tkn_bid)
        
        curves_ask = [
            r for r in orderuis.values() 
            if r.pair.pair_iso == pair_iso and r.tkn == tkn_ask
        ]
        curves_bid = [
            r for r in orderuis.values() 
            if r.pair.pair_iso == pair_iso and r.tkn == tkn_bid
        ]
        print(f"[calc_liquidity_approx] ask:{len(curves_ask)} bid:{len(curves_bid)}")
        
        tkn = pair.tknq if reverse else pair.tknb
        print(f"[calc_liquidity_approx] tkn={tkn}")
        liq_ask = [
            sum(r.liquidity_approx(p1, p2, tkn)/(p2-p1) for r in  curves_ask) 
            for p1, p2 in zip(prices, prices[1:])
        ]
        liq_bid = [
            sum(r.liquidity_approx(p1, p2, tkn)/(p2-p1) for r in  curves_bid) 
            for p1, p2 in zip(prices, prices[1:])
        ]
        pp = [0.5*(p1+p2) for p1, p2 in zip(prices, prices[1:])]
        
        if purgezero:
            liq_ask = [x if x else None for x in liq_ask]
            liq_bid = [x if x else None for x in liq_bid]
            
        return {
            "bid":      liq_bid, 
            "ask":      liq_ask,
            "prices":   pp,
            "pair":     pair,
            "price_u":  pair.price_convention,
            "liqtkn_u": tkn,
            "reverse":  reverse,
        }



    COLOR_BID = "g"
    COLOR_ASK = "r"

    @property
    def colorba(self):
        """returns the correct color depending on bid/ask"""
        return self.COLOR_BID if self.bidask==self.BID else self.COLOR_ASK
    
    def plot_tokenamount_chart(self):
        """
        plots the token amount chart based on the order book in self
        """
        ob=self
        # x = ob.src_amounts
        # y = ob.trg_amounts
        data = self.data_tokenamount_chart()
        x = data["src"]
        y = data["trg"]
        plt.plot(x, y, marker="", label="token amount")
        plt.title(f"Token trade (AMM {ob.amm_buysell_src} {ob.src_tkn}, {ob.amm_buysell_trg} {ob.trg_tkn})")
        plt.xlabel(f"Tokens {ob.src_token_outin} ({data['src_unit']})")
        plt.ylabel(f"Tokens {ob.trg_token_outin} ({data['trg_unit']})")
        plt.grid()
        #plt.legend()
        return f"plotted tokens received against trade size ({int(max(y)):,})"

    def data_tokenamount_chart(self, aspandas=False):
        """
        returns the data underlying the orderbook chart

        :aspandas:   if True, return data as data frame, otherwise dict
        """
        x = self.src_amounts
        y = self.trg_amounts
        result  = {
            "x": x,
            "src": x,
            "y": y,
            "trg": y,
            "src_unit": self.src_tkn,
            "trg_unit": self.trg_tkn,
        }
        if not aspandas:
            return result
        x_s = pd.Series(x, name=f"src_amt [{result['src_unit']}]")
        y_s = pd.Series(y, name=f"trg_amt [{result['trg_unit']}]")
        return pd.DataFrame([x_s, y_s]).T


    def plot_price_charto(self):
        """
        plots the price chart based on the order book in self
        """
        ob=self
        x1 = ob.src_amounts
        y1 = ob.prices
        plt.plot(x1, y1, marker="", label="effective price")
        x2 = ob.midpoints(x1)
        y2 = ob.marg_prices
        plt.plot(x2, y2, marker="", label="marginal price")
        plt.title("Price against trade size")
        plt.xlabel(f"Trade size ({ob.src_tkn}; AMM {ob.amm_buysell_src})")
        plt.ylabel(f"Price ({ob.trg_tkn} per {ob.src_tkn})")
        plt.grid()
        plt.legend()
        return "plotted marginal and effective prices against trade size"

    def plot_price_chart(self, reverse=False):
        """
        plots the price chart based on the order book in self
        """
        ob=self
        # x1 = ob.src_amounts
        # y1 = ob.pricesr(reverse)
        # x2 = ob.midpoints(x1)
        # y2 = ob.marg_pricesr(reverse)
        data = self.data_price_chart(reverse)
        x1 = data["size1"]
        y1 = data["price1_eff"]
        x2 = data["size2"]
        y2 = data["price2_marg"]
        plt.plot(x1, y1, marker="", label="effective price")
        plt.plot(x2, y2, marker="", label="marginal price")
        plt.title("Price against trade size")
        plt.xlabel(f"Trade size ({data['size_unit']}; AMM {data['ammm_buysell_src']})")
        plt.ylabel(f"Price ({data['prices_unit']})")
        plt.grid()
        plt.legend()
        return "plotted marginal and effective prices against trade size"

    def data_price_chart(self, reverse=False, aspandas=False):
        """
        returns the data underlying the price chart

        :aspandas:   if True, return data as data frame, otherwise dict
        """
        x1 = self.src_amounts
        y1 = self.pricesr(reverse)
        x2 = self.midpoints(x1)
        y2 = self.marg_pricesr(reverse)
        result  = {
            "x1": x1,
            "size1": x1,
            "y1": y1,
            "price1_eff": y1,
            "x2": x2,
            "size2": x2,
            "y2": y2,
            "price2_marg": y2,
            "ammm_buysell_src": self.amm_buysell_src,
            "size_unit": self.src_tkn,
            "prices_unit": self.pricesr_u(reverse),
        }
        if not aspandas:
            return result

        x1_s = pd.Series(x1, name=f"size1 [{result['size_unit']}]")
        y1_s = pd.Series(y1, name=f"price1_eff [{result['prices_unit']}]")
        x2_s = pd.Series(x2, name=f"size2 [{result['size_unit']}]")
        y2_s = pd.Series(y2, name=f"price2_marg [{result['prices_unit']}]")
        return pd.DataFrame([x1_s, y1_s, x2_s, y2_s, ]).T

    def plot_orderbook_chart(self, xmin=None, xmax=None, ymax=None, otherob=None):
        """
        plots order book chart based on the order book in self
        
        :otherob:   if given, also plot the other orderbook into the same chart
        """
        ob = self
        # y = ob.ob_liquidity
        # x = ob.ob_prices
        data = self.data_orderbook_chart()
        x = data["prices"]
        y = data["liquidity"]
        x_u = data["prices_unit"]
        y_u = data["liquidity_unit"]
        
        plt.plot(x, y, marker="", color=self.colorba, label=f"{ob.amm_bidask}")
        if otherob:
            yo = otherob.ob_liquidity
            xo = otherob.ob_prices
            plt.plot(xo, yo, marker="", color=otherob.colorba, label=f"{otherob.amm_bidask}")

        fragment = f" ({ob.amm_bidask})" if not otherob else " (bid and ask)"
        plt.title(f"Order book{fragment}")
        plt.xlabel(f"Price ({x_u})")
        plt.ylabel(f"Liquidity ({y_u})")
        plt.grid()
        if otherob:
            plt.legend()
        plt.xlim(xmin,xmax)
        plt.ylim(0,ymax)
        return f"plotted order book ({int(Analytics.vecdot(ob.dmarg_prices,y)):,})"

    def data_orderbook_chart(self, aspandas=False):
        """
        returns the data underlying the orderbook chart

        :aspandas:   if True, return data as data frame, otherwise dict
        """
        liq = self.ob_liquidity
        prc = self.ob_prices
        result  = {
            "liquidity": liq,
            "x": liq,
            "prices": prc,
            "y": prc,
            "liquidity_unit": self.ob_liquidity_u,
            "prices_unit": self.ob_prices_u,
        }
        if not aspandas:
            return result

        liq_s = pd.Series(liq, name=f"Liquidity [{result['liquidity_unit']}]")
        prc_s = pd.Series(prc, name=f"Price [{result['prices_unit']}]")
        return pd.DataFrame([prc_s, liq_s]).T

    @staticmethod
    def plot_approx_orderbook_chart(l):
        """
        plots approximate order book chart
        
        :l:   result returned from calc_liquidity_approx()
        """
        plt.title(f"Approximate Order Book (tknb={l['pair'].tknb}, tknq={l['pair'].tknq})")
        plt.xlabel(f"Price ({l['price_u']})")
        plt.ylabel(f"Liquidity ({l['liqtkn_u']})")
        plt.plot(l['prices'], l['bid'], color="g", label="bid")
        plt.plot(l['prices'], l['ask'], color="r", label="ask")
        plt.grid()
        plt.legend()

    def __repr__(self):
        return f"{self.__class__.__name__}(<src={self.src_tkn} trg={self.trg_tkn} bidask={self.bidask} rev={self.reverse_book}; {len(self.src_amounts)-1} records>)"

calc_liquidity_approx       = OrderBook.calc_liquidity_approx
plot_approx_orderbook_chart = OrderBook.plot_approx_orderbook_chart


