import matplotlib.pyplot as plt
import numpy as np

from src.simulator import run_trials

inventory_skews = [
    0.0,
    0.0025,
    0.005,
    0.01,
    0.02,
    0.05,
]

results = []

for skew in inventory_skews:
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
        low_sigma=0.10,
        high_sigma=0.10,          # no volatility regime change
        half_spread=0.05,
        inventory_skew=skew,
        vol_sensitivity=0.0,      # no volatility adaptation
        informed_prob=0.0,        # no adverse selection
        transaction_cost=0.0,     # no fees
    )

    results.append({
        "skew": skew,
        "pnl_risk": np.mean(pnls) / np.std(pnls),
        "avg_pnl": np.mean(pnls),
        "max_inventory": np.mean(max_inventories),
    })


skews = [r["skew"] for r in results]
pnl_risk = [r["pnl_risk"] for r in results]

plt.figure(figsize=(8, 5))
plt.plot(skews, pnl_risk, marker="o")

plt.xlabel("Inventory Skew")
plt.ylabel("P&L / Risk")
plt.title("Effect of Inventory Control on Risk-Adjusted Performance")
plt.tight_layout()

plt.savefig(
    "results/figures/inventory_skew.png",
    dpi=300,
)

plt.show()