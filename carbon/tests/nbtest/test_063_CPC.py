# ------------------------------------------------------------
# Auto generated test file `test_063_CPC.py`
# ------------------------------------------------------------
# source file   = NBTest_063_CPC.py
# source path   = /Users/skl/REPOES/Bancor/CarbonSimulator/resources/NBTest/
# target path   = /Users/skl/REPOES/Bancor/CarbonSimulator/resources/NBTest/
# test id       = 063
# test comment  = CPC
# ------------------------------------------------------------



from carbon.helpers.stdimports import *
from carbon import CarbonOrderUI
from carbon.tools.cpc import ConstantProductCurve as CPC, CPCContainer, T, CPCInverter
from carbon.tools.optimizer import CPCArbOptimizer, F
import carbon.tools.tokenscale as ts
plt.style.use('seaborn-dark')
plt.rcParams['figure.figsize'] = [12,6]
print("{0.__name__} v{0.__VERSION__} ({0.__DATE__})".format(CPC))
print("{0.__name__} v{0.__VERSION__} ({0.__DATE__})".format(CarbonOrderUI))
print("{0.__name__} v{0.__VERSION__} ({0.__DATE__})".format(ts.TokenScaleBase))
print("{0.__name__} v{0.__VERSION__} ({0.__DATE__})".format(CPCArbOptimizer))
print_version(require="2.4.2")



try:
    df = pd.read_csv("NBTEST_063_Curves.csv.gz")
except:
    df = pd.read_csv("carbon/tests/nbtest_data/NBTEST_063_Curves.csv.gz")
CCmarket = CPCContainer.from_df(df)


# ------------------------------------------------------------
# Test      063
# File      test_063_CPC.py
# Segment   P
# ------------------------------------------------------------
def test_p():
# ------------------------------------------------------------
    
    c = CPC.from_pk(pair="USDC/WETH", p=1, k=100, params=dict(exchange="univ3", a=dict(b=1, c=2)))
    assert c.P("exchange") == "univ3"
    assert c.P("a") == {'b': 1, 'c': 2}
    assert c.P("a:b") == 1
    assert c.P("a:c") == 2
    assert c.P("a:d") is None
    assert c.P("b") is None
    assert c.P("b", "meh") == "meh"
    

# ------------------------------------------------------------
# Test      063
# File      test_063_CPC.py
# Segment   TVL
# ------------------------------------------------------------
def test_tvl():
# ------------------------------------------------------------
    
    c = CPC.from_pk(pair="WETH/USDC", p=2000, k=1*2000)
    assert c.tvl(incltkn=True) == (4000.0, 'USDC', 1)
    assert c.tvl("USDC", incltkn=True) == (4000.0, 'USDC', 1)
    assert c.tvl("WETH", incltkn=True) == (2.0, 'WETH', 1)
    assert c.tvl("USDC", incltkn=True, mult=2) == (8000.0, 'USDC', 2)
    assert c.tvl("WETH", incltkn=True, mult=2) == (4.0, 'WETH', 2)
    assert c.tvl("WETH", incltkn=False) == 2.0
    assert c.tvl("WETH") == 2.0
    assert c.tvl() == 4000
    assert c.tvl("WETH", mult=2000) == 4000
    

# ------------------------------------------------------------
# Test      063
# File      test_063_CPC.py
# Segment   estimate prices
# ------------------------------------------------------------
def test_estimate_prices():
# ------------------------------------------------------------
    
    CC = CPCContainer()
    CC += [CPC.from_univ3(pair="WETH/USDC", cid="uv3", fee=0, descr="",
                         uniPa=2000, uniPb=2010, Pmarg=2005, uniL=10*sqrt(2000))]
    CC += [CPC.from_pk(pair="WETH/USDC", cid="uv2", fee=0, descr="",
                         p=1950, k=5**2*2000)]
    CC += [CPC.from_pk(pair="USDC/WETH", cid="uv2r", fee=0, descr="",
                         p=1/1975, k=5**2*2000)]
    CC += [CPC.from_carbon(pair="WETH/USDC", cid="carb", fee=0, descr="",
                         tkny="USDC", yint=1000, y=1000, pa=1850, pb=1750)]
    CC += [CPC.from_carbon(pair="WETH/USDC", cid="carb", fee=0, descr="",
                         tkny="WETH", yint=1, y=0, pb=1/1850, pa=1/1750)]
    CC += [CPC.from_carbon(pair="WETH/USDC", cid="carb", fee=0, descr="",
                         tkny="USDC", yint=1000, y=500, pa=1870, pb=1710)]
    #CC.plot()
    
    assert CC.price_estimate(tknq=T.WETH, tknb=T.USDC, result=CC.PE_PAIR) == f"{T.USDC}/{T.WETH}"
    assert CC.price_estimate(pair=f"{T.USDC}/{T.WETH}", result=CC.PE_PAIR) == f"{T.USDC}/{T.WETH}"
    assert raises(CC.price_estimate, tknq="a", result=CC.PE_PAIR)
    assert raises(CC.price_estimate, tknb="a", result=CC.PE_PAIR)
    assert raises(CC.price_estimate, tknq="a", tknb="b", pair="a/b", result=CC.PE_PAIR)
    assert raises(CC.price_estimate, pair="ab", result=CC.PE_PAIR)
    assert CC.price_estimates(tknqs=[T.WETH], tknbs=[T.USDC], pairs=True, 
                              unwrapsingle=False)[0][0] == f"{T.USDC}/{T.WETH}"
    assert CC.price_estimates(tknqs=[T.WETH], tknbs=[T.USDC], pairs=True, 
                              unwrapsingle=True)[0] == f"{T.USDC}/{T.WETH}"
    assert CC.price_estimates(tknqs=[T.WETH], tknbs=[T.USDC], pairs=True)[0] == f"{T.USDC}/{T.WETH}"
    r = CC.price_estimates(tknqs=list("ABC"), tknbs=list("DEFG"), pairs=True)
    assert r.ndim == 2
    assert r.shape == (3,4)
    r = CC.price_estimates(tknqs=list("A"), tknbs=list("DEFG"), pairs=True)
    assert r.ndim == 1
    assert r.shape == (4,)
    
    assert CC[0].at_boundary == False
    assert CC[1].at_boundary == False
    assert CC[2].at_boundary == False
    assert CC[3].at_boundary == True
    assert CC[3].at_xmin == True
    assert CC[3].at_ymin == False
    assert CC[3].at_xmax == False
    assert CC[3].at_ymax == True
    assert CC[4].at_boundary == True
    assert CC[4].at_ymin == True
    assert CC[4].at_xmin == True
    assert CC[4].at_ymax == True
    assert CC[4].at_xmax == True
    assert CC[5].at_boundary == True
    
    r = CC.price_estimate(tknq="USDC", tknb="WETH", result=CC.PE_CURVES)
    assert len(r)==3
    
    p,w = CC.price_estimate(tknq="USDC", tknb="WETH", result=CC.PE_DATA)
    assert len(p) == len(r)
    assert len(w) == len(r)
    assert iseq(sum(p), 5930)
    assert iseq(sum(w), 894.4271909999159)
    pe = CC.price_estimate(tknq="USDC", tknb="WETH")
    assert pe == np.average(p, weights=w)
    
    O = CPCArbOptimizer(CC)
    Om = CPCArbOptimizer(CCmarket)
    assert O.price_estimates(tknq="USDC", tknbs=["WETH"]) == CC.price_estimates(tknqs=["USDC"], tknbs=["WETH"])
    CCmarket.fp(onein="USDC")
    r = Om.price_estimates(tknq="USDC", tknbs=["WETH", "WBTC"])
    assert iseq(r[0],  1820.89875275)
    assert iseq(r[1],  28351.08150121)
    

