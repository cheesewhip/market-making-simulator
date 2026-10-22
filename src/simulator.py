import numpy as np

from src.strategies import compute_quotes
from src.metrics import (
    count_trades,
    max_abs_inventory,
    final_pnl,
    final_inventory,
    regime_pnls,
    regime_trade_counts,
    collect_markouts,
)

def simulate(
        T = 1000,
        initial_price = 100.0,
        low_sigma = 0.05, 
        high_sigma = 0.20, 
        half_spread = 0.05,
        trader_sigma = 0.10,
        inventory_skew = 0.02,
        vol_sensitivity = 0.25,
        informed_prob = 0.25, 
        information_strength = 1.0, 
        transaction_cost = 0.0025,
        seed = None,
):
    rng = np.random.default_rng(seed)

    price = initial_price
    cash = 0.0
    inventory = 0

    history = []

    for t in range(T):
        # 1. Determine current volatility regime
        if t < T // 2:
            current_sigma = low_sigma
        else:
            current_sigma = high_sigma

        # 2. Market maker posts quotes using CURRENT information
        (   reservation_price,
            current_half_spread,
            bid,
            ask,
        ) = compute_quotes(
            price = price,
            inventory = inventory,
            current_sigma = current_sigma,
            low_sigma = low_sigma,
            half_spread = half_spread,
            inventory_skew = inventory_skew,
            vol_sensitivity = vol_sensitivity,
        )

        # 3. Generate the NEXT price movement
        next_price_change = rng.normal(0, current_sigma)

        # 4. Determine whether trader is informed
        is_informed = rng.random() < informed_prob

        trader_noise = rng.normal(0, trader_sigma)

        if is_informed:
            trader_value = (
                price
                + information_strength * next_price_change
                + trader_noise
            )
        else:
            trader_value = price + trader_noise

        # 5. Trader decides whether to trade
        trade = "NONE"

        if trader_value >= ask:
            # Trader buys from us
            cash += ask
            cash -= transaction_cost
            inventory -= 1
            trade = "BUY"

        elif trader_value <= bid:
            # Trader sells to us
            cash -= bid
            cash -= transaction_cost
            inventory += 1
            trade = "SELL"

        # 6. Now the price actually moves
        price += next_price_change

        if trade == "BUY":
            markout = ask - price

        elif trade == "SELL":
            markout = price - bid

        else:
            markout = None

        # 7. Mark inventory to market
        pnl = cash + inventory * price

        # 8. Record results
        history.append({
            "time": t,
            "price": price,
            "bid": bid,
            "ask": ask,
            "trader_value": trader_value,
            "trade": trade,
            "cash": cash,
            "inventory": inventory,
            "pnl": pnl,
            "reservation_price": reservation_price,
            "sigma": current_sigma,
            "half_spread": current_half_spread,
            "is_informed": is_informed,
            "next_price_change": next_price_change,
            "markout": markout,
        })

    return history

def run_trials(
    num_trials=1000,
    T=1000,
    initial_price=100.0,
    low_sigma=0.05,
    high_sigma=0.20,
    trader_sigma=0.10,
    half_spread=0.10,
    inventory_skew=0.02,
    vol_sensitivity=0.25,
    informed_prob=0.25,
    information_strength=1.0,
    transaction_cost=0.0025,
):
    final_pnls = []
    final_inventories = []
    trade_counts = []
    max_abs_inventories = []

    low_regime_pnls = []
    high_regime_pnls = []

    low_regime_trades = []
    high_regime_trades = []

    informed_markouts = []
    uninformed_markouts = []

    for seed in range(num_trials):
        history = simulate(
            T=T,
            initial_price=initial_price,
            low_sigma=low_sigma,
            high_sigma=high_sigma,
            trader_sigma=trader_sigma,
            half_spread=half_spread,
            inventory_skew=inventory_skew,
            vol_sensitivity=vol_sensitivity,
            informed_prob=informed_prob,
            information_strength=information_strength,
            transaction_cost=transaction_cost,
            seed=seed,
        )

        # Overall metrics
        final_pnls.append(final_pnl(history))
        final_inventories.append(final_inventory(history))
        trade_counts.append(count_trades(history))
        max_abs_inventories.append(max_abs_inventory(history))

        # Volatility-regime metrics
        low_pnl, high_pnl = regime_pnls(history)
        low_regime_pnls.append(low_pnl)
        high_regime_pnls.append(high_pnl)

        low_trades, high_trades = regime_trade_counts(history)
        low_regime_trades.append(low_trades)
        high_regime_trades.append(high_trades)

        # Adverse-selection metrics
        informed, uninformed = collect_markouts(history)
        informed_markouts.extend(informed)
        uninformed_markouts.extend(uninformed)

    return (
        final_pnls,
        final_inventories,
        trade_counts,
        max_abs_inventories,
        low_regime_pnls,
        high_regime_pnls,
        low_regime_trades,
        high_regime_trades,
        informed_markouts,
        uninformed_markouts,
    )