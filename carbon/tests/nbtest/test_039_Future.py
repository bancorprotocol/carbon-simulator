# ------------------------------------------------------------
# Auto generated test file `test_039_Future.py`
# ------------------------------------------------------------
# source file   = NBTest_039_Future.py
# source path   = /Users/skl/REPOES/Bancor/CarbonSimulator/resources/NBTest/
# target path   = /Users/skl/REPOES/Bancor/CarbonSimulator/resources/NBTest/
# test id       = 039
# test comment  = Future
# ------------------------------------------------------------



from carbon import CarbonSimulatorUI, P, __version__, __date__
print(f"Carbon v{__version__} ({__date__})")
print("{0.__name__} v{0.__VERSION__} ({0.__DATE__})".format(CarbonSimulatorUI))





# ------------------------------------------------------------
# Test      039
# File      test_039_Future.py
# Segment   Future
# ------------------------------------------------------------
def test_future():
# ------------------------------------------------------------
    
    # +
    #help(CarbonSimulatorUI)
    # -
    
    Sim = CarbonSimulatorUI()
    SimXF = CarbonSimulatorUI(exclude_future=True)
    SimIF = CarbonSimulatorUI(exclude_future=False)
    
    assert(Sim.exclude_future==True)
    assert(SimXF.exclude_future==True)
    assert(SimIF.exclude_future==False)
    
    try:
        Sim._raise_if_future_restricted()
    except Sim.ExcludedFutureFunctionality as e:
        print(e)
        assert(str(e)=="Feature disabled (us `exclude_future = False` to enable)")
    
    try:
        SimXF._raise_if_future_restricted()
    except Sim.ExcludedFutureFunctionality as e:
        print(e)
        assert(str(e)=="Feature disabled (us `exclude_future = False` to enable)")
    
    assert(SimIF._raise_if_future_restricted()==None)
    
    