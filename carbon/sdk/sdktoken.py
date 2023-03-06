"""
class representing an ERC20 token, in particular holding the token name and address
"""
__VERSION__ = "1.0"
__DATE__ = "8/Mar/2023"

from dataclasses import dataclass

@dataclass
class SDKToken():
    """
    describes a token for the Carbon SDK

    :token:     token ticker (eg "ETH")
    :address:   token address ("0x...")
    :decimals:  number of decimals (default None is 18)
    :name:      token name (default None is token)
    """    
    __VERSION__ = __VERSION__
    __DATE__ = __DATE__

    token: str
    address: str
    decimals: int = None
    name: str = None
    
    def __post_init__(self):
        if not self.decimals is None:
            self.decimals = int(self.decimals)
        self.token = self.token.strip().upper()
        self.address = str(self.address).strip().lower()
        try:
            int(self.address, 16)
        except ValueError:
            raise ValueError(f"address {self.address} is not a hex number")
        if self.name is None: self.name = self.token

    @property
    def a(self):
        """alias for self.address"""
        return self.address
    
    @property
    def T(self):
        """alias for self.token"""
        return self.token 
    
    @property
    def d(self):
        """alias for self.decimals"""
        return self.decimals

    def w2t(self, wei):
        """converts wei to token"""
        return wei / 10**self.decimals
    
    def t2w(self, tokenmt):
        """converts tokenmt to wei"""
        return int(tokenmt * 10**self.decimals)
    
    @property
    def isnul(self):
        """returns True if token is NULTKN"""
        return self.token == "NULTKN"
    
    def __str__(self):
        return f"{self.token} ({self.address})"
    
    def __iter__(self):
        return iter((self.token, self.address, self.decimals, self.name))

NULTKN = SDKToken("NULTKN", "0x0000000000000000000000000000000000000000") 

class TokenContainer():
    """
    container class for SDKToken objects

    :tokens:        list of SDKToken objects
    :raiseonerror:  if True, raises KeyError if token not found; otherwise returns NULTKN
    """
    VERSION = __VERSION__
    DATE = __DATE__

    def __init__(self, tokens, raiseonerror=None):
        if raiseonerror is None: raiseonerror = True
        self.raiseonerror = raiseonerror
        self._byticker = {t.token: t for t in tokens}
        self._byaddr   = {t.address: t for t in tokens}
        self._tickers  = set(self._byticker.keys())
        if not len(self._tickers) == len(self._byaddr):
            raise ValueError(f"{len(self._tickers) - len(self._byaddr)} duplicate token tickers found", self._tickers, self._byaddr)

    @classmethod
    def fromlist(cls, tokens, raiseonerror=None):
        """creates a TokenContainer from a list of token parameters"""
        return cls([SDKToken(*tuple(t)) for t in tokens], raiseonerror)
    
    @classmethod
    def fromcsv(cls, csv, raiseonerror=None):
        """creates a TokenContainer from a csv string"""
        return cls.fromlist([t.split(",") for t in csv.strip().splitlines()], raiseonerror)
    
    @classmethod
    def restore(cls, ticker_or_addr_or_tkn, raiseonerror=None):
        """converts a ticker or address to an SDKToken from the TokenContainer (SDKToken not touched)"""
        if isinstance(ticker_or_addr_or_tkn, SDKToken):
            return ticker_or_addr_or_tkn
        try:
            tkn = cls.byaddr(ticker_or_addr_or_tkn, raiseonerror=True)
        except:
            try:
                tkn = cls.byticker(ticker_or_addr_or_tkn, raiseonerror=True)
            except:
                if raiseonerror:
                    raise ValueError(f"ticker or address {ticker_or_addr_or_tkn} not found in container")
                else:
                    tkn = None
        return tkn
    
    def byticker(self, token, raiseonerror=None, returnnultkn=True):
        """gets a token from the container (by ticker)"""
        if raiseonerror is None: raiseonerror = self.raiseonerror
        token = token.upper()
        try:
            return self._byticker[token]
        except KeyError:
            if raiseonerror:
                raise KeyError(f"token {token} not found in container")
            else:
                if returnnultkn:
                    return NULTKN
                else:
                    return None
    
    def byaddr(self, addr, raiseonerror=None, returnnultkn=True):
        """
        gets a token from the container (by address)
        
        :addr:          token address as hex string
        :raiseonerror:  if True, raises KeyError if token not found; otherwise returns nul value
        :returnnultkn:  if True, returns NULTKN if token not found; otherwise returns None
        """
        if raiseonerror is None: raiseonerror = self.raiseonerror
        addr = addr.lower()
        try:
            return self._byaddr[addr]
        except KeyError:
            if raiseonerror:
                raise KeyError(f"address {addr} not found in container") 
            else:
                if returnnultkn:
                    return NULTKN
                else:
                    return None
            
    def byaddr1(self, addr, tknonly=False):
        """
        gets a token from the container (by address); keeps addr if not found
        
        :addr:      token address as hex string
        :tknonly:   if True, returns only the token name; otherwise returns object
        :returns:   token name or object, depending on tknonly
        """
        addr = addr.lower()
        try:
            tkno = self._byaddr[addr]
            return tkno.T if tknonly else tkno
        except KeyError:
            return addr
    
    def containsall(self, tokenListorSet):
        """checks if all tokens in the list are in the container"""
        return tokenListorSet.issubset(self._tickers)

    @property
    def _all(self):
        """gets the full list of tokens from the container"""
        return tuple(self._byticker.values())
    
    def __getitem__(self, token):
        return self.byticker(token)
    
    def __getattr__(self, token):
        return self.byticker(token)
    
    def __len__(self):
        return len(self._byticker)
    
    def __iter__(self):
        return iter(self._all)
    
    def __repr__(self):
        return f"{self.__class__.__name__}({self._all})"
    
    def __hash__(self):
        return int(self.address, 16)
    
    def __str__(self):
        return str(tuple(self._byticker.keys()))
    
    def __call__(self, addr):
        """alias for self.byaddr1()"""
        return self.byaddr1(addr=addr)