# ------------------------------------------------------------
# Test      063
# File      test_063_CPC.py
# Segment   price estimates in optimizer
# ------------------------------------------------------------
def test_price_estimates_in_optimizer():
# ------------------------------------------------------------
    
    prices = {"USDC":1, "LINK": 5, "AAVE": 100, "MKR": 500, "WETH": 2000, "WBTC": 20000}
    CCfm, ctr = CPCContainer(), 0
    for tknb, pb in prices.items():
        for tknq, pq in prices.items():
            if pb>pq:
                pair = f"{tknb}/{tknq}"
                pp = pb/pq
                k = (100000)**2/(pb*pq)
                CCfm  += CPC.from_pk(p=pp, k=k, pair=pair, cid = f"mkt-{ctr}")
                ctr += 1
    
    O = CPCArbOptimizer(CCfm)
    assert O.MO_PSTART == O.MO_P
    tknq = "WETH"
    df = O.margp_optimizer(tknq, result=O.MO_PSTART)
    rd = df[tknq].to_dict()
    assert len(df) == len(prices)-1
    assert df.columns[0] == tknq
    assert df.index.name == "tknb"
    assert rd == {k:v/prices[tknq] for k,v in prices.items() if k!=tknq}
    df2 = O.margp_optimizer(tknq, result=O.MO_PSTART, params=dict(pstart=df))
    assert np.all(df == df2)
    df2 = O.margp_optimizer(tknq, result=O.MO_PSTART, params=dict(pstart=rd))
    assert np.all(df == df2)
    df
    

# ------------------------------------------------------------
# Test      063
# File      test_063_CPC.py
# Segment   Assertions and testing
# ------------------------------------------------------------
def test_assertions_and_testing():
# ------------------------------------------------------------
    
    c = CPC.from_px(p=2000,x=10, pair="ETH/USDC")
    assert c.pair == "ETH/USDC"
    assert c.tknb == c.pair.split("/")[0]
    assert c.tknx == c.tknb
    assert c.tknq == c.pair.split("/")[1]
    assert c.tkny == c.tknq
    assert f"{c.tknb}/{c.tknq}" == c.pair
    print (c.descr)
    
    c = CPC.from_xy(10,20)
    assert c == CPC.from_kx(c.k, c.x)
    assert c == CPC.from_ky(c.k, c.y)
    assert c == CPC.from_xy(c.x, c.y)
    assert c == CPC.from_pk(c.p, c.k)
    assert c == CPC.from_px(c.p, c.x)
    assert c == CPC.from_py(c.p, c.y)
    
    c
    
    c = CPC.from_px(p=2, x=100, x_act=10, y_act=20)
    assert c.y_max*c.x_min == c.k
    assert c.x_max*c.y_min == c.k
    assert c.p_min == c.y_min / c.x_max
    assert c.p_max == c.y_max / c.x_min
    assert c.p_max >= c.p_min
    
    c = CPC.from_px(p=2, x=100, x_act=10, y_act=20)
    e = 1e-5
    assert 95*c.yfromx_f(x=95) == c.k
    assert 105*c.yfromx_f(x=105) == c.k
    assert 190*c.xfromy_f(y=190) == c.k
    assert 210*c.xfromy_f(y=210) == c.k
    assert not c.yfromx_f(x=90) is None
    assert c.yfromx_f(x=90-e) is None
    assert not c.xfromy_f(y=180) is None
    assert c.xfromy_f(y=180-e) is None
    assert c.dyfromdx_f(dx=-5)
    assert (c.y+c.dyfromdx_f(dx=-5))*(c.x-5) == c.k
    assert (c.y+c.dyfromdx_f(dx=+5))*(c.x+5) == c.k
    assert (c.x+c.dxfromdy_f(dy=-5))*(c.y-5) == c.k
    assert (c.x+c.dxfromdy_f(dy=+5))*(c.y+5) == c.k
    
    c = CPC.from_pkpp(p=100, k=100)
    assert c.p_min == 100
    assert c.p_max == 100
    assert c.p == 100
    assert c.k == 100
    
    c = CPC.from_pkpp(p=100, k=100, p_min=80, p_max=120)
    assert c.p_min == 80
    assert iseq(c.p_max, 120)
    assert c.p == 100
    assert c.k == 100
    

# ------------------------------------------------------------
# Test      063
# File      test_063_CPC.py
# Segment   iseq
# ------------------------------------------------------------
def test_iseq():
# ------------------------------------------------------------
    
    assert iseq("a", "a", "ab") == False
    assert iseq("a", "a", "a")
    assert iseq(1.0, 1, 1.0)
    assert iseq(0,0)
    assert iseq(0,1e-10)
    assert iseq(0,1e-5) == False
    assert iseq(1, 1.00001) == False
    assert iseq(1, 1.000001)
    assert iseq(1, 1.000001, eps=1e-7) == False
    assert iseq("1", 1) == False
    

# ------------------------------------------------------------
# Test      063
# File      test_063_CPC.py
# Segment   CarbonOrderUI integration
# ------------------------------------------------------------
def test_carbonorderui_integration():
# ------------------------------------------------------------
    
    o = CarbonOrderUI.from_prices("ETH/USDC", "ETH", 2500, 3000, 10, 10)
    c = o.as_cpc
    assert o.pair.slashpair == "ETH/USDC"
    assert o.tkn == "ETH"
    assert o.p_start == 2500
    assert o.p_end == 3000
    assert o.p_marg == 2500
    assert o.y == 10
    assert o.yint == 10
    assert c.pair == o.pair.slashpair
    assert c.tknb == o.pair.tknb
    assert c.tknq == o.pair.tknq
    assert c.x_act == o.y
    assert c.y_act == 0
    assert iseq(o.p_start, c.p, c.p_min)
    assert iseq(o.p_end, c.p_max)
    
    o = CarbonOrderUI.from_prices("ETH/USDC", "USDC", 1500, 1000, 1000, 1000)
    c = o.as_cpc
    assert o.pair.slashpair == "ETH/USDC"
    assert o.tkn == "USDC"
    assert o.p_start == 1500
    assert o.p_end == 1000
    assert o.p_marg == 1500
    assert o.y == 1000
    assert o.yint == 1000
    assert c.pair == o.pair.slashpair
    assert c.tknb == o.pair.tknb
    assert c.tknq == o.pair.tknq
    assert c.x_act == 0
    assert c.y_act == o.y
    assert iseq(o.p_start, c.p, c.p_max)
    assert iseq(o.p_end, c.p_min)
    
    o = CarbonOrderUI.from_prices("ETH/USDC", "ETH", 2500, 3000, 10, 7)
    c = o.as_cpc
    assert o.y == 7
    assert iseq(c.x_act, o.y)
    assert iseq(c.y_act, 0)
    assert iseq(o.p_marg, c.p, c.p_min)
    assert iseq(o.p_end, c.p_max)
    
    o = CarbonOrderUI.from_prices("ETH/USDC", "USDC", 1500, 1000, 1000, 700)
    c = o.as_cpc
    assert o.y == 700
    assert iseq(c.x_act, 0)
    assert iseq(c.y_act, o.y)
    assert iseq(o.p_marg, c.p, c.p_max)
    assert iseq(o.p_end, c.p_min)
    

