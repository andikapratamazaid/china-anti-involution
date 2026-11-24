#!/usr/bin/env python3
"""Event study: abnormal returns around the subsidy-war policy events.

Reads data/processed/prices_daily.csv and data/curated/events.csv.
Benchmarks: KWEB for the US-listed ADRs (BABA, JD, PDD); 3067.HK
(iShares Hang Seng TECH ETF, the tradable tracker of the Hang Seng
TECH Index) for Meituan (3690.HK), which trades in Hong Kong.

For every event and stock, day 0 is the first trading day of that stock
on or after the event date (events announced on weekends or after the
close are therefore measured from the next session). Two abnormal
return definitions are reported:
  * market-adjusted: AR = R_stock - R_benchmark (same trading day)
  * market model:    AR = R_stock - (alpha + beta * R_benchmark),
    with alpha/beta estimated over trading days [-130, -11] relative to
    day 0; reported only when at least 60 estimation days exist.
CARs are computed for windows [-1, +1] and [0, +5] trading days.
Output: data/results/event_study.csv.
"""
from pathlib import Path

import numpy as np
import pandas as pd

ROOT = Path(__file__).resolve().parent.parent
PROC = ROOT / "data" / "processed"
CUR = ROOT / "data" / "curated"
RES = ROOT / "data" / "results"
RES.mkdir(parents=True, exist_ok=True)

BENCHMARK = {"BABA": "KWEB", "JD": "KWEB", "PDD": "KWEB",
             "3690.HK": "3067.HK"}
STOCKS = list(BENCHMARK)


def returns_frame(prices: pd.DataFrame, ticker: str) -> pd.DataFrame:
    # Adjusted closes, so dividend ex-dates (e.g. Alibaba's annual
    # dividend each June) do not masquerade as abnormal returns.
    g = prices[prices["ticker"] == ticker].sort_values("date")
    g = g[["date", "adj_close"]].rename(columns={"adj_close": "close"})
    g["ret"] = np.log(g["close"] / g["close"].shift(1))
    return g.reset_index(drop=True)


def car_for_event(stock: pd.DataFrame, bench: pd.DataFrame,
                  event_date: pd.Timestamp) -> dict | None:
    merged = stock.merge(bench, on="date", suffixes=("", "_b"))
    merged = merged.dropna(subset=["ret", "ret_b"]).reset_index(drop=True)
    pos = merged.index[merged["date"] >= event_date]
    if len(pos) == 0 or pos[0] + 5 >= len(merged):
        return None
    i0 = int(pos[0])
    out = {"day0_date": merged.loc[i0, "date"].date().isoformat()}

    ar_adj = merged["ret"] - merged["ret_b"]
    est = merged.iloc[max(0, i0 - 130): i0 - 10]
    if len(est) >= 60:
        x = est["ret_b"].to_numpy()
        y = est["ret"].to_numpy()
        beta, alpha = np.polyfit(x, y, 1)
        ar_mm = merged["ret"] - (alpha + beta * merged["ret_b"])
        out["beta"] = round(float(beta), 3)
        out["est_days"] = len(est)
    else:
        ar_mm = pd.Series(np.nan, index=merged.index)
        out["beta"] = np.nan
        out["est_days"] = len(est)

    for label, a, b in [("m1_p1", -1, 1), ("0_p5", 0, 5)]:
        seg_adj = ar_adj.iloc[i0 + a: i0 + b + 1]
        seg_mm = ar_mm.iloc[i0 + a: i0 + b + 1]
        out[f"car_adj_{label}_pct"] = round(float(seg_adj.sum()) * 100, 2)
        out[f"car_mm_{label}_pct"] = (
            round(float(seg_mm.sum()) * 100, 2)
            if seg_mm.notna().all() else np.nan)
    return out


def main():
    prices = pd.read_csv(PROC / "prices_daily.csv", parse_dates=["date"])
    events = pd.read_csv(CUR / "events.csv", parse_dates=["event_date"])
    frames = {t: returns_frame(prices, t)
              for t in set(STOCKS) | set(BENCHMARK.values())}
    rows = []
    for _, ev in events.iterrows():
        for stock in STOCKS:
            res = car_for_event(frames[stock], frames[BENCHMARK[stock]],
                                ev["event_date"])
            if res is None:
                continue
            rows.append({
                "event_id": ev["event_id"],
                "event_date": ev["event_date"].date().isoformat(),
                "event_name": ev["event_name"],
                "ticker": stock,
                "benchmark": BENCHMARK[stock],
                **res,
            })
    out = pd.DataFrame(rows)
    dest = RES / "event_study.csv"
    out.to_csv(dest, index=False)
    print(out.to_string(index=False))
    print("wrote", dest, len(out), "rows")


if __name__ == "__main__":
    main()
