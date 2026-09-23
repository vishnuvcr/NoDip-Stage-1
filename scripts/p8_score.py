from __future__ import annotations

import argparse
from pathlib import Path
import numpy as np
import pandas as pd

THRESHOLD = 1.20

def bootstrap(x: np.ndarray, reps: int = 10000, block: int = 3, seed: int = 20260923) -> tuple[float, float]:
    if len(x) == 0:
        return np.nan, np.nan
    rng = np.random.default_rng(seed)
    n = len(x)
    starts = rng.integers(0, n, size=(reps, int(np.ceil(n / block))))
    idx = (starts[:, :, None] + np.arange(block)[None, None, :]) % n
    vals = x[idx].reshape(reps, -1)[:, :n]
    totals = vals.sum(axis=1)
    return tuple(np.quantile(totals, [0.025, 0.975]))

def perf(x: pd.Series) -> dict:
    a = pd.to_numeric(x, errors="coerce").dropna().to_numpy(float)
    if len(a) == 0:
        return {"n":0,"gross":0.0,"mean":np.nan,"median":np.nan,"win":np.nan,"pf":np.nan,"dd":np.nan,"worst":np.nan}
    pos, neg = a[a > 0], a[a < 0]
    curve = np.cumsum(a)
    dd = curve - np.maximum.accumulate(curve)
    return {
        "n": len(a),
        "gross": float(a.sum()),
        "mean": float(a.mean()),
        "median": float(np.median(a)),
        "win": float((a > 0).mean()),
        "pf": float(pos.sum() / (-neg.sum())) if len(neg) else float("inf"),
        "dd": float(dd.min()),
        "worst": float(a.min()),
    }

def lot(expiry: pd.Timestamp) -> int:
    return 75 if expiry <= pd.Timestamp("2025-12-30") else 65

def net_cost(r: pd.Series, slip: float, exchange_rate: float) -> float:
    ln, lf = float(r["lot_near"]), float(r["lot_far"])
    eb = r["entry_near_pe"]*ln + r["entry_far_ce"]*lf
    es = r["entry_near_ce"]*ln + r["entry_far_pe"]*lf
    xb = r["exit_near_ce"]*ln + r["exit_far_pe"]*lf
    xs = r["exit_near_pe"]*ln + r["exit_far_ce"]*lf
    premium = eb + es + xb + xs
    er = 0.0015 if pd.Timestamp(r["entry_date"]) >= pd.Timestamp("2026-04-01") else 0.001
    xr = 0.0015 if pd.Timestamp(r["near_expiry"]) >= pd.Timestamp("2026-04-01") else 0.001
    brokerage = 8*20
    stt = es*er + xs*xr
    stamp = (eb+xb)*0.00003
    sebi = premium*0.000001
    exchange = premium*exchange_rate
    gst = 0.18*(brokerage+exchange+sebi)
    slippage = slip*(4*ln+4*lf)
    return float(r["pnl_inr"] - brokerage - stt - stamp - sebi - exchange - gst - slippage)