# ------------------------------------------------------------
# Test      063
# File      test_063_CPC.py
# Segment   New CPC features in v2
# ------------------------------------------------------------
def test_new_cpc_features_in_v2():
# ------------------------------------------------------------
    
    # +
    p = CPCContainer.Pair("ETH/USDC")
    assert str(p) == "ETH/USDC"
    assert p.pair == str(p)
    assert p.tknx == "ETH"
    assert p.tkny == "USDC"
    assert p.tknb == "ETH"
    assert p.tknq == "USDC"
    
    pp = CPCContainer.Pair.wrap(["ETH/USDC", "WBTC/ETH"])
    assert len(pp) == 2
    assert pp[0].pair == "ETH/USDC"
    assert pp[1].pair == "WBTC/ETH"
    assert pp[0].unwrap(pp) == ('ETH/USDC', 'WBTC/ETH')
    # -
    
    pairs = ["A", "B", "C"]
    assert CPCContainer.pairset(", ".join(pairs)) == set(pairs)
    assert CPCContainer.pairset(pairs) == set(pairs)
    assert CPCContainer.pairset(tuple(pairs)) == set(pairs)
    assert CPCContainer.pairset(p for p in pairs) == set(pairs)
    
    pairs = [f"{a}/{b}" for a in ["ETH", "USDC", "DAI"] for b in ["DAI", "WBTC", "LINK", "ETH"] if a!=b]
    CC = CPCContainer()
    fp = lambda **cond: CC.filter_pairs(pairs=pairs, **cond)
    assert fp(bothin="ETH, USDC, DAI") == {'DAI/ETH', 'ETH/DAI', 'USDC/DAI', 'USDC/ETH'}
    assert fp(onein="WBTC") == {'DAI/WBTC', 'ETH/WBTC', 'USDC/WBTC'}
    assert fp(onein="ETH") == fp(contains="ETH")
    assert fp(notin="WBTC, ETH, DAI") == {'USDC/LINK'}
    assert fp(tknbin="WBTC") == set()
    assert fp(tknqin="WBTC") == {'DAI/WBTC', 'ETH/WBTC', 'USDC/WBTC'}
    assert fp(tknbnotin="WBTC") == set(pairs)
    assert fp(tknbnotin="WBTC, ETH, DAI") == {'USDC/DAI', 'USDC/ETH', 'USDC/LINK', 'USDC/WBTC'}
    assert fp(notin_0="WBTC", notin_1="DAI") == fp(notin="WBTC, DAI")
    assert fp(onein = "ETH") == fp(anyall=CC.FP_ANY, tknbin="ETH", tknqin="ETH")
    
    P = CPCContainer.Pair
    ETHUSDC = P("ETH/USDC")
    USDCETH = P(ETHUSDC.pairr)
    assert ETHUSDC.pair == "ETH/USDC"
    assert ETHUSDC.pairr == "USDC/ETH"
    assert USDCETH.pairr == "ETH/USDC"
    assert USDCETH.pair == "USDC/ETH"
    assert ETHUSDC.isprimary
    assert not USDCETH.isprimary
    assert ETHUSDC.primary == ETHUSDC.pair
    assert ETHUSDC.secondary == ETHUSDC.pairr
    assert USDCETH.primary == USDCETH.pairr
    assert USDCETH.secondary == USDCETH.pair
    assert ETHUSDC.primary == USDCETH.primary
    assert ETHUSDC.secondary == USDCETH.secondary
    
    assert P("BTC/ETH").isprimary
    assert P("WBTC/ETH").isprimary
    assert P("BTC/WETH").isprimary
    assert P("WBTC/ETH").isprimary
    assert P("BTC/USDC").isprimary
    assert P("XYZ/USDC").isprimary
    assert P("XYZ/USDT").isprimary
    

# ------------------------------------------------------------
# Test      063
# File      test_063_CPC.py
# Segment   Real data and retrieval of curves
# ------------------------------------------------------------
def test_real_data_and_retrieval_of_curves():
# ------------------------------------------------------------
    
    try:
        df = pd.read_csv("NBTEST_063_Curves.csv.gz")
    except:
        df = pd.read_csv("carbon/tests/nbtest_data/NBTEST_063_Curves.csv.gz")
    CC = CPCContainer.from_df(df)
    assert len(CC) == 459
    assert len(CC) == len(df)
    assert len(CC.pairs()) == 326
    assert len(CC.tokens()) == 141
    assert CC.tokens_s
    assert CC.tokens_s()[:60] == '1INCH,1ONE,AAVE,ALCX,ALEPH,ALPHA,AMP,ANKR,ANT,APW,ARCONA,ARM'
    print("Num curves:", len(CC))
    print("Num pairs:", len(CC.pairs()))
    print("Num tokens:", len(CC.tokens()))
    #print(CC.tokens_s())
    
    assert CC.bypairs(CC.fp(onein="WETH, WBTC")) == CC.bypairs(CC.fp(onein="WETH, WBTC"), asgenerator=False)
    assert len(CC.bypairs(CC.fp(onein="WETH, WBTC"))) == 254
    assert len(CC.bypairs(CC.fp(onein="WETH, WBTC"), ascc=True)) == 254
    CC1 = CC.bypairs(CC.fp(onein="WBTC"), ascc=True)
    assert len(CC1) == 29
    cids = [c.cid for c in CC.bypairs(CC.fp(onein="WBTC"))]
    assert len(cids) == len(CC1)
    assert CC.bycid("bla") is None
    assert not CC.bycid(191) is None
    assert raises(CC.bycids, ["bla"])
    assert len(CC.bycids(cids)) == len(cids)
    assert len(CC.bytknx("WETH")) == 46
    assert len(CC.bytkny("WETH")) == 181
    assert len(CC.bytknys("WETH")) == len(CC.bytkny("WETH"))
    assert len(CC.bytknxs("USDC, USDT")) == 41
    assert len(CC.bytknxs(["USDC", "USDT"])) == len(CC.bytknxs("USDC, USDT"))
    assert len(CC.bytknys(["USDC", "USDT"])) == len(CC.bytknys({"USDC", "USDT"}))
    cs = CC.bytknx("WETH", asgenerator=True)
    assert raises(len, cs)
    assert len(tuple(cs)) == 46
    assert len(tuple(cs)) == 0  # generator empty
    
    CC2 = CC.bypairs(CC.fp(bothin="USDC, DAI, BNT, SHIB, ETH, AAVE, LINK"), ascc=True)
    tt = CC2.tokentable()
    assert tt["ETH"].x == []
    assert tt["ETH"].y == [0]
    assert tt["DAI"].x == [1,4,8]
    assert tt["DAI"].y == [3,6]
    tt
    
    assert CC2.tknxs() == {'AAVE', 'BNT', 'DAI', 'LINK'}
    assert CC2.tknxl() == ['BNT', 'DAI', 'LINK', 'LINK', 'DAI', 'LINK', 'LINK', 'AAVE', 'DAI']
    assert set(CC2.tknxl()) == CC2.tknxs() 
    assert set(CC2.tknyl()) == CC2.tknys() 
    assert len(CC2.tknxl()) == len(CC2.tknyl())
    assert len(CC2.tknxl()) == len(CC2)
    

# ------------------------------------------------------------
# Test      063
# File      test_063_CPC.py
# Segment   TokenScale tests
# ------------------------------------------------------------
def test_tokenscale_tests():
# ------------------------------------------------------------
    
    TSB = ts.TokenScaleBase()
    assert raises (TSB.scale,"ETH")
    assert TSB.DEFAULT_SCALE == 1e-2
    
    TS = ts.TokenScale.from_tokenscales(USDC=1e0, ETH=1e3, BTC=1e4)
    TS
    
    assert TS("USDC") == 1
    assert TS("ETH") == 1000
    assert TS("BTC") == 10000
    assert TS("MEH") == TS.DEFAULT_SCALE
    
    TSD = ts.TokenScaleData
    
    tknset = {'AAVE', 'BNT', 'BTC', 'ETH', 'LINK', 'USDC', 'USDT', 'WBTC', 'WETH'}
    assert tknset - set(TSD.scale_dct.keys()) == set()
    
    cc1 = CPC.from_xy(x=10, y=20000, pair="ETH/USDC")
    assert cc1.tokenscale is cc1.TOKENSCALE
    assert cc1.tknx == "ETH"
    assert cc1.tkny == "USDC"
    assert cc1.scalex == 1
    assert cc1.scaley == 1
    cc2 = CPC.from_xy(x=10, y=20000, pair="BTC/MEH")
    assert cc2.tknx == "BTC"
    assert cc2.tkny == "MEH"
    assert cc2.scalex == 1
    assert cc2.scaley == 1
    assert cc2.scaley == cc2.tokenscale.DEFAULT_SCALE
    
    cc1 = CPC.from_xy(x=10, y=20000, pair="ETH/USDC")
    cc1.set_tokenscale(TSD)
    assert cc1.tokenscale != cc1.TOKENSCALE
    assert cc1.tknx == "ETH"
    assert cc1.tkny == "USDC"
    assert cc1.scalex == 1e3
    assert cc1.scaley == 1e0
    cc2 = CPC.from_xy(x=10, y=20000, pair="BTC/MEH")
    cc2.set_tokenscale(TSD)
    assert cc2.tknx == "BTC"
    assert cc2.tkny == "MEH"
    assert cc2.scalex == 1e4
    assert cc2.scaley == 1e-2
    assert cc2.scaley == cc2.tokenscale.DEFAULT_SCALE
    

