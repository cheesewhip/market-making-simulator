def compute_quotes(
    price,
    inventory,
    current_sigma,
    low_sigma,
    half_spread,
    inventory_skew,
    vol_sensitivity,
):
    """
    Compute the market maker's reservation price, bid, and ask.

    Inventory skew shifts quotes to encourage inventory reduction.
    Volatility sensitivity widens the spread in high-volatility regimes.
    """

    reservation_price = (
        price - inventory_skew * inventory
    )

    current_half_spread = (
        half_spread
        + vol_sensitivity * (current_sigma - low_sigma)
    )

    bid = reservation_price - current_half_spread
    ask = reservation_price + current_half_spread

    return (
        reservation_price,
        current_half_spread,
        bid,
        ask,
    )