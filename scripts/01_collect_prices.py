#!/usr/bin/env python3
"""Collect daily stock prices from the Yahoo Finance chart API.

Tickers: BABA, JD, PDD (NYSE ADRs), 3690.HK (Meituan, HKEX) and two
benchmarks: KWEB (KraneShares China Internet ETF) for the ADRs and
3067.HK (iShares Hang Seng TECH ETF) for Meituan. Raw JSON responses are
cached under data/raw/ and parsed closes are written to
data/processed/prices_daily.csv (one row per ticker-date).
"""
import json
import time
from pathlib import Path

import pandas as pd
import requests

ROOT = Path(__file__).resolve().parent.parent
RAW = ROOT / "data" / "raw"
PROC = ROOT / "data" / "processed"
RAW.mkdir(parents=True, exist_ok=True)
PROC.mkdir(parents=True, exist_ok=True)

TICKERS = ["BABA", "JD", "PDD", "3690.HK", "KWEB", "3067.HK"]
# 2024-12-01 to 2026-11-24 (build date); the window starts ~2 months
# before the first event (JD food-delivery launch, 11 Feb 2025) so the
# event study has pre-event trading days for every event.
PERIOD1 = 1733011200  # 2024-12-01 UTC
PERIOD2 = 1795564800  # 2026-11-25 UTC
HEADERS = {"User-Agent": "Mozilla/5.0 (research project)"}


def fetch(ticker: str) -> pd.DataFrame:
    cache = RAW / f"yahoo_{ticker.replace('.', '_')}.json"
    if cache.exists():
        payload = json.loads(cache.read_text())
    else:
        from urllib.parse import quote
        url = (f"https://query1.finance.yahoo.com/v8/finance/chart/"
               f"{quote(ticker, safe='')}"
               f"?period1={PERIOD1}&period2={PERIOD2}&interval=1d")
        r = requests.get(url, headers=HEADERS, timeout=60)
        r.raise_for_status()
        payload = r.json()
        cache.write_text(json.dumps(payload))
        time.sleep(1)
    result = payload["chart"]["result"][0]
    ts = result["timestamp"]
    quote = result["indicators"]["quote"][0]
    adj = result["indicators"].get("adjclose", [{}])[0].get("adjclose")
    df = pd.DataFrame({
        "date": pd.to_datetime(ts, unit="s", utc=True).tz_convert(
            result["meta"].get("exchangeTimezoneName", "UTC")).date,
        "ticker": ticker,
        "open": quote["open"],
        "high": quote["high"],
        "low": quote["low"],
        "close": quote["close"],
        "adj_close": adj if adj is not None else quote["close"],
        "volume": quote["volume"],
    })
    return df.dropna(subset=["close"])


def main():
    frames = [fetch(t) for t in TICKERS]
    out = pd.concat(frames, ignore_index=True)
    out["date"] = pd.to_datetime(out["date"])
    out = out.sort_values(["ticker", "date"])
    dest = PROC / "prices_daily.csv"
    out.to_csv(dest, index=False, date_format="%Y-%m-%d")
    for t, g in out.groupby("ticker"):
        print(f"{t}: {len(g)} rows, {g['date'].min().date()} to "
              f"{g['date'].max().date()}")
    print("wrote", dest, len(out), "rows")


if __name__ == "__main__":
    main()