# ------------------------------------------------------------
# Test      063
# File      test_063_CPC.py
# Segment   dx_min and dx_max etc
# ------------------------------------------------------------
def test_dx_min_and_dx_max_etc():
# ------------------------------------------------------------
    
    cc = CPC.from_pkpp(p=100, k=100*10000, p_min=90, p_max=110)
    assert iseq(cc.x_act, 4.653741075440777)
    assert iseq(cc.y_act, 513.167019494862)
    assert cc.dx_min == -cc.x_act
    assert cc.dy_min == -cc.y_act
    assert iseq( (cc.x + cc.dx_max)*(cc.y + cc.dy_min), cc.k)
    assert iseq( (cc.y + cc.dy_max)*(cc.x + cc.dx_min), cc.k)
    

# ------------------------------------------------------------
# Test      063
# File      test_063_CPC.py
# Segment   xyfromp_f and dxdyfromp_f
# ------------------------------------------------------------
def test_xyfromp_f_and_dxdyfromp_f():
# ------------------------------------------------------------
    
    # +
    c = CPC.from_pkpp(p=100, k=100*10000, p_min=90, p_max=110, pair=f"{T.ETH}/{T.USDC}")
    
    assert c.pair == 'WETH-6Cc2/USDC-eB48'
    assert c.pairp == 'WETH/USDC'
    assert c.p == 100
    assert iseq(c.x_act, 4.653741075440777)
    assert iseq(c.y_act, 513.167019494862)
    assert c.tknx == T.ETH
    assert c.tkny == T.USDC
    assert c.tknxp == "WETH"
    assert c.tknyp == "USDC"
    assert c.xyfromp_f() == (c.x, c.y, c.p)
    assert c.xyfromp_f(withunits=True) == (100.0, 10000.0, 100.0, 'WETH', 'USDC', 'WETH/USDC')
    
    x,y,p = c.xyfromp_f(p=85, ignorebounds=True)
    assert p == 85
    assert iseq(x*y, c.k)
    assert iseq(y/x,85)
    
    x,y,p = c.xyfromp_f(p=115, ignorebounds=True)
    assert p == 115
    assert iseq(x*y, c.k)
    assert iseq(y/x,115)
    
    x,y,p = c.xyfromp_f(p=95)
    assert p == 95
    assert iseq(x*y, c.k)
    assert iseq(y/x,p)
    
    x,y,p = c.xyfromp_f(p=105)
    assert p == 105
    assert iseq(x*y, c.k)
    assert iseq(y/x,p)
    
    x,y,p = c.xyfromp_f(p=85)
    assert p == 85
    assert iseq(x*y, c.k)
    assert iseq(y/x,90)
    
    x,y,p = c.xyfromp_f(p=115)
    assert p == 115
    assert iseq(x*y, c.k)
    assert iseq(y/x,110)
    
    # +
    assert c.dxdyfromp_f(withunits=True) == (0.0, 0.0, 100.0, 'WETH', 'USDC', 'WETH/USDC')
    
    dx,dy,p = c.dxdyfromp_f(p=85, ignorebounds=True)
    assert p == 85
    assert iseq((c.x+dx)*(c.y+dy), c.k)
    assert iseq((c.y+dy)/(c.x+dx),p)
    
    dx,dy,p = c.dxdyfromp_f(p=115, ignorebounds=True)
    assert p == 115
    assert iseq((c.x+dx)*(c.y+dy), c.k)
    assert iseq((c.y+dy)/(c.x+dx),p)
    
    dx,dy,p = c.dxdyfromp_f(p=95)
    assert p == 95
    assert iseq((c.x+dx)*(c.y+dy), c.k)
    assert iseq((c.y+dy)/(c.x+dx),p)
    
    dx,dy,p = c.dxdyfromp_f(p=105)
    assert p == 105
    assert iseq((c.x+dx)*(c.y+dy), c.k)
    assert iseq((c.y+dy)/(c.x+dx),p)
    
    dx,dy,p = c.dxdyfromp_f(p=85)
    assert p == 85
    assert iseq((c.x+dx)*(c.y+dy), c.k)
    assert iseq((c.y+dy)/(c.x+dx), 90)
    assert iseq(dy, -c.y_act)
    
    dx,dy,p = c.dxdyfromp_f(p=115)
    assert p == 115
    assert iseq((c.x+dx)*(c.y+dy), c.k)
    assert iseq((c.y+dy)/(c.x+dx), 110)
    assert iseq(dx, -c.x_act)
    
    assert iseq(c.x_min*c.y_max, c.k)
    assert iseq(c.x_max*c.y_min, c.k)
    assert iseq(c.y_max/c.x_min, c.p_max)
    assert iseq(c.y_min/c.x_max, c.p_min)
    # -
    

# ------------------------------------------------------------
# Test      063
# File      test_063_CPC.py
# Segment   CPCInverter
# ------------------------------------------------------------
def test_cpcinverter():
# ------------------------------------------------------------
    
    c   = CPC.from_pkpp(p=2000,   k=10*20000, p_min=1800,   p_max=2200,   pair=f"{T.ETH}/{T.USDC}")
    c2  = CPC.from_pkpp(p=1/2000, k=10*20000, p_max=1/1800, p_min=1/2200, pair=f"{T.USDC}/{T.ETH}")
    ci  = CPCInverter(c)
    c2i = CPCInverter(c2)
    curves = CPCInverter.wrap([c,c2])
    assert c.pairo == c2i.pairo
    assert ci.pairo == c2.pairo
    
    #print("x_act", c.x_act, c2i.x_act)
    assert iseq(c.x_act, c2i.x_act)
    xact = c.x_act
    dx = -0.1*xact
    c_ex = c.execute(dx=dx)
    assert isinstance(c_ex, CPC)
    assert iseq(c_ex.x_act, xact+dx)
    assert iseq(c_ex.x, c.x+dx)
    c2i_ex = c2i.execute(dx=dx)
    assert iseq(c2i_ex.x_act, xact+dx)
    assert iseq(c2i_ex.x, c.x+dx)
    assert isinstance(c2i_ex, CPCInverter)
    
    assert len(curves) == 2
    assert set(c.pair for c in curves) == {'WETH-6Cc2/USDC-eB48'}
    assert len(set(c.pair for c in curves)) == 1
    assert len(set(c.tknx for c in curves)) == 1
    assert len(set(c.tkny for c in curves)) == 1
    
    assert c.tknx == ci.tkny
    assert c.tkny == ci.tknx
    assert c.tknxp == ci.tknyp
    assert c.tknyp == ci.tknxp
    assert c.tknb == ci.tknq
    assert c.tknq == ci.tknb
    assert c.tknbp == ci.tknqp
    assert c.tknqp == ci.tknbp
    assert f"{c.tknq}/{c.tknb}" == ci.pair
    assert f"{c.tknqp}/{c.tknbp}" == ci.pairp
    assert c.x == ci.y
    assert c.y == ci.x
    assert c.x_act == ci.y_act
    assert c.y_act == ci.x_act
    assert c.x_min == ci.y_min
    assert c.x_max == ci.y_max
    assert c.y_min == ci.x_min
    assert c.y_max == ci.x_max
    assert c.k == ci.k
    assert iseq(c.p, 1/ci.p)
    assert iseq(c.p_min, 1/ci.p_max)
    assert iseq(c.p_max, 1/ci.p_min)
    
    
    assert c.pair == c2i.pair
    assert c.tknx == c2i.tknx
    assert c.tkny == c2i.tkny
    assert c.tknxp == c2i.tknxp
    assert c.tknyp == c2i.tknyp
    assert c.tknb == c2i.tknb
    assert c.tknq == c2i.tknq
    assert c.tknbp == c2i.tknbp
    assert c.tknqp == c2i.tknqp
    assert iseq(c.p, c2i.p)
    assert iseq(c.p_min, c2i.p_min)
    assert iseq(c.p_max, c2i.p_max)
    assert c.x == c2i.x
    assert c.y == c2i.y
    assert c.x_act == c2i.x_act
    assert c.y_act == c2i.y_act
    assert c.x_min == c2i.x_min
    assert c.x_max == c2i.x_max
    assert c.y_min == c2i.y_min
    assert c.y_max == c2i.y_max
    assert c.k == c2i.k
    
    assert iseq(c.xfromy_f(c.y), c2i.xfromy_f(c2i.y))
    assert iseq(c.yfromx_f(c.x), c2i.yfromx_f(c2i.x))
    assert iseq(c.xfromy_f(c.y*1.05), c2i.xfromy_f(c2i.y*1.05))
    assert iseq(c.yfromx_f(c.x*1.05), c2i.yfromx_f(c2i.x*1.05))
    assert iseq(c.dxfromdy_f(1), c2i.dxfromdy_f(1))
    assert iseq(c.dyfromdx_f(1), c2i.dyfromdx_f(1))
    
    assert c.xyfromp_f() == c2i.xyfromp_f()
    assert c.dxdyfromp_f() == c2i.dxdyfromp_f()
    assert c.xyfromp_f(withunits=True) == c2i.xyfromp_f(withunits=True)
    assert c.dxdyfromp_f(withunits=True) == c2i.dxdyfromp_f(withunits=True)
    assert iseq(c.p, c2i.p)
    x,y,p    = c.xyfromp_f(c.p*1.05)
    x2,y2,p2 = c2i.xyfromp_f(c2i.p*1.05)
    assert iseq(x,x2)
    assert iseq(y,y2)
    assert iseq(p,p2)
    dx,dy,p    = c.dxdyfromp_f(c.p*1.05)
    dx2,dy2,p2 = c2i.dxdyfromp_f(c2i.p*1.05)
    assert iseq(dx,dx2)
    assert iseq(dy,dy2)
    assert iseq(p,p2)
    
    

