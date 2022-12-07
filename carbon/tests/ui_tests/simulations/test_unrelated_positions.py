from carbon import CarbonSimulatorUI


def test_unrelated_token_in_add_order():
    Sim = CarbonSimulatorUI(pair="ETH/USDC", verbose=False, raiseonerror=False)

    response = Sim.add_order("LINK", 100, 2000, 2000)
    assert response["success"] is False
    # assert (
    #     response["error"]
    #     == "('Invalid token specification (tkn not part of isopair)', 'ETHUSDC', 'LINK')"
    # )

    response = Sim.add_order("DNE", 100, 2000, 2000)
    assert response["success"] is False
    # assert (
    #     response["error"]
    #     == "('Invalid token specification (tkn not part of isopair)', 'ETHUSDC', 'DNE')"
    # )
