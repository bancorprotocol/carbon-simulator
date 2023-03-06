"""
wrapper classes for the node-based Carbon SDK via http
"""
__VERSION__ = "0.9"
__DATE__ = "8/Mar/2023"

import requests
from math import log10, floor
from .sdktoken import SDKToken, TokenContainer, Tokens
from ..pair import CarbonPair
from dataclasses import dataclass


class SDKBase:
    """
    base class for SDK access via http

    :url:           RPC URL
    :token:         API token
    :apibase:       API base path
    :syncdefault:   if True, by default call the sync endpoint
    :raiseonerror:  if True, serious errors raise an exception
    :disclaimer:    if True, print a disclaimer on instantiation
    :verbose:       if True, print messages when connecting
    :Tokens:        Token container object for token lookup
    """
    __VERSION__ = __VERSION__
    __DATE__ = __DATE__
    
    URL = None              # to be set in derived class
    TOKEN = None            # to be set in derived class
    APIBASE = None          # to be set in derived class
    SYNCDEFAULT = True      # if True, by default call the sync endpoint
    RAISEONERROR = True     # if True, serious errors raise an exception
    DISCLAIMER = True       # if True, print a disclaimer on instantiation
    VERBOSE = True          # if True, print messages when connecting
    
    def __init__(self, url=None, token=None, apibase=None, syncdefault=None, 
                        raiseonerror=None, disclaimer=None, verbose=None, Tokens=None):
        if url is None: url = self.URL
        self.url = url
        if token is None: token = self.TOKEN
        self.token = token
        if apibase is None: apibase = self.APIBASE
        self.apibase = apibase
        if syncdefault is None: syncdefault = self.SYNCDEFAULT
        self.syncdefault = syncdefault
        if raiseonerror is None: raiseonerror = self.RAISEONERROR
        self.raiseonerror = raiseonerror
        if disclaimer is None: disclaimer = self.DISCLAIMER
        self.disclaimer = disclaimer
        if verbose is None: verbose = self.VERBOSE
        self.verbose = verbose
        self.Tokens = Tokens
        if self.disclaimer:
            print(self.DISCLAIMERTEXT)
        
    POST = "post"
    GET  = "get"

    DISCLAIMERTEXT = """
    ================================================================
    WARNING: DO NOT USE IN PRODUCTION

    This is a demo and testing wrapper for the Carbon SDK. YOU MUST 
    NOT USE THIS SDK, OR ITS ASSOCIATED NODEJS CODE IN PRODUCTION 
    WHEN FUNDS ARE AT RISK. See the disclaimer on the Carbon SDK 
    NodeJS server for more information.
    ================================================================
    """

    class CarbonSDKValueError(ValueError): pass
    
    def _assertTokensProvided(self):
        if self.Tokens is None:
            raise self.CarbonSDKValueError("Tokens not provided in constructor to SDK", self)
    
    @dataclass
    class ErrorResponse():
        """
        dummy class for error responses from the SDK [returns 900 status code]
        """
        error: str

        @property
        def status_code(self):
            return 900
        
        def json(self):
            return {"status_code": self.status_code, "error": self.error}


    def req0(self, path, params=None, method=None):
        """
        execute a GET or POST request to the API server

        :path:      the full path of the call (everything after the server URL)
        :params:    the params transmitted to the API (POST only)
        :method:    self.GET or self.POST (default GET with no params, POST with)
        """
        if method is None: 
            method = self.GET if params is None else self.POST
            #print ("[req0] method is None, setting to", method, params)
        if params is None: params = dict()
        if method == self.GET and params:
            raise self.CarbonSDKValueError("Must not provide params for GET request", params, method)

        url = self.join(self.URL, path)
        if self.verbose:
            print(f"[req0] method={method}, url={url}, params={params}")
        if method == self.GET:
            try:
                return requests.get(url, headers={"token": self.token})
            except Exception as e:
                return self.ErrorResponse(error=str(e))
            
        elif method == self.POST:
            try:
                return requests.post(url, headers={"token": self.token}, json=params)
            except Exception as e:
                return self.ErrorResponse(error=str(e))
        else:
            raise self.CarbonSDKValueError("Unknown method", method)
    
    def req(self, ep, params=None, method=None):
        """
        execute a GET or POST request to the actual API

        :ep:        API endpoint, including the sync/async prefix (eg 'scall/plus')
        :params:    params transmitted to the API (POST only)
        :method:    self.GET or self.POST
        """
        return self.req0(self.join(self.apibase, ep), params, method)
    
    class APICallError(RuntimeError): pass
    class AsyncAPICallError(ValueError): pass

    def call(self, ep, params=None, method=None, sync=None):
        """
        execute a GET or POST request to the (sync or async) call API 

        :ep:        API endpoint, with the sync/async prefix (eg 'plus')
        :params:    params transmitted to the API (POST only)
        :method:    self.GET or self.POST
        :sync:      whether to call sync or async
        """
        url = self.join(self.callapi0(sync), ep)
        if sync: 
            return self.req(url, params, method)
        try:
            r = self.req(url, params, method)
            rj = r.json()
        except:
            raise self.APICallError("Error calling API", r)

        if not rj["success"]:
            if self.raiseonerror:
                raise self.AsyncAPICallError("posts", ep, params, rj)
            return False
        return rj["reqid"]

    def callapi0(self, sync=None):
        """returns "s" if  sync, else "as" """ 
        if sync is None: sync = self.syncdefault
        return "scall" if sync else "ascall"
    
    @staticmethod
    def join(url, path):
        if url[-1] == "/": url = url[:-1]
        if path[0] == "/": path = path[1:]
        return f"{url}/{path}"
    
    @staticmethod
    def c2s(camelCaseString):
        """converts camelCaseString to snake_case_string"""
        return ''.join(['_' + i.lower() if i.isupper() else i for i in camelCaseString]).lstrip('_')
    
    @staticmethod
    def s2c(snakeCaseString):
        """converts snake_case_string to camelCaseString"""
        f = snakeCaseString.split('_')
        return ''.join([f[0]]+[i.title() for i in f[1:]])
    
    @staticmethod
    def roundsd(x, nsd=6):
        """
        rounds the value to significant decimals (returns x unmodified if not a number or zero)
        
        :x:      the value to be rounded
        :nsd:    number of significant decimals
        """
        try:
            magnitude = floor(log10(x))
        except:
            return x
        if magnitude <= nsd:
            return round(x,nsd-magnitude-1)
        else:
            shift = 10**(magnitude-nsd)
            return shift*round(x/shift,0)
        
    @staticmethod
    def bn2int(item):
        """
        converts BigNumber dict to int (if item is a BND; else returns item)

        :returns: int(item) if bn BigNumber dict, else item
        """
        if not isinstance(item, dict): return item
        if not item.get("type") == 'BigNumber': return item
        return int(item["hex"], 16) 
        
    @classmethod
    def bn2intd(cls, dct):
        """
        converts dict with bignumber entries converted to int entries; other items remain
        """
        return {k:cls.bn2int(v) for (k,v) in dct.items()}

    @staticmethod
    def int2str(item):
        """
        converts all instances of int to str (if item is int; else returns item)
        """
        if isinstance(item, int): return str(item)
        return item

    @classmethod
    def int2strd(cls, dct):
        """
        converts all instances of int to str in dict; other items remain
        """
        return {k:cls.int2str(v) for (k,v) in dct.items()}

    @staticmethod
    def int2bn(i):
        """
        converts int (or float) to bignumber dict
        """
        return {"type": "BigNumber", 'hex': hex(int(i))}

