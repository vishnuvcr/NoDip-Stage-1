
from __future__ import annotations

from pathlib import Path
import importlib.util
import numpy as np
import pandas as pd
import duckdb
from huggingface_hub import hf_hub_download

ROOT = Path(__file__).resolve().parents[1]
P10_SUMMARY = ROOT / "reports/nifty_calendar/P10_ENTRY_DAY_OFFSET_SUMMARY.csv"
P8_CYCLES = ROOT / "reports/nifty_calendar/P8_CYCLES_2025_ONWARD.csv"
OUT_LEDGER = ROOT / "reports/nifty_calendar/P11_FORWARD_TRADE_LEDGER.csv"
OUT_COSTS = ROOT / "reports/nifty_calendar/P11_FORWARD_COST_SENSITIVITY.csv"
OUT_REPORT = ROOT / "reports/nifty_calendar/P11_FORWARD_VALIDATION_REPORT.md"
OUT_CONCLUSION = ROOT / "reports/nifty_calendar/P11_FINAL_RESEARCH_CONCLUSION.md"
OUT_STATUS = ROOT / "docs/nifty_calendar/PHASE_STATUS.md"

p8_spec = importlib.util.spec_from_file_location("p8", ROOT / "scripts/p8_score.py")
p8 = importlib.util.module_from_spec(p8_spec)
assert p8_spec.loader is not None
p8_spec.loader.exec_module(p8)

# P9 contains the validated Rissin/Upstox 1-minute panel helpers.
p9_spec = importlib.util.spec_from_file_location("p9", ROOT / "scripts/p9_rissin_oos_compare.py")
p9 = importlib.util.module_from_spec(p9_spec)
assert p9_spec.loader is not None
p9_spec.loader.exec_module(p9)

rec_spec = importlib.util.spec_from_file_location("rec", ROOT / "scripts/reconcile_rejections_nse.py")
rec = importlib.util.module_from_spec(rec_spec)
assert rec_spec.loader is not None
rec_spec.loader.exec_module(rec)

ATM_MAX_DISTANCE_POINTS = 25.0
CBR_THRESHOLD = 1.20
P10_OOS_CUTOFF = pd.Timestamp("2026-08-26")


def select_development_offset() -> tuple[int, pd.Series]:
    s = pd.read_csv(P10_SUMMARY)
    d = s[s["sample"].eq("DEVELOPMENT")].copy()
    q = d[(d["coverage"] >= 0.90) & (d["pf"] > 2.0)].copy()
    if q.empty:
        raise RuntimeError("No P10 development offset satisfies the frozen P11 selection rule")
    q = q.sort_values(["net_2pt", "pf", "coverage"], ascending=[False, False, False])
    row = q.iloc[0]
    return int(row["offset"]), row


def load_daily_2026() -> pd.DataFrame:
    path = hf_hub_download(
        repo_id="rissin/nse-options-intraday",
        filename="historical_daily/NIFTY/NIFTY_2026.parquet",
        repo_type="dataset",
    )
    df = pd.read_parquet(path)
    df["date"] = pd.to_datetime(df["date"], errors="coerce").dt.normalize()
    df["expiry"] = pd.to_datetime(df["expiry"], errors="coerce").dt.normalize()
    df = df[df["underlying"].astype(str).str.upper().eq("NIFTY")].copy()
    return df


