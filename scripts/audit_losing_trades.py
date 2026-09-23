from __future__ import annotations

import argparse
from pathlib import Path

import numpy as np
import pandas as pd


def bootstrap_ci(x: np.ndarray, reps: int = 20000, block: int = 3, seed: int = 20260923) -> tuple[float, float]:
    if len(x) == 0:
        return (float("nan"), float("nan"))
    rng = np.random.default_rng(seed)
    n = len(x)
    nb = int(np.ceil(n / block))
    starts = rng.integers(0, n, size=(reps, nb))
    offsets = np.arange(block)
    idx = (starts[:, :, None] + offsets[None, None, :]) % n
    vals = x[idx].reshape(reps, nb * block)[:, :n]
    return tuple(np.quantile(vals.sum(axis=1), [0.025, 0.975]))


def perf(frame: pd.DataFrame, pnl_col: str = "pnl_inr") -> dict:
    x = frame[pnl_col].astype(float)
    if len(x) == 0:
        return {"n": 0, "gross": 0.0, "mean": np.nan, "win": np.nan, "pf": np.nan, "dd": np.nan, "worst": np.nan}
    pos = x[x > 0]
    neg = x[x < 0]
    curve = x.cumsum()
    dd = curve - curve.cummax()
    return {
        "n": int(len(x)),
        "gross": float(x.sum()),
        "mean": float(x.mean()),
        "win": float((x > 0).mean()),
        "pf": float(pos.sum() / (-neg.sum())) if len(neg) else float("inf"),
        "dd": float(dd.min()),
        "worst": float(x.min()),
    }


def add_features(df: pd.DataFrame, recon: pd.DataFrame) -> pd.DataFrame:
    out = df.copy()
    ln = out["lot_near"].astype(float)
    lf = out["lot_far"].astype(float)

    out["near_pe_pnl"] = (out["exit_near_pe"] - out["entry_near_pe"]) * ln
    out["near_ce_pnl"] = (out["entry_near_ce"] - out["exit_near_ce"]) * ln
    out["far_ce_pnl"] = (out["exit_far_ce"] - out["entry_far_ce"]) * lf
    out["far_pe_pnl"] = (out["entry_far_pe"] - out["exit_far_pe"]) * lf

    out["entry_net_inr"] = (
        out["entry_near_pe"] * ln
        + out["entry_far_ce"] * lf
        - out["entry_near_ce"] * ln
        - out["entry_far_pe"] * lf
    )
    out["entry_gross_inr"] = (
        out["entry_near_pe"] * ln
        + out["entry_far_ce"] * lf
        + out["entry_near_ce"] * ln
        + out["entry_far_pe"] * lf
    )
    out["entry_debit_ratio"] = out["entry_net_inr"] / out["entry_gross_inr"]

    out["call_ratio"] = out["entry_far_ce"] / out["entry_near_ce"]
    out["put_ratio"] = out["entry_far_pe"] / out["entry_near_pe"]
    out["calendar_balance_ratio"] = out["call_ratio"] / out["put_ratio"]
    out["call_calendar_points"] = out["entry_far_ce"] - out["entry_near_ce"]
    out["put_calendar_points"] = out["entry_far_pe"] - out["entry_near_pe"]
    out["calendar_asymmetry"] = (
        abs(out["call_calendar_points"] - out["put_calendar_points"])
        / (abs(out["call_calendar_points"]) + abs(out["put_calendar_points"]) + 1e-9)
    )

    def loss_reason(row: pd.Series) -> str:
        if row["pnl_inr"] >= 0:
            return "NON_LOSS"
        np_ = row["near_pe_pnl"]
        nc = row["near_ce_pnl"]
        if np_ < 0 and nc < 0:
            return "BOTH_NEAR_ADVERSE"
        if np_ < 0 <= nc:
            return "NEAR_PUT_ADVERSE"
        if nc < 0 <= np_:
            return "NEAR_CALL_ADVERSE"
        return "BOTH_NEAR_FAVORABLE_BUT_FAR_OFFSETTING"

    out["loss_reason"] = out.apply(loss_reason, axis=1)
    far_sum = out["far_ce_pnl"] + out["far_pe_pnl"]
    out["far_legs_direction"] = np.where(
        far_sum > 0,
        "FAR_NET_FAVORABLE",
        np.where(far_sum < 0, "FAR_NET_ADVERSE", "FAR_NET_FLAT"),
    )

    key = ["entry_date", "near_expiry", "far_expiry"]
    if recon is not None and not recon.empty:
        r = recon[key + ["primary_spot_open", "primary_strike", "secondary_strike", "comparison_status"]].copy()
        out = out.merge(r, on=key, how="left")
        out["entry_abs_moneyness"] = (
            (out["primary_strike"] - out["primary_spot_open"]).abs()
            / out["primary_spot_open"]
        )

    out["year"] = pd.to_datetime(out["entry_date"]).dt.year
    out["candidate_gate"] = out["calendar_balance_ratio"] <= 1.20
    return out


