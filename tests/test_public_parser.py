import pandas as pd

from scripts.prepare_public_2022_2024 import parse_options_vectorized


def test_public_cp_ticker_schema():
    raw = pd.DataFrame(
        {
            "Ticker": [
                "NIFTY04JAN24C18300",
                "NIFTY04JAN24P18300",
                "NIFTY04JAN24C18350",
            ],
            "Date/Time": pd.to_datetime(
                [
                    "2024-01-02 09:15:00",
                    "2024-01-02 09:15:00",
                    "2024-01-02 09:16:00",
                ]
            ),
            "Open": [100.0, 110.0, 95.0],
            "Close": [101.0, 109.0, 96.0],
            "Volume": [1.0, 1.0, 1.0],
            "Open Interest": [10.0, 10.0, 10.0],
        }
    )
    out = parse_options_vectorized(raw)
    assert len(out) == 3
    assert set(out["option_type"]) == {"C", "P"}
    assert set(out["strike"]) == {18300.0, 18350.0}
    assert str(out.iloc[0]["expiry"].date()) == "2024-01-04"
