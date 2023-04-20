# ------------------------------------------------------------
# Auto generated test file `test_066_Uniswap.py`
# ------------------------------------------------------------
# source file   = NBTest_066_Uniswap.py
# source path   = /Users/skl/REPOES/Bancor/CarbonSimulator/resources/NBTest/
# target path   = /Users/skl/REPOES/Bancor/CarbonSimulator/resources/NBTest/
# test id       = 066
# test comment  = Uniswap
# ------------------------------------------------------------



from carbon.helpers.stdimports import *
from carbon.tools.cpc import ConstantProductCurve as CPC, CPCContainer, T, CPCInverter
from carbon.tools.univ3calc import Univ3Calculator as U3
from dataclasses import dataclass, asdict
plt.style.use('seaborn-dark')
plt.rcParams['figure.figsize'] = [12,6]
print("{0.__name__} v{0.__VERSION__} ({0.__DATE__})".format(CPC))
print("{0.__name__} v{0.__VERSION__} ({0.__DATE__})".format(U3))
print_version(require="2.4.2")




# ------------------------------------------------------------
# Test      066
# File      test_066_Uniswap.py
# Segment   u3 standalone
# ------------------------------------------------------------
def test_u3_standalone():
# ------------------------------------------------------------
    
    data = {
        "token0": "0xA0b86991c6218b36c1d19D4a2e9Eb0cE3606eB48", # USDC
        "token1": "0xC02aaA39b223FE8D0A0e5C4F27eAD9083C756Cc2", # WETH 
        "sqrt_price_q96": "1725337071198080486317035748446190", 
        "tick": "199782", 
        "liquidity": "36361853546581410773"
    }
    
    u1 = U3(
        tkn0="USDC", 
        tkn0decv=6, 
        tkn1="WETH", 
        tkn1decv=18,
        sp96=data["sqrt_price_q96"],
        tick=data["tick"],
        liquidity=data["liquidity"],
        fee_const = U3.FEE500,
    )
    u2 = U3.from_dict(data, U3.FEE500)
    assert u1 == u2
    u = u2
    assert asdict(u) == {
        'tkn0': 'USDC',
        'tkn1': 'WETH',
        'sp96': int(data["sqrt_price_q96"]),
        'tick': int(data["tick"]),
        'liquidity': int(data["liquidity"]),
        'fee_const': U3.FEE500
    }
    assert u.tkn0 == "USDC"
    assert u.tkn1 == "WETH"
    assert u.tkn0dec == 6
    assert u.tkn1dec == 18
    assert u.decf == 1e-12
    assert u.dec_factor_wei0_per_wei1 == u.decf
    assert iseq(u.p, 0.00047422968986928404)
    assert iseq(1/u.p, 2108.6828205033694)
    assert u.p == u.price_tkn1_per_tkn0
    assert 1/u.p == u.price_tkn0_per_tkn1
    assert u.price_convention == 'USDC/WETH [WETH per USDC]'
    assert iseq(u._price_f(1725337071198080486317035748446190), 474229689.86928403)
    assert iseq(u._price_f(u.sp96), 474229689.86928403)
    assert u.ticksize == 10
    ta, tb =  u.tickab
    par, pbr = u.papb_raw
    pa, pb = u.papb_tkn1_per_tkn0
    pai, pbi = u.papb_tkn0_per_tkn1
    assert ta <= u.tick
    assert tb >= u.tick
    assert ta % u.ticksize == 0
    assert tb % u.ticksize == 0
    assert tb-ta == u.ticksize
    assert iseq(par, 474134297.0246954)
    assert iseq(pbr, 474608644.73905975)
    assert iseq(pbr/par, 1.0001**u.ticksize)
    assert iseq(pa, 0.0004741342970246954)
    assert iseq(pb, 0.00047460864473905973)
    assert iseq(pbr/par, pb/pa)
    assert iseq(pbr/par, pai/pbi)
    assert pa<pb
    assert pai>pbi
    assert pa == par * u.decf
    assert pb == pbr * u.decf
    assert iseq(pai, 2109.1070742514007)
    assert iseq(pbi, 2106.999126722188)
    assert pai == 1/pa
    assert pbi == 1/pb
    assert u.p >= pa
    assert u.p <= pb
    assert u.fee_const == 500
    assert u.fee == 0.0005
    assert u.info()
    print(u.info())
    
    assert u.liquidity == int(data["liquidity"])
    assert u.L == 36361853.54658141
    assert u.liquidity/u.L == 1e18/1e6
    assert u.L2 == u.L**2
    assert u.Lsquared == u.L**2
    assert u.k == u.L2
    assert u.kbar == u.L
    u.tkn0reserve(incltoken=True), u.tkn1reserve(incltoken=True), u.tvl(incltoken=True)
    

