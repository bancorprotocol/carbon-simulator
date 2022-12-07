from carbon import CarbonSimulatorUI
import pandas as pd


def test_liquidity_as_dataframe():
    """
    Derived from `passed_tests` notebook test-34
    """
    Sim = CarbonSimulatorUI(verbose=True)
    Sim.add_order("ETH", 10, 2000, 3000, "ETH/USDC")
    Sim.add_order("ETH", 20, 2010, 3010, "ETH/USDC")
    Sim.add_order("ETH", 30, 2020, 3020, "ETH/USDC")
    Sim.add_order("ETH", 40, 2030, 2030, "ETH/USDC")
    Sim.add_strategy("ETH", 10, 2000, 3000, 5000, 1000, 900, "ETH/USDC")
    Sim.add_strategy("ETH", 20, 2010, 3010, 5100, 1010, 910, "ETH/USDC")
    Sim.add_strategy("ETH", 30, 2020, 3020, 5200, 1020, 920, "ETH/USDC")
    Sim.add_strategy("ETH", 40, 2030, 3030, 5300, 1030, 930, "ETH/USDC")
    Sim.add_order("ETH", 10, 2000, 3000, "ETH/DAI")
    Sim.add_order("ETH", 20, 2010, 3010, "ETH/DAI")
    Sim.add_order("ETH", 30, 2020, 3020, "ETH/DAI")
    Sim.add_order("ETH", 40, 2030, 2030, "ETH/DAI")
    Sim.add_strategy("ETH", 10, 2000, 3000, 5000, 1000, 900, "ETH/DAI")
    Sim.add_strategy("ETH", 20, 2010, 3010, 5100, 1010, 910, "ETH/DAI")
    Sim.add_strategy("ETH", 30, 2020, 3020, 5200, 1020, 920, "ETH/DAI")
    Sim.add_strategy("ETH", 40, 2030, 3030, 5300, 1030, 930, "ETH/DAI")
    Sim.add_order("ETH", 10, 3000, 2000, pair="ETH/USDC")

    df = Sim.liquidity(Sim.ASDF)
    dct = df.to_dict(orient="dict")["y"]
    assert isinstance(df, pd.DataFrame)
    assert dct == {
        ("ETHDAI", "DAI"): 20600.0,
        ("ETHDAI", "ETH"): 200.0,
        ("ETHUSDC", "ETH"): 210.0,
        ("ETHUSDC", "USDC"): 20600.0,
    }

    pairs = set(k[0] for k in dct)
    assert pairs == {"ETHDAI", "ETHUSDC"}
    assert {p: {k[1]: 1 for k in dct if k[0] == p} for p in pairs} == {
        "ETHUSDC": {"ETH": 1, "USDC": 1},
        "ETHDAI": {"DAI": 1, "ETH": 1},
    }


def test_liquidity_as_dict():
    """
    Derived from `passed_tests` notebook test-34
    """
    Sim = CarbonSimulatorUI(verbose=True)
    Sim.add_order("ETH", 10, 2000, 3000, "ETH/USDC")
    Sim.add_order("ETH", 20, 2010, 3010, "ETH/USDC")
    Sim.add_order("ETH", 30, 2020, 3020, "ETH/USDC")
    Sim.add_order("ETH", 40, 2030, 2030, "ETH/USDC")
    Sim.add_strategy("ETH", 10, 2000, 3000, 5000, 1000, 900, "ETH/USDC")
    Sim.add_strategy("ETH", 20, 2010, 3010, 5100, 1010, 910, "ETH/USDC")
    Sim.add_strategy("ETH", 30, 2020, 3020, 5200, 1020, 920, "ETH/USDC")
    Sim.add_strategy("ETH", 40, 2030, 3030, 5300, 1030, 930, "ETH/USDC")
    Sim.add_order("ETH", 10, 2000, 3000, "ETH/DAI")
    Sim.add_order("ETH", 20, 2010, 3010, "ETH/DAI")
    Sim.add_order("ETH", 30, 2020, 3020, "ETH/DAI")
    Sim.add_order("ETH", 40, 2030, 2030, "ETH/DAI")
    Sim.add_strategy("ETH", 10, 2000, 3000, 5000, 1000, 900, "ETH/DAI")
    Sim.add_strategy("ETH", 20, 2010, 3010, 5100, 1010, 910, "ETH/DAI")
    Sim.add_strategy("ETH", 30, 2020, 3020, 5200, 1020, 920, "ETH/DAI")
    Sim.add_strategy("ETH", 40, 2030, 3030, 5300, 1030, 930, "ETH/DAI")
    Sim.add_order("ETH", 10, 3000, 2000, pair="ETH/USDC")

    dic = Sim.liquidity(Sim.ASDICT)
    assert isinstance(dic, dict)
    assert dic == {
        "ETHDAI": {"DAI": 20600.0, "ETH": 200.0},
        "ETHUSDC": {"ETH": 210.0, "USDC": 20600.0},
    }
