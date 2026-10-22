def count_trades(history):
    return sum(
        1
        for step in history
        if step["trade"] != "NONE"
    )


def max_abs_inventory(history):
    return max(
        abs(step["inventory"])
        for step in history
    )


def final_pnl(history):
    return history[-1]["pnl"]


def final_inventory(history):
    return history[-1]["inventory"]


def regime_pnls(history):
    midpoint = len(history) // 2

    low_end_pnl = history[midpoint - 1]["pnl"]
    final_pnl_value = history[-1]["pnl"]

    low_pnl = low_end_pnl
    high_pnl = final_pnl_value - low_end_pnl

    return low_pnl, high_pnl


def regime_trade_counts(history):
    midpoint = len(history) // 2

    low_history = history[:midpoint]
    high_history = history[midpoint:]

    low_trades = count_trades(low_history)
    high_trades = count_trades(high_history)

    return low_trades, high_trades


def collect_markouts(history):
    informed = []
    uninformed = []

    for step in history:
        markout = step["markout"]

        if markout is None:
            continue

        if step["is_informed"]:
            informed.append(markout)
        else:
            uninformed.append(markout)

    return informed, uninformed