# ------------------------------------------------------------
# Test      063
# File      test_063_CPC.py
# Segment   simple_optimizer
# ------------------------------------------------------------
def test_simple_optimizer():
# ------------------------------------------------------------
    
    CC = CPCContainer(CPC.from_pk(p=2000+i*10, k=10*20000, pair=f"{T.ETH}/{T.USDC}") for i in range(11))
    c0 = CC.curves[0]
    c1 = CC.curves[-1]
    CC0 = CPCContainer([c0])
    assert len(CC) == 11
    assert iseq([c.p for c in CC][-1], 2100)
    assert len(CC0) == 1
    assert iseq([c.p for c in CC0][-1], 2000)
    
    # +
    O = CPCArbOptimizer(CC)
    O0 = CPCArbOptimizer(CC0)
    func = O.simple_optimizer(result=O.SO_DXDYVECFUNC)
    func0 = O0.simple_optimizer(result=O.SO_DXDYVECFUNC)
    funcs = O.simple_optimizer(result=O.SO_DXDYSUMFUNC)
    funcvx = O.simple_optimizer(result=O.SO_DXDYVALXFUNC)
    funcvy = O.simple_optimizer(result=O.SO_DXDYVALYFUNC)
    x,y = func0(2100)[0]
    xb, yb, _ = c0.dxdyfromp_f(2100)
    assert x == xb
    assert y == yb
    x,y = func(2100)[-1]
    xb, yb, _ = c1.dxdyfromp_f(2100)
    assert x == xb
    assert y == yb
    assert np.all(sum(func(2100)) == funcs(2100))
    
    p = 2100
    dx, dy = funcs(p)
    assert iseq(dy + p*dx, funcvy(p))
    assert iseq(dy/p + dx, funcvx(p))
    
    p = 1500
    dx, dy = funcs(p)
    assert iseq(dy + p*dx, funcvy(p))
    assert iseq(dy/p + dx, funcvx(p))
    
    assert iseq(float(O0.simple_optimizer(result=O.SO_PMAX)), c0.p)
    assert iseq(float(O.simple_optimizer(result=O.SO_PMAX)), 2049.6451720862074, eps=1e-3)
    # -
    
    O.simple_optimizer(result=O.SO_PMAX)
    
    # ### global max
    
    r = O.simple_optimizer()
    r_ = O.simple_optimizer(result=O.SO_GLOBALMAX)
    assert raises(O.simple_optimizer, targettkn=T.WETH, result=O.SO_GLOBALMAX)
    assert iseq(float(r), float(r_))
    assert len(r.curves) == len(CC)
    assert np.all(r.dxdy_sum == sum(r.dxdy_vec))
    dx, dy = r.dxdy_vecs
    assert tuple(tuple(_) for _ in r.dxdy_vec) == tuple(zip(dx,dy))
    assert r.result == r.dxdy_valx
    for dp in np.linspace(-500,500,100):
        assert r.dxdyfromp_valx_f(p) < r.dxdy_valx
        assert r.dxdyfromp_valy_f(p) < r.dxdy_valy
    
    CC_ex = CPCContainer(c.execute(dx=dx) for c, dx in zip(r.curves, r.dxvalues))
    # CC.plot()
    # CC_ex.plot()
    prices = [c.p for c in CC]
    prices_ex = [c.p for c in CC_ex]
    assert iseq(np.std(prices), 31.622776601683707)
    assert iseq(np.std(prices_ex), 4.547473508864641e-13)
    #prices, prices_ex
    
    # ### target token
    
    r = O.simple_optimizer(targettkn=T.WETH)
    r_ = O.simple_optimizer(targettkn=T.WETH, result=O.SO_TARGETTKN)
    assert raises(O.simple_optimizer,targettkn=T.DAI)
    assert raises(O.simple_optimizer, result=O.SO_TARGETTKN)
    assert iseq(float(r), float(r_))
    assert abs(sum(r.dyvalues) < 1e-6)
    assert sum(r.dxvalues) < 0
    assert iseq(float(r),sum(r.dxvalues))
    
    r = O.simple_optimizer(targettkn=T.USDC)
    assert abs(sum(r.dxvalues) < 1e-6)
    assert sum(r.dyvalues) < 0
    assert iseq(float(r),sum(r.dyvalues))
    

# ------------------------------------------------------------
# Test      063
# File      test_063_CPC.py
# Segment   optimizer plus inverted curves
# ------------------------------------------------------------
def test_optimizer_plus_inverted_curves():
# ------------------------------------------------------------
    
    CCr = CPCContainer(CPC.from_pk(p=2000+i*100, k=10*(20000+10000*i), pair=f"{T.ETH}/{T.USDC}") for i in range(11))
    CCi = CPCContainer(CPC.from_pk(p=1/(2050+i*100), k=10*(20000+10000*i), pair=f"{T.USDC}/{T.ETH}") for i in range(11))
    CC  = CCr.bycids()
    assert len(CC) == len(CCr)
    CC += CCi
    assert len(CC) == len(CCr) + len(CCi)
    
    # +
    # CC.plot()
    # -
    
    O = CPCArbOptimizer(CC)
    r = O.simple_optimizer()
    print(f"Arbitrage gains: {-r.valx:.4f} {r.tknxp} [time={r.time:.4f}s]")
    assert iseq(r.result, -1.3194573866437527)
    
    CC_ex = CPCContainer(c.execute(dx=dx) for c, dx in zip(r.curves, r.dxvalues))
    # CC.plot()
    # CC_ex.plot()
    
    prices_ex = [c.pairo.primary_price(c.p) for c in CC_ex]
    assert iseq(np.std(prices_ex), 5.130242014436283e-13)
    

