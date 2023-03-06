from .sdktoken import SDKToken, Tokens
from ..pair import CarbonPair
from .carbonsdk0 import CarbonSDK0
from dataclasses import dataclass


#########################################################################################################
##  DATA CLASSES
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

@dataclass
class MarketByPair():
    """
    market overview for a given pair

    :pair:              pair (as str)
    :bestBid:           best bid available in the market
    :bestAsk:           best ask available in the market
    :liqBid:            liquidity on the bid side of the market
    :liqAsk:            liquidity on the ask side of the market 
    :lastBid:           last bid available in the market
    :lastAsk:           last ask available in the market
    ----
    :inverted:          True if the pair is inverted (bid > ask)
    :mid:               mid price
    :spread:            spread in price units
    :spreadpc:          spread as a percentage of the mid price
    :cpair:             associated CarbonPair object
    :price_convention:  price convention of all prices in this object
    :liqBidUnit:        unit of the bid liquidity (=tknq)
    :liqAskUnit:        unit of the ask liquidity (=tknb)
    :bidAMMSells:       token sold by AMM on the bid side (=tknq)
    :askAMMSells:       token sold by AMM on the ask side (=tknb)
    :bidTraderSells:    token sold by Trader on the bid side (=tknb)
    :askTraderSells:    token sold by Trader on the ask side (=tknq)
    """
    pair: str
    bestBid: float
    bestAsk: float
    liqBid: float
    liqAsk: float
    lastBid: float
    lastAsk: float
    
    @property
    def inverted(self):
        return self.bestBid > self.bestAsk
    
    @property
    def mid(self):
        return 0.5*(self.bestBid+self.bestAsk)
    
    @property
    def spreadpc(self):
        return self.spread/self.mid
    
    @property
    def spread(self):
        return self.bestAsk-self.bestBid
    
    @property
    def cpair(self):
        return CarbonPair(self.pair)
    
    @property
    def price_convention(self):
        return self.cpair.price_convention
    
    @property
    def liqBidUnit(self):
        return self.cpair.tknq
    
    @property
    def liqAskUnit(self):
        return self.cpair.tknb
    
    @property
    def liqBidUnit(self):
        return self.cpair.tknq
    
    @property
    def bidAMMSells(self):
        return self.cpair.tknq
    
    @property
    def askAMMSells(self):
        return self.cpair.tknb
    
    @property
    def bidTraderSells(self):
        return self.cpair.tknb
    
    @property
    def askTraderSells(self):
        return self.cpair.tknq
    
    def ibid(self, x):
        """
        interpolate bid price (x=0: best bid; x=1: last bid)
        """
        return self.bestBid + x*(self.lastBid-self.bestBid)
    
    def iask(self, x):
        """
        interpolate ask price (x=0: best ask; x=1: last ask)
        """
        return self.bestAsk + x*(self.lastAsk-self.bestAsk)
    
    def iall(self, x):
        """
        interpolate all prices (x=0: last bid; x=1: last ask)
        """
        return self.lastBid + x*(self.lastAsk-self.lastBid)
         
@dataclass
class TradeData:
    """
    an object containing the data needed to execute a trade

    :pair:                  the pair to which the trade applies
    :tkn:                   the token specified by the trader
    :traderBuySell:         whether this token is bought or sold by the trader
    :amount:                the amount of tkn to be bought or sold
    :sourceToken:           the token that the trader sells (as SDKToken object)
    :targetToken:           the token that the trader buys (as SDKToken object)
    :tradeActions:          the trade actions (input for the next step)
    :actionsWei:            the trade actions in wei
    :actionsTokenRes:       the trade actions in token resolution
    :tradeByTargetAmount:   corresponding SDK parameter
    """
    pair: str
    tkn: str
    traderBuySell: str
    amount: float
    sourceToken: SDKToken 
    targetToken: SDKToken
    tradeByTargetAmount: bool
    tradeActions: list
    actionsWei: list
    actionsTokenRes: list
    tradeData: dict

    @property
    def cttkwargs(self):
        """kwargs for mComposeTradeTransaction"""
        return dict(
            sourceToken=self.sourceToken,
            targetToken=self.targetToken,
            tradeActions=self.tradeActions,
            tradeData=self.tradeData,
            tradeByTargetAmount=self.tradeByTargetAmount,
        )
    
    @property
    def cttargs(self):
        """args for mComposeTradeTransaction"""
        return tuple(self.cttkwargs.values())
    