def build_fresh_cycles(daily: pd.DataFrame) -> pd.DataFrame:
    trading_dates = sorted(pd.Series(daily["date"].dropna().unique()).tolist())
    if not trading_dates:
        raise RuntimeError("No 2026 NIFTY daily dates available")

    # Use the already frozen P8 expiry sequence through its last known expiry,
    # then extend it only with expiries actually present in the new source.
    p8 = pd.read_csv(P8_CYCLES)
    last_known_near = pd.Timestamp(p8["near_expiry"].max())

    available_exp = sorted(pd.Series(daily["expiry"].dropna().unique()).tolist())
    max_date = max(trading_dates)

    schedule = [last_known_near]
    for nominal in pd.date_range(last_known_near + pd.Timedelta(days=1), max_date + pd.Timedelta(days=21), freq="W-TUE"):
        eligible = [e for e in available_exp if e <= nominal and e > schedule[-1]]
        if eligible:
            candidate = eligible[-1]
            if (candidate - schedule[-1]).days <= 14:
                schedule.append(candidate)

    # De-duplicate while preserving order.
    schedule = list(dict.fromkeys(schedule))
    rows = []
    for i in range(len(schedule) - 3):
        previous_expiry = pd.Timestamp(schedule[i])
        near_expiry = pd.Timestamp(schedule[i + 1])
        far_expiry = pd.Timestamp(schedule[i + 4])

        if previous_expiry <= last_known_near:
            pass

        before_prev = [d for d in trading_dates if d < previous_expiry]
        if not before_prev:
            continue
        entry_date = pd.Timestamp(before_prev[-1])

        # Fresh means strictly after the P10 OOS entry cutoff and fully completed
        # as of the source's last available trading date.
        if entry_date <= P10_OOS_CUTOFF:
            continue
        if near_expiry > max_date:
            continue

        rows.append(
            {
                "cycle_id": f"P11_{entry_date.strftime('%Y%m%d')}",
                "offset": -1,
                "offset_label": "D-1",
                "previous_expiry": previous_expiry.strftime("%Y-%m-%d"),
                "near_expiry": near_expiry.strftime("%Y-%m-%d"),
                "far_expiry": far_expiry.strftime("%Y-%m-%d"),
                "entry_date": entry_date.strftime("%Y-%m-%d"),
            }
        )

    return pd.DataFrame(rows).drop_duplicates("cycle_id")


def load_intraday(cycles: pd.DataFrame):
    con = duckdb.connect()
    con.execute("INSTALL httpfs; LOAD httpfs; SET threads=8")

    entry_dates = set(cycles["entry_date"])
    exit_dates = set(cycles["near_expiry"])
    all_dates = entry_dates | exit_dates
    expiries = set(cycles["near_expiry"]) | set(cycles["far_expiry"])

    dates_2026 = sorted(all_dates)
    exps_2026 = sorted(expiries)

    raw = p9.load_year(con, 2026, dates_2026, exps_2026)
    if raw.empty:
        raise RuntimeError("No fresh P11 intraday NIFTY option rows returned from the Rissin dataset")

    date_sql = ",".join("'" + d + "'" for d in sorted(all_dates))
    spot_path = "hf://datasets/thetrademarkk/india-index-options-1m/index/NIFTY.parquet"
    spot_q = f"""
        SELECT timestamp, open AS spot_open, close AS spot_close
        FROM read_parquet('{spot_path}')
        WHERE CAST(timestamp AS DATE) IN ({date_sql})
    """
    spot = con.execute(spot_q).fetch_df()
    spot["timestamp"] = pd.to_datetime(spot["timestamp"], errors="coerce")
    if getattr(spot["timestamp"].dt, "tz", None) is not None:
        spot["timestamp"] = spot["timestamp"].dt.tz_convert("Asia/Kolkata").dt.tz_localize(None)
    spot["spot_open"] = pd.to_numeric(spot["spot_open"], errors="coerce")
    spot["spot_close"] = pd.to_numeric(spot["spot_close"], errors="coerce")
    spot = spot.dropna(subset=["timestamp", "spot_open", "spot_close"])

    return raw, spot


