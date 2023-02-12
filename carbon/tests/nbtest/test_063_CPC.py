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
from carbon import ConstantProductCurve as CPC, CarbonOrderUI
plt.style.use('seaborn-dark')
plt.rcParams['figure.figsize'] = [12,6]
print("{0.__name__} v{0.__VERSION__} ({0.__DATE__})".format(CPC))
print("{0.__name__} v{0.__VERSION__} ({0.__DATE__})".format(CarbonOrderUI))
print_version(require="2.3.3")




# ------------------------------------------------------------
# Test      063
# File      test_063_CPC.py
# Segment   Assertions and testing
# ------------------------------------------------------------
def test_assertions_and_testing():
# ------------------------------------------------------------
    
    c = CPC.from_px(p=2000,x=10, pair="eth/usdc")
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
    
    