@dataclass
class EncodedOrder():
    """
    a single curve as encoded by the SDK

    :y:          number of token wei to sell on the curve
    :z:          curve capacity in number of token wei
    :A:          curve parameter A, multiplied by 2**48
    :B:          curve parameter B, multiplied by 2**48
    ----
    :A_:         curve parameter A in proper units
    :B_:         curve parameter B in proper units
    :p_start:    start token wei price of the order (in dy/dx)
    :p_end:      end token wei price of the order (in dy/dx)
    :sx:         scaling exponent (hardcoded)
    :ONE:        scaling factor (=2**sx)
    """
    token: str
    y: int
    z: int
    A: int
    B: int
        
    @classmethod
    def from_sdk(cls, token, order):
        return cls(token=token, **order)
    
    @property
    def descr(self):
        s=self
        return f"selling {s.token} @ ({1/s.p_start}..{1/s.p_end})  [TKNwei] per {s.token}wei"
        
    def __getitem__(self, item):
        return getattr(self, item)
    
    @property
    def sx(self):
        return 48
    
    @property
    def ONE(self):
        return 2**self.sx
    
    def decodeFloat(self, value):
        """undoes the mantisse/exponent encoding in A,B"""
        return (value % self.ONE) << (value // self.ONE)
    
    def decode(self, value):
        """decodes A,B to float"""
        return self.decodeFloat(value)/self.ONE
    
    @property
    def A_(self):
        return self.decode(self.A)
    
    @property
    def B_(self):
        return self.decode(self.B)
    
    @property
    def p_end(self):
        return self.B_*self.B_
    
    @property
    def p_start(self):
        return self.p_end + self.A_*self.A_
        
@dataclass
class EncodedStrategy():
    """
    a single strategy as encoded by the SDK

    :sid:        strategy id
    :order0:     order selling token0 (ie y=token0, dy/dx = token0 per token1)
    :order1:     order selling token1 (ie y=token1, dy/dx = token1 per token0)
    """
    sid: int
    order0: EncodedOrder
    order1: EncodedOrder
    
    @classmethod
    def from_sdk(cls, dct):
        order0 = CarbonSDK.EncodedOrder.from_sdk(dct["token0"], dct["order0"])
        order1 = CarbonSDK.EncodedOrder.from_sdk(dct["token1"], dct["order1"])
        return cls(sid=dct["id"], order0=order0, order1=order1)

    @property
    def token0(self):
        return self.order0.token
    
    @property
    def token1(self):
        return self.order1.token
    
    @property
    def descr(self):
        de = self
        s0 = f"order0: selling {de.token0} @ ({1/de.order0.p_start}..{1/de.order0.p_end}) {de.token1}wei per {de.token0}wei"
        s1 = f"order1: buying  {de.token0} @ ({de.order1.p_start}..{de.order1.p_end}) {de.token1}wei per {de.token0}wei"
        return [s0,s1]
    
    def __getitem__(self, item):
        if item == "id": 
            return self.sid
        # elif item == "token0":
        #     return self.order0.token
        # elif item == "token1":
        #     return self.order1.token
        return getattr(self, item) 

@dataclass
class Strategy():
    """
    single strategy, as returned by the API (encoded and decoded)
    """
    sid: int
    baseToken: str
    quoteToken: str
    buyPriceLow: float
    buyPriceHigh: float
    buyBudget: float
    sellPriceLow: float
    sellPriceHigh: float
    sellBudget: float
    encoded: EncodedStrategy

    def __post_init__(self):
        assert self.baseToken == self.encoded.order0.token, "base token not equal to token0"
        assert self.quoteToken == self.encoded.order1.token, "quote token not equal to token1"

    @property
    def descr(self):
        d = self
        s0 = f"order0: selling {d.baseToken} @ ({d.sellPriceLow}..{d.sellPriceHigh}) {d.quoteToken} per {d.baseToken}"
        s1 = f"order1: buying  {d.baseToken} @ ({d.buyPriceHigh}..{d.buyPriceLow}) {d.quoteToken} per {d.baseToken}"
        return [s0,s1]
    
    @classmethod
    def from_sdk(cls, dct):
        encoded = CarbonSDK.EncodedStrategy.from_sdk(dct["encoded"])
        sid = dct["id"]
        dct1 = {k:v for k,v in dct.items() if not k in ["id", "encoded"]}
        return cls(sid=sid, encoded=encoded, **dct1)
    
    def __getitem__(self, item):
        if item == "id": 
            return self.sid 
        return getattr(self, item) 

#########################################################################################################
##  CLASS CARBON SDK
class CarbonSDK(CarbonSDK0):
    """
    additional layer of abstraction to the CarbonSDK0 class
    """

    ########################################################################
    ## data containers and constants    
    SELL = "SELL"
    BUY = "BUY"

    PairLiquidity = PairLiquidity
    RangeByPair = RangeByPair
    MarketByPair = MarketByPair
    TradeData = TradeData
    EncodedOrder = EncodedOrder
    EncodedStrategy = EncodedStrategy
    Strategy = Strategy

    ########################################################################
    ## market information
    def mHasLiquidityByPair(self, pair, AMMsells):
        """
        whether a specfic pair has any open liquidity positions

        :pair:          pair (as CarbonPair object)
        :AMMsells:      the token the AMM sells (as token name)
        :returns:       whether the directed pair has liquidity (boolean)
        """
        T = self._assertTokensProvided()
        pair=CarbonPair(pair)
        targetToken = AMMsells
        sourceToken = pair.other(targetToken)
        targetTokenO = T[targetToken]
        sourceTokenO = T[sourceToken]
        hasliqudity = self.hasLiquidityByPair(sourceTokenO.a, targetTokenO.a)
        return hasliqudity

    def mHasLiquidityByPairs(self, pairs):
        """
        whether a list of pairs has any open liquidity positions in any direction

        :pairs:     list of pairs (as CarbonPair objects or slashpair strings),
                    or a string of slashpairs separeted by commas 
        """
        T = self._assertTokensProvided()
        pairList = []
        pairListMeta = []
        if isinstance(pairs, str):
            pairs = [s.strip() for s in pairs.split(",")]
        for pair in pairs:
            if isinstance(pair, str):
                pair = CarbonPair(pair)
            targetTokenO = T[pair.tknq] # sic target = ...tknq
            sourceTokenO = T[pair.tknb]
            pairListMeta += [{"pair": pair, "AMMsells": targetTokenO.T}]
            pairList += [{"sourceToken": sourceTokenO.a, "targetToken": targetTokenO.a}]
            targetTokenO = T[pair.tknb]
            sourceTokenO = T[pair.tknq]
            pairListMeta += [{"pair": pair, "AMMsells": targetTokenO.T}]
            pairList += [{"sourceToken": sourceTokenO.a, "targetToken": targetTokenO.a}]
        result = self.hasLiquidityByPair(pairs=pairList)
        return tuple({**m, "hasLiquidity": r} for m, r in zip(pairListMeta, result))

    def mGetLiquidityByPair(self, pair, AMMsells):
        """
        liquidity values for multiple pairs

        :pair:          pair (as CarbonPair object or slashpair string)
        :AMMsells:      the token the AMM sells (as token name)
        :returns:       RangeByPair object
        """
        T = self._assertTokensProvided()
        pair = CarbonPair(pair)
        targetToken = AMMsells
        sourceToken = pair.other(targetToken)
        targetTokenO = T[targetToken]
        sourceTokenO = T[sourceToken]
        amount = self.getLiquidityByPair(sourceTokenO.a, targetTokenO.a)
        return self.PairLiquidity(
            amount=amount, 
            unit=targetToken, 
            AMMsells=AMMsells, 
            bidAsk="ask" if pair.has_basetoken(AMMsells) else "bid",
            pair=pair,
        )

    def mGetRangeByPair(self, pair, AMMsells):
        """
        gets the minimum and maximum exchange rate offered on Carbon between those two tokens

        :pair:          pair (as CarbonPair object or slashpair string)
        :AMMsells:      the token the AMM sells (as token name)
        :returns:       RangeByPair object
        """
        T = self._assertTokensProvided()
        pair = CarbonPair(pair)
        targetToken = AMMsells
        sourceToken = pair.other(targetToken)
        sourceTokenO = T[sourceToken]
        targetTokenO = T[targetToken]
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

    def mGetRateLiquidityDepthByPair(self, rate, pair, AMMsells):
        """
        liquidity depth (ie cumulative liquidity) at a given exchange rate

        :rate:          rate at which liquidity is evaluated (in units of the pair)
                        if the rate is an Array then the liquidity is evaluated at each rate
        :pair:          pair (as CarbonPair object or slashpair string)
        :AMMsells:      the token the AMM sells (as token name)
        :returns:       RangeByPair object; if rate is an Array so is the amount
        """
        T = self._assertTokensProvided()
        pair = CarbonPair(pair)
        targetToken = AMMsells
        sourceToken = pair.other(targetToken)
        sourceTokenO = T[sourceToken]
        targetTokenO = T[targetToken]
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
    
    def mGetMarketByPair(self, pair):
        """
        summarises market information for a given pair
        
        :pair:          pair (as CarbonPair object or slashpair string)
        :returns:       MarketByPair object
        """
        T = self._assertTokensProvided()
        pair = CarbonPair(pair)
        bidRange = self.mGetRangeByPair(pair, pair.tknq)
        askRange = self.mGetRangeByPair(pair, pair.tknb)
        bidLiq = self.mGetLiquidityByPair(pair, pair.tknq)
        askLiq = self.mGetLiquidityByPair(pair, pair.tknb)
        
        return self.MarketByPair(
            pair=pair.slashpair,
            bestBid=bidRange.startRate,
            lastBid=bidRange.endRate,
            liqBid=bidLiq.amount,
            bestAsk=askRange.startRate,
            lastAsk=askRange.endRate,
            liqAsk=askLiq.amount,
        )
    
    ########################################################################
    ## user information
    def mGetUserStrategies(self, user, nsd=True):
        """
        gets the strategies that are owned by the user

        :user:      user (as address)
        :returns:   a list of modified strategy objects
        :nsd:       number significant digits (True=default; None=no rounding)
        
        """
        strategies_raw = self.getUserStrategies(user)
        strategies = (self.reformatStrategy(s, nsd=nsd) for s in strategies_raw)
        strategies = (self.Strategy.from_sdk(s) for s in strategies)
        return tuple(strategies)


    ########################################################################
    ## maker actions
    def mCreateStrategy(self, pair, sellRangeStart, sellRangeEnd, sellAmountTknB, buyRangeStart, buyRangeEnd, buyAmountTknQ, overrides):
        """
        creates a strategy buying and selling tokens on a given pair


        :pair:                  pair (as CarbonPair object or slashpair string)
        :sellRangeStart:        minimum exchange rate at which to sell (in units of the pair)*
        :sellRangeEnd:          maximum exchange rate at which to sell (in units of the pair)*
        :sellAmountTknB:        amount to be sold (in units of base token)
        :buyRangeStart:         minimum exchange rate at which to buy (in units of the pair)*
        :buyRangeEnd:           maximum exchange rate at which to buy (in units of the pair)*
        :buyAmountTknQ:         amount to be bought (in units of quote token)

        *sell and buy in this case refers to the base token of the pair; maker orders are are buy low, 
        sell high, so the buy range -- in the natural quote direction of the pair -- is below the sell 
        range; selling starts at the low price and buying starts at the high price, so usually the order
        of the ranges is 
            
            buyRangeEnd < buyRangeStart <= sellRangeStart < sellRangeEnd
        """
        T = self._assertTokensProvided()
        pair = CarbonPair(pair)

        if not sellRangeStart <= sellRangeEnd:
            sellRangeStart, sellRangeEnd = sellRangeEnd, sellRangeStart
            print("[mCreateStrategy] sellRangeStart > sellRangeEnd, swapping", sellRangeStart, sellRangeEnd)

        if not buyRangeStart >= buyRangeEnd:
            buyRangeStart, buyRangeEnd = buyRangeEnd, buyRangeStart
            print("[mCreateStrategy] buyRangeStart < buyRangeEnd, swapping", buyRangeStart, buyRangeEnd)

        if not sellRangeStart > buyRangeStart:
            raise ValueError("sellRangeStart <= buyRangeStart", sellRangeStart, buyRangeStart)
        
        data = self.createBuySellStrategy(
            baseToken = T.ETH.a, 
            quoteToken = T.USDC.a, 
            buyPriceLow = buyRangeEnd, 
            buyPriceHigh = buyRangeStart, 
            buyBudget = buyAmountTknQ,
            sellPriceLow = sellRangeStart, 
            sellPriceHigh = sellRangeEnd, 
            sellBudget = sellAmountTknB,
            overrides = overrides, 
        )
        return data


    ########################################################################
    ## taker actions
    def mPrepareTrade(self, pair, traderBuySell, tkn, amount):
        """
        prepares a trade, calling getTradeData

        :pair:              pair (as CarbonPair object or slashpair string)
        :traderBuySell:     cls.BUY or cls.SELL, from PoV of the trader
        :tkn:               token to be bought or sold (as token name)
        :amount:            amount to be bought or sold (in units of tkn)
        :returns:           a TradeData object
        """
        T = self._assertTokensProvided()
        pair = CarbonPair(pair)
        if not traderBuySell in (self.BUY, self.SELL):
            raise ValueError("traderBuySell must be cls.BUY or cls.SELL", traderBuySell, self.BUY, self.SELL)
        if not pair.has_token(tkn):
            raise ValueError("tkn must be in pair", tkn, pair)
        if not amount > 0:
            raise ValueError("amount must be positive", amount)
        sourceToken = tkn if traderBuySell == self.SELL else pair.other(tkn)
        targetToken = pair.other(sourceToken)
        sourceTokenO = T[sourceToken]
        targetTokenO = T[targetToken]
        tradeByTargetAmount = (tkn == targetToken)
        if not Tokens.containsall({sourceToken, targetToken}):
            raise ValueError("not all token addresses are availabe", pair, Tokens)
        data = self.getTradeData(
            sourceToken=sourceTokenO.a, 
            targetToken=targetTokenO.a, 
            tradeByTargetAmount=tradeByTargetAmount, 
            amount=amount, 
        )
        tradeActions = [self.bn2intd(d) for d in data["tradeActions"]]
        actionsWei = [self.bn2intd(d) for d in data["actionsWei"]]
        actionsTokenRes = [self.bn2intd(self.str2floatd(d)) for d in data["actionsTokenRes"]]
        del data["tradeActions"]
        del data["actionsWei"]
        del data["actionsTokenRes"]
        tradeData =self.str2floatd(data)
        result = self.TradeData(
            pair=pair.slashpair,
            tkn=tkn,
            traderBuySell=traderBuySell,
            amount=amount,
            sourceToken=sourceTokenO,
            targetToken=targetTokenO,
            tradeByTargetAmount=tradeByTargetAmount,
            tradeActions = tradeActions,
            actionsWei = actionsWei,
            actionsTokenRes = actionsTokenRes,
            tradeData=tradeData,
        )
        return result
    
    MAXDEVIATIONPC = 0.1
    def mComposeTradeTransaction(self, sourceToken, targetToken, tradeActions, tradeData, tradeByTargetAmount, maxDeviationPc=None, deadline=None, overrides=None):
        """
        compose a trade transaction mostly based on the results of mPrepareTrade

        :sourceToken:               as returned by mPrepareTrade*
        :targetToken:               as returned by mPrepareTrade*
        :tradeActions:              as returned by mPrepareTrade*
        :tradeData:                 as returned by mPrepareTrade*
        :tradeByTargetAmount:       as returned by mPrepareTrade*
        :deadline:                  deadline (TODO)
        :maxDeviationPc:            max deviation from expected trade outcome in pc (default: 0.1 = 10%)**
        :overrides:                 overrides (TODO)
        :returns:                   a transaction object
        
        *NOTE: used cttargs or cttkwargs on the TradeData object to generate those
        **depending on the side specified this either determines a minimum amount received
        or a maximum amount delivered; this is expressed as percentage of the amount in tradeData
        """

        if maxDeviationPc is None: maxDeviationPc = self.MAXDEVIATIONPC
        if tradeByTargetAmount:
            data = self.composeTradeByTargetTransaction(
                    sourceToken=sourceToken.a, 
                    targetToken=targetToken.a, 
                    tradeActions=tradeActions, 
                    deadline=deadline,
                    maxInput=tradeData["totalSourceAmount"]*(1+maxDeviationPc),
                    overrides=overrides,
            )
        else:
            data = self.composeTradeBySourceTransaction(
                    sourceToken=sourceToken.a, 
                    targetToken=targetToken.a, 
                    tradeActions=tradeActions, 
                    deadline=deadline,
                    minReturn=tradeData["totalTargetAmount"]*(1-maxDeviationPc),
                    overrides=overrides,
            )
        return data

    

    ########################################################################
    ## helpers
    @classmethod
    def reformatOrders(cls, orders):
        """
        converts orders dict from BigNumber to int
        """
        return {k: cls.bn2intd(v) for k, v in orders.items()}