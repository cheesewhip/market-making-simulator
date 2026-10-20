import numpy as np
import matplotlib.pyplot as plt

def simulate(
        T = 1000,
        initial_price = 100.0,
        low_sigma = 0.05, 
        high_sigma = 0.20, 
        half_spread = 0.05,
        trader_sigma = 0.10,
        inventory_skew = 0.02,
        vol_sensitivity = 0.25,
        informed_prob = 0.2, 
        information_strength = 1.0, 
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
        reservation_price = price - inventory_skew * inventory

        current_half_spread = (
            half_spread
            + vol_sensitivity * (current_sigma - low_sigma)
        )

        bid = reservation_price - current_half_spread
        ask = reservation_price + current_half_spread

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
            inventory -= 1
            trade = "BUY"

        elif trader_value <= bid:
            # Trader sells to us
            cash -= bid
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
    num_trials = 1000,
    T = 1000,
    initial_price = 100.0,
    low_sigma = 0.05,
    high_sigma = 0.20, 
    trader_sigma = 0.10,
    half_spread = 0.05,
    inventory_skew = 0.02,
    vol_sensitivity = 0.25,
    informed_prob = 0.20, 
    information_strength = 1.0,
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
            T = T,
            initial_price = initial_price,
            low_sigma = low_sigma, 
            high_sigma = high_sigma,
            trader_sigma = trader_sigma,
            half_spread = half_spread,
            inventory_skew = inventory_skew,
            vol_sensitivity = vol_sensitivity,
            informed_prob = informed_prob, 
            information_strength = information_strength, 
            seed = seed,
        )

        midpoint = T // 2

        low_history = history[:midpoint]
        high_history = history[midpoint:]

        num_trades = sum(
            1 for step in history
            if step["trade"] != "NONE"
        )

        trade_counts.append(num_trades)
        
        max_abs_inventory = max(
        abs(step["inventory"]) for step in history
        )

        max_abs_inventories.append(max_abs_inventory)

        final = history[-1]

        low_end_pnl = low_history[-1]["pnl"]
        final_pnl = high_history[-1]["pnl"]

        low_pnl = low_end_pnl
        high_pnl = final_pnl - low_end_pnl

        low_regime_pnls.append(low_pnl)
        high_regime_pnls.append(high_pnl)

        low_trades = sum(1 for step in low_history if step["trade"] != "NONE")
        high_trades = sum(1 for step in high_history if step["trade"] != "NONE")

        low_regime_trades.append(low_trades)
        high_regime_trades.append(high_trades)

        final_pnls.append(final["pnl"])
        final_inventories.append(final["inventory"])

        for step in history:
            if step["markout"] is None:
                continue

            if step["is_informed"]:
                informed_markouts.append(step["markout"])
            else:
                uninformed_markouts.append(step["markout"])

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

informed_probs = [0.0, 0.1, 0.25, 0.5, 0.75]

half_spreads = [
    0.03,
    0.05,
    0.075,
    0.10,
    0.125,
    0.15,
    0.20,
]

for p in informed_probs:

    best_spread = None
    best_pnl = -np.inf

    print(f"\n===== Informed probability: {p} =====")

    for spread in half_spreads:

        (
            pnls,
            inventories,
            trade_counts,
            max_inventories,
            low_pnls,
            high_pnls,
            low_trades,
            high_trades,
            informed_markouts,
            uninformed_markouts,
        ) = run_trials(
            num_trials=1000,
            half_spread=spread,
            inventory_skew=0.02,
            vol_sensitivity=0.25,
            informed_prob=p,
            information_strength=1.0,
        )

        avg_pnl = np.mean(pnls)
        pnl_std = np.std(pnls)
        avg_trades = np.mean(trade_counts)

        print(f"\nHalf-spread: {spread}")
        print("Average P&L:", avg_pnl)
        print("P&L std:", pnl_std)
        print("Average trades:", avg_trades)
        print("P&L / risk:", avg_pnl / pnl_std)

        if avg_pnl > best_pnl:
            best_pnl = avg_pnl
            best_spread = spread

    print(
        f"\nBest spread for informed probability {p}: "
        f"{best_spread} with average P&L {best_pnl}"
    )