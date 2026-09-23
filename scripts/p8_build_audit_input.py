from __future__ import annotations

import argparse
from pathlib import Path
import pandas as pd

def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--cycles", required=True, type=Path)
    ap.add_argument("--spot", required=True, type=Path)
    ap.add_argument("--out-audit", required=True, type=Path)
    args = ap.parse_args()

    cycles = pd.read_csv(args.cycles)
    spot = pd.read_csv(args.spot)
    out = cycles.copy()
    out["spot_open"] = out["entry_date"].map(dict(zip(spot["entry_date"], spot["spot_open"])))
    out["primary_reason"] = "VALID"
    out["primary_strike"] = ""
    out["primary_spot_open"] = out["spot_open"]
    for col in [
        "primary_near_pe_open","primary_near_ce_open","primary_far_ce_open","primary_far_pe_open",
        "primary_near_pe_close","primary_near_ce_close","primary_far_ce_close","primary_far_pe_close"
    ]:
        out[col] = ""
    args.out_audit.parent.mkdir(parents=True, exist_ok=True)
    out.to_csv(args.out_audit, index=False)
    print(f"audit_rows={len(out)}")

if __name__ == "__main__":
    main()