def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--cycles", required=True, type=Path)
    ap.add_argument("--spot", required=True, type=Path)
    ap.add_argument("--rows", required=True, type=Path)
    ap.add_argument("--out-ledger", required=True, type=Path)
    ap.add_argument("--out-costs", required=True, type=Path)
    ap.add_argument("--out-report", required=True, type=Path)
    args = ap.parse_args()

    cycles = pd.read_csv(args.cycles)
    spot = pd.read_csv(args.spot)
    raw = pd.read_csv(args.rows)

    for frame in (cycles, spot, raw):
        if "entry_date" in frame:
            frame["entry_date"] = frame["entry_date"].astype(str)
    raw["date"] = raw["date"].astype(str)
    raw["expiry"] = raw["expiry"].astype(str)
    raw["open"] = pd.to_numeric(raw["open"], errors="coerce")
    raw["close"] = pd.to_numeric(raw["close"], errors="coerce")
    raw["contracts"] = pd.to_numeric(raw["contracts"], errors="coerce")
    raw["strike"] = pd.to_numeric(raw["strike"], errors="coerce")
    spot_map = dict(zip(spot["entry_date"], spot["spot_open"]))

    rows = []
    for c in cycles.itertuples(index=False):
        entry = str(c.entry_date)
        near = str(c.near_expiry)
        far = str(c.far_expiry)
        base = {
            "entry_date": entry,
            "near_expiry": near,
            "far_expiry": far,
            "expiry_regime": getattr(c, "expiry_regime"),
            "spot_open": spot_map.get(entry, np.nan),
            "status": "NON_EXECUTABLE",
            "status_detail": "",
            "gate_pass": False,
        }
        if not entry or entry not in spot_map:
            base["status_detail"] = "MISSING_SPOT"
            rows.append(base)
            continue
        ed = raw[raw["date"] == entry].copy()
        xd = raw[raw["date"] == near].copy()
        spot_open = float(spot_map[entry])
        strikes = sorted(set(ed.loc[ed["expiry"] == near, "strike"].dropna()) &
                         set(ed.loc[ed["expiry"] == far, "strike"].dropna()))
        valid = []
        for strike in strikes:
            ok = True
            for exp, opt in ((near,"PE"),(near,"CE"),(far,"CE"),(far,"PE")):
                m = ed[(ed["expiry"] == exp)&(ed["option_type"] == opt)&(ed["strike"] == strike)]
                if len(m) != 1:
                    ok = False
                    break
                if not (m["open"].iloc[0] > 0 and m["contracts"].iloc[0] > 0):
                    ok = False
                    break
            if ok:
                valid.append(float(strike))
        if not valid:
            base["status_detail"] = "NO_EXECUTABLE_COMMON_STRIKE"
            rows.append(base)
            continue
        strike = min(valid, key=lambda k:(abs(k-spot_open), k))
        base["strike"] = strike

        def get(df, exp, opt, field):
            m = df[(df["expiry"] == exp)&(df["option_type"] == opt)&(df["strike"] == strike)]
            if len(m) != 1:
                return np.nan
            return float(m[field].iloc[0]) if pd.notna(m[field].iloc[0]) else np.nan

        vals = {
            "entry_near_pe": get(ed, near, "PE", "open"),
            "entry_near_ce": get(ed, near, "CE", "open"),
            "entry_far_ce": get(ed, far, "CE", "open"),
            "entry_far_pe": get(ed, far, "PE", "open"),
            "exit_near_pe": get(xd, near, "PE", "close"),
            "exit_near_ce": get(xd, near, "CE", "close"),
            "exit_far_ce": get(xd, far, "CE", "close"),
            "exit_far_pe": get(xd, far, "PE", "close"),
        }
        base.update(vals)
        if any(not np.isfinite(v) or v <= 0 for k,v in vals.items() if k.startswith("entry_")):
            base["status_detail"] = "INVALID_ENTRY_PRINT"
            rows.append(base)
            continue
        if any(not np.isfinite(vals[k]) for k in vals if k.startswith("exit_")):
            base["status_detail"] = "MISSING_EXIT_PRINT"
            rows.append(base)
            continue

        base["lot_near"] = lot(pd.Timestamp(near))
        base["lot_far"] = lot(pd.Timestamp(far))
        base["call_ratio"] = base["entry_far_ce"]/base["entry_near_ce"]
        base["put_ratio"] = base["entry_far_pe"]/base["entry_near_pe"]
        base["calendar_balance_ratio"] = base["call_ratio"]/base["put_ratio"]
        base["gate_pass"] = bool(base["calendar_balance_ratio"] <= THRESHOLD)
        ln, lf = base["lot_near"], base["lot_far"]
        base["pnl_points"] = (
            base["exit_near_pe"]-base["entry_near_pe"]
            + base["entry_near_ce"]-base["exit_near_ce"]
            + base["exit_far_ce"]-base["entry_far_ce"]
            + base["entry_far_pe"]-base["exit_far_pe"]
        )
        base["pnl_inr"] = (
            (base["exit_near_pe"]-base["entry_near_pe"])*ln
            + (base["entry_near_ce"]-base["exit_near_ce"])*ln
            + (base["exit_far_ce"]-base["entry_far_ce"])*lf
            + (base["entry_far_pe"]-base["exit_far_pe"])*lf
        )
        base["status"] = "EXECUTABLE"
        base["status_detail"] = "GATE_PASS" if base["gate_pass"] else "GATE_FAIL"
        rows.append(base)

    ledger = pd.DataFrame(rows).sort_values(["near_expiry","entry_date"])
    exe = ledger[ledger["status"] == "EXECUTABLE"].copy()
    gate = exe[exe["gate_pass"]].copy()
    base_p = perf(exe["pnl_inr"])
    gate_p = perf(gate["pnl_inr"])
    bci = bootstrap(exe["pnl_inr"].to_numpy(float))
    gci = bootstrap(gate["pnl_inr"].to_numpy(float))

    cost_rows = []
    for slip in (0.0,0.5,1.0,2.0):
        for name, frame in (("P6_baseline",exe),("P7_fixed_gate",gate)):
            cost_rows.append({
                "sample":name,
                "slippage_points":slip,
                "exchange_rate":0.0005,
                "n":len(frame),
                "net_pnl_inr":frame.apply(lambda r: net_cost(r,slip,0.0005),axis=1).sum(),
            })
    costs = pd.DataFrame(cost_rows)
    losses = exe[exe["pnl_inr"] < 0]
    skipped = exe[~exe["gate_pass"]]
    skipped_losses = skipped[skipped["pnl_inr"] < 0]

    report = [
        "# P8 Out-of-Sample Validation Report — NIFTY 4-Leg Calendar",
        "",
        "## Frozen validation design",
        "- Development sample: 2022-2024.",
        "- Unseen OOS sample: 2025 onward.",
        "- Frozen candidate gate: calendar-balance ratio <= 1.20.",
        "- No additional threshold or filter search was permitted.",
        "",
        "## Coverage",
        f"- Scheduled cycles: {len(ledger)}",
        f"- Executable cycles: {len(exe)}",
        f"- Non-executable cycles: {len(ledger)-len(exe)}",
        f"- Gate-pass cycles: {len(gate)} ({len(gate)/len(exe):.1%})",
        "",
        "## Gross performance",
        "",
        "| Metric | P6 baseline | P7 fixed gate |",
        "|---|---:|---:|",
        f"| Cycles | {base_p['n']} | {gate_p['n']} |",
        f"| Gross P&L | ₹{base_p['gross']:,.2f} | ₹{gate_p['gross']:,.2f} |",
        f"| Mean cycle | ₹{base_p['mean']:,.2f} | ₹{gate_p['mean']:,.2f} |",
        f"| Median cycle | ₹{base_p['median']:,.2f} | ₹{gate_p['median']:,.2f} |",
        f"| Win rate | {base_p['win']:.2%} | {gate_p['win']:.2%} |",
        f"| Profit factor | {base_p['pf']:.3f} | {gate_p['pf']:.3f} |",
        f"| Max drawdown | ₹{abs(base_p['dd']):,.2f} | ₹{abs(gate_p['dd']):,.2f} |",
        f"| Worst trade | ₹{base_p['worst']:,.2f} | ₹{gate_p['worst']:,.2f} |",
        "",
        "## Bootstrap 95% intervals",
        f"- P6 baseline: ₹{bci[0]:,.2f} to ₹{bci[1]:,.2f}",
        f"- P7 fixed gate: ₹{gci[0]:,.2f} to ₹{gci[1]:,.2f}",
        "",
        "## Loss audit",
        f"- Baseline losses: {len(losses)}",
        f"- Losses skipped by fixed gate: {len(skipped_losses)}",
        f"- Winning cycles skipped by fixed gate: {len(skipped[skipped['pnl_inr'] > 0])}",
        f"- Residual gate-pass losses: {len(gate[gate['pnl_inr'] < 0])}",
        "",
        "## Cost model",
        "- Paytm Money brokerage: ₹20 per executed order.",
        "- Eight option executions per completed cycle.",
        "- STT: 0.10% on option-sale premium through 31-Mar-2026; 0.15% from 1-Apr-2026.",
        "- Stamp duty: 0.003% on option buys.",
        "- SEBI fee: 0.0001%.",
        "- GST: 18% on brokerage, exchange and SEBI charges.",
        "- Exchange-charge sensitivity: 0.05% stress case.",
        "- Adverse slippage: 0, 0.5, 1 and 2 index points per execution.",
        "",
        costs.to_markdown(index=False),
        "",
        "## Interpretation",
        "P8 is a temporal validation of a pre-frozen historical candidate. Positive OOS evidence is limited to the observed holdout and execution assumptions; it is not a guarantee of future performance.",
        "",
        "## Strengths and limitations",
        "- Strengths: genuine temporal holdout, frozen threshold, independent NSE-derived option archive, independent spot-open input, full executable-cycle audit and explicit cost/slippage stress.",
        "- Limitations: daily OHLC does not reconstruct intraday bid/ask paths; no market-impact model; mirror is a redistribution of exchange archives; Yahoo OPEN may differ slightly from exchange timestamp conventions.",
        "",
        "## Reproducibility",
        "- scripts/p8_prepare_cycles.py",
        "- scripts/p8_fetch_spot.py",
        "- scripts/p8_build_audit_input.py",
        "- scripts/reconcile_rejections_nse.py",
        "- reports/nifty_calendar/P8_OOS_TRADE_LEDGER_2025_ONWARD.csv",
        "- reports/nifty_calendar/P8_OOS_COST_SENSITIVITY_2025_ONWARD.csv",
    ]
    args.out_ledger.parent.mkdir(parents=True, exist_ok=True)
    args.out_costs.parent.mkdir(parents=True, exist_ok=True)
    args.out_report.parent.mkdir(parents=True, exist_ok=True)
    exe.to_csv(args.out_ledger, index=False)
    costs.to_csv(args.out_costs, index=False)
    args.out_report.write_text("\n".join(report), encoding="utf-8")
    print({"scheduled":len(ledger),"executable":len(exe),"gate":len(gate),"baseline_gross":base_p["gross"],"gate_gross":gate_p["gross"]})

if __name__ == "__main__":
    main()
