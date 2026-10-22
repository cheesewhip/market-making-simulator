import pytest 

from src.simulator import simulate

def test_same_seed_produces_same_history():
    history1 = simulate(T=100, seed=42)
    history2 = simulate(T=100, seed=42)

    assert history1 == history2

def test_different_seeds_produce_different_histories():
    history1 = simulate(T=100, seed=42)
    history2 = simulate(T=100, seed=43)

    assert history1 != history2

def test_pnl_accounting_identity():
    history = simulate(T=100, seed=42)

    for step in history:
        expected_pnl = (
            step["cash"]
            + step["inventory"] * step["price"]
        )

        assert step["pnl"] == pytest.approx(expected_pnl)

def test_inventory_changes_match_trades():
    history = simulate(T=100, seed=42)

    previous_inventory = 0

    for step in history:
        if step["trade"] == "BUY":
            assert step["inventory"] == previous_inventory - 1

        elif step["trade"] == "SELL":
            assert step["inventory"] == previous_inventory + 1

        else:
            assert step["inventory"] == previous_inventory

        previous_inventory = step["inventory"]

def test_markout_calculation():
    history = simulate(T=100, seed=42)

    for step in history:
        if step["trade"] == "BUY":
            expected = step["ask"] - step["price"]
            assert step["markout"] == pytest.approx(expected)

        elif step["trade"] == "SELL":
            expected = step["price"] - step["bid"]
            assert step["markout"] == pytest.approx(expected)

        else:
            assert step["markout"] is None