# note: use the script below to generate the csv string

# first run this in Node.js to get the token addresses
# import { ethers } from 'ethers';
# const rpcUrl = process.env.ALCHEMY_RPCURL;
# const provider = new ethers.providers.JsonRpcProvider(rpcUrl);
# const abi = ['function decimals() view returns (uint8)']; // replace with the ABI of the ERC20 contract
# const tokens = ['0x7fc66500c84a76ad7e9c93437bfc5ac33e2ddae9',...]; // replace with the addresses of the ERC20 contracts
# var   tokenDecimals = {}
# for (var i = 0; i < tokens.length; i++) {
#     let taddr = tokens[i]
#     let tcontract = new ethers.Contract(taddr, abi, provider);
#     let tdecimals
#     try{
#         tdecimals = await tcontract.decimals()
#     } catch (e) {
#         tdecimals = "error"
#     }
#     console.log(taddr, tdecimals)
#     tokenDecimals[taddr] = tdecimals
# }
# console.log(tokenDecimals)
#
# then run this in Python to generate the csv string
# decs = <output from console.log(tokenDecimals)>
# for t in Tokens:
#    print(f"{t.token}, {t.a}, {decs[t.a]}")
# ETH of course need to be adjusted manually to 18 decs

Tokens = TokenContainer.fromcsv("""
AAVE, 0x7fc66500c84a76ad7e9c93437bfc5ac33e2ddae9, 18
ALEPH, 0x27702a26126e0b3702af63ee09ac4d1a084ef628, 18
ANT, 0x960b236a07cf122663c4303350609a66a7b288c0, 18
BAL, 0xba100000625a3754423978a60c9317c58a424e3d, 18
BAND, 0xba11d00c5f74255f56a5e366f4f77f5a186d7f55, 18
BAT, 0x0d8775f648430679a709e98d2b0cb6250d2887ef, 18
BNB, 0xb8c77482e45f1f44de1745f52c74426c631bdd52, 18
BNT, 0x1f573d6fb3f13d689ff844b4ce37794d79a7ff1c, 18
BUSD, 0x4fabb145d64652a948d72533023f6e7a623c7c53, 18
BZRX, 0x56d811088235f11c8920698a204a5010a788f4b3, 18
CEL, 0xaaaebe6fe48e54f431b0c390cfaf0b017d09d42d, 4
CHERRY, 0x4ecb692b0fedecd7b486b4c99044392784877e8c, 4
COMP, 0xc00e94cb662c3520282e6f5717214004a7f26888, 18
CRO, 0xa0b73e1ff0b80914ab6fe0444e65848c4c34450b, 8
CRV, 0xd533a949740bb3306d119cc777fa900ba034cd52, 18
DAI, 0x6b175474e89094c44da98b954eedeac495271d0f, 18
DXD, 0xa1d65e8fb6e87b60feccbc582f7f97804b725521, 18
ELF, 0xbf2179859fc6d5bee9bf9158632dc51678a4100e, 18
ENJ, 0xf629cbd94d3791c9250152bd8dfbdf380e2a3b9c, 18
ETH, 0xeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeee, 18
EWTB, 0x178c820f862b14f316509ec36b13123da19a6054, 18
FTT, 0x50d1c9771902476076ecfc8b2a83ad6b9355a4c9, 18
GNO, 0x6810e776880c02933d47db1b9fc05908e5386b96, 18
GUSD, 0x056fd409e1d7a124bd7017459dfea2f387b6d5cd, 2
JRT, 0x8a9c67fee641579deba04928c4bc45f66e26343a, 18
KNC, 0xdd974d5c2e2928dea5f71b9825b8b646686bd200, 18
LEND, 0x80fb784b7ed66730e8b1dbd9820afd29931aab03, 18
LINK, 0x514910771af9ca656af840dff83e8264ecf986ca, 18
LRC, 0xbbbbca6a901c926f240b89eacb641d8aec7aeafd, 18
MANA, 0x0f5d2fb29fb7d3cfee444a200298f468908cc942, 18
MATIC, 0x7d1afa7b718fb893db30a3abc0cfc608aacfebb0, 18
MKR, 0x9f8f72aa9304c8b593d555f12ef6589cc3a579a2, 18
MLN, 0xec67005c4e498ec7f55e092bd1d35cbc47c91892, 18
MTA, 0xa3bed4e1c75d00fa6f4e5e6922db7261b5e9acd2, 18
NMR, 0x1776e1f26f98b1a5df9cd347953a26dd3cb46671, 18
OCEAN, 0x967da4048cd07ab37855c090aaf366e4ce1b9f48, 18
OMG, 0xd26114cd6ee289accf82350c8d8487fedb8a0c07, 18
PBTC, 0x5228a22e72ccc52d415ecfd199f99d0665e7733b, 18
RARI, 0xfca59cd816ab1ead66534d82bc21e7515ce441cf, 18
REN, 0x408e41876cccdc0f92210600ef50372656052a38, 18
RENBTC, 0xeb4c2781e4eba804ce9a9803c67d0893436bb27d, 8
RENZEC, 0x1c5db575e2ff833e46a2e9864c22f4b22e0b37c2, 8
RPL, 0xb4efd85c19999d84251304bda99e90b92300bd93, 18
RSR, 0x8762db106b2c2a0bccb3a80d1ed41273552616e8, 18
SNX, 0xc011a73ee8576fb46f5e1c5751ca3b9fe0af2a6f, 18
SRM, 0x476c5e26a75bd202a9683ffd34359c0cc15be0ff, 6
STAKE, 0x0ae055097c6d159879521c384f1d2123d1f195e6, 18
SBTC, 0xfe18be6b3bd88a2d2a7f928d00292e7a9963cfc6, 18
SUSD, 0x57ab1ec28d129707052df4df418d58a2d46d5f51, 18
SUSHI, 0x6b3595068778dd592e39a122f4f5a5cf09c90fe2, 18
SWRV, 0xb8baa0e4287890a5f79863ab62b7f175cecbd433, 18
SXP, 0x8ce9137d39326ad0cd6491fb5cc0cba0e089b6a9, 18
TOMOE, 0x05d3606d5c81eb9b7b18530995ec9b29da05faba, 18
UNI, 0x1f9840a85d5af5bf1d1762f925bdaddc4201f984, 18
USDC, 0xa0b86991c6218b36c1d19d4a2e9eb0ce3606eb48, 6
USDT, 0xdac17f958d2ee523a2206206994597c13d831ec7, 6
WBTC, 0x2260fac5e5542a773aa44fbcfedf7c193bc2c599, 8
WNXM, 0x0d438f3b5175bebc262bf23753c1e53d03432bde, 18
XDCE, 0x41ab1b6fcbb2fa9dced81acbdec13ea6315f2bf2, 18
YFI, 0x0bc529c00c6401aef6d220be8c6ea1667f6ad93e, 18
UMA, 0x04fa0d235c4abf4bcf4787af4cf447de572ef828, 18
QNT, 0x4a220e6096b25eadb88358cb44068a3248254675, 18
ZRX, 0xe41d2489571d322189246dafa5ebde1f4699f498, 18
CORE, 0x62359ed7505efc61ff1d56fef82158ccaffa23d7, 18
CREAM, 0x2ba592f78db6436527729929aaf6c908497cb200, 18
PICKLE, 0x429881672b9ae42b8eba0e26cd9c73711b891ca5, 18
RCN, 0xf970b8e36e23f7fc3fd752eea86f8be8d83375a6, 18
""")