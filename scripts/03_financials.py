#!/usr/bin/env python3
"""Assemble the hand-extracted company financials and build the
subsidy-burn tracker.

Inputs: data/curated/financials_baba.csv, financials_jd.csv,
financials_pdd.csv, financials_meituan.csv - one row per
company-quarter, every value transcribed from the company's official
earnings release (SEC EDGAR 6-K exhibits for BABA/JD/PDD, HKEXnews
announcements for Meituan), each row carrying its source.

Outputs:
  data/curated/financials_quarterly.csv - combined file with the
    computed column sm_pct_of_revenue (sales & marketing expense as a
    percentage of revenue, computed only from the two disclosed inputs)
  data/results/sm_tracker.csv - the tracker used by the charts:
    S&M % of revenue and the food-delivery segment operating line by
    company-quarter, plus each company's S&M % change vs its pre-war
    baseline quarter (Q4 2024).
"""
import re
from pathlib import Path

import pandas as pd

ROOT = Path(__file__).resolve().parent.parent
CUR = ROOT / "data" / "curated"
RES = ROOT / "data" / "results"
RES.mkdir(parents=True, exist_ok=True)

FILES = ["financials_baba.csv", "financials_jd.csv",
         "financials_pdd.csv", "financials_meituan.csv"]
QORDER = {q: i for i, q in enumerate(
    ["Q4 2024", "Q1 2025", "Q2 2025", "Q3 2025", "Q4 2025",
     "Q1 2026", "Q2 2026", "Q3 2026"])}


def main():
    frames = []
    for f in FILES:
        p = CUR / f
        if not p.exists():
            raise SystemExit(f"missing curated input: {p}")
        frames.append(pd.read_csv(p))
    df = pd.concat(frames, ignore_index=True)
    # Normalise labelling differences between the four extraction
    # files: quarter written as "2025Q1" becomes "Q1 2025", and
    # "Alibaba Group" is shortened to "Alibaba".
    def norm_quarter(q):
        m = re.match(r"^(\d{4})Q([1-4])$", str(q))
        return f"Q{m.group(2)} {m.group(1)}" if m else q
    df["calendar_quarter"] = df["calendar_quarter"].map(norm_quarter)
    df["company"] = df["company"].replace({"Alibaba Group": "Alibaba"})
    df["sm_pct_of_revenue"] = (
        df["sm_expense_rmb_mn"] / df["revenue_rmb_mn"] * 100).round(2)
    df["qsort"] = df["calendar_quarter"].map(QORDER)
    df = df.sort_values(["company", "qsort"]).drop(columns="qsort")
    dest = CUR / "financials_quarterly.csv"
    df.to_csv(dest, index=False)
    print(f"combined {len(df)} company-quarters -> {dest}")

    base = (df[df["calendar_quarter"] == "Q4 2024"]
            .set_index("company")["sm_pct_of_revenue"])
    tr = df[["company", "ticker", "calendar_quarter", "period_end",
             "revenue_rmb_mn", "revenue_yoy_pct", "sm_expense_rmb_mn",
             "sm_pct_of_revenue", "operating_profit_rmb_mn",
             "net_income_rmb_mn", "segment_name", "segment_metric_name",
             "segment_value_rmb_mn"]].copy()
    tr["sm_pct_vs_q4_2024_pp"] = (
        tr["sm_pct_of_revenue"] - tr["company"].map(base)).round(2)
    tr["segment_value_rmb_bn"] = (tr["segment_value_rmb_mn"] / 1000).round(2)
    dest2 = RES / "sm_tracker.csv"
    tr.to_csv(dest2, index=False)
    print(tr[["company", "calendar_quarter", "sm_pct_of_revenue",
              "sm_pct_vs_q4_2024_pp", "segment_value_rmb_bn"]]
          .to_string(index=False))
    print("wrote", dest2)


if __name__ == "__main__":
    main()
