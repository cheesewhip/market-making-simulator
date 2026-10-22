import matplotlib.pyplot as plt
import numpy as np

from src.simulator import run_trials

strategies = [
    {
        "name": "Naive baseline",
        "inventory_skew": 0.0,
        "vol_sensitivity": 0.0,
        "half_spread": 0.05,
    },
    {
        "name": "Inventory-aware",
        "inventory_skew": 0.02,
        "vol_sensitivity": 0.0,
        "half_spread": 0.05,
    },
    {
        "name": "Inventory + volatility",
        "inventory_skew": 0.02,
        "vol_sensitivity": 0.25,
        "half_spread": 0.05,
    },
    {
        "name": "Fully risk-aware",
        "inventory_skew": 0.02,
        "vol_sensitivity": 0.25,
        "half_spread": 0.10,
    },
]

results = []

for strategy in strategies:
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
        low_sigma=0.05,
        high_sigma=0.20,
        trader_sigma=0.10,
        inventory_skew=strategy["inventory_skew"],
        vol_sensitivity=strategy["vol_sensitivity"],
        half_spread=strategy["half_spread"],
        informed_prob=0.25,
        information_strength=1.0,
        transaction_cost=0.0025,
    )

    results.append({
        "name": strategy["name"],
        "avg_pnl": np.mean(pnls),
        "pnl_std": np.std(pnls),
        "pnl_risk": np.mean(pnls) / np.std(pnls),
        "avg_trades": np.mean(trade_counts),
        "max_inventory": np.mean(max_inventories),
    })

names = [result["name"] for result in results]
pnl_risk = [result["pnl_risk"] for result in results]

plt.figure(figsize=(9, 5))
plt.bar(names, pnl_risk)

plt.ylabel("P&L / Risk")
plt.title("Risk-Adjusted Performance by Market-Making Strategy")
plt.xticks(rotation=15)
plt.tight_layout()

plt.savefig(
    "results/figures/final_strategy_comparison.png",
    dpi=300,
)

plt.show()

print("\nFinal Strategy Comparison")
print(
    f"{'Strategy':<25}"
    f"{'Avg P&L':>12}"
    f"{'P&L Std':>12}"
    f"{'P&L/Risk':>12}"
    f"{'Trades':>12}"
    f"{'Max |Inv|':>12}"
)

for result in results:
    print(
        f"{result['name']:<25}"
        f"{result['avg_pnl']:>12.2f}"
        f"{result['pnl_std']:>12.2f}"
        f"{result['pnl_risk']:>12.2f}"
        f"{result['avg_trades']:>12.1f}"
        f"{result['max_inventory']:>12.2f}"
    )