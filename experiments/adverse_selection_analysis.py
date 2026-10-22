import numpy as np
import matplotlib.pyplot as plt

from src.simulator import run_trials


informed_probs = [
    0.0,
    0.10,
    0.25,
    0.50,
    0.75,
    1.0,
]

results = []

for p in informed_probs:
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
        half_spread=0.05,
        inventory_skew=0.02,
        vol_sensitivity=0.25,
        informed_prob=p,
        information_strength=1.0,
        transaction_cost=0.0,
    )

    results.append({
        "informed_prob": p,
        "avg_pnl": np.mean(pnls),
    })


probs = [r["informed_prob"] for r in results]
avg_pnls = [r["avg_pnl"] for r in results]

plt.figure(figsize=(8, 5))
plt.plot(probs, avg_pnls, marker="o")

plt.axhline(y=0, linestyle="--")

plt.xlabel("Informed Trader Probability")
plt.ylabel("Average P&L")
plt.title("Effect of Adverse Selection on Market-Maker Profitability")
plt.tight_layout()

plt.savefig(
    "results/figures/adverse_selection.png",
    dpi=300,
)

plt.show()