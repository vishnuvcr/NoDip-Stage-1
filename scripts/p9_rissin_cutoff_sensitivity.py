from __future__ import annotations
from pathlib import Path
import importlib.util
import numpy as np
import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
INPUT = ROOT / 'reports/nifty_calendar/P9_RISSIN_OOS_COMPARISON.csv'
OUT = ROOT / 'reports/nifty_calendar/P9_RISSIN_CUTOFF_SENSITIVITY.csv'
REPORT = ROOT / 'reports/nifty_calendar/P9_RISSIN_CUTOFF_SENSITIVITY_REPORT.md'

p8_path = ROOT / 'scripts/p8_score.py'
spec = importlib.util.spec_from_file_location('p8', p8_path)
p8 = importlib.util.module_from_spec(spec)
assert spec.loader is not None
spec.loader.exec_module(p8)

CUTOFFS = ['15:00', '15:15', '15:30', '15:40']

def metrics(df: pd.DataFrame) -> dict[str, float]:
    p = pd.to_numeric(df['event_pnl_inr'], errors='coerce').dropna().to_numpy(float)
    if len(p):
        pos = p[p > 0]
        neg = p[p < 0]
        curve = np.cumsum(p)
        dd = float((curve - np.maximum.accumulate(curve)).min())
        gross = float(p.sum())
        win_rate = float((p > 0).mean())
        pf = float(pos.sum() / (-neg.sum())) if len(neg) else np.nan
        worst = float(p.min())
    else:
        gross = 0.0
        win_rate = np.nan
        pf = np.nan
        dd = np.nan
        worst = np.nan
    return {'event_trades': int(len(p)), 'gross_pnl_inr': gross, 'win_rate': win_rate, 'profit_factor': pf, 'max_drawdown_inr': abs(dd) if len(p) else np.nan, 'worst_trade_inr': worst}

def net_for(df: pd.DataFrame, slip: float) -> float:
    total = 0.0
    for _, r in df.iterrows():
        row = pd.Series({'entry_date': r['entry_date'], 'near_expiry': r['near_expiry'], 'lot_near': r['lot_near'], 'lot_far': r['lot_far'], 'entry_near_pe': r['event_entry_near_pe'], 'entry_near_ce': r['event_entry_near_ce'], 'entry_far_ce': r['event_entry_far_ce'], 'entry_far_pe': r['event_entry_far_pe'], 'exit_near_pe': r['event_exit_near_pe'], 'exit_near_ce': r['event_exit_near_ce'], 'exit_far_ce': r['event_exit_far_ce'], 'exit_far_pe': r['event_exit_far_pe'], 'pnl_inr': r['event_pnl_inr']})
        total += p8.net_cost(row, slip, 0.0005)
    return float(total)

def main() -> None:
    out = pd.read_csv(INPUT)
    out['entry_date'] = pd.to_datetime(out['entry_date'], errors='coerce')
    out['event_signal_timestamp'] = pd.to_datetime(out['event_signal_timestamp'], errors='coerce')
    out['gate_pass'] = out['gate_pass'].astype(str).str.lower().eq('true')
    out = out[out['event_status'].eq('EXECUTABLE')].copy()
    out['signal_time'] = out['event_signal_timestamp'].dt.strftime('%H:%M')
    rows = []
    for cutoff in CUTOFFS:
        sub = out[out['signal_time'].le(cutoff)].sort_values('entry_date').copy()
        m = metrics(sub)
        gatepass = sub[sub['gate_pass']]
        gatefail = sub[~sub['gate_pass']]
        ref = pd.to_numeric(gatepass['pnl_inr'], errors='coerce').fillna(0).sum()
        r = {'cutoff': cutoff, **m, 'event_net_0pt_inr': net_for(sub, 0.0), 'event_net_0.5pt_inr': net_for(sub, 0.5), 'event_net_1pt_inr': net_for(sub, 1.0), 'event_net_2pt_inr': net_for(sub, 2.0), 'event_gatepass_trades': int(len(gatepass)), 'event_gatefail_trades': int(len(gatefail)), 'event_gatepass_gross_inr': float(gatepass['event_pnl_inr'].sum()) if len(gatepass) else 0.0, 'event_gatefail_gross_inr': float(gatefail['event_pnl_inr'].sum()) if len(gatefail) else 0.0, 'p8_gate_reference_gross_on_event_gatepass_dates_inr': float(ref), 'event_minus_p8_gate_reference_gross_inr': float(m['gross_pnl_inr'] - ref)}
        rows.append(r)
    pd.DataFrame(rows).to_csv(OUT, index=False)
    df = pd.DataFrame(rows)
    lines = ['# P9 Rissin pre-specified latest-entry sensitivity', '', '- This is a pre-specified operational cutoff sensitivity, not a post-hoc parameter search.', '- Entry rule remains frozen: first intraday qualifying CBR <= 1.20 with a true ATM common strike and all four executable legs.', '- ATM QC: NIFTY strike interval is 50 points; common strike must be within 25 points of contemporaneous spot.', '- Signal uses the minute close; entry uses the next available minute open.', '', '## Summary']
    for _, r in df.iterrows():
        lines.append(f\"- {r['cutoff']}: {int(r['event_trades'])} trades, gross ₹{r['gross_pnl_inr']:,.2f}, PF {r['profit_factor']:.3f}, net at 1-point slippage ₹{r['event_net_1pt_inr']:,.2f}, net at 2-point slippage ₹{r['event_net_2pt_inr']:,.2f}.\")
    lines += ['', '## Interpretation rule', 'No cutoff is selected for profitability. The cutoffs are reported as pre-registered sensitivity checks.', '', 'NSE contract specification source:', 'https://www.nseindia.com/static/products-services/equity-derivatives-nifty50']
    REPORT.write_text('\n'.join(lines) + '\n', encoding='utf-8')

if __name__ == '__main__': main()
