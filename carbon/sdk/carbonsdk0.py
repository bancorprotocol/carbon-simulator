from .sdktoken import Tokens
from .sdkbase import SDKBase

n = SDKBase.c2s

class CarbonSDK0(SDKBase):
    """
    mostly 1:1 wrapper around the http interface to the carbon SDK
    """
    URL = "http://localhost:3118" # C=3, A=1, R=18 (Carbon)
    TOKEN = "carbontoken"
    APIBASE = "api"
    SYNCDEFAULT = False

    ########################################
    ## Test API requests
    def mul(self, a, b, sync=None):
        "multiplies a,b, plus random wait"
        return self.call("mul", params={"a": a, "b": b}, sync=sync)

    def plus(self, a, b, sync=None):
        "adds a,b, plus random wait"
        return self.call("plus", params={"a": a, "b": b}, sync=sync)
    
    def qmul(self, a, b, sync=None):
        "multiplies a,b, no wait"
        return self.call("qmul", params={"a": a, "b": b}, sync=sync)

    def qplus(self, a, b, sync=None):
        "adds a,b, no wait"
        return self.call("qplus", params={"a": a, "b": b}, sync=sync)

    ########################################
    ## ERC20 API requests
    def getERC20Balance(self, tokens, address):
        """
        calls the ERC20 balanceOf method for each token in tokens

        :tokens:    list of SDKToken objects
        :address:   address to check balance of
        :returns:   dict of balances in token units
        """
        r = self.req("erc20/balance_of", params={
                "tokens": [t.a for t in tokens],
                "address": address,
            })
        data = self._checkresult(r)
        bal = (self.bn2int(bal) for bal in data)
        result = {t.T: t.w2t(b) for t,b in zip(tokens, bal)}
        return result
    
    def getERC20Decimals(self, tokens):
        """
        calls the ERC20 decimals method for each token in tokens

        :tokens:    list of SDKToken objects
        :returns:   dict
        """
        r = self.req("erc20/decimals", params={
                "tokens": [t.a for t in tokens],
            })
        data = self._checkresult(r)
        result = {t.T: d for t,d in zip(tokens, data)}
        return result

    def getERC20Symbol(self, tokens):
        """
        calls the ERC20 symbol method for each token in tokens

        :tokens:    list of SDKToken objects or addresses
        :returns:   dict
        """
        try:
            tokensa = [t.a for t in tokens]
            tokenst = [t.T for t in tokens]
        except:
            tokensa = tokens
            tokenst = tokens

        r = self.req("erc20/symbol", params={
                "tokens": tokensa,
            })
        data = self._checkresult(r)
        result = {t: d for t,d in zip(tokenst, data)}
        return result
    
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
        returns the wallet address of the server

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
        T = self.Tokens
        r = self.call(n("pairs"), params={}, sync=True)
        pairs_raw = self._checkresult(r)
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
        return self._checkresult(r)
        
    
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
        data = self._checkresult(r)
        return float(data)
       
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
        data = self._checkresult(r)
        return float(data)

    def getMaxRateByPair(self, sourceTokenAddr, targetTokenAddr):
        """
        gets the maximum exchange rate offered on Carbon between those two tokens

        :sourceTokenAddr:   source token* (as address; also base token)
        :targetTokenAddr:   target token* (as address; also quote token)
        :returns:           maximum rate (target token per source token)
        
        *source and target are seen from the point of view of the trader, not the AMM/LP
        """
        r = self.call(n("getMaxRateByPair"), params={
                "sourceToken": str(sourceTokenAddr), 
                "targetToken": str(targetTokenAddr)
            }, sync=True)
        data = self._checkresult(r)
        return float(data)
        
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
        data = self._checkresult(r)
        try:
            data = float(data)
        except:
            data = [float(d) if not isinstance(d, dict) else None for d in data]
        return data
        
    def getUserStrategies(self, user):
        """
        gets the strategies that are owned by the user

        :user:      user (as address)
        :returns:   a list of strategy objects
        """
        r = self.call(n("getUserStrategies"), params={
                "user": str(user)
            }, sync=True)
        return self._checkresult(r)

    
    ########################################################################
    ## main trade functions (taker actions)
    MAXDEADLINE = str(2**32-1)
    MAXMAXINPUT = str(2**128-1) # TODO: wrong; maxInput is a token resultion number (string)
    
    def getTradeData(self, sourceToken, targetToken, amount, tradeByTargetAmount, filter=None):
        """
        Get the data needed to process a trade (trade action step 1)

        :sourceToken:               source token (as address)
        :targetToken:               target token (as address)
        :amount:                    amount of the trade
        :tradeByTargetAmount:       whether the trade, as seen by the trader, is by 
                                    target amount (True) or by source amount (False)
        :filter:                    filter to apply to the orders
        :returns:                   trade data dict
        """
        if filter is None: filter = []
        r = self.call(n("getTradeData"), params={
                "sourceToken": str(sourceToken), 
                "targetToken": str(targetToken), 
                "amount": str(amount), 
                "tradeByTargetAmount": bool(tradeByTargetAmount), 
                "filter": filter
            }, sync=True)
        return self._checkresult(r)

    def composeTradeByTargetTransaction(self, sourceToken, targetToken, tradeActions=None, deadline=None, maxInput=None, overrides=None):
        """
        Composes a trade by target transaction (trade action step 2)

        :sourceToken:               source token (as address)
        :targetToken:               target token (as address)
        :tradeActions:              list of actions to apply to the orders
        :deadline:                  deadline of the trade (block number as string; None=unlimited)
        :maxInput:                  maximum input amount (as string; None=unlimited)
        :overrides:                 overrides to apply to the transaction
        """
        if deadline is None: deadline = self.MAXDEADLINE
        if maxInput is None: maxInput = self.MAXMAXINPUT
        if overrides is None: overrides = dict()
        if not overrides.get("gasLimit"): overrides["gasLimit"] = 999999999
        if tradeActions is None: tradeActions = []
        tradeActions = [self.int2strd(d) for d in tradeActions]
        r = self.call(n("composeTradeByTargetTransaction"), params={
                "sourceToken": str(sourceToken), 
                "targetToken": str(targetToken), 
                "tradeActions": tradeActions, 
                "deadline": str(deadline), 
                "maxInput": str(maxInput), 
                "overrides": overrides
            }, sync=True)
        return self._checkresult(r)

    def composeTradeBySourceTransaction(self, sourceToken, targetToken, tradeActions, deadline=None, minReturn=None, overrides=None):
        """
        Composes a trade by source transaction (trade action step 2)

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
        r = self.call(n("composeTradeBySourceTransaction"), params={
                "sourceToken": str(sourceToken), 
                "targetToken": str(targetToken), 
                "tradeActions": tradeActions, 
                "deadline": str(deadline), 
                "minReturn": str(minReturn), 
                "overrides": overrides
            }, sync=True)
        return self._checkresult(r)


    #######################################################
    ## other trade functions (taker actions)
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

    ########################################################################
    ## maker actions
    def createBuySellStrategy(self, baseToken, quoteToken, buyPriceLow, buyPriceHigh, buyBudget, sellPriceLow, sellPriceHigh, sellBudget, overrides=None):
        """
        Creates a Carbon Strategy, composed of one buy order and one sell order

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
        r = self.call(n("createBuySellStrategy"), params={
                "baseToken": str(baseToken), 
                "quoteToken": str(quoteToken), 
                "buyPriceLow": str(buyPriceLow), 
                "buyPriceHigh": str(buyPriceHigh), 
                "buyBudget": str(buyBudget), 
                "sellPriceLow": str(sellPriceLow), 
                "sellPriceHigh": str(sellPriceHigh), 
                "sellBudget": str(sellBudget), 
                "overrides": overrides
            }, sync=True)
        return self._checkresult(r)

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
    
    def deleteStrategy(self, strategyId, overrides=None):
        """
        deletes a strategy

        :strategyId:        strategy id
        :overrides:         overrides to apply to the transaction
        :returns:           ??? TODO
        """
        if overrides is None: overrides = dict()
        if not overrides.get("gasLimit"): overrides["gasLimit"] = 999999999
        r = self.call(n("deleteStrategy"), params={
                "strategyId": str(strategyId), 
                "overrides": overrides,
            }, sync=True)
        return self._checkresult(r)   
    
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
        r = self.req(n("signsubmittx"), params={"tx": tx, sign: bool(sign)})
        return self._checkresult(r)
    
    ########################################
    ## Helper functions
    def _checkresult(self, r):
        """
        checks the result of a call to the API and returns the data or raises an error

        :r:     the request objects returns by the call to the API
        """
        if not r.status_code == 200:
            raise RuntimeError(f"ERROR (status = {r.status_code}): {r}")
        try:
            rj = r.json()
        except:
            raise RuntimeError(f"ERROR: can't convert to json {r.body}")
        try:
            return rj["data"]
        except:
            raise RuntimeError(f"ERROR: {rj}")
 

    def reformatStrategy(self, strat, nsd=True):
        """
        converts the values of a strategy (`createBuySellStrategy`) into Python-native objects
        
        :strat:   the strategy object returned from the API
        :nsd:     number significant digits (True=default; None=no rounding)
        """
        T = self._assertTokensProvided()
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
