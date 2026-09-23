from __future__ import annotations

import argparse
import re
import subprocess
from pathlib import Path
import pandas as pd

BOUNDARY = pd.Timestamp("2024-12-26")

def archives(root: Path) -> dict[pd.Timestamp, str]:
    raw = subprocess.check_output(
        ["git", "-C", str(root), "ls-tree", "-r", "--name-only", "HEAD", "data/2025", "data/2026"],
        text=True,
    )
    pat = re.compile(r"data/(?:2025|2026)/\d{2}/BhavCopy_NSE_FO_0_0_0_(\d{8})_F_0000\.csv\.zip$")
    out = {}
    for line in raw.splitlines():
        m = pat.match(line.strip())
        if m:
            out[pd.Timestamp(m.group(1), format="%Y%m%d")] = line.strip()
    if not out:
        raise RuntimeError("No 2025-2026 mirror archives found")
    return dict(sorted(out.items()))

def expiry_dates(trading_dates: list[pd.Timestamp]) -> list[pd.Timestamp]:
    nominal = list(pd.date_range("2025-01-02", "2025-08-28", freq="W-THU"))
    nominal += list(pd.date_range("2025-09-02", max(trading_dates), freq="W-TUE"))
    out = [BOUNDARY]
    for n in nominal:
        prev = [d for d in trading_dates if d <= n]
        if prev and prev[-1] > out[-1]:
            out.append(prev[-1])
    return out

def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--mirror-root", required=True, type=Path)
    ap.add_argument("--out-cycles", required=True, type=Path)
    ap.add_argument("--out-archives", required=True, type=Path)
    args = ap.parse_args()
    files = archives(args.mirror_root)
    dates = sorted(files)
    exps = expiry_dates(dates)
    rows = []
    for i in range(1, len(exps) - 3):
        prev, near, far = exps[i-1], exps[i], exps[i+3]
        entry = next((d for d in dates if d > prev and d < near), None)
        rows.append({
            "entry_date": entry.strftime("%Y-%m-%d") if entry is not None else "",
            "near_expiry": near.strftime("%Y-%m-%d"),
            "far_expiry": far.strftime("%Y-%m-%d"),
            "expiry_regime": "THURSDAY" if near < pd.Timestamp("2025-09-02") else "TUESDAY",
        })
    args.out_cycles.parent.mkdir(parents=True, exist_ok=True)
    args.out_archives.parent.mkdir(parents=True, exist_ok=True)
    pd.DataFrame(rows).to_csv(args.out_cycles, index=False)
    pd.DataFrame(
        [{"trade_date": d.strftime("%Y-%m-%d"), "path": p} for d, p in files.items()]
    ).to_csv(args.out_archives, index=False)
    print(f"archives={len(files)} cycles={len(rows)}")

if __name__ == "__main__":
    main()
