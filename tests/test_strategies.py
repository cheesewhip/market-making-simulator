import pytest

from src.strategies import compute_quotes


def test_zero_inventory_quotes_are_symmetric():
    reservation_price, current_half_spread, bid, ask = compute_quotes(
        price=100.0,
        inventory=0,
        current_sigma=0.05,
        low_sigma=0.05,
        half_spread=0.05,
        inventory_skew=0.02,
        vol_sensitivity=0.25,
    )

    assert reservation_price == pytest.approx(100.0)
    assert current_half_spread == pytest.approx(0.05)
    assert bid == pytest.approx(99.95)
    assert ask == pytest.approx(100.05)

def test_positive_inventory_lowers_quotes():
    reservation_price, _, bid, ask = compute_quotes(
        price=100.0,
        inventory=10,
        current_sigma=0.05,
        low_sigma=0.05,
        half_spread=0.05,
        inventory_skew=0.02,
        vol_sensitivity=0.0,
    )

    assert reservation_price == pytest.approx(99.8)
    assert bid == pytest.approx(99.75)
    assert ask == pytest.approx(99.85)

def test_negative_inventory_raises_quotes():
    reservation_price, _, bid, ask = compute_quotes(
        price=100.0,
        inventory=-10,
        current_sigma=0.05,
        low_sigma=0.05,
        half_spread=0.05,
        inventory_skew=0.02,
        vol_sensitivity=0.0,
    )

    assert reservation_price == pytest.approx(100.2)
    assert bid == pytest.approx(100.15)
    assert ask == pytest.approx(100.25)

def test_high_volatility_widens_spread():
    _, low_spread, _, _ = compute_quotes(
        price=100.0,
        inventory=0,
        current_sigma=0.05,
        low_sigma=0.05,
        half_spread=0.05,
        inventory_skew=0.02,
        vol_sensitivity=0.25,
    )

    _, high_spread, _, _ = compute_quotes(
        price=100.0,
        inventory=0,
        current_sigma=0.20,
        low_sigma=0.05,
        half_spread=0.05,
        inventory_skew=0.02,
        vol_sensitivity=0.25,
    )

    assert low_spread == pytest.approx(0.05)
    assert high_spread == pytest.approx(0.0875)

    assert high_spread > low_spread