n = SDKBase.c2s

class CarbonSDK(SDKBase):
    """
    thin wrapper around the http interface to the carbon SDK
    """
    URL = "http://localhost:3118" # C=3, A=1, R=18 (Carbon)
    TOKEN = "carbontoken"
    APIBASE = "api"
    SYNCDEFAULT = False

    ########################################
    ## Test API requests
    def mul(self, a, b, sync=None):
        return self.call("mul", params={"a": a, "b": b}, sync=sync)

    def plus(self, a, b, sync=None):
        return self.call("plus", params={"a": a, "b": b}, sync=sync)
    
    def qmul(self, a, b, sync=None):
        return self.call("qmul", params={"a": a, "b": b}, sync=sync)

    def qplus(self, a, b, sync=None):
        return self.call("qplus", params={"a": a, "b": b}, sync=sync)
    
    ########################################
    ## Call API requests
    def getMatchActions(self, amountWei, tradeByTargetAmount, orders, sync=None):
        """
        TODO: docstring

        :amountWei:             amount of the trade in Wei  
        :tradeByTargetAmount:   whether the trade is by target amount (True) or by source amount (False) 
        :orders:                list of orders to match against
        :sync:                  whether to call sync or async
        """
        return self.call(n("getMatchActions"), params={
                "amountWei": str(amountWei), 
                "tradeByTargetAmount": bool(tradeByTargetAmount), 
                "orders": orders
            }, sync=sync)
    
    # def startDataSync(self, sync=None):
    #     """
    #     fetches blockchain data and subscribes to events

    #     :sync:      whether to call sync or async (should only be called async)
    #     :returns:   a promise that resolves when the data sync is complete
        
    #     This method should be called before any other actions are taken with the SDK,
    #     with the exception of strategy creation, update and delete that don't rely 
    #     on cached data. The promise returned resolves when the data sync is complete.
    #     """
    #     return self.call(n("startDataSync"), params={}, sync=sync)

    # def isInitialized(self, sync=None):
    #     """
    #     whether or not the SDK has been initialized, ie whether startDataSync has completed

    #     :sync:      whether to call sync or async (should be called sync)
    #     :returns:   whether the SDK has been initialized as a boolean
    #     """
    #     return self.call(n("isInitialized"), params={}, sync=sync)
    
    def addr(self):
        """
        returns the wallet address of the server [WORKING]

        :sync:      whether to call sync or async (should be called sync)
        :returns:   the wallet address of the server as a string
        """
        r = self.req(n("addr"))
        rj = r.json()
        if rj["success"]:
            return rj["data"]
        else:
            return None

    def pairs(self, inclstr=False):
        """
        all token pairs present in the Carbon contract

        :inclstr:   whether to include the string representation of the pairs
        :returns:   token pairs as an array of token addresses if self.Tokens is None, 
                    else as an list of pairs of SDKToken objects if inclstr is False,
                    else also a string of pairs of token symbols

        """
        Tokens = self.Tokens
        r = self.call(n("pairs"), params={}, sync=True)
        if not r.status_code == 200:
            raise RuntimeError(f"ERROR: {r}")
        pairs_raw = r.json()["data"]
        if Tokens is None:
            return pairs_raw
        pairs = [ [Tokens(p[0]), Tokens(p[1])] for p in pairs_raw]
        if not inclstr:
            return pairs
        pairs_s = ", ".join([f"{p[0].T}/{p[1].T}" for p in pairs])
        return pairs, pairs_s
        
    def hasLiquidityByPair(self, sourceTokenAddr=None, targetTokenAddr=None, pairs=None):
        """
        whether a specfic pair has any open liquidity positions

        :sourceTokenAddr:       source token* (as address)
        :targetTokenAddr:       target token* (as address)
        :pairs:                 pairs of dicts {"sourceToken":..., "targetToken":...} of token addresses**
        :returns:               whether the directed pair has liquidity (boolean)

        *source and target are seen from the point of view of the trader, not the AMM/LP
        **either pairs or sourceTokenAddr and targetTokenAddr must be provided, but not both
        """
        if not pairs is None:
            if not (sourceTokenAddr is None and targetTokenAddr is None):
                raise ValueError("ERROR: either pairs or sourceTokenAddr and targetTokenAddr must be provided, but not both")
            r = self.call(n("hasLiquidityByPair"), params={
                "pairList": [{k: str(v) for k,v in p.items()} for p in pairs], 
            }, sync=True)
        else:
            r = self.call(n("hasLiquidityByPair"), params={
                    "sourceToken": str(sourceTokenAddr), 
                    "targetToken": str(targetTokenAddr)
                }, sync=True)
        if not r.status_code == 200:
            raise RuntimeError(f"ERROR: {r}")
        return r.json()["data"]

    def mHasLiquidityByPair(self, pair, AMMsells):
        """
        whether a specfic pair has any open liquidity positions

        :pair:          pair (as CarbonPair object)
        :AMMsells:      the token the AMM sells (as token name)
        :returns:       whether the directed pair has liquidity (boolean)
        """
        self._assertTokensProvided()
        pair=CarbonPair(pair)
        targetToken = AMMsells
        sourceToken = pair.other(targetToken)
        targetTokenO = self.Tokens[targetToken]
        sourceTokenO = self.Tokens[sourceToken]
        hasliqudity = self.hasLiquidityByPair(sourceTokenO.a, targetTokenO.a)
        return hasliqudity

    def mHasLiquidityByPairs(self, pairs):
        """
        whether a list of pairs has any open liquidity positions in any direction

        :pairs:     list of pairs (as CarbonPair objects or slashpair strings),
                    or a string of slashpairs separeted by commas 
        """
        self._assertTokensProvided()
        pairList = []
        pairListMeta = []
        if isinstance(pairs, str):
            pairs = [s.strip() for s in pairs.split(",")]
        for pair in pairs:
            if isinstance(pair, str):
                pair = CarbonPair(pair)
            targetTokenO = self.Tokens[pair.tknq] # sic target = ...tknq
            sourceTokenO = self.Tokens[pair.tknb]
            pairListMeta += [{"pair": pair, "AMMsells": targetTokenO.T}]
            pairList += [{"sourceToken": sourceTokenO.a, "targetToken": targetTokenO.a}]
            targetTokenO = self.Tokens[pair.tknb]
            sourceTokenO = self.Tokens[pair.tknq]
            pairListMeta += [{"pair": pair, "AMMsells": targetTokenO.T}]
            pairList += [{"sourceToken": sourceTokenO.a, "targetToken": targetTokenO.a}]
        result = self.hasLiquidityByPair(pairs=pairList)
        return tuple({**m, "hasLiquidity": r} for m, r in zip(pairListMeta, result))

    
    def getLiquidityByPair(self, sourceTokenAddr, targetTokenAddr):
        """
        liquidity value for a specific pair

        :sourceTokenAddr:       source token* (as address)
        :targetTokenAddr:       target token* (as address)
        :sync:                  whether to call sync or async (should be called sync)
        :returns:               liquidity value in units of the target token as a float
        
        *source and target are seen from the point of view of the trader, not the AMM/LP
        """
        r = self.call(n("getLiquidityByPair"), params={
                "sourceToken": str(sourceTokenAddr), 
                "targetToken": str(targetTokenAddr)
            }, sync=True)
        if not r.status_code == 200:
            raise RuntimeError(f"ERROR: {r}")
        return float(r.json()["data"])
    
    @dataclass
    class PairLiquidity:
        """
        a range object for a specific pair

        :amount:    the amount of liquidity in the pair (float or tuple of floats)
        :unit:      the unit of the liquidity amount (as token name)
        :AMMsells:  the token the AMM sells (as token name)
        :bidAsk:    the bid/ask direction (as string)
        :pair:      the pair (as CarbonPair object)
        :rate:      the rate of the quoted liquidity (None = total; float or tuple of floats)
        :inverted:  whether the rate is inverted compared to the raw API values
        :islist:    whether the liquidity is a list (tuple of floats)
        """
        amount: any
        unit: str
        AMMsells: str
        bidAsk: str
        pair: CarbonPair
        rate: any=None
        inverted: bool=None
        islist: bool=None
        
    def mGetLiquidityByPair(self, pair, AMMsells):
        """
        liquidity values for multiple pairs

        :pair:          pair (as CarbonPair object or slashpair string)
        :AMMsells:      the token the AMM sells (as token name)
        :returns:       RangeByPair object
        """
        self._assertTokensProvided()
        pair = CarbonPair(pair)
        targetToken = AMMsells
        sourceToken = pair.other(targetToken)
        targetTokenO = self.Tokens[targetToken]
        sourceTokenO = self.Tokens[sourceToken]
        amount = self.getLiquidityByPair(sourceTokenO.a, targetTokenO.a)
        return self.PairLiquidity(
            amount=amount, 
            unit=targetToken, 
            AMMsells=AMMsells, 
            bidAsk="ask" if pair.has_basetoken(AMMsells) else "bid",
            pair=pair,
        )

    def getMinRateByPair(self, sourceTokenAddr, targetTokenAddr):
        """
        the minimum exchange rate offered on Carbon between those two tokens

        :sourceTokenAddr:   source token* (as address; also base token)
        :targetTokenAddr:   target token* (as address; also quote token)
        :returns:           minimum rate (target token per source token)

        *source and target are seen from the point of view of the trader, not the AMM/LP
        """
        r = self.call(n("getMinRateByPair"), params={
                "sourceToken": str(sourceTokenAddr), 
                "targetToken": str(targetTokenAddr)
            }, sync=True)
        if not r.status_code == 200:
            raise RuntimeError(f"ERROR: {r}")
        return float(r.json()["data"])

    def getMaxRateByPair(self, sourceTokenAddr, targetTokenAddr):
        """
        gets the minimum exchange rate offered on Carbon between those two tokens

        :sourceTokenAddr:   source token* (as address; also base token)
        :targetTokenAddr:   target token* (as address; also quote token)
        :returns:           maximum rate (target token per source token)
        
        *source and target are seen from the point of view of the trader, not the AMM/LP
        """
        r = self.call(n("getMaxRateByPair"), params={
                "sourceToken": str(sourceTokenAddr), 
                "targetToken": str(targetTokenAddr)
            }, sync=True)
        if not r.status_code == 200:
            raise RuntimeError(f"ERROR: {r}")
        return float(r.json()["data"])
    
    @dataclass
    class RangeByPair:
        """
        a range object for a specific pair

        :startRate:     the exchange rate at which selling starts, in units of the pair
        :endRate:       the exchange rate at which selling ends, in units of the pair
        :AMMsells:      the token the AMM sells (as token name)
        :AMMbuys:       the token the AMM buys (as token name)
        :bidAsk:        the bid/ask direction (as string)
        :pair:          the pair (as CarbonPair object)
        :inverted:      whether the price is inverted as compared to the raw API calls
        """
        startRate: float
        endRate: float
        AMMsells: str
        AMMbuys: str
        bidAsk: str
        pair: CarbonPair
        inverted: bool
        
    def mGetRangeByPair(self, pair, AMMsells):
        """
        gets the minimum and maximum exchange rate offered on Carbon between those two tokens

        :pair:          pair (as CarbonPair object or slashpair string)
        :AMMsells:      the token the AMM sells (as token name)
        :returns:       RangeByPair object
        """
        self._assertTokensProvided()
        pair = CarbonPair(pair)
        targetToken = AMMsells
        sourceToken = pair.other(targetToken)
        sourceTokenO = self.Tokens[sourceToken]
        targetTokenO = self.Tokens[targetToken]
        minRateRaw = self.getMinRateByPair(sourceTokenO.a, targetTokenO.a)
        maxRateRaw = self.getMaxRateByPair(sourceTokenO.a, targetTokenO.a)
        return self.RangeByPair(
            startRate = pair.price(price0=maxRateRaw, tknb0=sourceTokenO.T, tknq0=targetTokenO.T),
            endRate   = pair.price(price0=minRateRaw, tknb0=sourceTokenO.T, tknq0=targetTokenO.T),
            AMMbuys   = sourceTokenO.T,
            AMMsells  = targetTokenO.T,
            bidAsk    = "ask" if pair.has_basetoken(AMMsells) else "bid",
            pair      = pair, 
            inverted  = pair.has_quotetoken(targetTokenO.T), 
        )

    def getRateLiquidityDepthByPair(self, sourceTokenAddr, targetTokenAddr, rate):
        """
        liquidity depth (ie cumulative liquidity) at a given exchange rate

        :sourceTokenAddr:   source token* (as address; also base token)
        :targetTokenAddr:   target token* (as address; also quote token)
        :rate:              rate (target token per source token)
        :returns:           liquidity depth, ie cumulative liquidity at rate or better for trader
                            measured in units of the target token**
        
        *source and target are seen from the point of view of the trader, not the AMM/LP
        **the liqudity function is a decreasing function of the rate; at max rate it is
        at the value returned by getLiquidityByPair, and at min rate it is 0
        """
        try:
            rate = [str(r) for r in rate]
        except:
            rate = str(rate)
        #print("[getRateLiquidityDepthByPair}", rate)
    
        r = self.call(n("getRateLiquidityDepthByPair"), params={
                "sourceToken": str(sourceTokenAddr), 
                "targetToken": str(targetTokenAddr), 
                "rate": rate
            }, sync=True)
        if not r.status_code == 200:
            raise RuntimeError(f"ERROR: {r}")
        #print("[getRateLiquidityDepthByPair}", r.json())
        data = r.json()["data"]
        try:
            data = float(data)
        except:
            data = [float(d) if not isinstance(d, dict) else None for d in data]
        return data
        

    def mGetRateLiquidityDepthByPair(self, rate, pair, AMMsells):
        """
        liquidity depth (ie cumulative liquidity) at a given exchange rate

        :rate:          rate at which liquidity is evaluated (in units of the pair)
                        if the rate is an Array then the liquidity is evaluated at each rate
        :pair:          pair (as CarbonPair object or slashpair string)
        :AMMsells:      the token the AMM sells (as token name)
        :returns:       RangeByPair object; if rate is an Array so is the amount
        """
        self._assertTokensProvided()
        pair = CarbonPair(pair)
        targetToken = AMMsells
        sourceToken = pair.other(targetToken)
        sourceTokenO = self.Tokens[sourceToken]
        targetTokenO = self.Tokens[targetToken]
        inverted = pair.has_basetoken(targetTokenO.T)
        try:
            rate_raw = [1/r if inverted else r for r in rate]
            islist = True
        except:
            rate_raw = 1/rate if inverted else rate
            islist = False
        amount = self.getRateLiquidityDepthByPair(sourceTokenO.a, targetTokenO.a, rate_raw)
        return self.PairLiquidity(
            amount=amount, 
            unit=targetToken, 
            AMMsells=AMMsells, 
            bidAsk="ask" if pair.has_basetoken(AMMsells) else "bid",
            pair=pair,
            rate=rate,
            inverted=inverted,
            islist=islist,
        )
    
    def getUserStrategies(self, user):
        """
        gets the strategies that are owned by the user

        :user:      user (as address)
        :returns:   a list of strategy objects
        """
        r = self.call(n("getUserStrategies"), params={
                "user": str(user)
            }, sync=True)
        if not r.status_code == 200:
            raise RuntimeError(f"ERROR: {r}")
        return r.json()["data"]
    
    def mGetUserStrategies(self, user, nsd=True):
        """
        gets the strategies that are owned by the user

        :user:      user (as address)
        :returns:   a list of modified strategy objects
        :nsd:       number significant digits (True=default; None=no rounding)
        
        """
        strategies_raw = self.getUserStrategies(user)
        strategies = tuple(self.reformatStrategy(s, nsd=nsd) for s in strategies_raw)
        return strategies

    
    def getMatchParams(self, sourceToken, targetToken, amount, tradeByTargetAmount, sync=None):
        """
        returns the data needed to process a trade

        :sourceToken:               source token (as address)
        :targetToken:               target token (as address)
        :amount:                    amount of the trade
        :tradeByTargetAmount:       whether the trade, as seen by the trader, is by 
                                    target amount (True) or by source amount (False)
        :sync:                      whether to call sync or async
        :returns:                   ??? TODO

        this function returns the data for a given source and target token pair; this data
        can then be used to call matchBySourceAmount or matchByTargetAmount; to finally get 
        the actions those will be passed to getTradeDataFromActions
        """
        return self.call(n("getMatchParams"), params={
                "sourceToken": str(sourceToken), 
                "targetToken": str(targetToken), 
                "amount": str(amount), 
                "tradeByTargetAmount": bool(tradeByTargetAmount)
            }, sync=sync)
    
    def getTradeData(self, sourceToken, targetToken, amount, tradeByTargetAmount, filter=None, sync=None):
        """
        step 1 of a trade: get the data needed to process a trade

        :sourceToken:               source token (as address)
        :targetToken:               target token (as address)
        :amount:                    amount of the trade
        :tradeByTargetAmount:       whether the trade, as seen by the trader, is by 
                                    target amount (True) or by source amount (False)
        :filter:                    filter to apply to the orders
        :sync:                      whether to call sync or async
        :returns:                   ??? TODO
        """
        if filter is None: filter = []
        return self.call(n("getTradeData"), params={
                "sourceToken": str(sourceToken), 
                "targetToken": str(targetToken), 
                "amount": str(amount), 
                "tradeByTargetAmount": bool(tradeByTargetAmount), 
                "filter": filter
            }, sync=sync)

    def getTradeDataFromActions(self, sourceToken, targetToken, tradeByTargetAmount, actionsWei=None, sync=None):
        """
        Creates an unsigned transaction to fulfill a trade using an array of trade actions

        :sourceToken:               source token (as address)
        :targetToken:               target token (as address)
        :tradeByTargetAmount:       whether the trade, as seen by the trader, is by 
                                    target amount (True) or by source amount (False)
        :actionsWei:                actions to apply to the orders in Wei
        :sync:                      whether to call sync or async
        :returns:                   ??? TODO
        """
        if actionsWei is None: actionsWei = []
        actionsWei = [self.int2strd(d) for d in actionsWei]
        return self.call(n("getTradeDataFromActions"), params={
                "sourceToken": str(sourceToken), 
                "targetToken": str(targetToken), 
                "tradeByTargetAmount": bool(tradeByTargetAmount), 
                "actionsWei": actionsWei
            }, sync=sync)

    MAXDEADLINE = str(2**32-1)
    MAXMAXINPUT = str(2**128-1)

    def composeTradeByTargetTransaction(self, sourceToken, targetToken, tradeActions=None, deadline=None, maxInput=None, overrides=None, sync=None):
        """
        step 2 of a trade: composes a trade by target transaction

        :sourceToken:               source token (as address)
        :targetToken:               target token (as address)
        :tradeActions:              list of actions to apply to the orders
        :deadline:                  deadline of the trade (block number as string; None=unlimited)
        :maxInput:                  maximum input amount (as string; None=unlimited)
        :overrides:                 overrides to apply to the transaction
        :sync:                      whether to call sync or async
        """
        if deadline is None: deadline = self.MAXDEADLINE
        if maxInput is None: maxInput = self.MAXMAXINPUT
        if overrides is None: overrides = dict()
        if not overrides.get("gasLimit"): overrides["gasLimit"] = 999999999
        if tradeActions is None: tradeActions = []
        tradeActions = [self.int2strd(d) for d in tradeActions]
        return self.call(n("composeTradeByTargetTransaction"), params={
                "sourceToken": str(sourceToken), 
                "targetToken": str(targetToken), 
                "tradeActions": tradeActions, 
                "deadline": str(deadline), 
                "maxInput": str(maxInput), 
                "overrides": overrides
            }, sync=sync)

    def composeTradeBySourceTransaction(self, sourceToken, targetToken, tradeActions, deadline=None, minReturn=None, overrides=None, sync=None):
        """
         step 2 of a trade: composes a trade by target transaction

        :sourceToken:               source token (as address)
        :targetToken:               target token (as address)
        :tradeActions:              actions to apply to the orders
        :deadline:                  deadline of the trade (block number as string; None=unlimited)
        :minReturn:                 minimum return amount (as string; None=unlimited)
        :overrides:                 overrides to apply to the transaction
        :sync:                      whether to call sync or async
        """

        if deadline is None: deadline = self.MAXDEADLINE
        if minReturn is None: minReturn = 1
        if overrides is None: overrides = dict()
        if not overrides.get("gasLimit"): overrides["gasLimit"] = 999999999
        if tradeActions is None: tradeActions = []
        tradeActions = [self.int2strd(d) for d in tradeActions]
        return self.call(n("composeTradeBySourceTransaction"), params={
                "sourceToken": str(sourceToken), 
                "targetToken": str(targetToken), 
                "tradeActions": tradeActions, 
                "deadline": str(deadline), 
                "minReturn": str(minReturn), 
                "overrides": overrides
            }, sync=sync)

    def createBuySellStrategy(self, baseToken, quoteToken, buyPriceLow, buyPriceHigh, buyBudget, sellPriceLow, sellPriceHigh, sellBudget, overrides=None, sync=None):
        """
        Creates a Carbon Strategy, composed of on buy order and one sell order

        :baseToken:         base token (as address; base token = risk asset)
        :quoteToken:        quote token (as address; quote token = numeraire asset)
        :buyPriceLow:       low buy price (in quote token per base token)
        :buyPriceHigh:      high buy price (ditto)
        :buyBudget:         buy budget (in quote token)
        :sellPriceLow:      low sell price (ditto)
        :sellPriceHigh:     high sell price (ditto)
        :sellBudget:        sell budget (in base token)
        :overrides:         overrides to apply to the transaction
        :sync:              whether to call sync or async
        :returns:           unsigned transaction that can be used to create the strategy
        """
        if overrides is None: overrides = dict()
        if not overrides.get("gasLimit"): overrides["gasLimit"] = 999999999
        return self.call(n("createBuySellStrategy"), params={
                "baseToken": str(baseToken), 
                "quoteToken": str(quoteToken), 
                "buyPriceLow": str(buyPriceLow), 
                "buyPriceHigh": str(buyPriceHigh), 
                "buyBudget": str(buyBudget), 
                "sellPriceLow": str(sellPriceLow), 
                "sellPriceHigh": str(sellPriceHigh), 
                "sellBudget": str(sellBudget), 
                "overrides": overrides
            }, sync=sync)

    def updateStrategy(self, strategyId, encoded, baseToken, quoteToken, update, buyMarginalPrice, sellMarginalPrice, overrides=None, sync=None):
        """
        updates an existing strategy

        :strategyId:            strategy id
        :encoded:               encoded strategy ??? TODO
        :baseToken:             base token (as address)
        :quoteToken:            quote token (as address)
        :update:                update to apply to the strategy
        :buyMarginalPrice:      buy marginal price (in quote token per base token)
        :sellMarginalPrice:     sell marginal price (ditto)
        :overrides:             overrides to apply to the transaction
        :sync:                  whether to call sync or async
        :returns:               ??? TODO
        """
        if overrides is None: overrides = dict()
        if not overrides.get("gasLimit"): overrides["gasLimit"] = 999999999
        return self.call(n("updateStrategy"), params={
                "strategyId": str(strategyId), 
                "encoded": encoded, 
                "baseToken": str(baseToken), 
                "quoteToken": str(quoteToken), 
                "update": bool(update), 
                "buyMarginalPrice": str(buyMarginalPrice), 
                "sellMarginalPrice": str(sellMarginalPrice), 
                "overrides": overrides
            }, sync=sync)
    
    def deleteStrategy(self, strategyId, overrides=None, sync=None):
        """
        deletes a strategy

        :strategyId:        strategy id
        :overrides:         overrides to apply to the transaction
        :sync:              whether to call sync or async
        :returns:           ??? TODO
        """
        if overrides is None: overrides = dict()
        if not overrides.get("gasLimit"): overrides["gasLimit"] = 999999999
        return self.call(n("deleteStrategy"), params={
                "strategyId": str(strategyId), 
                "overrides": overrides,
            }, sync=sync)   
    
    ########################################
    ## Non-call API requests
    def version(self):
        """calls the root endpoint of the API server (version)"""
        r = self.req0("/")
        return r.json()

    class UnknownReqIdError(ValueError): pass
    def result(self, reqid):
        """
        retrieves the result corresponding to reqid [sync]
        
        :returns:   return value depends on the state encapsulated in the API result
                    :available:     if the result of the API call is available then the result
                                    is returned; note that some of the returned API data is 
                                    removed (specifially, only r["data"]["result"] returned)
                    :awaiting:      if the result of the API call is still awaiting returns True
                    :unknown:       if reqid is unknown, returns False (or raises UnknownReqIdError)
        """
        try:
            url = self.join("result", str(reqid))
            r = self.req(url)
            rj = r.json()
        except:
            raise self.APICallError("Error calling result API", url, r)
        if rj["success"]:
            return rj["data"]["result"]
        if rj["awaiting"] is True:
            return True
        if self.raiseonerror:
            raise self.UnknownReqIdError("Unknown request id", reqid)
        return False
    
    def signsubmittx(self, tx, sign=True):
        """
        signs and submits a transaction (sync only)
        
        :tx:        the transaction to be submitted (signed or unsigned)
        :sign:      whether to sign the transaction (True=sign)
        :returns:   the transaction receipt
        """
        return self.req(n("signsubmittx"), params={"tx": tx, sign: bool(sign)})
    
    ########################################
    ## Helper functions
    def reformatStrategy(self, strat, nsd=True):
        """
        converts the values of a strategy (`createBuySellStrategy`) into Python-native objects
        
        :strat:   the strategy object returned from the API
        :nsd:     number significant digits (True=default; None=no rounding)
        """
        self._assertTokensProvided()
        if nsd is True: nsd = 8
        s2 = dict({"encoded": dict()})
        for f in ("buyPriceLow", "buyPriceHigh", "buyBudget", "sellPriceLow", "sellPriceHigh", "sellBudget"):
            s2[f] = float(strat[f]) if nsd is None else self.roundsd(float(strat[f]), nsd)
        s2["id"] = s2["encoded"]["id"] = self.bn2int(strat["id"])
        for f in ("baseToken", "quoteToken"):
            s2[f] = self.Tokens.byaddr1(strat[f], tknonly=True)
        for f in ("token0", "token1"):
            s2["encoded"][f] = self.Tokens.byaddr1(strat["encoded"][f], tknonly=True)
        for o in ("order0", "order1"):
            s2["encoded"][o] = dict()
            for f in ("y", "z", "A", "B"):
                s2["encoded"][o][f] = self.bn2int(strat["encoded"][o][f])
        return s2
    

    @classmethod
    def reformatOrders(cls, orders):
        """
        converts orders dict from BigNumber to int
        """
        return {k: cls.bn2intd(v) for k, v in orders.items()}