# ------------------------------------------------------------
# Test      063
# File      test_063_CPC.py
# Segment   posx and negx
# ------------------------------------------------------------
def test_posx_and_negx():
# ------------------------------------------------------------
    
    O = CPCArbOptimizer
    a = O.a
    
    assert O.posx([0,-1,2]) == (0, 0, 2)
    assert O.posx((-1,-2, 3)) == (0, 0, 3)
    assert O.negx([0,-1,2]) == (0, -1, 0)
    assert O.negx((-1,-2, 3)) == (-1, -2, 0)
    assert np.all(O.posx(a([0,-1,2])) == a((0, 0, 2)))
    assert O.t(a((-1,-2))) == (-1,-2)
    
    for v in ((1,2,3), (1,-1,5-10,0), (-10.5,8,2.34,-17)):
        assert np.all(O.posx(a(v))+O.negx(a(v)) == v)
    

# ------------------------------------------------------------
# Test      063
# File      test_063_CPC.py
# Segment   TradeInstructions
# ------------------------------------------------------------
def test_tradeinstructions():
# ------------------------------------------------------------
    
    TI = CPCArbOptimizer.TradeInstruction
    
    ti = TI.new(curve_or_cid="1", tkn1="ETH", amt1=1, tkn2="USDC", amt2=-2000)
    print(f"cid={ti.cid}, out={ti.amtout} {ti.tknout}, , out={ti.amtin} {ti.tknin}")
    assert ti.tknin == "ETH"
    assert ti.amtin > 0
    assert ti.tknout == "USDC"
    assert ti.amtout < 0
    assert ti.price_outperin == 2000
    assert ti.price_inperout == 1/2000
    assert ti.prices == (2000, 1/2000)
    assert ti.price_outperin == ti.p
    assert ti.price_inperout == ti.pr
    assert ti.prices == ti.pp
    
    assert not raises(TI, cid="1", tknin="USDC", amtin=2000, tknout="ETH", amtout=-1)
    assert raises(TI, cid="1", tknin="USDC", amtin=2000, tknout="ETH", amtout=1)
    assert raises(TI, cid="1", tknin="USDC", amtin=-2000, tknout="ETH", amtout=-1)
    assert raises(TI, cid="1", tknin="USDC", amtin=-2000, tknout="ETH", amtout=1)
    assert raises(TI, cid="1", tknin="USDC", amtin=2000, tknout="ETH", amtout=0)
    assert raises(TI, cid="1", tknin="USDC", amtin=0, tknout="ETH", amtout=-1)
    assert not raises(TI.new, curve_or_cid="1", tkn1="USDC", amt1=2000, tkn2="ETH", amt2=-1)
    assert not raises(TI.new, curve_or_cid="1", tkn1="USDC", amt1=-2000, tkn2="ETH", amt2=1)
    assert raises(TI.new, curve_or_cid="1", tkn1="USDC", amt1=2000, tkn2="ETH", amt2=1)
    assert raises(TI.new, curve_or_cid="1", tkn1="USDC", amt1=-2000, tkn2="ETH", amt2=-1)
    assert raises(TI.new, curve_or_cid="1", tkn1="USDC", amt1=0, tkn2="ETH", amt2=1)
    assert raises(TI.new, curve_or_cid="1", tkn1="USDC", amt1=-2000, tkn2="ETH", amt2=0)
    
    til = [
        TI.new(curve_or_cid=f"{i+1}", tkn1="ETH", amt1=1*(1+i/100), tkn2="USDC", amt2=-2000*(1+i/100)) 
        for i in range(10)
    ]
    tild = TI.to_dicts(til)
    tildf = TI.to_df(til)
    assert len(tild) == 10
    assert len(tildf) == 10
    assert tild[0] == {'cid': '1', 'tknin': 'ETH', 'amtin': 1.0, 'tknout': 'USDC', 'amtout': -2000.0}
    assert dict(tildf.iloc[0]) == {
        'pair': '',
        'pairp': '',
        'tknin': 'ETH',
        'tknout': 'USDC',
        'ETH': 1.0,
        'USDC': -2000.0
    }
    
    tildf
    

# ------------------------------------------------------------
# Test      063
# File      test_063_CPC.py
# Segment   margp_optimizer
# ------------------------------------------------------------
def test_margp_optimizer():
# ------------------------------------------------------------
    
    # ### no arbitrage possible
    
    CCa = CPCContainer()
    CCa += CPC.from_pk(pair="WETH/USDC", p=2000, k=10*20000, cid="c0")
    CCa += CPC.from_pk(pair="WETH/USDT", p=2000, k=10*20000, cid="c1")
    CCa += CPC.from_pk(pair="USDC/USDT", p=1.0, k=200000*200000, cid="c2")
    O = CPCArbOptimizer(CCa)
    
    r = O.margp_optimizer("WETH", result=O.MO_DEBUG)
    assert isinstance(r, dict)
    prices0 = r["price_estimates_t"]
    assert not prices0 is None, f"prices0 must not be None [{prices0}]"
    r1 = O.arb("WETH")
    r2 = O.SelfFinancingConstraints.arb("WETH")
    assert isinstance(r1, CPCArbOptimizer.SelfFinancingConstraints)
    assert r1 == r2
    assert r["sfc"] == r1
    assert r1.is_arbsfc()
    assert r1.optimizationvar == "WETH"
    
    r
    
    prices0
    
    f = O.margp_optimizer("WETH", result=O.MO_DTKNFROMPF, params=dict(verbose=True, debug=False))
    r3 = f(prices0, islog10=False)
    assert np.all(r3 == (0,0))
    r4, r3b = f(prices0, asdct=True, islog10=False)
    assert np.all(r3==r3b)
    assert len(r4) == len(r3)+1
    assert tuple(r4.values()) == (0,0,0)
    assert set(r4) == {'USDC', 'USDT', 'WETH'}
    
    r = O.margp_optimizer("WETH", result=O.MO_MINIMAL, params=dict(verbose=True))
    rd = r.asdict
    assert abs(float(r)) < 1e-10
    assert r.result == float(r)
    assert r.method == "margp"
    assert r.curves is None
    assert r.targettkn == "WETH"
    assert r.dtokens is None
    assert sum(abs(x) for x in r.dtokens_t) < 1e-10
    assert r.p_optimal is None
    assert iseq(0.0005, r.p_optimal_t[0], r.p_optimal_t[1])
    assert set(r.tokens_t) == {'USDC', 'USDT'}
    assert r.errormsg is None
    assert r.is_error == False
    assert r.time > 0
    assert r.time < 0.1
    
    # +
    r = O.margp_optimizer("WETH", result=O.MO_FULL)
    rd = r.asdict()
    r2 = O.margp_optimizer("WETH")
    r2d = r2.asdict()
    for k in rd:
        #print(k)
        if not k in ["time", "curves"]:
            assert rd[k] == r2d[k]
    assert r2.curves == r.curves # the TokenScale object fails in the dict
    
    assert abs(float(r)) < 1e-10
    assert r.result == float(r)
    assert r.method == "margp"
    assert len(r.curves) == 3
    assert r.targettkn == "WETH"
    assert set(r.dtokens.keys()) == set(['USDT', 'WETH', 'USDC'])
    assert sum(abs(x) for x in r.dtokens.values()) < 1e-10
    assert sum(abs(x) for x in r.dtokens_t) < 1e-10
    assert iseq(0.0005, r.p_optimal["USDC"], r.p_optimal["USDT"])
    assert iseq(0.0005, r.p_optimal_t[0], r.p_optimal_t[1])
    assert tuple(r.p_optimal.values()) == r.p_optimal_t
    assert set(r.tokens_t) == set(('USDC', 'USDT'))
    assert r.errormsg is None
    assert r.is_error == False
    assert r.time > 0
    assert r.time < 0.1
    # -
    
    # ### arbitrage
    
    CCa = CPCContainer()
    CCa += CPC.from_pk(pair="WETH/USDC", p=2000, k=10*20000, cid="c0")
    CCa += CPC.from_pk(pair="WETH/USDT", p=2000, k=10*20000, cid="c1")
    CCa += CPC.from_pk(pair="USDC/USDT", p=1.2, k=200000*200000, cid="c2")
    O = CPCArbOptimizer(CCa)
    
    r = O.margp_optimizer("WETH", result=O.MO_DEBUG)
    assert isinstance(r, dict)
    prices0 = r["price_estimates_t"]
    r1 = O.arb("WETH")
    r2 = O.SelfFinancingConstraints.arb("WETH")
    assert isinstance(r1, CPCArbOptimizer.SelfFinancingConstraints)
    assert r1 == r2
    assert r["sfc"] == r1
    assert r1.is_arbsfc()
    assert r1.optimizationvar == "WETH"
    
    f = O.margp_optimizer("WETH", result=O.MO_DTKNFROMPF)
    r3 = f(prices0, islog10=False)
    assert set(r3.astype(int)) == set((17425,-19089))
    r4, r3b = f(prices0, asdct=True, islog10=False)
    assert np.all(r3==r3b)
    assert len(r4) == len(r3)+1
    assert set(r4) == {'USDC', 'USDT', 'WETH'}
    
    r = O.margp_optimizer("WETH", result=O.MO_FULL)
    assert iseq(float(r), -0.03944401129301944)
    assert r.result == float(r)
    assert r.method == "margp"
    assert len(r.curves) == 3
    assert r.targettkn == "WETH"
    assert abs(r.dtokens_t[0]) < 1e-6
    assert abs(r.dtokens_t[1]) < 1e-6
    assert r.dtokens["WETH"] == float(r)
    assert tuple(r.p_optimal.values()) == r.p_optimal_t
    assert tuple(r.p_optimal) == r.tokens_t
    assert iseq(r.p_optimal_t[0], 0.0005421803152482512) or iseq(r.p_optimal_t[0], 0.00045575394031021585)
    assert iseq(r.p_optimal_t[1], 0.0005421803152482512) or iseq(r.p_optimal_t[1], 0.00045575394031021585)
    assert tuple(r.p_optimal.values()) == r.p_optimal_t
    assert set(r.tokens_t) == set(('USDC', 'USDT'))
    assert r.errormsg is None
    assert r.is_error == False
    assert r.time > 0
    assert r.time < 0.1
    
    abs(r.dtokens_t[0])
    
    
    

