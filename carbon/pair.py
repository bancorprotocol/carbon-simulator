"""
represents a Carbon token pair; mostly helps with not getting confused on price quotes

(c) Copyright Bprotocol foundation 2022. 
Licensed under MIT

VERSION HISTORY
v2.0 -- changed constructor to allow for slashpair string
v2.0.1 -- convert_price
v2.0.2 -- allow constructor to take CarbonPair
"""
__version__ = "2.0.2"
__date__ = "11/Dec/2022"

from dataclasses import dataclass


@dataclass
class CarbonPair:
    """
    static information about a carbon token pair

    :slashpair:     the pair string in TKNB/TKNQ form, eg "ETH/USDC"; 
                    can also be a CarbonPair instance
    :tknb:          the base token (risk token) of the pair, eg ETH*
    :tknq:          the quote token (numeraire token) of the pair, eg USDC*

    * the differentiation between numeraire and risk tokens matter only for price quotes:
    in a given pair, _all_ prices will be quote as tknn per tknr, eg USDC per ETH

    see also https://www.investopedia.com/terms/i/isocurrencycode.asp for ISO currency code
    """
    __VERSION__ = __version__
    __DATE__    = __date__
    
    slashpair: any = None
    tknb: str = None 
    tknq: str = None

    def __post_init__(self):

        if self.slashpair:
            #print("[CarbonPair] slashpair has been provided", self.slashpair, self.tknb, self.tknq)
            if self.tknb or self.tknq:
                if self.tknb:
                    raise ValueError(
                        f"Parameters are pair, tknb, tknq; did you mean `tknb='{self.slashpair}', tknq='{self.tknb}'` ?",
                        self.slashpair, self.tknb, self.tknq)
                raise ValueError("Must not provide both pair and tknb, tknq", self.slashpair, self.tknb, self.tknq)
            
            if isinstance(self.slashpair, self.__class__):
                #print("[CarbonPair] creating pair from CarbonPair", self.__class__, self.slashpair.__class__, self.slashpair.slashpair)
                self.slashpair = self.slashpair.slashpair
            else:
                pass
                #print("[CarbonPair] creating pair from string", self.__class__, self.slashpair)

            self.slashpair = self.slashpair.upper()

            try:
                self.tknb, self.tknq = self.slashpair.split("/")
            except:
                raise ValueError("Illegal slashpair", self.slashpair)
            #print("[CarbonPair] {self.slashpair} -> tknb={self.tknb}, tknq={self.tknq}")        
        
        else:
            #print("[CarbonPair] tknb, tknq has hopefully been provided", self.tknb, self.tknq)
            if self.tknb is None or self.tknq is None:
                raise ValueError("If pair is None must provide tknb, tknq", self.slashpair, self.tknb, self.tknq)            
            self.tknb = self.tknb.upper()
            self.tknq = self.tknq.upper()
            self.slashpair = f"{self.tknb}/{self.tknq}"

    def __repr__(self):
        return f"P('{self.slashpair}')"
        return f"{self.__class__.__name__}('{self.slashpair}')"

    @classmethod
    def from_isopair_and_tkn(cls, isopair, tkn=None):
        """
        creates a class instance from and iso pair string and a token

        :isopair:   the pair, in ISO format (BASQUO)
        :tkn:       any token that is part of the pair*

        *tkn is only used to separate the two tokens in the pair string; it is is None,
        and the lenght of the pair string is 3 or 8, then it is split in the middle; if
        None and odd an exception is raised
        """
        isopair = isopair.upper()
        if tkn is None:
            if len(isopair) == 6:
                tknb, tknq = isopair[:3], isopair[3:]
            elif len(isopair) == 8:
                tknb, tknq = isopair[:4], isopair[4:]
            else:
                raise ValueError(
                    "If tkn not given, length of isopair must be 6 or 8",
                    isopair,
                    len(isopair),
                    tkn,
                )
        else:
            tkn2 = isopair.replace(tkn, ".")
            if tkn2 == isopair:
                raise ValueError(
                    "Invalid token specification (tkn not part of isopair)",
                    isopair,
                    tkn,
                )
            if tkn2[0] == ".":
                tknb = tkn
                tknq = tkn2[1:]
            elif tkn2[-1] == ".":
                tknb = tkn2[:-1]
                tknq = tkn
            else:
                raise ValueError(
                    "Invalid token specification (tkn inside isopair)", isopair, tkn
                )

        return cls(tknb=tknb, tknq=tknq)

    @classmethod
    def from_slashpair(cls, slashpair):
        """
        creates a pair from a slashstring (tknb/tknq, eg "ETH/USDC")

        :slashpair:     the pair, in the format tknb/tknq, eg "ETH/USDC"
        """
        slashpair = slashpair.upper()
        tokens = slashpair.split("/")
        if not len(tokens) == 2:
            raise ValueError("slashpair must be of form TKNB/TKNQ", slashpair, tokens)
        tknb = tokens[0].strip()
        tknq = tokens[1].strip()
        return cls(f"{tknb}/{tknq}")
        

    @classmethod
    def create(cls, arg1=None, arg2=None):
        """
        alternative constructor, allowing various paramerisations

        EXAMPLES

        p = Carbonpair.create("ETH/USDC")   # Method1: from slashpair
        Carbonpair.create(p)                # Method 2: from other CarbonPair
        Carbonpair.create("ETH", "USDC")    # Method 3: quote token, base token
        Carbonpair.create()                 # None
        """

        if arg1 is None and arg2 is None:
            return None

        if isinstance(arg1, cls):
            if not arg2 is None:
                raise ValueError("Second argument must be None if arg1 is pair", arg1, arg2)
            return arg1
        if arg2 is None:
            return cls(arg1)
        return cls(tknb=arg1, tknq=arg2)

    
    @property
    def price_convention(self):
        """
        returns the price convention of the pair, eg 'USDC per ETH'
        """
        return f"{self.tknq} per {self.tknb}"

    # @property
    # def pair_id(self):
    #     """
    #     returns the canonic Carbon id of the pair

    #     The Carbon ID of the pair is the concatenation of the token names
    #     in alphabetical order, in upper case, separated by colon.
    #     A carbon id does not imply any specific quote conventions
    #     """
    #     if self.tknb < self.tknq:
    #         return f"{self.tknb}:{self.tknq}"
    #     return f"{self.tknq}:{self.tknb}"

    # @property
    # def pair_id_is_reversed(self):
    #     """
    #     returns True iff Carbon id is reversed compared to iso

    #     if the carbon id is TKN1:TKN2 then ISO id of TKN1TKN2 will yield False, and TKN2TKN1 True
    #     """
    #     return self.tknb > self.tknq


    @property
    def pair_iso(self):
        """
        returns the name of the pair in iso format*, ie BASQUO

        *see https://www.investopedia.com/terms/i/isocurrencycode.asp
        """
        return f"{self.tknb}{self.tknq}"

    @property
    def pair_slash(self):
        """convenience access for slashpair"""
        return self.slashpair

    @property
    def reverse(self):
        """
        returns the pair with base and quote token reversed
        """
        return self.__class__(tknb=self.tknq, tknq=self.tknb)

    @property
    def basetoken(self):
        """alias for tknb"""
        return self.tknb 
    
    def has_basetoken(self, tkn):
        """
        returns True if `tkn` is the base token of the pair, otherwise False
        """
        return tkn == self.basetoken

    @property
    def quotetoken(self):
        """alias for tknq"""
        return self.tknq 
    
    def has_quotetoken(self, tkn):
        """
        returns True if `tkn` is the quote token of the pair, otherwise False
        """
        return tkn == self.quotetoken

    def has_token(self, tkn):
        """
        returns True if `tkn` is one of the tokens of the pair, otherwise False
        """
        if self.has_quotetoken(tkn):
            return True
        return self.has_basetoken(tkn)

    def other(self, tkn):
        """
        returns the other token, ie the one that is not `tkn`
        """
        if self.has_basetoken(tkn):
            return self.tknq
        if self.has_quotetoken(tkn):
            return self.tknb
        return None

    def convert(self, amtfrom, tknfrom, tknto, price):
        """
        converts one token amount into the other, with price according to curve convention

        :amtfrom:   the amount of tknfrom
        :tknfrom:   source token
        :tknto:     target token; can be the same as source token, in which case price is unity
        :price:     the price, in the price_convention of the pair
        :returns:   the amount of target token to be returned, or None if one of the tokens not in pair
        """
        if not self.has_token(tknfrom):
            return None
        if not self.has_token(tknto):
            return None
        if tknfrom == tknto:
            return amtfrom

        ismult = self.has_basetoken(tknfrom)
        if ismult:
            return amtfrom * price
        return amtfrom / price

    def price(self, price0, tknb0, tknq0):
        """
        the normalized price, according to convention

        :price0:    the raw price, as tknq0 per tknb0
        :tknb0:     the base token of price0
        :tknq0:     the quote token of price0
        :returns:   the amount of tarket token to be returned
        """
        if not self.has_token(tknb0):
            return None
        if not self.has_token(tknq0):
            return None
        if tknb0 == tknq0:
            return None

        isreverse = self.has_basetoken(tknq0)
        if isreverse:
            return 1.0 / price0
        return price0

    def convert_price(self, price, tknq):
        """
        converts a price expressed in the tknq numeraire in the numeraire of the pair

        :price:     the price to be converted, with numeraire being `tknq`
        :tknq:      the numeraire token in which the `price` is expressed
        :returns:   the price expressed in the numeraire conventions of the pair;
                    returns None if tknq not part of this pair or price is None
        """
        if price is None:
            return None
        if not self.has_token(tknq):
            return None
        if self.has_quotetoken(tknq):
            return price
        return 1 / price

    BUY = "buy"
    SELL = "sell"
    MAKERBUY = "buy"  # the MAKER is the person who placed the order
    MAKERSELL = (
        "sell"  # they own the optionality, ie they will only buy if in the money
    )
    TAKERBUY = "sell"  # the TAKER is the counterparty to this order; they have no
    TAKERSELL = (
        "buy"  # optionality here, so they'll execute iff it is beneficial for the MAKER
    )

    def limit_is_met(
        self, tkn, limit_price, buysell, current_price, reverse=False, asphrase=False
    ):
        """
        checks whether a limit order has been met

        :tkn:               the token to be bought or sold
        :limit_price:       the price at which the token is to be bought or sold; quoted
                            in the price convention of this pair
        :buysell:           whether the limit order is for buying or selling `tkn`; this is
                            from the point of view of the person who PLACED the order; use
                            `reverse=True` to do it from the point of view of the person
                            who ACCEPTED the orders; use the constants BUY and SELL
        :current_price:     the price which is tested against the limit order
        :asphrase:          returns the result as an explanatory phrase instead of bool
        :returns:           True if the limit order will lead to execution, false if not
        """
        if not self.has_token(tkn):
            print(f"[limit_is_met] invalid token {tkn} for pair {self.pair_iso}")
            return None

        if asphrase:
            limit_is_met = self.limit_is_met(
                tkn, limit_price, buysell, current_price, reverse
            )
            action = f"{buysell}s" if limit_is_met else f"does not {buysell}"
            result = f"Order placer {action} {tkn} at {current_price} {self.price_convention} (limit={limit_price})"
            return result

        # if the prices coincide, both buy and sell orders will be executed
        if current_price == limit_price:
            return True

        reverse = self.has_quotetoken(tkn)

        if buysell == self.BUY:
            # the order placer BUYs at limit or better
            # print(f"[limit_is_met] BUY cp={current_price} lp={limit_price} cp<=lp:{current_price<=limit_price}", )
            if not reverse:
                return (
                    current_price < limit_price
                )  # order placer only BUYS at limit or BELOW
            else:
                return current_price > limit_price  # ...reverse

        elif buysell == self.SELL:
            # the order placer SELLs at limit or better
            # print(f"[limit_is_met] SELL cp={current_price} lp={limit_price} cp<=lp:{current_price<=limit_price}", )
            if not reverse:
                return (
                    current_price > limit_price
                )  # order placer only SELLS at limit or ABOVE
            else:
                return current_price < limit_price  # ...reverse
        else:
            print(f"[limit_is_met] invalid choice for buysell [{buysell}]")
