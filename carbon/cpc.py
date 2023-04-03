"""
Carbon -- representing a levered constant product curve

(c) Copyright Bprotocol foundation 2023. 
Licensed under MIT

NOTE: this class is not part of the API of the Carbon protocol, and you must expect breaking
changes even in minor version updates. Use at your own risk.

v1.0: ConstantProductCurve class
v1.1: added CPCContainer class
v1.1.1: bugfix
v1.2: UniV2, UniV3, and Carbon constructors; serialization
v1.3: plot
v1.3.1: params
v2.0: container allows curve selection; analytics; trade execution
"""
__VERSION__ = "2.1"
__DATE__ = "3/Apr/2023"

from dataclasses import dataclass, field, asdict, InitVar
import random
from math import sqrt
import numpy as np
import pandas as pd
import json
from matplotlib import pyplot as plt
from carbon.tools.params import Params
import itertools

try:
    dataclass_ = dataclass(frozen=True, kw_only=True)
except:
    dataclass_ = dataclass(frozen=True)

class AttrDict(dict):
    """
    A dictionary that allows for attribute-style access
    
    see https://stackoverflow.com/questions/4984647/accessing-dict-keys-like-an-attribute
    """
    def __init__(self, *args, **kwargs):
        super(AttrDict, self).__init__(*args, **kwargs)
        self.__dict__ = self

@dataclass
class Pair:
    """
    a pair in notation TKNB/TKNQ; can also be provided as list
    """
    tknb: str=field(init=False)
    tknq: str=field(init=False)
    pair: InitVar[str]=None

    def __post_init__(self, pair):
        if isinstance(pair, CPCContainer.Pair):
            self.tknb = pair.tknb
            self.tknq = pair.tknq
        elif isinstance(pair, str):
            self.tknb, self.tknq = pair.split("/")
        elif pair is False:
            # used in alternative constructors
            pass
        else:
            try:
                self.tknb, self.tknq = pair
            except:
                raise ValueError(f"pair must be a string or list of two strings {pair}")

    @classmethod
    def from_tokens(cls, tknb, tknq):
        pair = cls(False)
        pair.tknb = tknb
        pair.tknq = tknq
        return pair
    
    def __str__(self):
        return f"{self.tknb}/{self.tknq}"
    
    @property
    def pair(self):
        """string representation of the pair"""
        return str(self)
    
    @property
    def pairt(self):
        """tuple representation of the pair"""
        return (self.tknb, self.tknq)
    
    @property
    def pairr(self):
        """returns the reversed pair"""
        return f"{self.tknq}/{self.tknb}"
    
    @property
    def pairrt(self):
        """tuple representation of the reverse pair"""
        return (self.tknq, self.tknb)
    
    @property
    def tknx(self):
        return self.tknb
    
    @property
    def tkny(self):
        return self.tknq
    
    NUMERAIRE_TOKENS = {
        tkn:i for i, tkn in enumerate(["USDC", "USDT", "DAI", "TUSD", "BUSD", "PAX", "GUSD", 
            "USDS", "sUSD", "mUSD", "HUSD", "USDN", "USDP", "USDQ", "ETH", "WETH", "WBTC", "BTC"])}

    @property
    def isprimary(self):
        """whether the representation is primary or secondary"""
        tknqix = self.NUMERAIRE_TOKENS.get(self.tknq, 1e10)
        tknbix = self.NUMERAIRE_TOKENS.get(self.tknb, 1e10)
        if tknqix == tknbix:
            return self.tknb < self.tknq
        return tknqix < tknbix
    
    def primary_price(self, p):
        """returns the primary price (p if primary, 1/p if secondary)"""
        return p if self.isprimary else 1/p
    pp = primary_price
        
    @property
    def primary(self):
        """returns the primary pair"""
        return self.pair if self.isprimary else self.pairr
    
    @property
    def secondary(self):
        """returns the secondary pair"""
        return self.pairr if self.isprimary else self.pair
    
    @classmethod
    def wrap(cls, pairlist):
        """wraps a list of strings into Pairs"""
        return tuple(cls(p) for p in pairlist)
    
    @classmethod
    def unwrap(cls, pairlist):
        """unwraps a list of Pairs into strings"""
        return tuple(str(p) for p in pairlist)