# ------------------------------------------------------------
# Test      063
# File      test_063_CPC.py
# Segment   simple_optimizer demo [NOTEST]
# ------------------------------------------------------------
def notest_simple_optimizer_demo():
# ------------------------------------------------------------
    
    CC = CPCContainer(CPC.from_pk(p=2000+i*100, k=10*(20000+i*10000), pair=f"{T.ETH}/{T.USDC}") for i in range(11))
    O = CPCArbOptimizer(CC)
    c0 = CC.curves[0]
    CC0 = CPCContainer([c0])
    O = CPCArbOptimizer(CC)
    O0 = CPCArbOptimizer(CC0)
    funcvx = O.simple_optimizer(result=O.SO_DXDYVALXFUNC)
    funcvy = O.simple_optimizer(result=O.SO_DXDYVALYFUNC)
    funcvx0 = O0.simple_optimizer(result=O.SO_DXDYVALXFUNC)
    funcvy0 = O0.simple_optimizer(result=O.SO_DXDYVALYFUNC)
    #CC.plot()
    
    xr = np.linspace(1500, 3000, 50)
    plt.plot(xr, [funcvx(x)/len(CC) for x in xr], label="all curves [scaled]")
    plt.plot(xr, [funcvx0(x) for x in xr], label="curve 0 only")
    plt.xlabel(f"price [{c0.pairp}]")
    plt.ylabel(f"value [{c0.tknxp}]")
    plt.grid()
    plt.show()
    plt.plot(xr, [funcvy(x)/len(CC) for x in xr], label="all curves [scaled]")
    plt.plot(xr, [funcvy0(x) for x in xr], label="curve 0 only")
    plt.xlabel(f"price [{c0.pairp}]")
    plt.ylabel(f"value [{c0.tknyp}]")
    plt.grid()
    plt.show()
    
    r = O.simple_optimizer()
    print(f"Arbitrage gains: {-r.valx:.4f} {r.tknxp} [time={r.time:.4f}s]")
    
    CC_ex = CPCContainer(c.execute(dx=dx) for c, dx in zip(r.curves, r.dxvalues))
    CC.plot()
    CC_ex.plot()
    

# ------------------------------------------------------------
# Test      063
# File      test_063_CPC.py
# Segment   MargP Optimizer Demo [NOTEST]
# ------------------------------------------------------------
def notest_margp_optimizer_demo():
# ------------------------------------------------------------
    
    CCa = CPCContainer()
    CCa += CPC.from_pk(pair="WETH/USDC", p=2000, k=10*20000, cid="c0")
    CCa += CPC.from_pk(pair="WETH/USDT", p=2000, k=10*20000, cid="c1")
    CCa += CPC.from_pk(pair="USDC/USDT", p=1.2, k=20000*20000, cid="c2")
    O = CPCArbOptimizer(CCa)
    
    CCa.plot()
    
    r = O.margp_optimizer("WETH", params=dict(verbose=True))
    rd = r.asdict
    r
    
    rd
    
    CCa1 = O.adjust_curves(r.dxvalues)
    CCa1.plot()
    

# ------------------------------------------------------------
# Test      063
# File      test_063_CPC.py
# Segment   Optimizer plus inverted curves [NOTEST]
# ------------------------------------------------------------
def notest_optimizer_plus_inverted_curves():
# ------------------------------------------------------------
    
    CCr = CPCContainer(CPC.from_pk(p=2000+i*100, k=10*(20000+10000*i), pair=f"{T.ETH}/{T.USDC}") for i in range(11))
    CCi = CPCContainer(CPC.from_pk(p=1/(2050+i*100), k=10*(20000+10000*i), pair=f"{T.USDC}/{T.ETH}") for i in range(11))
    CC  = CCr.bycids()
    assert len(CC) == len(CCr)
    CC += CCi
    assert len(CC) == len(CCr) + len(CCi)
    CC.plot()
    
    O = CPCArbOptimizer(CC)
    r = O.simple_optimizer()
    print(f"Arbitrage gains: {-r.valx:.4f} {r.tknxp} [time={r.time:.4f}s]")
    CC_ex = CPCContainer(c.execute(dx=dx) for c, dx in zip(r.curves, r.dxvalues))
    prices_ex = [c.pairo.primary_price(c.p) for c in CC_ex]
    print("prices post arb:", prices_ex)
    print("stdev", np.std(prices_ex))
    #CC.plot()
    CC_ex.plot()
    

# ------------------------------------------------------------
# Test      063
# File      test_063_CPC.py
# Segment   Operating on leverage ranges [NOTEST]
# ------------------------------------------------------------
def notest_operating_on_leverage_ranges():
# ------------------------------------------------------------
    
    N = 10
    
    # +
    CCc, CCm, ctr = CPCContainer(), CPCContainer(), 0
    U, U1 = CPCContainer.u, CPCContainer.u1
    tknb, tknq = T.ETH, T.USDC
    pb, pq = 2000, 1
    pair = f"{tknb}/{tknq}"
    pp = pb/pq
    k = 100000**2/(pb*pq)
    CCm += CPC.from_pk(p=pp, k=k, pair=pair, cid = f"mkt-{pair}", params=dict(xc="market"))
    #print("\n***PAIR:", tknb, pb, tknq, pq, pair, pp)
    for i in range(N):
        p = pp * (1+0.2*U(-0.5, 0.5))
        p_min, p_max = (p, U(1.001, 1.5)*p) if U1()>0.5 else (U(0.8, 0.999)*p, p)
        amtusdc = U(10000, 200000)
        k = amtusdc**2/(pb*pq)
        #print("*curve", int(amtusdc), p, p_min, p_max, int(k))
        CCc += CPC.from_pkpp(p=p, k=k, p_min=p_min, p_max=p_max, 
                             pair=pair, cid = f"carb-{ctr}", params=dict(xc="carbon"))
        ctr += 1
        
    CC = CCc.bycids().add(CCm)
    CC.plot()
    # -
    
    O = CPCArbOptimizer(CC)
    r = O.simple_optimizer()
    print(f"Arbitrage gains: {-r.valx:.4f} {r.tknxp} [time={r.time:.4f}s]")
    CC_ex = CPCContainer(c.execute(dx=dx) for c, dx in zip(r.curves, r.dxvalues))
    prices_ex = [c.pairo.primary_price(c.p) for c in CC_ex]
    print("prices post arb:", prices_ex)
    print("stdev", np.std(prices_ex))
    #CC.plot()
    CC_ex.plot()
    
    r.dxvalues
    

