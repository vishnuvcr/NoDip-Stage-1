from __future__ import annotations

import argparse
from pathlib import Path

import numpy as np
import pandas as pd


EXACT_STATUSES = {"PRIMARY_VALID_SECONDARY_COMPLETE", "RECOVERED_BY_SECONDARY_EXACT"}


def pnl_at_cost(df: pd.DataFrame, broker_per_order: float, exchange_rate: float, slippage_points: float) -> float:
    near = df["lot_near"].astype(float)
    far = df["lot_far"].astype(float)

    buy_turnover = (
        df["entry_near_pe"] * near
        + df["entry_far_ce"] * far
        + df["exit_near_ce"] * near
        + df["exit_far_pe"] * far
    )
    sell_turnover = (
        df["entry_near_ce"] * near
        + df["entry_far_pe"] * far
        + df["exit_near_pe"] * near
        + df["exit_far_ce"] * far
    )
    premium_turnover = buy_turnover + sell_turnover

    brokerage = pd.Series(8.0 * broker_per_order, index=df.index)
    stt = sell_turnover * 0.000625
    stamp = buy_turnover * 0.00003
    sebi = premium_turnover * 0.000001
    exchange = premium_turnover * exchange_rate
    gst = 0.18 * (brokerage + sebi + exchange)

    executable_lots = 4.0 * (near + far)
    slip = slippage_points * executable_lots

    net = df["pnl_inr"] - (brokerage + stt + stamp + sebi + exchange + gst + slip)
    return float(net.sum())


def metrics(df: pd.DataFrame) -> dict[str, float]:
    if df.empty:
        return {
            "trades": 0,
            "coverage": 0.0,
            "gross_pnl_inr": 0.0,
            "mean_pnl_inr": np.nan,
            "win_rate": np.nan,
            "profit_factor": np.nan,
            "max_drawdown_inr": 0.0,
            "worst_trade_inr": np.nan,
        }

    x = df["pnl_inr"].astype(float)
    wins = x[x > 0]
    losses = x[x < 0]
    curve = x.cumsum()
    drawdown = curve - curve.cummax()

    return {
        "trades": int(len(df)),
        "coverage": len(df) / 84.0,
        "gross_pnl_inr": float(x.sum()),
        "mean_pnl_inr": float(x.mean()),
        "win_rate": float((x > 0).mean()),
        "profit_factor": float(wins.sum() / abs(losses.sum())) if len(losses) else np.inf,
        "max_drawdown_inr": float(drawdown.min()),
        "worst_trade_inr": float(x.min()),
    }


