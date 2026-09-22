import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

import pandas as pd

from src.nifty_calendar.backtest import build_trades


def test_four_leg_pnl_and_next_session_entry():
    rows = []

    def add(d, e, k, opt, op, cl, lot=50):
        rows.append(
            {
                "date": pd.Timestamp(d),
                "symbol": "NIFTY",
                "expiry": pd.Timestamp(e),
                "strike": k,
                "option_type": opt,
                "open": op,
                "close": cl,
                "lot_size": lot,
            }
        )

    dates = [
        "2024-01-04",
        "2024-01-05",
        "2024-01-11",
        "2024-01-18",
        "2024-01-25",
        "2024-02-01",
    ]
    exps = [
        "2024-01-04",
        "2024-01-11",
        "2024-01-18",
        "2024-01-25",
        "2024-02-01",
    ]

    for d in dates:
        for e in exps:
            if pd.Timestamp(e) >= pd.Timestamp(d):
                for opt in ["CE", "PE"]:
                    add(d, e, 21000, opt, 100.0, 90.0)

    for r in rows:
        if r["date"] == pd.Timestamp("2024-01-05"):
            if r["expiry"] == pd.Timestamp("2024-01-11"):
                r["open"] = 10.0 if r["option_type"] == "PE" else 12.0
            if r["expiry"] == pd.Timestamp("2024-02-01"):
                r["open"] = 20.0 if r["option_type"] == "CE" else 22.0
        if r["date"] == pd.Timestamp("2024-01-11"):
            if r["expiry"] == pd.Timestamp("2024-01-11"):
                r["close"] = 15.0 if r["option_type"] == "PE" else 8.0
            if r["expiry"] == pd.Timestamp("2024-02-01"):
                r["close"] = 25.0 if r["option_type"] == "CE" else 18.0

    fo = pd.DataFrame(rows)
    spot = pd.DataFrame(
        {
            "date": pd.to_datetime(
                ["2024-01-04", "2024-01-05", "2024-01-11"]
            ),
            "open": [20950.0, 21010.0, 21050.0],
        }
    )

    out = build_trades(fo, spot)

    assert len(out) >= 1
    t = out.iloc[0]
    assert t["entry_date"] == pd.Timestamp("2024-01-05")
    assert t["near_expiry"] == pd.Timestamp("2024-01-11")
    assert t["far_expiry"] == pd.Timestamp("2024-02-01")
    assert t["strike"] == 21000

    expected = (15 - 10) + (12 - 8) + (25 - 20) + (22 - 18)
    assert t["pnl_points"] == expected