# ------------------------------------------------------------
# Test      066
# File      test_066_Uniswap.py
# Segment   with cpc
# ------------------------------------------------------------
def test_with_cpc():
# ------------------------------------------------------------
    
    data = {
        "token0": "0xA0b86991c6218b36c1d19D4a2e9Eb0cE3606eB48", 
        "token1": "0xC02aaA39b223FE8D0A0e5C4F27eAD9083C756Cc2", 
        "sqrt_price_q96": "1727031172247131125466697684053376", 
        "tick": "199801", 
        "liquidity": "37398889145617323159"
    }
    u = U3.from_dict(data, U3.FEE500)
    
    pa, pb = u.papb_tkn1_per_tkn0
    curve = CPC.from_univ3(
        Pmarg = u.p,
        uniL = u.L,
        uniPa = pa,
        uniPb = pb,
        pair = u.pair,
        fee = u.fee,
        descr = "",
        params = dict(uv3raw=asdict(u)),
        cid = "0",
    )
    curve
    
    c = curve
    print(f"Reserve: {c.x_act:,.3f} {c.tknx}, {c.y_act:,.3f} {c.tkny}")
    print(f"TVL = {c.tvl(tkn=c.tknx):,.3f} {c.tknx} = {c.tvl(tkn=c.tkny):,.3f} {c.tkny}")
    assert iseq(c.x_act, 716877.5715601444)
    assert iseq(c.y_act, 66.88731140131131)
    assert iseq(c.tvl(tkn=c.tknx), 857645.1222000704)
    assert iseq(c.tvl(tkn=c.tkny), 407.51988721569177)
    
    print(f"Reserve: {u.tkn0reserve():,.3f} {c.tknx}, {u.tkn1reserve():,.3f} {c.tkny}")
    print(f"TVL = {u.tvl(astkn0=True):,.3f} {c.tknx} = {u.tvl(astkn0=False):,.3f} {c.tkny}")
    assert iseq(u.tkn0reserve(), c.x_act)
    assert iseq(u.tkn1reserve(), c.y_act)
    assert iseq(u.tvl(astkn0=False), c.tvl(tkn=c.tkny))
    assert iseq(u.tvl(astkn0=True), c.tvl(tkn=c.tknx))
    assert u.tkn0reserve(incltoken=True)[1] == u.tkn0
    assert u.tkn1reserve(incltoken=True)[1] == u.tkn1
    assert u.tvl(astkn0=True, incltoken=True)[1] == u.tkn0
    assert u.tvl(astkn0=False, incltoken=True)[1] == u.tkn1
    u.tkn0reserve(incltoken=True), u.tkn1reserve(incltoken=True), u.tvl(incltoken=True)
    
    curve = CPC.from_univ3(
        **u.cpc_params(),
        descr = "",
        params = dict(uv3raw=asdict(u)),
        cid = "0",
    )
    curve
    
    c = curve
    print(f"Reserve: {c.x_act:,.3f} {c.tknx}, {c.y_act:,.3f} {c.tkny}")
    print(f"TVL = {c.tvl(tkn=c.tknx):,.3f} {c.tknx} = {c.tvl(tkn=c.tkny):,.3f} {c.tkny}")
    
    curve = CPC.from_univ3(
        **u.cpc_params(
            cid = "0",
            descr = "",
            #params = dict(uv3raw=asdict(u)),
        ),
    )
    curve
    
    
    c = curve
    print(f"Reserve: {c.x_act:,.3f} {c.tknx}, {c.y_act:,.3f} {c.tkny}")
    print(f"TVL = {c.tvl(tkn=c.tknx):,.3f} {c.tknx} = {c.tvl(tkn=c.tkny):,.3f} {c.tkny}")
    
    