@dataclass_
class ConstantProductCurve():
    """
    represents a, potentially levered, constant product curve
    
    :k:        pool constant k = xy [x=k/y, y=k/x]
    :x:        (virtual) pool state x (virtual number of base tokens for sale)
    :x_act:    actual pool state x (actual number of base tokens for sale)
    :y_act:    actual pool state y (actual number of quote tokens for sale)
    :pair:     token pair in slash notation ("TKNB/TKNQ"); TKNB is on the x-axis, TKNQ on the y-axis
    :cid:      unique id (optional)
    :fee:      fee (optional); eg 0.01 for 1%
    :descr:    description (optional; eg. "UniV3 0.1%")
    :params:   additional parameters (optional)
    
    NOTE: use the alternative constructors `from_xx` rather then the canonical one 
    """
    __VERSION__ = __VERSION__
    __DATE__ = __DATE__
    
    k: float
    x: float
    x_act: float = None
    y_act: float = None
    pair: str = None
    cid: any=None
    fee: float=None
    descr: str=None
    params: AttrDict = field(default=None, repr=True, hash=False)
        
    def __post_init__(self):

        if self.params is None:
            super().__setattr__('params', AttrDict())
        elif isinstance(self.params, str):
            super().__setattr__('params', AttrDict(json.loads(self.params)))
        elif isinstance(self.params, dict):
            super().__setattr__('params', AttrDict(self.params))
        
        if self.x_act is None: 
            super().__setattr__('x_act', self.x) # required because class frozen
        
        if self.y_act is None: 
            super().__setattr__('y_act', self.y) # ditto
            
        if self.pair is None:
            super().__setattr__('pair', "TKNB/TKNQ")
        
        super().__setattr__('pairo', Pair(self.pair))

        if self.isbigger(big=self.x_act, small=self.x):
            print("[ConstantProductCurve] x_act > x:", self.x_act, self.x)
            
        if self.isbigger(big=self.y_act, small=self.y):
            print("[ConstantProductCurve] y_act > y:", self.y_act, self.y)
    
    def asdict(self):
        "returns a dict representation of the curve"
        return asdict(self)
    
    @classmethod
    def from_dict(cls, d):
        "returns a curve from a dict representation"
        return cls(**d)
    
    def setcid(self, cid):
        """sets the curve id [can only be done once]"""
        assert self.cid is None, "cid can only be set once"
        super().__setattr__('cid', cid)
        return self

    @classmethod
    def from_kx(cls, k, x, x_act=None, y_act=None, pair=None, cid=None, fee=None, descr=None):
        "constructor: from k,x (and x_act, y_act)"
        return cls(k=k, x=x, x_act=x_act, y_act=y_act, pair=pair, cid=cid, fee=fee, descr=descr)
   
    @classmethod
    def from_ky(cls, k, y, x_act=None, y_act=None, pair=None, cid=None, fee=None, descr=None):
        "constructor: from k,y (and x_act, y_act)"
        return cls(k=k, x=k/y, x_act=x_act, y_act=y_act, pair=pair, cid=cid, fee=fee, descr=descr) 
    
    @classmethod
    def from_xy(cls, x, y, x_act=None, y_act=None, pair=None, cid=None, fee=None, descr=None):
        "constructor: from x,y (and x_act, y_act)"
        return cls(k=x*y, x=x, x_act=x_act, y_act=y_act, pair=pair, cid=cid, fee=fee, descr=descr)
    
    @classmethod
    def from_pk(cls, p, k, x_act=None, y_act=None, pair=None, cid=None, fee=None, descr=None):
        "constructor: from k,p (and x_act, y_act)"
        return cls(k=k, x=sqrt(k/p), x_act=x_act, y_act=y_act, pair=pair, cid=cid, fee=fee, descr=descr)
    
    @classmethod
    def from_px(cls, p, x, x_act=None, y_act=None, pair=None, cid=None, fee=None, descr=None):
        "constructor: from x,p (and x_act, y_act)"
        return cls(k=x*x*p, x=x, x_act=x_act, y_act=y_act, pair=pair, cid=cid, fee=fee, descr=descr)
    
    @classmethod
    def from_py(cls, p, y, x_act=None, y_act=None, pair=None, cid=None, fee=None, descr=None):
        "constructor: from y,p (and x_act, y_act)"
        return cls(k=y*y/p, x=y/p, x_act=x_act, y_act=y_act, pair=pair, cid=cid, fee=fee, descr=descr)
    
    @classmethod
    def from_pkpp(cls, p, k, p_min=None, p_max=None, pair=None, cid=None, fee=None, descr=None, params=None):
        "constructor: from k, p, p_min, p_max (default for last two is p)"
        if p_min is None: p_min = p
        if p_max is None: p_max = p
        x0 = sqrt(k/p)
        y0 = sqrt(k*p)
        xa = x0 - sqrt(k/p_max)
        ya = y0 - sqrt(k*p_min)
        return cls(k=k, x=x0, x_act=xa, y_act=ya, pair=pair, cid=cid, fee=fee, descr=descr, params=params)
    
    @classmethod
    def from_univ2(cls, x_tknb=None, y_tknq=None, k=None, pair=None, fee=None, cid=None, descr=None, params=None):
        """
        constructor: from Uniswap V2 pool (see class docstring for other parameters)
        
        :x_tknb:    current pool liquidity in token x (base token of the pair)*
        :y_tknq:    current pool liquidity in token y (quote token of the pair)*
        :k:         uniswap liquidity parameter (k = xy)*
        
        *exactly one of k,x,y must be None; all other parameters must not be None;
        a reminder that x is TKNB and y is TKNQ
        """
        x = x_tknb
        y = y_tknq

        assert not pair is None, "pair must not be None"
        assert not cid is None, "cid must not be None"
        assert not descr is None, "descr must not be None"
        assert not fee is None, "fee must not be None"

        if k is None:
            assert x is not None and y is not None, "k is None, so x,y must not"
            k = x * y
        elif x is None:
            assert y is not None, "x is None, so y must not"
            x = k/y
        elif y is None:
            y = k/x
        else:
            assert False, "exactly one of k,x,y must be None"
        
        return cls(k=k, x=x, x_act=x, y_act=y, pair=pair, cid=cid, fee=fee, descr=descr, params=params)
    
    @classmethod
    def from_univ3(cls, Pmarg, uniL, uniPa, uniPb, pair, cid, fee, descr, params=None):
        """
        constructor: from Uniswap V3 pool (see class docstring for other parameters)
        
        :Pmarg:     current pool marginal price
        :uniL:      uniswap liquidity parameter (L**2 == k)
        :uniPa:     uniswap price range lower bound Pa (Pa < P < Pb)
        :uniPb:     uniswap price range upper bound Pb (Pa < P < Pb)
        """

        P = Pmarg
        assert uniPa < uniPb, f"uniPa < uniPb required ({uniPa}, {uniPb})"
        assert uniPa < P < uniPb, f"uniPa < Pmarg < uniPb required ({uniPa}, {P}, {uniPb})"
        if params is None: 
            params = AttrDict(L=uniL)
        else:
            params = AttrDict({**params, L:uniL})
        k = uniL * uniL
        return cls.from_pkpp(
            p=P, 
            k=k, 
            p_min=uniPa, 
            p_max=uniPb, 
            pair=pair, 
            cid=cid, 
            fee=fee, 
            descr=descr,
            params = params,
            )
    
    @classmethod
    def from_carbon(cls, yint=None, y=None, pa=None, pb=None, A=None, B=None, pair=None, tkny=None, fee=None, cid=None, descr=None, params=None, isdydx=True):
        """
        constructor: from a single Carbon order (see class docstring for other parameters)*
        
        :yint:      current pool y-intercept**
        :y:         current pool liquidity in token y
        :pa:        carbon price range left bound (higher price in dy/dx)
        :pb:        carbon price range right bound (lower price in dy/dx)
        :A:         alternative to pa, pb: A = sqrt(pa) - sqrt(pb) in dy/dy
        :B:         alternative to pa, pb: B = sqrt(pb) in dy/dy
        :tkny:      token y
        :isdydx:    if True prices in dy/dx, if False in quote direction of the pair

        *Note that ALL parameters are mandatory, except that EITHER pa, bp OR A, B 
        must be given but not both; we do not correct for incorrect assignment of
        pa and pb, so if pa <= pb IN THE DY/DX DIRECTION, MEANING THAT THE NUMBERS
        ENTERED MAY SHOW THE OPPOSITE RELATIONSHIP, then an exception will be raised

        **note that the result does not depend on yint, and for the time being we
        allow to omit yint (in which case it is set to y, but this does not make
        a difference for the result)
        """
        assert not yint is None, "yint must not be None"
        assert not y is None, "y must not be None"
        assert not pair is None, "pair must not be None"
        assert not tkny is None, "tkny must not be None"
        #assert not fee is None, "fee must not be None"
        #assert not cid is None, "cid must not be None"
        #assert not descr is None, "descr must not be None"

        # if yint is None:
        #     yint = y
        assert y <= yint, "y must be <= yint"
        assert y >= 0, "y must be >= 0"

        if A is None or B is None:
            # A,B is None, so we look at prices and isdydx  
            #print("[from_carbon] A, B:", A, B, pa, pb)
            assert A is None and B is None, "A or B is None, so both must be None"
            assert pa is not None and pb is not None, "A,B is None, so pa,pb must not"
            
        if pa is None or pb is None:
            # pa,pb is None, so we look at A,B and isdydx must be True
            #print("[from_carbon] pa, pb:", A, B, pa, pb)
            assert pa is None and pb is None, "pa or pb is None, so both must be None"
            assert A is not None and B is not None, "pa,pb is None, so A,B must not"
            assert isdydx is True, "we look at A,B so isdydx must be True"
            assert A >= 0, "A must be non-negative" # we only check for this one as it is a difference

        assert not (A is not None and B is not None and pa is not None and pb is not None), "either A,B or pa,pb must be None"
            
        tknb, tknq = pair.split("/")
        assert tkny in (tknb, tknq), f"tkny must be in pair ({tkny}, {pair})"
        tknx = tknb if tkny == tknq else tknq
        
        if A is None or B is None:
            # A,B is None, so we look at prices and isdydx  
            
            # pair quote direction is tknq per tknb; dy/dx is tkny per tknx
            # therefore, dy/dx equals pair quote direction if tkny == tknq, otherwise reverse
            if not isdydx:
                if not tkny == tknq:
                    pa, pb = 1/pa, 1/pb

            # zero-width ranges are somewhat extended for numerical stability
            if pa == pb:
                pa *= 1.0000001
                pb /= 1.0000001
            
            # validation
            assert pa > pb, f"pa > pb required ({pa}, {pb})"

            # finally set A, B
            A = sqrt(pa) - sqrt(pb)
            B = sqrt(pb)
        
        # set some intermediate parameters (see handwritten notes in repo)
        yasym = yint * B/A
        kappa = yint**2 / A**2

        params0 = dict(y=y, yint=yint, A=A, B=B)
        if params is None: 
            params = AttrDict(params0)
        else:
            params = AttrDict({**params, **params0})

        # finally instantiate the pool
        return cls(
            k = kappa,
            x = kappa/(y + yasym),
            x_act = 0,
            y_act = y,
            pair = f"{tknx}/{tkny}",
            cid = cid,
            fee = fee,
            descr = descr,
            params = params,
        )

    def execute(self, dx=None, dy=None, verbose=False):
        """
        executes a transaction in the pool, returning a new curve object

        :dx:        amount of token x to be +added to/-removed from the pool*
        :dy:        amount of token y to be +added to/-removed from the pool*
        :returns:   new curve object

        *at least one of dx, dy must be None
        """
        if not dx is None and not dy is None:
            raise ValueError(f"either dx or dy must be None {dx} {dy}")
        
        if dx is None and dy is None:
            dx = 0
        
        if not dx is None:
            if not dx >= -self.x_act:
                raise ValueError(f"dx must be >= -x_act ({dx}, {self.x_act})")
            newx = self.x + dx
            newy = self.k / newx

        else:
            if not dy >= -self.y_act:
                raise ValueError(f"dy must be >= -y_act ({dy}, {self.y_act})")
            newy = self.y + dy
            newx = self.k / newy
        if verbose:
            if dx is None: dx=newx-self.x
            if dy is None: dy=newy-self.y
            print(f"{self.pair} dx={dx:.2f} {self.tknx} dy={dy:.2f} {self.tkny} | x:{self.x:.1f}->{newx:.1f} xa:{self.x_act:.1f}->{self.x_act+newx-self.x:.1f} ya:{self.y_act:.1f}->{self.y_act+newy-self.y:.1f} k={self.k:.1f}")
        return self.__class__(
            k = self.k,
            x = newx,
            x_act = self.x_act + newx - self.x,
            y_act = self.y_act + newy - self.y,
            pair = self.pair,
            cid = None,
            fee = self.fee,
            descr = f"{self.descr} [dx={dx}]",
            params = {**self.params, "traded": {"dx": dx, "dy": dy}},
        )
            
    @property
    def tknb(self):
        "base token"
        return self.pair.split("/")[0]
    tknx = tknb
    
    @property
    def tknq(self):
        "quote token"
        return self.pair.split("/")[1]
    tkny = tknq

    @property
    def description(self):
        "description of the pool"
        s1 = f"tknx = {self.x_act} [virtual: {self.x}] {self.tknx}"
        s2 = f"tkny = {self.y_act} [virtual: {self.y}] {self.tkny}"
        s3 = f"p    = {self.p} [min={self.p_min}, max={self.p_max}] {self.tknq} per {self.tknb}"
        s4 = f"fee  = {self.fee}, cid = {self.cid}, descr = {self.descr}"
        return "\n".join([s1,s2,s3,s4])
    
    @property
    def y(self):
        "(virtual) pool state x (virtual number of base tokens for sale)"
        return self.k/self.x
    
    @property
    def p(self):
        "pool price (in dy/dx)"
        return self.y/self.x
    
    @property
    def pp(self):
        "pool price in the native quote of the curve Pair object"
        return self.pairo.pp(self.p)

    @property
    def kbar(self):
        "kbar = sqrt(k); kbar scales linearly with the pool size"
        return sqrt(self.k)
    
    @property
    def x_min(self):
        "minimum (virtual) x value"
        return self.x - self.x_act
    
    @property
    def y_min(self):
        "minimum (virtual) y value"
        return self.y - self.y_act
    
    @property
    def x_max(self):
        "maximum (virtual) x value"
        if self.y_min > 0:
            return self.k/self.y_min
        else:
            return None
    
    @property
    def y_max(self):
        "maximum (virtual) y value"
        if self.x_min > 0:
            return self.k/self.x_min
        else:
            return None
    
    @property
    def p_max(self):
        "maximum pool price (in dy/dx; None if unlimited) = y_max/x_min"
        if not self.x_min is None and self.x_min > 0:
            return self.y_max/self.x_min
        else:
            return None
    
    @property
    def p_min(self):
        "minimum pool price (in dy/dx; None if unlimited) = y_min/x_max"
        if not self.x_max is None and self.x_max > 0:
            return self.y_min/self.x_max
        else:
            return None
        
    def yfromx_f(self, x, ignorebounds=False):
        "y value for given x value (if in range; None otherwise)"
        y = self.k/x
        if ignorebounds:
            return y
        if not self.inrange(y, self.y_min, self.y_max):
            return None
        return y
    
    def xfromy_f(self, y, ignorebounds=False):
        "x value for given y value (if in range; None otherwise)"
        x = self.k/y
        if ignorebounds:
            return x
        if not self.inrange(x, self.x_min, self.x_max):
            return None
        return x
    
    def dyfromdx_f(self, dx, ignorebounds=False):
        "dy value for given dx value (if in range; None otherwise)"
        y = self.yfromx_f(self.x + dx, ignorebounds=ignorebounds)
        if y is None:
            return None
        return y-self.y
    
    def dxfromdy_f(self, dy, ignorebounds=False):
        "dx value for given dy value (if in range; None otherwise)"
        x = self.xfromy_f(self.y + dy, ignorebounds=ignorebounds)
        if x is None:
            return None
        return x-self.x
    
    @staticmethod
    def inrange(v, minv=None, maxv=None):
        "True if minv <= v <= maxv; None means no boundary"
        if not minv is None:
            if v < minv:
                return False
        if not maxv is None:
            if v > maxv:
                return False
        return True
    
    EPS = 1e-6
    def isequal(self, x,y):
        "returns True if x and y are equal within EPS"
        if x == 0:
            return abs(y) < self.EPS
        return abs(y/x-1) < self.EPS

    def isbigger(self, small, big):
        "returns True if small is bigger than big within EPS"
        if small == 0:
            return big > self.EPS
        return big/small > 1+self.EPS
    
    