# ------------------------------------------------------------
# Test      063
# File      test_063_CPC.py
# Segment   Arbitrage testing [NOTEST]
# ------------------------------------------------------------
def notest_arbitrage_testing():
# ------------------------------------------------------------
    
    c1 = CPC.from_pkpp(p=95, k=100*10000, p_min=90, p_max=110, pair=f"{T.ETH}/{T.USDC}")
    c2 = CPC.from_pkpp(p=105, k=90*10000, p_min=90, p_max=110, pair=f"{T.ETH}/{T.USDC}")
    CC = CPCContainer([c1,c2])
    CC.plot()
    
    a = lambda x: np.array(x)
    pr = np.linspace(70,130,200)
    dx1, dy1, p = zip(*(c1.dxdyfromp_f(p) for p in pr))
    assert np.all(p == pr)
    dx2, dy2, p = zip(*(c2.dxdyfromp_f(p) for p in pr))
    assert np.all(p == pr)
    v1 = a(dy1)+a(p)*a(dx1)
    v2 = a(dy2)+a(p)*a(dx2)
    plt.plot(p, v1, label="Value curve c1")
    plt.plot(p, v2, label="Value curve c2")
    plt.plot(p, v1+v2, label="Value combined curves")
    plt.legend()
    plt.grid()
    
    
    def vfunc(p):
        
        dx1, dy1, _ = c1.dxdyfromp_f(p)
        dx2, dy2, _ = c2.dxdyfromp_f(p)
        v1 = dy1 + p*dx1
        v2 = dy2 + p*dx2
        v = v1+v2
        #print(f"[v] v({p}) = {v}")
        return -v
    
    
    O = CPCArbOptimizer
    O.findmin(vfunc, 100, N=100)
    
    func1 = lambda x: (x-2)**2
    O.findmin(func1, 1)
    
    func2 = lambda x: 1-(x-3)**2
    O.findmax(func2, 2.5)
    
    val = tuple(float(O.findmin(func1, 100, N=n)) for n in range(100))
    val = tuple(abs(v-val[-1]) for v in val)
    val = tuple(v for v in val if v > 0)
    plt.plot(val)
    plt.yscale('log')
    plt.grid()
    
    val = tuple(float(O.findmin(func2, 100, N=n)) for n in range(100))
    val = tuple(abs(v-val[-1]) for v in val)
    val = tuple(v for v in val if v > 0)
    plt.plot(val)
    plt.yscale('log')
    plt.grid()
    
    val0 = tuple(float(O.findmin(vfunc, 99, N=n)) for n in range(100))
    val = tuple(abs(v-val0[-1]) for v in val0)
    val = tuple(v for v in val if v > 0)
    print(val0[-1])
    plt.plot(val)
    plt.yscale('log')
    plt.grid()
    
    val0 = tuple(float(O.findmin_gd(vfunc, 99, N=n)) for n in range(100))
    val = tuple(abs(v-val0[-1]) for v in val0)
    val = tuple(v for v in val if v > 0)
    print(val0[-1])
    plt.plot(val)
    plt.yscale('log')
    plt.grid()
    
    O.findmin(vfunc, 99, N=700)
    

# ------------------------------------------------------------
# Test      063
# File      test_063_CPC.py
# Segment   Charts [NOTEST]
# ------------------------------------------------------------
def notest_charts():
# ------------------------------------------------------------
    
    # ### Chars (x,y)
    
    xr = np.linspace(1,300,200)
    
    # +
    defaults = dict(p=2)
    curves = [
        CPC.from_px(x=100, **defaults),
        CPC.from_px(x=50, **defaults),
        CPC.from_px(x=150, **defaults),
    ]
    for c in curves:
        plt.plot(xr, [c.yfromx_f(x) for x in xr])
    
    plt.ylim((0,1000))
    plt.xlim((0,300))
    plt.grid()
    
    # +
    defaults = dict(p=2, x_act=10)
    curves = [
        CPC.from_px(x=100, **defaults),
        CPC.from_px(x=50, **defaults),
        CPC.from_px(x=150, **defaults),
    ]
    for c in curves:
        plt.plot(xr, [c.yfromx_f(x) for x in xr])
    
    plt.ylim((0,1000))
    plt.xlim((0,300))
    plt.grid()
    
    # +
    defaults = dict(p=2, y_act=20)
    curves = [
        CPC.from_px(x=100, **defaults),
        CPC.from_px(x=50, **defaults),
        CPC.from_px(x=150, **defaults),
    ]
    for c in curves:
        plt.plot(xr, [c.yfromx_f(x) for x in xr])
    
    plt.ylim((0,1000))
    plt.xlim((0,300))
    plt.grid()
    
    # +
    defaults = dict(p=2, x_act=10, y_act=20)
    curves = [
        CPC.from_px(x=100, **defaults),
        CPC.from_px(x=50, **defaults),
        CPC.from_px(x=150, **defaults),
    ]
    for c in curves:
        plt.plot(xr, [c.yfromx_f(x) for x in xr])
    
    plt.ylim((0,1000))
    plt.xlim((0,300))
    plt.grid()
    # -
    # ### Charts (dx, dy)
    
    
    e=1e-5
    dxr = np.linspace(-50+e,50-e,100)
    
    # +
    defaults = dict(p=2)
    curves = [
        CPC.from_px(x=100, **defaults),
        CPC.from_px(x=50, **defaults),
        CPC.from_px(x=150, **defaults),
    ]
    for c in curves:
        plt.plot(dxr, [c.dyfromdx_f(dx) for dx in dxr])
    
    plt.ylim((-100,200))
    plt.xlim((-50,50))
    plt.grid()
    
    # +
    defaults = dict(p=2, x_act=10)
    curves = [
        CPC.from_px(x=100, **defaults),
        CPC.from_px(x=50, **defaults),
        CPC.from_px(x=150, **defaults),
    ]
    for c in curves:
        plt.plot(dxr, [c.dyfromdx_f(dx) for dx in dxr])
    
    plt.ylim((-100,200))
    plt.xlim((-50,50))
    plt.grid()
    
    # +
    defaults = dict(p=2, y_act=20)
    curves = [
        CPC.from_px(x=100, **defaults),
        CPC.from_px(x=50, **defaults),
        CPC.from_px(x=150, **defaults),
    ]
    for c in curves:
        plt.plot(dxr, [c.dyfromdx_f(dx) for dx in dxr])
    
    plt.ylim((-100,200))
    plt.xlim((-50,50))
    plt.grid()
    
    # +
    defaults = dict(p=2, x_act=10, y_act=20)
    curves = [
        CPC.from_px(x=100, **defaults),
        CPC.from_px(x=50, **defaults),
        CPC.from_px(x=150, **defaults),
    ]
    for c in curves:
        plt.plot(dxr, [c.dyfromdx_f(dx) for dx in dxr])
    
    plt.ylim((-100,200))
    plt.xlim((-50,50))
    plt.grid()
    
    # +
    defaults = dict(p=2, x_act=10, y_act=20)
    curves = [
        CPC.from_px(x=100, **defaults),
        CPC.from_px(x=50, **defaults),
        CPC.from_px(x=150, **defaults),
    ]
    for c in curves:
        plt.plot(dxr, [c.dyfromdx_f(dx) for dx in dxr])
    
    # plt.ylim((-100,200))
    # plt.xlim((-50,50))
    plt.grid()
    # -
    
    
    
    
    