def fixed_0915_open_signal(panel: pd.DataFrame, spot: pd.DataFrame):
    if panel.empty or spot.empty:
        return None

    z = panel.copy()
    sp = spot[spot["timestamp"].dt.strftime("%Y-%m-%d").isin([str(z["timestamp"].dt.strftime("%Y-%m-%d").iloc[0])])].copy()
    merged = pd.merge_asof(
        z.sort_values("timestamp"),
        sp.sort_values("timestamp"),
        on="timestamp",
        direction="backward",
        tolerance=pd.Timedelta(minutes=1),
    )
    merged = merged[merged["timestamp"].dt.strftime("%H:%M").eq("09:15")].copy()
    if merged.empty:
        return None

    # Use the 09:15 spot opening observation for ATM selection and option opens
    # for both the gate and entry. This preserves the frozen P10 open-entry rule.
    merged["atm_distance_points"] = (merged["strike"] - merged["spot_open"]).abs()
    merged["atm_distance_pct"] = merged["atm_distance_points"] / merged["spot_open"] * 100.0
    merged = merged[merged["atm_distance_points"] <= ATM_MAX_DISTANCE_POINTS].copy()
    if merged.empty:
        return None

    merged["cbr"] = (
        (merged["far_open_CE"] / merged["near_open_CE"])
        / (merged["far_open_PE"] / merged["near_open_PE"])
    )
    hit = merged.sort_values(["atm_distance_points", "strike"]).head(1)
    if hit.empty:
        return None
    h = hit.iloc[0]
    if not np.isfinite(h["cbr"]) or h["cbr"] > CBR_THRESHOLD:
        return None

    return {
        "signal_timestamp": h["timestamp"],
        "strike": float(h["strike"]),
        "cbr": float(h["cbr"]),
        "spot_open": float(h["spot_open"]),
        "atm_distance_points": float(h["atm_distance_points"]),
        "atm_distance_pct": float(h["atm_distance_pct"]),
        "entry_near_ce": float(h["near_open_CE"]),
        "entry_near_pe": float(h["near_open_PE"]),
        "entry_far_ce": float(h["far_open_CE"]),
        "entry_far_pe": float(h["far_open_PE"]),
    }


def run_cycle(c: dict, raw: pd.DataFrame, spot: pd.DataFrame):
    entry = raw[
        raw["date"].eq(c["entry_date"])
        & raw["expiry"].isin([c["near_expiry"], c["far_expiry"]])
        & raw["open"].gt(0)
        & raw["volume"].fillna(0).gt(0)
    ].copy()
    if entry.empty:
        return {"cycle_id": c["cycle_id"], "entry_date": c["entry_date"], "status": "NO_ENTRY_PANEL"}

    near = entry[entry["expiry"].eq(c["near_expiry"])]
    far = entry[entry["expiry"].eq(c["far_expiry"])]

    def pv(frame, prefix):
        x = frame.pivot_table(
            index=["timestamp", "strike"],
            columns="option_type",
            values=["open", "close", "volume"],
            aggfunc="last",
        )
        if x.empty:
            return pd.DataFrame()
        x.columns = [f"{prefix}_{a}_{b}" for a, b in x.columns]
        return x.reset_index()

    a = pv(near, "near")
    b = pv(far, "far")
    if a.empty or b.empty:
        return {"cycle_id": c["cycle_id"], "entry_date": c["entry_date"], "status": "NO_COMMON_PANEL"}

    panel = a.merge(b, on=["timestamp", "strike"], how="inner")
    req = [
        "near_open_CE", "near_open_PE", "far_open_CE", "far_open_PE",
        "near_volume_CE", "near_volume_PE", "far_volume_CE", "far_volume_PE",
    ]
    panel = panel.dropna(subset=req)
    panel = panel[(panel[["near_open_CE","near_open_PE","far_open_CE","far_open_PE"]] > 0).all(axis=1)]
    panel = panel[(panel[["near_volume_CE","near_volume_PE","far_volume_CE","far_volume_PE"]] > 0).all(axis=1)]

    day_spot = spot[spot["timestamp"].dt.strftime("%Y-%m-%d").eq(c["entry_date"])][
        ["timestamp", "spot_open", "spot_close"]
    ].copy()
    sig = fixed_0915_open_signal(panel, day_spot)
    if sig is None:
        return {"cycle_id": c["cycle_id"], "entry_date": c["entry_date"], "status": "NO_0915_GATE"}

    exitd = raw[
        raw["date"].eq(c["near_expiry"])
        & raw["expiry"].isin([c["near_expiry"], c["far_expiry"]])
        & raw["strike"].eq(sig["strike"])
        & raw["close"].gt(0)
        & raw["volume"].fillna(0).gt(0)
    ].copy()
    if exitd.empty:
        return {
            "cycle_id": c["cycle_id"], "entry_date": c["entry_date"],
            "status": "NO_EXIT_PANEL", **sig
        }

    rows = []
    for ts, g in exitd.groupby("timestamp"):
        row = {"exit_timestamp": ts}
        ok = True
        for exp, opt, key in [
            (c["near_expiry"], "PE", "exit_near_pe"),
            (c["near_expiry"], "CE", "exit_near_ce"),
            (c["far_expiry"], "CE", "exit_far_ce"),
            (c["far_expiry"], "PE", "exit_far_pe"),
        ]:
            m = g[(g["expiry"].eq(exp)) & (g["option_type"].eq(opt))]
            if len(m) != 1:
                ok = False
                break
            row[key] = float(m["close"].iloc[0])
        if ok:
            rows.append(row)
    if not rows:
        return {
            "cycle_id": c["cycle_id"], "entry_date": c["entry_date"],
            "status": "NO_COMMON_EXIT", **sig
        }

    ex = sorted(rows, key=lambda r: r["exit_timestamp"])[-1]
    lot_near = rec.lot_size(pd.Timestamp(c["near_expiry"]))
    lot_far = rec.lot_size(pd.Timestamp(c["far_expiry"]))

    pnl_points, pnl_inr = p8.trade_pnl(
        {
            "entry_near_pe": sig["entry_near_pe"],
            "entry_near_ce": sig["entry_near_ce"],
            "entry_far_ce": sig["entry_far_ce"],
            "entry_far_pe": sig["entry_far_pe"],
        },
        ex,
        lot_near,
        lot_far,
    )

    return {
        **c,
        **sig,
        **ex,
        "status": "EXECUTABLE",
        "lot_near": lot_near,
        "lot_far": lot_far,
        "pnl_points": pnl_points,
        "pnl_inr": pnl_inr,
    }


