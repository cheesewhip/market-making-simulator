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

    print(f"\n===== {strategy['name']} =====")
    print("Average P&L:", np.mean(pnls))
    print("P&L std:", np.std(pnls))
    print("P&L / risk:", np.mean(pnls) / np.std(pnls))
    print("Average trades:", np.mean(trade_counts))
    print("Average max |inventory|:", np.mean(max_inventories))

    if informed_markouts:
        print(
            "Average informed markout:",
            np.mean(informed_markouts),
        )

    if uninformed_markouts:
        print(
            "Average uninformed markout:",
            np.mean(uninformed_markouts),
        )