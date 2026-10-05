import numpy as np
import matplotlib.pyplot as plt

def simulate(
        T = 1000,
        initial_price = 100.0,
        sigma = 0.10, 
        half_spread = 0.05,
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
        bid = price - half_spread
        ask = price + half_spread

        # 3. Randomly generate a buyer/seller
        trader_buys = rng.random() < 0.5

        # 4. Execute the trade
        if trader_buys: 
            # Trader buys from us, so we sell at the ask
            cash += ask
            inventory -= 1
        else: 
            # Trader sells to us, so we buy at the bid
            cash -= bid
            inventory += 1

        # 5. Mark our position to market
        pnl = cash + inventory * price

        # 6. Save this timestep
        history.append({
            "time": t, 
            "price": price, 
            "bid": bid, 
            "ask": ask, 
            "cash": cash, 
            "inventory": inventory, 
            "pnl": pnl,
        })

    return history

def run_trials(
    num_trials=1000,
    T=1000,
    initial_price=100.0,
    sigma=0.10,
    half_spread=0.05,
):
    final_pnls = []
    final_inventories = []

    for seed in range(num_trials):
        history = simulate(
            T=T,
            initial_price=initial_price,
            sigma=sigma,
            half_spread=half_spread,
            seed=seed,
        )

        final = history[-1]

        final_pnls.append(final["pnl"])
        final_inventories.append(final["inventory"])

    return final_pnls, final_inventories

pnls, inventories = run_trials(num_trials=1000)

print("Average P&L:", np.mean(pnls))
print("P&L standard deviation:", np.std(pnls))
print("Minimum P&L:", np.min(pnls))
print("Maximum P&L:", np.max(pnls))

print("Average final inventory:", np.mean(inventories))
print("Inventory standard deviation:", np.std(inventories))