def run():
    selected_offset, selected_dev = select_development_offset()
    if selected_offset != -1:
        raise RuntimeError(f"Frozen P11 selection rule was expected to select D-1 but selected offset {selected_offset}")

    daily = load_daily_2026()
    cycles = build_fresh_cycles(daily)
    if cycles.empty:
        last_source_date = pd.Timestamp(daily["date"].max()).strftime("%Y-%m-%d")
        selected_rule = f"D-1 entry at 09:15 IST with CBR <= {CBR_THRESHOLD:.2f}"
        OUT_LEDGER.parent.mkdir(parents=True, exist_ok=True)
        pd.DataFrame([{
            "selected_offset": "D-1",
            "status": "BLOCKED_NO_FRESH_COMPLETED_CYCLE",
            "p10_oos_cutoff_entry_date": P10_OOS_CUTOFF.strftime("%Y-%m-%d"),
            "latest_source_trading_date": last_source_date,
        }]).to_csv(OUT_LEDGER, index=False)
        pd.DataFrame([{
            "selected_offset": "D-1",
            "status": "BLOCKED_NO_FRESH_COMPLETED_CYCLE",
            "slippage_points": 0.0,
            "net_pnl_inr": np.nan,
        },{
            "selected_offset": "D-1",
            "status": "BLOCKED_NO_FRESH_COMPLETED_CYCLE",
            "slippage_points": 0.5,
            "net_pnl_inr": np.nan,
        },{
            "selected_offset": "D-1",
            "status": "BLOCKED_NO_FRESH_COMPLETED_CYCLE",
            "slippage_points": 1.0,
            "net_pnl_inr": np.nan,
        },{
            "selected_offset": "D-1",
            "status": "BLOCKED_NO_FRESH_COMPLETED_CYCLE",
            "slippage_points": 2.0,
            "net_pnl_inr": np.nan,
        }]).to_csv(OUT_COSTS, index=False)
        report = [
            "# P11 Forward / Paper-Execution Validation Report",
            "",
            "## Frozen selection",
            "Development-only selection rule: coverage >= 90%, PF > 2, maximize development net P&L at 2-point adverse slippage.",
            f"Selected offset: D-1 (development net at 2-point slippage = ₹{selected_dev['net_2pt']:,.2f}).",
            f"Frozen rule: {selected_rule}.",
            "No 2025+ P10 OOS result was used to select the offset.",
            "",
            "## Fresh-data gate",
            f"P10 OOS cutoff entry date: {P10_OOS_CUTOFF.strftime('%Y-%m-%d')}",
            f"Latest completed NIFTY daily source date available to the P11 runner: {last_source_date}",
            "Completed fresh P11 cycles after the cutoff: 0",
            "Executable fresh trades: 0",
            "",
            "## Decision",
            "**PAPER-MONITORING ONLY / INSUFFICIENT FRESH SAMPLE**",
            "",
            "No fresh completed cycle exists beyond the frozen P10 cutoff in the pinned option-data source. Therefore P11 cannot test the development-selected D-1 rule without reusing observations that were already in the P10 OOS sample.",
            "",
            "This is a data-availability stop, not a strategy-loss result. No additional entry-day offsets are searched.",
            "",
            "## Execution/data limitation",
            "The Rissin/Upstox source used for P10 provides the required 1-minute OHLCV fields but no historical bid/ask quote series. Modeled slippage is therefore a sensitivity, not a claim of realized Paytm Money fills.",
        ]
        OUT_REPORT.write_text("\n".join(report) + "\n", encoding="utf-8")
        OUT_CONCLUSION.write_text(
            "\n".join([
                "# P11 Final Research Conclusion",
                "",
                f"Selected development-only rule: {selected_rule}.",
                f"P10 OOS cutoff: {P10_OOS_CUTOFF.strftime('%Y-%m-%d')}.",
                f"Latest source date available: {last_source_date}.",
                "Fresh completed cycles after the cutoff: 0.",
                "Decision: **PAPER-MONITORING ONLY / INSUFFICIENT FRESH SAMPLE**.",
                "",
                "The absence of a fresh completed cycle prevents an unbiased forward validation. The P10 seven-offset study remains closed and no additional timing offsets are searched in this research phase.",
                "A future prospective paper-validation run may begin only when a completed post-cutoff expiry cycle is added to the pinned intraday dataset.",
            ]) + "\n",
            encoding="utf-8",
        )
        OUT_STATUS.write_text(
            "\n".join([
                "# Phase Status",
                "",
                "Last updated: 2026-09-23 — P11 stopped at the fresh-data availability gate.",
                "",
                "| Phase | Status | Notes |",
                "|---|---|---|",
                "| P0 Specification freeze | COMPLETE | Frozen four-leg calendar structure and 09:15 entry. |",
                "| P1 Literature / market structure | COMPLETE | Sources, market structure and cost literature reviewed. |",
                "| P2 Data acquisition | COMPLETE | 2022-2024 source data and later validation datasets cached/validated. |",
                "| P3 Engine/tests | COMPLETE | Frozen engine and regression controls complete. |",
                "| P4 Historical backtest | COMPLETE | Original 59-trade result preserved. |",
                "| P5 Verification/robustness | COMPLETE | Independent reconciliation completed. |",
                "| P6 Final manuscript | COMPLETE | Strict 84-cycle manuscript completed. |",
                "| P7 Loss audit / entry tuning | COMPLETE | 32 losses audited; CBR <= 1.20 retained only as candidate. |",
                "| P8 Unseen post-2024 validation | COMPLETE | Fixed 09:15 CBR gate validated on 2025+ holdout; not live-approved. |",
                "| P9 Event-driven intraday entry timing | COMPLETE | Event-driven replacement rejected after source QC and cost sensitivity. |",
                "| P10 Entry-day offset research | COMPLETE | Seven offsets tested; no direct OOS promotion. |",
                "| P11 Forward / paper-execution validation | BLOCKED — FRESH DATA UNAVAILABLE | No completed cycle exists after the P10 cutoff in the pinned option source; no reuse of P10 OOS data permitted. |",
                "",
                "Research stop condition: P11 is closed for this dataset. No further offsets or parameter searches are performed.",
            ]) + "\n",
            encoding="utf-8",
        )
        print(OUT_REPORT.read_text())
        return
    raw, spot = load_intraday(cycles)

    rows = [run_cycle(c, raw, spot) for c in cycles.to_dict("records")]
    ledger = pd.DataFrame(rows)

    # Explicit cost sensitivity. p8.net_cost requires lot sizes and entry/exit prices.
    costs = []
    trades = ledger[ledger["status"].eq("EXECUTABLE")].copy()
    for slip in [0.0, 0.5, 1.0, 2.0]:
        net = 0.0
        for _, r in trades.iterrows():
            rr = pd.Series(
                {
                    "entry_date": r["entry_date"],
                    "near_expiry": r["near_expiry"],
                    "lot_near": r["lot_near"],
                    "lot_far": r["lot_far"],
                    "entry_near_pe": r["entry_near_pe"],
                    "entry_near_ce": r["entry_near_ce"],
                    "entry_far_ce": r["entry_far_ce"],
                    "entry_far_pe": r["entry_far_pe"],
                    "exit_near_pe": r["exit_near_pe"],
                    "exit_near_ce": r["exit_near_ce"],
                    "exit_far_ce": r["exit_far_ce"],
                    "exit_far_pe": r["exit_far_pe"],
                    "pnl_inr": r["pnl_inr"],
                }
            )
            net += p8.net_cost(rr, slip, 0.0005)

        p = trades["pnl_inr"].astype(float).to_numpy() if len(trades) else np.array([])
        pos = p[p > 0]
        neg = p[p < 0]
        curve = np.cumsum(p) if len(p) else np.array([])
        dd = (curve - np.maximum.accumulate(curve)).min() if len(p) else np.nan
        costs.append(
            {
                "selected_offset": "D-1",
                "trades": len(p),
                "gross_pnl_inr": float(p.sum()) if len(p) else 0.0,
                "win_rate": float((p > 0).mean()) if len(p) else np.nan,
                "profit_factor": float(pos.sum() / (-neg.sum())) if len(neg) else np.nan,
                "max_drawdown_inr": abs(float(dd)) if len(p) else np.nan,
                "worst_trade_inr": float(p.min()) if len(p) else np.nan,
                "slippage_points": slip,
                "net_pnl_inr": net,
            }
        )

    OUT_LEDGER.parent.mkdir(parents=True, exist_ok=True)
    ledger.to_csv(OUT_LEDGER, index=False)
    pd.DataFrame(costs).to_csv(OUT_COSTS, index=False)

    last_source_date = pd.Timestamp(daily["date"].max()).strftime("%Y-%m-%d")
    completed = len(ledger)
    executable = int(len(trades))
    gross = float(trades["pnl_inr"].sum()) if executable else 0.0
    worst = float(trades["pnl_inr"].min()) if executable else np.nan
    max_share = float(trades["pnl_inr"].max() / gross) if executable and gross > 0 else np.nan

    report = [
        "# P11 Forward / Paper-Execution Validation Report",
        "",
        "## Frozen selection",
        "- Development selection rule: coverage >= 90%, PF > 2, maximize development net P&L at 2-point slippage.",
        f"- Selected offset: D-1 (development net at 2-point slippage = ₹{selected_dev['net_2pt']:,.2f}).",
        "- No 2025+ P10 OOS result was used to select the offset.",
        "",
        "## Fresh holdout",
        f"- P10 OOS cutoff entry date: {P10_OOS_CUTOFF.strftime('%Y-%m-%d')}",
        f"- Latest source trading date: {last_source_date}",
        f"- Completed fresh cycles: {completed}",
        f"- Executable D-1 trades: {executable}",
        "",
        "## Results before modeled costs",
        f"- Gross P&L: ₹{gross:,.2f}",
        f"- Worst trade: ₹{worst:,.2f}",
        f"- Largest single-trade share of gross: {max_share:.1%}" if np.isfinite(max_share) else "- Largest single-trade share of gross: n/a",
        "",
        "## Cost sensitivity",
    ]
    cost_df = pd.DataFrame(costs)
    for _, r in cost_df.iterrows():
        report.append(
            f"- {r['slippage_points']:.1f} points/leg: net ₹{r['net_pnl_inr']:,.2f}; win rate {r['win_rate']:.1%}; PF {r['profit_factor']:.3f}"
            if np.isfinite(r["win_rate"])
            else f"- {r['slippage_points']:.1f} points/leg: net ₹{r['net_pnl_inr']:,.2f}; no executable trades"
        )
    report += [
        "",
        "## Evidence classification",
        "- The P11 sample is intentionally fresh and untouched by P10 selection.",
        "- The Rissin/Upstox 1-minute source provides OHLCV, not historical bid/ask quotes; no bid/ask is inferred.",
        "- Modeled slippage and charges are sensitivities, not realized Paytm Money fills.",
    ]

    if completed < 8:
        decision = "PAPER-MONITORING ONLY / INSUFFICIENT FRESH SAMPLE"
        report += [
            "",
            "## Decision",
            f"**{decision}**",
            "The fresh sample is too short for a production-level validation decision. No further entry-day offsets are searched in P11.",
        ]
    elif executable == 0:
        decision = "REJECTED — NO EXECUTABLE FRESH TRADES"
        report += [
            "",
            "## Decision",
            f"**{decision}**",
        ]
    elif cost_df.loc[cost_df.slippage_points.eq(1.0), "net_pnl_inr"].iloc[0] <= 0 or cost_df.loc[cost_df.slippage_points.eq(2.0), "net_pnl_inr"].iloc[0] <= 0:
        decision = "REJECTED — FAILED COST ROBUSTNESS"
        report += [
            "",
            "## Decision",
            f"**{decision}**",
            "The frozen development-selected D-1 rule did not clear the predefined 1-point and 2-point cost gates.",
        ]
    elif np.isfinite(max_share) and max_share > 0.5:
        decision = "PAPER-MONITORING ONLY — CONCENTRATED RESULT"
        report += [
            "",
            "## Decision",
            f"**{decision}**",
            "More than half of gross P&L came from a single trade, so the result is not sufficiently diversified for promotion.",
        ]
    else:
        decision = "PAPER-ELIGIBLE, SUBJECT TO PROSPECTIVE MONITORING"
        report += [
            "",
            "## Decision",
            f"**{decision}**",
            "The frozen development-selected rule cleared the defined modeled-cost and concentration gates; it still requires prospective paper monitoring before any capital decision.",
        ]

    OUT_REPORT.write_text("\n".join(report) + "\n", encoding="utf-8")

    conclusion = [
        "# P11 Final Research Conclusion",
        "",
        f"- Selected rule: D-1 entry, 09:15 IST, CBR <= {CBR_THRESHOLD:.2f}.",
        f"- Fresh cycles evaluated: {completed}.",
        f"- Executable trades: {executable}.",
        f"- Fresh gross P&L: ₹{gross:,.2f}.",
        f"- Decision: {decision}.",
        "",
        "No additional entry-day offsets are searched in P11. Any future work is prospective monitoring or a separately preregistered research phase.",
    ]
    OUT_CONCLUSION.write_text("\n".join(conclusion) + "\n", encoding="utf-8")

    phase = [
        "# Phase Status",
        "",
        f"Last updated: 2026-09-23 — P11 execution completed; decision recorded in P11 report.",
        "",
        "| Phase | Status | Notes |",
        "|---|---|---|",
        "| P0 Specification freeze | COMPLETE | Frozen four-leg calendar structure and 09:15 entry. |",
        "| P1 Literature / market structure | COMPLETE | Sources, market-structure and cost literature reviewed. |",
        "| P2 Data acquisition | COMPLETE | 2022-2024 source data and later validation datasets cached/validated. |",
        "| P3 Engine/tests | COMPLETE | Frozen engine and regression controls complete. |",
        "| P4 Historical backtest | COMPLETE | 59-trade original result preserved. |",
        "| P5 Verification/robustness | COMPLETE | Independent reconciliation completed. |",
        "| P6 Final manuscript | COMPLETE | Strict 84-cycle manuscript completed. |",
        "| P7 Loss audit / entry tuning | COMPLETE | 32 losses audited; CBR <= 1.20 retained only as candidate. |",
        "| P8 Unseen post-2024 validation | COMPLETE | Fixed 09:15 CBR gate validated on 2025+ holdout, not promoted. |",
        "| P9 Event-driven intraday entry timing | COMPLETE | Event-driven replacement rejected after source QC and cost sensitivity. |",
        "| P10 Entry-day offset research | COMPLETE | Seven offsets tested; no direct OOS promotion. |",
        "| P11 Forward / paper-execution validation | COMPLETE | Development-only offset selection followed by fresh post-P10 validation. |",
        "",
        f"P11 decision: **{decision}**",
        "",
        "Research stop condition: no additional entry-day offsets are searched within this study.",
    ]
    OUT_STATUS.write_text("\n".join(phase) + "\n", encoding="utf-8")

    print(OUT_REPORT.read_text())
    print(OUT_CONCLUSION.read_text())


if __name__ == "__main__":
    run()