def conservative_net(frame: pd.DataFrame, broker_per_order: float = 20.0, exchange_rate: float = 0.0005, slippage_points: float = 2.0) -> pd.Series:
    ln = frame["lot_near"].astype(float)
    lf = frame["lot_far"].astype(float)
    buy_turnover = (
        frame["entry_near_pe"] * ln
        + frame["entry_far_ce"] * lf
        + frame["exit_near_ce"] * ln
        + frame["exit_far_pe"] * lf
    )
    sell_turnover = (
        frame["entry_near_ce"] * ln
        + frame["entry_far_pe"] * lf
        + frame["exit_near_pe"] * ln
        + frame["exit_far_ce"] * lf
    )
    premium = buy_turnover + sell_turnover
    brokerage = pd.Series(8 * broker_per_order, index=frame.index)
    stt = sell_turnover * 0.000625
    stamp = buy_turnover * 0.00003
    sebi = premium * 0.000001
    exchange = premium * exchange_rate
    gst = 0.18 * (brokerage + sebi + exchange)
    slippage = slippage_points * (4 * ln + 4 * lf)
    return frame["pnl_inr"] - (
        brokerage + stt + stamp + sebi + exchange + gst + slippage
    )


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--ledger", required=True, type=Path)
    ap.add_argument("--recon", required=True, type=Path)
    ap.add_argument("--out-loss-audit", required=True, type=Path)
    ap.add_argument("--out-top-losses", required=True, type=Path)
    ap.add_argument("--out-grid", required=True, type=Path)
    ap.add_argument("--out-report", required=True, type=Path)
    ap.add_argument("--out-candidate", required=True, type=Path)
    args = ap.parse_args()

    ledger = pd.read_csv(args.ledger, parse_dates=["entry_date", "near_expiry", "far_expiry"])
    recon = pd.read_csv(args.recon, parse_dates=["entry_date", "near_expiry", "far_expiry"])

    if len(ledger) != 84:
        raise SystemExit(f"Expected 84 strict trades, got {len(ledger)}")

    d = add_features(ledger, recon)
    d["conservative_net20_2pt"] = conservative_net(d)

    args.out_loss_audit.parent.mkdir(parents=True, exist_ok=True)
    d.to_csv(args.out_loss_audit, index=False)

    top = d[d["pnl_inr"] < 0].sort_values("pnl_inr").head(15).copy()
    top.to_csv(args.out_top_losses, index=False)

    rows = []
    for threshold in [1.15, 1.20, 1.25, 1.30]:
        mask = d["calendar_balance_ratio"] <= threshold
        allp = perf(d[mask])
        train = d[mask & d["year"].le(2023)]
        test = d[mask & d["year"].eq(2024)]
        rows.append(
            {
                "threshold": threshold,
                "all_n": allp["n"],
                "all_gross_pnl": allp["gross"],
                "all_win_rate": allp["win"],
                "all_profit_factor": allp["pf"],
                "all_max_drawdown": allp["dd"],
                "all_conservative_net20_2pt": d.loc[mask, "conservative_net20_2pt"].sum(),
                "train_n_2022_2023": len(train),
                "train_gross_pnl_2022_2023": train["pnl_inr"].sum(),
                "train_conservative_net20_2pt": train["conservative_net20_2pt"].sum(),
                "test_n_2024": len(test),
                "test_gross_pnl_2024": test["pnl_inr"].sum(),
                "test_conservative_net20_2pt": test["conservative_net20_2pt"].sum(),
            }
        )

    grid = pd.DataFrame(rows)
    grid.to_csv(args.out_grid, index=False)

    losses = d[d["pnl_inr"] < 0].copy()
    gate = d["candidate_gate"]
    filtered_losses = losses[~losses["candidate_gate"]]
    retained_losses = losses[losses["candidate_gate"]]
    candidate = d[gate]

    primary_boot_lo, primary_boot_hi = bootstrap_ci(d["pnl_inr"].to_numpy(float))
    candidate_boot_lo, candidate_boot_hi = bootstrap_ci(candidate["pnl_inr"].to_numpy(float))

    by_reason = losses.groupby("loss_reason").agg(count=("pnl_inr", "size"), gross_loss=("pnl_inr", "sum")).sort_values("count", ascending=False)

    report_lines = [
        "# P7 Losing-Trade Audit and Entry-Tuning Report — NIFTY 4-Leg Calendar — 2022-2024",
        "",
        "## Scope",
        "- P6 strict validation population: 84 cycles.",
        "- P7 does not modify or replace the P6 frozen result.",
        "- The proposed entry screen is a candidate rule for a future validation phase.",
        "",
        "## Loss audit",
        f"- Total trades: {len(d)}",
        f"- Losing trades: {(d['pnl_inr'] < 0).sum()} ({(d['pnl_inr'] < 0).mean():.2%})",
        f"- Total gross P&L: ₹{d['pnl_inr'].sum():,.2f}",
        f"- Aggregate losses: ₹{losses['pnl_inr'].sum():,.2f}",
        f"- Mean loss: ₹{losses['pnl_inr'].mean():,.2f}",
        f"- Median loss: ₹{losses['pnl_inr'].median():,.2f}",
        "",
        "### Loss mechanism by near-expiry legs",
        "",
        "| Loss reason | Count | Share of losses | Gross loss |",
        "|---|---:|---:|---:|",
    ]

    for reason, row in by_reason.iterrows():
        report_lines.append(f"| {reason} | {int(row['count'])} | {row['count']/len(losses):.1%} | ₹{row['gross_loss']:,.2f} |")

    wins = d[d["pnl_inr"] > 0]
    report_lines += [
        "",
        "### Entry-feature separation: losing vs winning trades",
        "",
        "| Feature | Loss median | Winner median |",
        "|---|---:|---:|",
    ]
    for col in ["calendar_balance_ratio", "call_ratio", "put_ratio", "entry_debit_ratio", "calendar_asymmetry"]:
        report_lines.append(f"| {col} | {losses[col].median():.3f} | {wins[col].median():.3f} |")

    report_lines += [
        "",
        "### Leg contribution finding",
        f"- Both near-expiry legs were individually adverse in {int(((losses['near_pe_pnl'] < 0) & (losses['near_ce_pnl'] < 0)).sum())} of {len(losses)} losses.",
        f"- Both far-expiry legs were individually favorable in {int(((losses['far_ce_pnl'] > 0) & (losses['far_pe_pnl'] > 0)).sum())} of {len(losses)} losses.",
        "",
        "## Candidate entry gate",
        "",
        "Enter only when calendar-balance ratio <= 1.20.",
        "",
        "calendar-balance ratio = (far CE entry / near CE entry) / (far PE entry / near PE entry)",
        "",
        "This is an entry-time condition. It uses no future P&L, exit information or post-entry adjustment.",
        "",
        "### Candidate population effect",
        f"- Retained cycles: {len(candidate)} / {len(d)} ({len(candidate)/len(d):.1%}).",
        f"- Gross P&L: ₹{candidate['pnl_inr'].sum():,.2f}.",
        f"- Win rate: {perf(candidate)['win']:.2%}.",
        f"- Profit factor: {perf(candidate)['pf']:.3f}.",
        f"- Maximum drawdown: ₹{abs(perf(candidate)['dd']):,.2f}.",
        f"- Bootstrap 95% interval: ₹{candidate_boot_lo:,.2f} to ₹{candidate_boot_hi:,.2f}.",
        f"- Losses filtered: {len(filtered_losses)} of {len(losses)} ({len(filtered_losses)/len(losses):.1%}).",
        f"- Aggregate loss removed from the retained sample: ₹{filtered_losses['pnl_inr'].sum():,.2f}.",
        f"- Remaining losses: {len(retained_losses)}.",
        "",
        "### Development/temporal diagnostic",
        "",
        "| Population | Baseline gross P&L | Candidate gross P&L |",
        "|---|---:|---:|",
        f"| 2022-2023 development | ₹{d.loc[d['year'].le(2023),'pnl_inr'].sum():,.2f} | ₹{d.loc[(d['year'].le(2023)) & gate,'pnl_inr'].sum():,.2f} |",
        f"| 2024 temporal holdout | ₹{d.loc[d['year'].eq(2024),'pnl_inr'].sum():,.2f} | ₹{d.loc[(d['year'].eq(2024)) & gate,'pnl_inr'].sum():,.2f} |",
        "",
        "| Population | Baseline trades | Candidate trades | Baseline win | Candidate win |",
        "|---|---:|---:|---:|---:|",
        f"| 2022-2023 | {int((d['year'].le(2023)).sum())} | {int(((d['year'].le(2023)) & gate).sum())} | {(d.loc[d['year'].le(2023),'pnl_inr']>0).mean():.2%} | {(d.loc[(d['year'].le(2023)) & gate,'pnl_inr']>0).mean():.2%} |",
        f"| 2024 | {int((d['year'].eq(2024)).sum())} | {int(((d['year'].eq(2024)) & gate).sum())} | {(d.loc[d['year'].eq(2024),'pnl_inr']>0).mean():.2%} | {(d.loc[(d['year'].eq(2024)) & gate,'pnl_inr']>0).mean():.2%} |",
        "",
        "The 2024 line is a temporal diagnostic, not a clean independent confirmation, because the full 2022-2024 sample was inspected during research. A future post-2024 holdout is required before promoting this gate.",
        "",
        "## Threshold sensitivity",
        grid.to_markdown(index=False),
        "",
        "## Conservative cost check",
        f"- Candidate net P&L at ₹20/order brokerage, 0.05000% exchange charges and 2-point adverse slippage: ₹{candidate['conservative_net20_2pt'].sum():,.2f}.",
        "",
        "## Interpretation",
        "The largest recurring loss mechanism is front-expiry deterioration: both near-expiry legs are adverse in most losing trades, while the far legs are often favorable. The candidate balance ratio is intended to screen out entry configurations where the call calendar is disproportionately richer than the put calendar.",
        "",
        "The 1.20 threshold is a candidate research parameter, not a claimed optimal parameter. It must be frozen before any genuinely unseen post-2024 validation.",
        "",
        "## Backtest-overfitting control",
        "Finance research literature warns that repeatedly searching historical variants can create apparently strong in-sample results that fail out of sample. This phase therefore keeps one interpretable candidate gate, reports alternative thresholds, and explicitly reserves post-2024 data for future validation.",
        "",
        "## Reproducibility",
        "- docs/nifty_calendar/P7_LOSS_AUDIT_PLAN.md",
        "- docs/nifty_calendar/P7_ENTRY_CRITERIA_LOCK.md",
        "- reports/nifty_calendar/LOSS_AUDIT_2022_2024.csv",
        "- reports/nifty_calendar/LOSS_TOP_TRADES_2022_2024.csv",
        "- reports/nifty_calendar/ENTRY_FILTER_GRID_2022_2024.csv",
        "- reports/nifty_calendar/ENTRY_CRITERIA_CANDIDATE_2022_2024.md",
    ]
    args.out_report.write_text("\n".join(report_lines), encoding="utf-8")

    candidate_doc = f"""# P7 Candidate Entry Criteria — v1

Enter only when:

calendar-balance ratio <= 1.20

where:

calendar-balance ratio = (far CE entry / near CE entry) / (far PE entry / near PE entry)

Keep every P6 rule unchanged:
- first session after prior NIFTY weekly expiry
- 09:15 IST entry
- nearest common ATM strike
- long near PE
- short near CE
- long far CE
- short far PE
- exit at near-expiry close
- one historical lot
- no adjustments

Descriptive full-sample effect:
- 52 of 84 trades retained
- gross P&L ₹{candidate['pnl_inr'].sum():,.2f}
- win rate {perf(candidate)['win']:.2%}
- profit factor {perf(candidate)['pf']:.3f}
- maximum drawdown ₹{abs(perf(candidate)['dd']):,.2f}

Conservative cost scenario:
- ₹20/order brokerage
- 0.05000% exchange-charge sensitivity
- 2.00-point adverse slippage per execution
- candidate net P&L ₹{candidate['conservative_net20_2pt'].sum():,.2f}

This is a candidate rule only. Do not replace the P6 frozen strategy. Validate unchanged on a genuinely unseen post-2024 sample before any production use.
"""
    args.out_candidate.write_text(candidate_doc, encoding="utf-8")


if __name__ == "__main__":
    main()
