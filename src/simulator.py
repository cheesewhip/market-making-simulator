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
        seed = None,
):
    rng = np.random.default_rng(seed)

    price = initial_price
    cash = 0.0
    inventory = 0

    history = []

    for t in range(T):
        # 1. Move fair price
        if t < T // 2:
            current_sigma = low_sigma
        else:
            current_sigma = high_sigma

        price += rng.normal(0, current_sigma)
        
        # 2. Set our quotes
        reservation_price = price - inventory_skew * inventory

        current_half_spread = half_spread + vol_sensitivity * (current_sigma - low_sigma)
        bid = reservation_price - current_half_spread
        ask = reservation_price + current_half_spread

        # 3. Generate the trader's private valuation
        trader_value = price + rng.normal(0, trader_sigma)

        # 4. Execute a trade only if our quote is attractive
        trade = "NONE"

        if trader_value >= ask: 
            # Trader values the stock above our ask, so they buy from us
            cash += ask
            inventory -= 1
            trade = "BUY"

        elif trader_value <= bid: 
            # Trader values the stock below our bid, so they sell to us
            cash -= bid
            inventory += 1
            trade = "SELL"

        # 5. Mark our position to market
        pnl = cash + inventory * price

        # 6. Save this timestep
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
            "half_spread": current_half_spread,
            "sigma": current_sigma,
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
):
    final_pnls = []
    final_inventories = []
    trade_counts = []
    max_abs_inventories = []

    low_regime_pnls = []
    high_regime_pnls = []

    low_regime_trades = []
    high_regime_trades = []

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

    return (final_pnls, final_inventories, trade_counts, max_abs_inventories, 
            low_regime_pnls,high_regime_pnls, low_regime_trades, high_regime_trades)

# Run Monte Carlo trials
vol_sensitivities = [0.0, 0.1, 0.25, 0.5, 0.75, 1.0]

for beta in vol_sensitivities:
    (
        pnls,
        inventories,
        trade_counts,
        max_inventories,
        low_pnls,
        high_pnls,
        low_trades,
        high_trades,
    ) = run_trials(
        num_trials=1000,
        inventory_skew=0.02,
        vol_sensitivity=beta,
    )

    print(f"\nVol sensitivity: {beta}")
    print("Total average P&L:", np.mean(pnls))
    print("Low-vol average P&L:", np.mean(low_pnls))
    print("High-vol average P&L:", np.mean(high_pnls))

    print("Low-vol trades:", np.mean(low_trades))
    print("High-vol trades:", np.mean(high_trades))

    print("P&L std:", np.std(pnls))
    print("Average max |inventory|:", np.mean(max_inventories))
    print("P&L / risk:", np.mean(pnls) / np.std(pnls))