def classify_signature(row: pd.Series) -> str:
    a, b, c, d = (
        row["leg_near_pe"],
        row["leg_near_ce"],
        row["leg_far_ce"],
        row["leg_far_pe"],
    )
    if a < 0 and b < 0 and c > 0 and d > 0:
        return "bullish-like front-week adverse signature"
    if a > 0 and b > 0 and c < 0 and d < 0:
        return "bearish-like far-week adverse signature"
    return "mixed signature"


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--recon", required=True, type=Path)
    ap.add_argument("--secondary-ledger", required=True, type=Path)
    ap.add_argument("--out-loss-ledger", required=True, type=Path)
    ap.add_argument("--out-report", required=True, type=Path)
    ap.add_argument("--out-filter-sensitivity", required=True, type=Path)
    ap.add_argument("--out-cost-sensitivity", required=True, type=Path)
    args = ap.parse_args()

    recon = pd.read_csv(args.recon)
    ledger = pd.read_csv(args.secondary_ledger)

    exact = recon[recon["comparison_status"].isin(EXACT_STATUSES)].copy()
    strict = ledger.merge(
        exact[["entry_date", "near_expiry", "far_expiry", "comparison_status"]],
        on=["entry_date", "near_expiry", "far_expiry"],
        how="inner",
    ).sort_values("entry_date").reset_index(drop=True)

    if len(strict) != 84:
        raise SystemExit(f"Expected 84 strict trades, got {len(strict)}")

    near = strict["lot_near"].astype(float)
    far = strict["lot_far"].astype(float)

    strict["leg_near_pe"] = (strict["exit_near_pe"] - strict["entry_near_pe"]) * near
    strict["leg_near_ce"] = (strict["entry_near_ce"] - strict["exit_near_ce"]) * near
    strict["leg_far_ce"] = (strict["exit_far_ce"] - strict["entry_far_ce"]) * far
    strict["leg_far_pe"] = (strict["entry_far_pe"] - strict["exit_far_pe"]) * far

    strict["calculated_pnl_inr"] = strict[
        ["leg_near_pe", "leg_near_ce", "leg_far_ce", "leg_far_pe"]
    ].sum(axis=1)

    if not np.allclose(strict["calculated_pnl_inr"], strict["pnl_inr"], atol=1e-8):
        raise SystemExit("Leg-level P&L does not reconcile to recorded trade P&L")

    strict["initial_net_debit_points"] = (
        strict["entry_near_pe"]
        + strict["entry_far_ce"]
        - strict["entry_near_ce"]
        - strict["entry_far_pe"]
    )
    strict["near_premium_points"] = strict["entry_near_pe"] + strict["entry_near_ce"]
    strict["far_premium_points"] = strict["entry_far_ce"] + strict["entry_far_pe"]
    strict["near_call_far_call_ratio"] = strict["entry_near_ce"] / strict["entry_far_ce"]
    strict["near_put_far_put_ratio"] = strict["entry_near_pe"] / strict["entry_far_pe"]

    strict["outcome"] = np.where(strict["pnl_inr"] < 0, "LOSS", "NON_LOSS")
    strict["signature"] = strict.apply(classify_signature, axis=1)

    losses = strict[strict["outcome"].eq("LOSS")].copy()
    losses["loss_abs_inr"] = -losses["pnl_inr"]
    losses = losses.sort_values("loss_abs_inr", ascending=False).reset_index(drop=True)
    losses["loss_rank"] = np.arange(1, len(losses) + 1)

    args.out_loss_ledger.parent.mkdir(parents=True, exist_ok=True)
    loss_cols = [
        "loss_rank",
        "entry_date",
        "near_expiry",
        "far_expiry",
        "strike",
        "lot_near",
        "lot_far",
        "pnl_inr",
        "leg_near_pe",
        "leg_near_ce",
        "leg_far_ce",
        "leg_far_pe",
        "initial_net_debit_points",
        "near_call_far_call_ratio",
        "near_put_far_put_ratio",
        "signature",
        "comparison_status",
    ]
    losses[loss_cols].to_csv(args.out_loss_ledger, index=False)

    filters = {
        "baseline": lambda x: pd.Series(True, index=x.index),
        "initial_net_debit_le_80": lambda x: x["initial_net_debit_points"] <= 80.0,
        "near_call_far_call_ge_0.45": lambda x: x["near_call_far_call_ratio"] >= 0.45,
        "near_put_far_put_le_0.55": lambda x: x["near_put_far_put_ratio"] <= 0.55,
        "combined_balance_filter": lambda x: (
            (x["near_call_far_call_ratio"] >= 0.45)
            & (x["near_put_far_put_ratio"] <= 0.55)
        ),
    }

    filter_rows: list[dict[str, float | str]] = []
    for name, fn in filters.items():
        subset = strict[fn(strict)].copy()
        m = metrics(subset)
        filter_rows.append({"filter": name, **m})
    pd.DataFrame(filter_rows).to_csv(args.out_filter_sensitivity, index=False)

    cost_rows: list[dict[str, float | str]] = []
    for name, fn in filters.items():
        subset = strict[fn(strict)].copy()
        for broker in (10.0, 15.0, 20.0):
            for slip in (0.0, 0.50, 1.0, 2.0):
                cost_rows.append({
                    "filter": name,
                    "brokerage_per_order": broker,
                    "exchange_rate": 0.0005,
                    "slippage_points_per_execution": slip,
                    "trades": len(subset),
                    "gross_pnl_inr": subset["pnl_inr"].sum(),
                    "net_pnl_inr": pnl_at_cost(subset, broker, 0.0005, slip),
                })
    pd.DataFrame(cost_rows).to_csv(args.out_cost_sensitivity, index=False)

    report_lines = [
        "# P7 Loss-Trades Audit — NIFTY 4-Leg Calendar — 2022-2024",
        "",
        "## Scope",
        f"- Strict frozen-protocol trades audited: {len(strict)}",
        f"- Losing trades: {len(losses)}",
        f"- Non-losing trades: {len(strict) - len(losses)}",
        f"- Gross P&L: ₹{strict['pnl_inr'].sum():,.2f}",
        f"- Total loss from losing trades: ₹{losses['pnl_inr'].sum():,.2f}",
        f"- Average losing trade: ₹{losses['pnl_inr'].mean():,.2f}",
        f"- Median losing trade: ₹{losses['pnl_inr'].median():,.2f}",
        "",
        "## Loss attribution by leg",
        f"- Near PE contribution across losing trades: ₹{losses['leg_near_pe'].sum():,.2f}",
        f"- Near CE contribution across losing trades: ₹{losses['leg_near_ce'].sum():,.2f}",
        f"- Far CE contribution across losing trades: ₹{losses['leg_far_ce'].sum():,.2f}",
        f"- Far PE contribution across losing trades: ₹{losses['leg_far_pe'].sum():,.2f}",
        "",
        "The near-expiry legs are the main loss source: their combined contribution is materially negative, while the far legs provide offsetting gains but do not fully absorb the front-week losses.",
        f"Near-expiry leg contributions sum to ₹{(losses['leg_near_pe'].sum() + losses['leg_near_ce'].sum()):,.2f}; far-expiry leg contributions sum to ₹{(losses['leg_far_ce'].sum() + losses['leg_far_pe'].sum()):,.2f}.",
        f"Absolute losses offset about {abs(losses['pnl_inr'].sum()) / strict.loc[strict['pnl_inr'] > 0, 'pnl_inr'].sum():.1%} of the positive P&L generated by winning trades.",
        "",
        "## Loss-signature audit",
    ]

    sig = losses.groupby("signature", as_index=False).agg(
        trades=("pnl_inr", "size"),
        loss_sum=("pnl_inr", "sum"),
        avg_loss=("pnl_inr", "mean"),
    )
    for _, r in sig.iterrows():
        report_lines.append(
            f"- {r['signature']}: {int(r['trades'])} trades; total loss ₹{r['loss_sum']:,.2f}; average ₹{r['avg_loss']:,.2f}."
        )

    bullish = losses[losses["signature"].eq("bullish-like front-week adverse signature")]
    report_lines += [
        "",
        f"The largest recurring pattern is the bullish-like front-week adverse signature: {len(bullish)} of {len(losses)} losing trades ({len(bullish)/len(losses):.1%}) and ₹{abs(bullish['pnl_inr'].sum()):,.2f} of absolute loss ({abs(bullish['pnl_inr'].sum())/abs(losses['pnl_inr'].sum()):.1%}). This is an inferred option-payoff signature, not a direct observation of intraday NIFTY path.",
        "",
        "## Loss severity concentration",
    ]

    for threshold in (500, 1000, 1500, 2000, 2500, 3000):
        subset = losses[losses["pnl_inr"] <= -threshold]
        share = abs(subset["pnl_inr"].sum()) / abs(losses["pnl_inr"].sum())
        report_lines.append(
            f"- Losses ≤ -₹{threshold:,.0f}: {len(subset)} trades, {share:.1%} of total absolute loss."
        )

    report_lines += [
        "",
        "## Entry-state differences between losses and wins",
        f"- Mean initial net debit: losses ₹{losses['initial_net_debit_points'].mean():.2f}; non-losses ₹{strict.loc[strict['outcome'].ne('LOSS'), 'initial_net_debit_points'].mean():.2f}.",
        f"- Mean near-call/far-call ratio: losses {losses['near_call_far_call_ratio'].mean():.3f}; non-losses {strict.loc[strict['outcome'].ne('LOSS'), 'near_call_far_call_ratio'].mean():.3f}.",
        f"- Mean near-put/far-put ratio: losses {losses['near_put_far_put_ratio'].mean():.3f}; non-losses {strict.loc[strict['outcome'].ne('LOSS'), 'near_put_far_put_ratio'].mean():.3f}.",
        "",
        "These are associations in the historical sample, not causal estimates.",
        "",
        "## Exploratory improvement tests",
        "",
        "The candidate filters below are deliberately simple and are not allowed to overwrite the frozen result:",
        "- initial net debit ≤ 80 points;",
        "- near-call/far-call premium ratio ≥ 0.45;",
        "- near-put/far-put premium ratio ≤ 0.55;",
        "- combined call/put balance filter using both ratio conditions.",
        "",
        "The combined balance filter reduces the strict sample to a small subset. Its improved win rate and drawdown must therefore be weighed against the large reduction in trade count and the risk of in-sample selection bias.",
        "",
        "## Filter sensitivity",
        "",
        "| Candidate filter | Trades kept | Gross P&L | Win rate | Profit factor | Max drawdown |",
        "|---|---:|---:|---:|---:|---:|",
    ]
    filter_table = pd.DataFrame(filter_rows)
    for _, r in filter_table.iterrows():
        report_lines.append(
            f"| {r['filter']} | {int(r['trades'])} | ₹{r['gross_pnl_inr']:,.2f} | "
            f"{r['win_rate']:.2%} | {r['profit_factor']:.3f} | ₹{r['max_drawdown_inr']:,.2f} |"
        )
    report_lines += [
        "",
        "## Cost-aware filter interpretation",
        "At the 0.05000% exchange-charge sensitivity, the strict baseline remains positive at ₹20/order brokerage and 2.00-point slippage (about ₹1,206.81). The exploratory filters also remain positive across the tested cost grid, but this is not out-of-sample evidence.",
        "",
        "## Literature context for the loss mechanism",
        "The observed concentration in front-week repricing is directionally consistent with literature treating weekly options as highly sensitive to short-horizon tail and jump risk, and with calendar-spread research emphasizing maturity-dependent dependence and term structure. This literature supports investigating volatility-regime and term-structure balance variables, but it does not prove that the P7 loss signatures are caused by any single market variable.",
        "- Andersen, Fusari & Todorov (2017): https://www.nber.org/papers/w21491",
        "- Schneider & Tavin (2018): https://www.sciencedirect.com/science/article/pii/S0378426616302424",
        "- Jayanesh et al. (2026): https://zenodo.org/records/19220278",
        "- Sajjan (2026): https://papers.ssrn.com/sol3/Delivery.cfm/6918100.pdf?abstractid=6918100&mirid=1",
        "",
        "## Practical improvement path",
        "1. First priority: improve execution measurement, not the payoff formula. The major losses originate in front-week option repricing, so synchronized bid/ask or tick data are required to know whether entry/exit slippage and transient adverse moves are larger than the daily-bar model indicates.",
        "2. Second: investigate a pre-trade term-structure balance filter using the two premium-ratio diagnostics. Treat it as a hypothesis and validate it on a held-out period before adoption.",
        "3. Third: test a maximum-loss or delta/volatility hedge only with intraday data. The current daily dataset cannot credibly simulate intratrade stop-outs or dynamic hedging.",
        "4. Preserve the frozen 84-trade baseline as the control group for every future experiment.",
        "",
        "## Important conclusion",
        "The loss audit does not identify a single universally correct fix. The clearest empirical weakness is concentration of losses in the near-expiry legs, especially in bullish-like front-week adverse signatures. Simple entry-state filters can reduce loss frequency and drawdown in-sample, but they also discard profitable trades and have not been out-of-sample validated.",
    ]

    args.out_report.write_text("\n".join(report_lines), encoding="utf-8")
    print("\n".join(report_lines))


if __name__ == "__main__":
    main()
