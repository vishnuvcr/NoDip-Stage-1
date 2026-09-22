from __future__ import annotations

import argparse
import io
import zipfile
from datetime import date, timedelta
from pathlib import Path

import pandas as pd
import requests

UA = "Mozilla/5.0 (compatible; NoDip-Stage-1 research)"
TIMEOUT = 45

def urls_for_day(d: date):
    stamp = d.strftime("%Y%m%d")
    mon = d.strftime("%b").upper()
    legacy = (
        "https://archives.nseindia.com/content/historical/DERIVATIVES/"
        f"{d:%Y}/{mon}/fo{d:%d}{mon}{d:%Y}bhav.csv.zip"
    )
    udiff = (
        "https://archives.nseindia.com/content/fo/"
        f"BhavCopy_NSE_FO_0_0_0_{stamp}_F_0000.csv.zip"
    )
    return [udiff, legacy]

def get_bytes(session, d):
    for url in urls_for_day(d):
        try:
            r = session.get(url, timeout=TIMEOUT)
        except requests.RequestException:
            continue
        if r.status_code == 200 and len(r.content) > 1000:
            return r.content, url
    return None

def find_col(columns, candidates):
    upper = {str(c).strip().upper(): c for c in columns}
    for c in candidates:
        if c in upper:
            return upper[c]
    return None

def parse_day(blob, d):
    with zipfile.ZipFile(io.BytesIO(blob)) as z:
        csv_names = [n for n in z.namelist() if n.lower().endswith(".csv")]
        if not csv_names:
            raise ValueError("No CSV inside downloaded NSE zip")
        with z.open(csv_names[0]) as f:
            raw = pd.read_csv(f, low_memory=False)

    spec = {
        "symbol": ["TCKRSYMB", "SYMBOL"],
        "expiry": ["XPRYDT", "EXPIRY_DT", "EXPIRY"],
        "strike": ["STRKPRIC", "STRIKE_PR", "STRIKEPRICE"],
        "opt": ["OPTNTP", "OPTION_TYP", "OPTIONTYPE"],
        "open": ["OPNPRIC", "OPEN"],
        "close": ["CLSPRIC", "CLOSE"],
        "lot": ["NEWBRDLOTQTY", "LOTSIZE", "LOT_SIZE"],
        "volume": ["TTLTRADGVOL", "CONTRACTS", "VOLUME"],
        "oi": ["OPNINTRST", "OPEN_INT", "OPENINTEREST"],
        "underlying": ["UNDRLYNGVAL", "UNDERLYING"],
        "instrument": ["FININSTRMTP", "INSTRUMENT"],
    }
    c = {k: find_col(raw.columns, v) for k, v in spec.items()}

    missing = [k for k in ["symbol", "expiry", "strike", "opt", "open", "close"] if c[k] is None]
    if missing:
        raise ValueError(f"Unrecognised NSE schema on {d}: missing {missing}")

    out = pd.DataFrame({
        "date": pd.Timestamp(d),
        "symbol": raw[c["symbol"]].astype(str).str.upper(),
        "expiry": pd.to_datetime(raw[c["expiry"]], errors="coerce"),
        "strike": pd.to_numeric(raw[c["strike"]], errors="coerce"),
        "option_type": raw[c["opt"]].astype(str).str.upper(),
        "open": pd.to_numeric(raw[c["open"]], errors="coerce"),
        "close": pd.to_numeric(raw[c["close"]], errors="coerce"),
        "lot_size": pd.to_numeric(raw[c["lot"]], errors="coerce") if c["lot"] else pd.NA,
        "volume": pd.to_numeric(raw[c["volume"]], errors="coerce") if c["volume"] else pd.NA,
        "open_interest": pd.to_numeric(raw[c["oi"]], errors="coerce") if c["oi"] else pd.NA,
        "underlying": pd.to_numeric(raw[c["underlying"]], errors="coerce") if c["underlying"] else pd.NA,
    })

    if c["instrument"]:
        inst = raw[c["instrument"]].astype(str).str.upper()
        out = out[inst.str.contains("OPTIDX", na=False)]

    out = out[out["symbol"].eq("NIFTY")]
    out = out[out["option_type"].isin(["CE", "PE"])]
    out = out[out["expiry"].notna() & out["strike"].notna()]
    return out.reset_index(drop=True)

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--start", required=True)
    ap.add_argument("--end", required=True)
    ap.add_argument("--out", required=True, type=Path)
    ap.add_argument("--manifest", required=True, type=Path)
    args = ap.parse_args()

    start = date.fromisoformat(args.start)
    end = date.fromisoformat(args.end)
    rows = []
    manifest = []

    s = requests.Session()
    s.headers.update({"User-Agent": UA, "Accept": "*/*"})

    d = start
    while d <= end:
        got = get_bytes(s, d)
        if got is None:
            manifest.append({"date": str(d), "status": "MISSING"})
        else:
            blob, url = got
            try:
                day = parse_day(blob, d)
                rows.append(day)
                manifest.append({"date": str(d), "status": "OK", "source": url, "rows": len(day)})
            except Exception as exc:
                manifest.append({"date": str(d), "status": "PARSE_ERROR", "source": url, "error": str(exc)})
        d += timedelta(days=1)

    args.out.parent.mkdir(parents=True, exist_ok=True)
    args.manifest.parent.mkdir(parents=True, exist_ok=True)
    if not rows:
        raise RuntimeError("No valid NSE derivative files were acquired")

    fo = pd.concat(rows, ignore_index=True)
    fo.to_parquet(args.out, index=False)
    pd.DataFrame(manifest).to_csv(args.manifest, index=False)
    print(f"Saved {len(fo):,} NIFTY option rows")

if __name__ == "__main__":
    main()