@dataclass
class CPCContainer():
    """
    container for ConstantProductCurve objects (use += to add items)
    """
    __VERSION__ = __VERSION__
    __DATE__ = __DATE__
    Pair = Pair
    
    curves: list = field(default_factory=list)

    def __post_init__(self):
        if not isinstance(self.curves, list):
            self.curves = list(self.curves)
        for i, c in enumerate(self.curves):
            if c.cid is None:
                c.setcid(i)
        self.curves_by_cid = {c.cid: c for c in self.curves}
        self.curveix_by_curve = {c: i for i, c in enumerate(self.curves)}
        self.curves_by_primary_pair = {c.pairo.primary: c for c in self.curves}
        # for c in self.curves:
        #     try:
        #         self.curves_by_primary_pair[c.pairo.primary].append(c)
        #     except KeyError:
        #         self.curves_by_primary_pair[c.pairo.primary] = [c]
    
    def asdicts(self):
        """returns list of dictionaries representing the curves"""
        return [c.asdict() for c in self.curves]
    
    def asdf(self):
        """returns pandas dataframe representing the curves"""
        return pd.DataFrame.from_dict(self.asdicts()).set_index("cid")
    
    @classmethod
    def from_dicts(cls, dicts):
        """creates a container from a list of dictionaries"""
        return cls([ConstantProductCurve.from_dict(d) for d in dicts])
       
    @classmethod
    def from_df(cls, df):
        "creates a container from a dataframe representation"
        if "cid" in df.columns:
            df = df.set_index("cid")
        return cls.from_dicts(df.reset_index().to_dict("records"))
    
    def add(self, item):
        """adds a single ConstantProductCurve item to the container"""
        assert isinstance(item, ConstantProductCurve), f"item must be a ConstantProductCurve object {item}"
        if item.cid is None:
            item.setcid(len(self))
        self.curves_by_cid[item.cid] = item
        self.curveix_by_curve[item] = len(self)
        self.curves += [item]
        try:
            self.curves_by_primary_pair[item.pairo.primary].append(item)
        except KeyError:
            self.curves_by_primary_pair[item.pairo.primary] = [item]
        return self
    
    def price(self, tknb, tknq):
        """returns price of tknb in tknq (tknb per tknq)"""
        pairo = Pair.from_tokens(tknb, tknq)
        curves = self.curves_by_primary_pair.get(pairo.primary, None)
        if curves is None:
            return None
        pp = sum(c.pp for c in curves) / len(curves)
        return pp if pairo.isprimary else 1/pp
    
    def __iadd__(self, other):
        """alias for either add"""
        return self.add(other)
    
    def __iter__(self):
        return iter(self.curves)
    
    def __len__(self):
        return len(self.curves)
    
    def __getitem__(self, key):
        return self.curves[key]
    
    def __contains__(self, curve):
        return curve in self.curveix_by_curve
    
    def tknys(self, curves=None):
        """returns set of all base tokens used by the curves"""
        if curves is None:
            curves = self.curves
        return {c.tknb for c in curves}
    
    def tknxs(self, curves=None):
        """returns set of all quote tokens used by the curves"""
        if curves is None:
            curves = self.curves
        return {c.tknq for c in curves}
    
    def tkns(self, curves=None):
        """returns set of all tokens used by the curves"""
        return self.tknxs(curves).union(self.tknys(curves))
    tokens = tkns

    def tokens_s(self, curves=None):
        """returns set of all tokens used by the curves as a string"""
        return ",".join(sorted(self.tokens(curves)))
    
    def pairs(self):
        """returns set of all pairs"""
        return {c.pair for c in self}
    
    @staticmethod
    def pairset(pairs):
        """converts string, list or set of pairs into a set of pairs"""
        if isinstance(pairs, str):
            pairs = (p.strip() for p in pairs.split(","))
        return set(pairs)
    
    def make_symmetric(self, df):
        """converts df into upper triangular matrix by adding the lower triangle"""
        df = df.copy()
        fields = df.index.union(df.columns)
        df = df.reindex(index=fields, columns=fields)
        df = df + df.T
        df = df.fillna(0).astype(int)
        return df

    FP_ANY = "any"
    FP_ALL = "all"
    def filter_pairs(self, pairs=None, anyall=FP_ALL, **conditions):
        """
        filters the pairs according to the target conditions(s)
        :pairs:         list of pairs to filter; if None, all pairs are used
        :anyall:        how conditions are combined (FP_ANY or FP_ALL)
        :condition*:    determines the filtering condition; all or any must be met
                        :bothin:    both tokens must be in the list
                        :onein:     at least one token must be in the list
                        :notin:     none of the tokens must be in the list
                        :contains:  alias for onein
                        :tknbin:    tknb must be in the list
                        :tknbnotin: tknb must not be in the list
                        :tknqin:    tknq must be in the list
                        :tknqnotin: tknq must not be in the list

        *an arbitrary differentiator can be appended to the condition using "_"
        (eg onein_1, onein_2, onein_3, ...) allowing to specify multiple conditions
        of the same type
        """
        if pairs is None:
            pairs = self.pairs()
        if not conditions:
            return pairs
        pairs = self.Pair.wrap(pairs)
        results = []
        for condition in conditions:
            cpairs = self.pairset(conditions[condition])
            condition0 = condition.split("_")[0]
            #print(f"condition: {condition} | {condition0} [{conditions[condition]}]")
            if condition0 == "bothin":
                results += [{str(p) for p in pairs if p.tknb in cpairs and p.tknq in cpairs}]
            elif condition0 == "contains" or condition0 == "onein":
                results += [{str(p) for p in pairs if p.tknb in cpairs or p.tknq in cpairs}]
            elif condition0 == "notin":
                results += [{str(p) for p in pairs if p.tknb not in cpairs and p.tknq not in cpairs}]
            elif condition0 == "tknbin":
                results += [{str(p) for p in pairs if p.tknb in cpairs}]
            elif condition0 == "tknbnotin":
                results += [{str(p) for p in pairs if p.tknb not in cpairs}]
            elif condition0 == "tknqin":
                results += [{str(p) for p in pairs if p.tknq in cpairs}]
            elif condition0 == "tknqnotin":
                results += [{str(p) for p in pairs if p.tknq not in cpairs}]
            else:
                raise ValueError(f"unknown condition {condition}")
        
        #print(f"results: {results}")
        if anyall == self.FP_ANY:
            #print(f"anyall = {anyall}: union")
            return set.union(*results)
        elif anyall == self.FP_ALL:
            #print(f"anyall = {anyall}: intersection")
            return set.intersection(*results)
        else:
            raise ValueError(f"unknown anyall {anyall}")
    def fp(self, pairs=None, **conditions):
        """alias for filter_pairs (for interactive use)"""
        return self.filter_pairs(pairs, **conditions)
    
    def fpb(self, bothin, pairs=None, anyall=FP_ALL, **conditions):
        """alias for filter_pairs bothin (for interactive use)"""
        return self.filter_pairs(pairs=pairs, bothin=bothin, anyall=anyall, **conditions)
    
    def fpo(self, onein, pairs=None, anyall=FP_ALL, **conditions):
        """alias for filter_pairs onein (for interactive use)"""
        return self.filter_pairs(pairs=pairs, onein=onein, anyall=anyall, **conditions)
    
    @classmethod
    def _record(cls, c=None):
        """returns the record (or headings, if none) for the pair c"""
        if not c is None:
            p = cls.Pair(c.pair)
            return (c.tknx, c.tkny, c.tknb, c.tknq, p.pair, p.primary, p.isprimary, c.p, p.pp(c.p), c.x, c.x_act, c.y, c.y_act, c.cid)
        else:
            return ( "tknx", "tkny", "tknb", "tknq", "pair", "primary", "isprimary", "p",     "pp",  "x", "xa",    "y", "ya",  "cid")
        
    AT_LIST = "list"
    AT_LISTDF = "listdf"
    AT_VOLUMES = "volumes"
    AT_VOLUMESAGG = "vaggr"
    AT_VOLSAGG = "vaggr"
    AT_PIVOTXY = "pivotxy"
    AT_PIVOTXYS = "pivotxys"
    AT_PIVOTBQ = "pivotbq"
    AT_PIVOTBQS = "pivotbqs"
    AT_PRICES  = "prices"
    AT_MAX = "max"
    AT_MIN = "min"
    AT_SD = "std"
    AT_SDPC = "stdpc"
    AT_PRICELIST = "pricelist"
    AT_PRICELISTAGG = "plaggr"
    AT_PLAGG = "plaggr"
    def pairs_analysis(self, target=AT_PIVOTBQ, pretty=False, pairs=None, **params):
        """
        returns a dataframe with the analysis of the pairs according to the analysis target

        :target:    :AT_LIST:       list of pairs and associated data
                    :AT_LISTDF:     ditto but as a dataframe
                    :AT_VOLUMES:    list of volume per token and curve
                    :AT_VOLSAGG:    ditto but also aggregated by curve
                    :AT_PIVOTXY:    pivot table number of pairs tknx/tkny
                    :AT_PIVOTBQ:    ditto but with tknb/tknq
                    :AT_PIVOTXYS:   above anlysis but symmetric matrix*
                    :AT_PIVOTBQS:   ditto
                    :AT_PRICES:     average prices per (directed) pair
                    :AT_MAX:        ditto max
                    :AT_MIN:        ditto min
                    :AT_SD:         ditto price standard deviation
                    :AT_SDPC:       ditto percentage standard deviation
                    :AT_PRICELIST:  list of prices per curve
                    :AT_PLAGG:      list of prices aggregated by pair
        :pretty:    in some cases, returns a prettier but less useful result
        :pairs:     list of pairs to analyze; if None, all pairs
        :params:    kwargs that some of the analysis targets may use
        
        *eg ETH/USDC would appear in ETH/USDC and in USDC/ETH
        """
        record = self._record
        cols   = self._record()

        if pairs is None:
            pairs = self.pairs()
        curvedata = (record(c) for c in self.bypairs(pairs))
        if target == self.AT_LIST:
            return tuple(curvedata)
        df = pd.DataFrame(curvedata, columns=cols)
        if target == self.AT_LISTDF:
            return df
        
        if target == self.AT_VOLUMES or target == self.AT_VOLSAGG:
            dfb = df[["tknb", "cid", "x", "xa"]].copy().rename(columns={"tknb": "tkn", "x": "amtv", "xa": "amt"})
            dfq = df[["tknq", "cid", "y", "ya"]].copy().rename(columns={"tknq": "tkn", "y": "amtv", "ya": "amt"})
            df1 = pd.concat([dfb, dfq], axis=0)
            df1 = df1.sort_values(["tkn", "cid"])
            if target == self.AT_VOLUMES: 
                df1 = df1.set_index(["tkn", "cid"])
                df1["lvg"] = df1["amtv"]/df1["amt"]
                return df1
            df1["n"] = (1,)*len(df1)
            #df1 = df1.groupby(["tkn"]).sum()
            df1 = df1.pivot_table(
                index="tkn", 
                values=["amtv", "amt", "n"], 
                aggfunc={"amtv":["sum", AF.herfindahl, AF.herfindahlN], "amt":["sum", AF.herfindahl, AF.herfindahlN], "n":"count"}
                )
            price_eth = (self.price(tknb=t, tknq="WETH") if t != "WETH" else 1 for t in df1.index)
            df1["price_eth"] = tuple(price_eth)
            df1["amtv_eth"] = df1[("amtv", "sum")]*df1["price_eth"]
            df1["amt_eth"] = df1[("amt", "sum")]*df1["price_eth"]
            df1["lvg"] = df1["amtv_eth"]/df1["amt_eth"]
            return df1
    
        if target == self.AT_PIVOTXY or target == self.AT_PIVOTXYS:
            pivot = df.pivot_table(index="tknx", columns="tkny", values="tknb", aggfunc="count").fillna(0).astype(int)
            if target == self.AT_PIVOTXY: return pivot
            return self.make_symmetric(pivot)
        
        if target == self.AT_PIVOTBQ or target == self.AT_PIVOTBQS:
            pivot = df.pivot_table(index="tknb", columns="tknq", values="tknx", aggfunc="count").fillna(0).astype(int)
            if target == self.AT_PIVOTBQ: 
                if pretty: return pivot.replace(0, "")
                return pivot
            pivot = self.make_symmetric(pivot)
            if pretty: return pivot.replace(0, "")
            return pivot
        
        if target == self.AT_PRICES:
            pivot = df.pivot_table(index="tknb", columns="tknq", values="p", aggfunc="mean")
            pivot = pivot.fillna(0).astype(float)
            if pretty: return pivot.replace(0, "")
            return pivot
        
        if target == self.AT_MAX:
            pivot = df.pivot_table(index="tknb", columns="tknq", values="p", aggfunc=np.max)
            pivot = pivot.fillna(0).astype(float)
            if pretty: return pivot.replace(0, "")
            return pivot
        
        if target == self.AT_MIN:
            pivot = df.pivot_table(index="tknb", columns="tknq", values="p", aggfunc=np.min)
            pivot = pivot.fillna(0).astype(float)
            if pretty: return pivot.replace(0, "")
            return pivot
        
        if target == self.AT_SD:
            pivot = df.pivot_table(index="tknb", columns="tknq", values="p", aggfunc=np.std)
            pivot = pivot.fillna(0).astype(float)
            if pretty: return pivot.replace(0, "")
            return pivot
        
        if target == self.AT_SDPC:
            pivot = df.pivot_table(index="tknb", columns="tknq", values="p", aggfunc=AF.sdpc)
            if pretty: return pivot.replace(0, "")
            return pivot
        
        if target == self.AT_PRICELIST:
            pivot = df.pivot_table(
                index=["tknb", "tknq", "cid"], 
                values=["primary", "pair", "pp", "p"], 
                aggfunc={"primary": AF.first, "pair": AF.first, "pp": "mean", "p": "mean"},
            )
            return pivot
        
        if target == self.AT_PRICELISTAGG: # AT_PLAGG
            aggfs = ["mean", "count", AF.sdpc100, min, max, AF.rangepc100, AF.herfindahl]
            pivot = df.pivot_table(
                index=["tknb", "tknq"], 
                values=["primary", "pair", "pp"], 
                aggfunc={"primary": AF.first, "pp": aggfs},
            )
            return pivot
        
        raise ValueError(f"unknown target {target}")

    def _convert(self, generator, asgenerator, ascc):
        """takes a generator and returns a tuple, generator or CC object"""
        if asgenerator: return generator
        if ascc: return self.__class__(generator)
        return tuple(generator)
    
    def curveix(self, curve):
        """returns index of curve in container"""
        return self.curveix_by_curve.get(curve, None)
    
    def bycid(self, cid):
        """returns curve by cid"""
        return self.curves_by_cid.get(cid, None)
    
    def bycids(self, cids, asgenerator=False, ascc=False):
        """returns curves by cids (as tuple, generator or CC object)"""
        result = (self.curves_by_cid[cid] for cid in cids)
        return self._convert(result, asgenerator, ascc)
    
    def bypair(self, pair, directed=True, asgenerator=False, ascc=False):
        """returns all curves by (usually directed) pair (as tuple, genator or CC object)"""
        result = (c for c in self if c.pair==pair)
        if not directed:
            pairr = "/".join(pair.split("/")[::-1])
            result = itertools.chain(result, (c for c in self if c.pair==pairr))
        return self._convert(result, asgenerator, ascc)
    
    def bp(self, pair, directed=False, asgenerator=False, ascc=False):
        """alias for bypair by with directed=False for interactive use"""
        return self.bypair(pair, directed=directed, asgenerator=asgenerator, ascc=ascc)

    def bypairs(self, pairs=None, directed=True, asgenerator=False, ascc=False):
        """returns all curves by (usually directed) pairs (as tuple, generator or CC object)"""
        if pairs is None:
            return self.curves
        assert directed, "undirected pairs not implemented"
        pairs = set(pairs)
        result = (c for c in self if c.pair in pairs)
        return self._convert(result, asgenerator, ascc)
    
    def bytknx(self, tknx, asgenerator=False, ascc=False):
        """returns all curves by quote token tknx (tknq) (as tuple, generator or CC object)"""
        result = (c for c in self if c.tknx==tknx)
        return self._convert(result, asgenerator, ascc)
    bytknq = bytknx
    
    def bytknxs(self, tknxs=None, asgenerator=False, ascc=False):
        """returns all curves by quote token tknx (tknq) (as tuple, generator or CC object)"""
        if tknxs is None:
            return self.curves
        if isinstance(tknxs, str):
            tknxs = set(t.strip() for t in tknxs.split(","))
        tknxs = set(tknxs)
        result = (c for c in self if c.tknx in tknxs)
        return self._convert(result, asgenerator, ascc)
    bytknxs = bytknxs
    
    def bytkny(self, tkny, asgenerator=False, ascc=False):
        """returns all curves by base token tkny (tknb) (as tuple, generator or CC object)"""
        result = (c for c in self if c.tkny==tkny)
        return self._convert(result, asgenerator, ascc)
    bytknb = bytkny

    def bytknys(self, tknys=None, asgenerator=False, ascc=False):
        """returns all curves by quote token tkny (tknb) (as tuple, generator or CC object)"""
        if tknys is None:
            return self.curves
        if isinstance(tknys, str):
            tknys = set(t.strip() for t in tknys.split(","))
        tknys = set(tknys)
        result = (c for c in self if c.tkny in tknys)
        return self._convert(result, asgenerator, ascc)
    bytknys = bytknys
    
    @staticmethod                      
    def u(minx, maxx):
        """helper: returns uniform random var"""
        return random.uniform(minx, maxx)
    
    @property                      
    def u1(self):
        """helper: returns uniform [0,1] random var"""
        return random.uniform(0, 1)
    
    @dataclass
    class xystatsd():
        mean: any
        minv: any
        maxv: any
        sdev: any
            
    def xystats(self, curves=None):
        """calculates mean, min, max, stdev of x and y"""
        if curves is None:
            curves = self.curves
        tknx = {c.tknq for c in curves}
        tkny = {c.tknb for c in curves}
        assert len(tknx)==1 and len(tkny)==1, "all curves must have same tknq and tknb"
        x = [c.x for c in curves]
        y = [c.y for c in curves]
        return (
            self.xystatsd(np.mean(x), np.min(x), np.max(x), np.std(x)), 
            self.xystatsd(np.mean(y), np.min(y), np.max(y), np.std(y))
        )
    
    @dataclass
    class TokenTableEntry():
        x: list
        y: list

        def __repr__(self):
            return f"TTE(x={self.x}, y={self.y})"
        
        def __len__(self):
            return len(self.x) + len(self.y)
    
    def tokentable(self, curves=None):
        """returns dict associating tokens with the curves on which they appeay"""

        if curves is None:
            curves = self.curves

        r = ((tkn, self.TokenTableEntry(
                        x = [i for i,c in enumerate(curves) if c.tknb == tkn], 
                        y = [i for i,c in enumerate(curves) if c.tknq == tkn],
            ))
            for tkn in self.tkns()
        )
        r = {r[0]: r[1] for r in r if len(r[1])>0} 
        return r
    
    Params = Params
    PLOTPARAMS = Params(
        printline = "pair = {pair}",                                            # print line before plotting; {pair} is replaced
        title = "{pair}",                                                       # plot title; {pair} and {c} are replaced
        xlabel = "{c.tknx}",                                                    # x axis label; ditto
        ylabel = "{c.tkny}",                                                    # y axis label; ditto
        label =  "[{c.cid}-{c.descr}]: p={c.p:.1f}, k={c.k:.1f}",               # label for legend; ditto
        marker = "*",                                                           # marker for plot
        plotf = dict(color="lightgrey", linestyle="dotted"),                    # additional kwargs for plot of the _f_ull curve
        plotr = dict(color="grey"),                                             # ditto for the _r_ange
        plotm = dict(),                                                         # dittto for the _m_arker
        grid = True,                                                            # plot grid if True
        legend = True,                                                          # plot legend if True
        show = True,                                                            # finish with plt.show() if True
    )

    def plot(self, pairs=None, curves=None, params=None):
        """
        plots the curves in curvelist or all curves if None

        :pairs:      list of pairs to plot
        :curves:     list of curves to plot
        :params:     plot parameters, as params struct (see PLOTPARAMS)
        """
        p = Params.construct(params, defaults=self.PLOTPARAMS.params)
        
        if isinstance(pairs, str):
            pairs = [pairs]

        if pairs is None:
            pairs = self.pairs()

        assert curves is None, "restricting curves not implemented yet"

        for pair in pairs:
            if p.printline:
                print(p.printline.format(pair=pair))
            curves = self.bypair(pair)
            statx, staty = self.xystats(curves)
            xr = np.linspace(0.0000001, statx.maxv*1.2,500)
            for i, c in enumerate(curves):
                # plotf is the full curve
                plt.plot(xr, [c.yfromx_f(x_, ignorebounds=True) for x_ in xr], **p.plotf)
                # plotr is the curve with bounds
                plt.plot(xr, [c.yfromx_f(x_) for x_ in xr], **p.plotr)

            plt.gca().set_prop_cycle(None)
            for c in curves:
                # plotm are the markers
                label = None if not p.label else p.label.format(pair=pair, c=c)
                plt.plot(c.x, c.y, marker=p.marker, label=label, **p.plotm) 

            plt.title(p.title.format(pair=pair, c=c))
            plt.ylim((0, staty.maxv*2))
            plt.xlabel(p.xlabel.format(pair=pair, c=c))
            plt.ylabel(p.ylabel.format(pair=pair, c=c))
            
            if p.legend:
                if isinstance(p.legend, dict):
                    plt.legend(**p.legend)
                else:
                    plt.legend()
            
            if p.grid:
                if isinstance(p.grid, dict):
                    plt.grid(**p.grid)
                else:
                    plt.grid(b=True)
            
            if p.show:
                if isinstance(p.show, dict):
                    plt.show(**p.show)
                else:
                    plt.show()

class AF():
    """aggregator functions (for pivot tables)"""

    @staticmethod
    def range(x):
        return np.max(x) - np.min(x)
    
    @staticmethod
    def rangepc(x):
        mx = np.max(x)
        if mx == 0:
            return 0
        return (mx - np.min(x))/mx
    
    @classmethod
    def rangepc100(cls, x):
        return cls.rangepc(x) * 100
    
    @staticmethod
    def sdpc(x):
        return np.std(x) / np.mean(x)
    
    @classmethod
    def sdpc100(cls, x):
        return cls.sdpc(x) * 100
    
    @staticmethod
    def first(x):
        return x.iloc[0]
    
    @staticmethod
    def herfindahl(x):
        return np.sum(x**2)/np.sum(x)**2
    
    @classmethod
    def herfindahlN(cls, x):
        return 1/cls.herfindahl(x)