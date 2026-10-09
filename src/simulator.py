import numpy as np
import matplotlib.pyplot as plt

def simulate(
        T = 1000,
        initial_price = 100.0,
        sigma = 0.10, 
        half_spread = 0.05,
        trader_sigma = 0.10,
        inventory_skew = 0.01,
        seed = None,
):
    rng = np.random.default_rng(seed)

    price = initial_price
    cash = 0.0
    inventory = 0

    history = []

    for t in range(T):
        # 1. Move fair price
        price += rng.normal(0, sigma)
        
        # 2. Set our quotes
        reservation_price = price - inventory_skew * inventory

        bid = reservation_price - half_spread
        ask = reservation_price + half_spread

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
            "reservation_price": reservation_price
        })

    return history

def run_trials(
    num_trials=1000,
    T=1000,
    initial_price=100.0,
    sigma=0.10,
    trader_sigma = 0.10,
    half_spread=0.05,
    inventory_skew = 0.01
):
    final_pnls = []
    final_inventories = []
    trade_counts = []
    max_abs_inventories = []

    for seed in range(num_trials):
        history = simulate(
            T=T,
            initial_price=initial_price,
            sigma=sigma,
            trader_sigma = trader_sigma,
            half_spread=half_spread,
            inventory_skew = inventory_skew,
            seed=seed,
        )

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

        final_pnls.append(final["pnl"])
        final_inventories.append(final["inventory"])

    return final_pnls, final_inventories, trade_counts, max_abs_inventories

pnls, inventories, trade_counts, max_inventories = run_trials(num_trials=1000)

inventory_skews = [0.0, 0.0025, 0.005, 0.01, 0.02, 0.05]

for skew in inventory_skews:
    pnls, inventories, trade_counts, max_inventories = run_trials(
        num_trials=1000,
        inventory_skew=skew,
    )

    print(f"\nInventory skew: {skew}")
    print("Average P&L:", np.mean(pnls))
    print("P&L std:", np.std(pnls))
    print("Inventory std:", np.std(inventories))
    print("Average max |inventory|:", np.mean(max_inventories))
    print("Average trades:", np.mean(trade_counts))
    print("P&L / risk:", np.mean(pnls) / np.std(pnls))