import matplotlib.pyplot as plt
import numpy as np

from src.simulator import run_trials

vol_sensitivities = [
    0.0,
    0.1,
    0.25,
    0.5,
    0.75,
    1.0,
]

results = []

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
        informed_markouts,
        uninformed_markouts,
    ) = run_trials(
        num_trials=1000,
        low_sigma=0.05,
        high_sigma=0.20,
        half_spread=0.05,
        inventory_skew=0.02,
        vol_sensitivity=beta,
        informed_prob=0.0,
        transaction_cost=0.0,
    )

    results.append({
        "beta": beta,
        "high_pnl": np.mean(high_pnls),
        "high_trades": np.mean(high_trades),
    })


betas = [r["beta"] for r in results]
high_pnls = [r["high_pnl"] for r in results]

plt.figure(figsize=(8, 5))
plt.plot(betas, high_pnls, marker="o")

plt.xlabel("Volatility Sensitivity")
plt.ylabel("High-Volatility Average P&L")
plt.title("Effect of Volatility-Sensitive Quoting")
plt.tight_layout()

plt.savefig(
    "results/figures/volatility_sensitivity.png",
    dpi=300,
)

plt.show()