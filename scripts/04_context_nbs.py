#!/usr/bin/env python3
"""Market context from China's National Bureau of Statistics (NBS).

Reads data/curated/nbs_releases.csv (the list of official English
press releases, one per cumulative period), downloads each release
into data/raw/nbs/ (cached), and extracts the figures NBS publishes:
  * cumulative total retail sales of consumer goods (RMB bn) and YoY %
  * cumulative online retail sales of goods (RMB bn) and YoY %
  * cumulative online retail sales of goods and services, where the
    release reports it (published from 2025 onwards)
  * the single-month total retail sales value and YoY %, where the
    release's table reports it (not published for Jan-Feb)

Monthly values are then derived ONLY by differencing consecutive
cumulative figures inside the same calendar year; every derived row
records how many months it spans (the Jan-Feb release is a two-month
block because NBS does not publish January separately, and any gap in
the collected releases widens the span). No interpolation is done.

Output: data/processed/nbs_retail.csv (cumulative as published) and
data/results/nbs_monthly_derived.csv.
"""
import re
from pathlib import Path

import pandas as pd
import requests

ROOT = Path(__file__).resolve().parent.parent
CUR = ROOT / "data" / "curated"
RAW = ROOT / "data" / "raw" / "nbs"
PROC = ROOT / "data" / "processed"
RES = ROOT / "data" / "results"
for d in (RAW, PROC, RES):
    d.mkdir(parents=True, exist_ok=True)
HEADERS = {"User-Agent": "Mozilla/5.0 (research project)"}


def fetch(url: str, slug: str) -> str:
    cache = RAW / f"{slug}.html"
    if not cache.exists():
        r = requests.get(url, headers=HEADERS, timeout=60)
        r.raise_for_status()
        cache.write_text(r.text, encoding="utf-8")
    return cache.read_text(encoding="utf-8", errors="ignore")


def to_text(html_doc: str) -> str:
    t = re.sub(r"<script.*?</script>|<style.*?</style>", " ", html_doc,
               flags=re.S)
    t = re.sub(r"<[^>]+>", " ", t)
    t = t.replace("\xa0", " ").replace("&nbsp;", " ")
    return re.sub(r"\s+", " ", t)


def num(s: str) -> float:
    return float(s.replace(",", ""))


def extract(text: str) -> dict:
    """Pull the published figures out of one release's text.

    Cumulative figures are anchored to the releases' cumulative
    sentences ("From January to October, ... reached ..."), because
    the same releases also contain single-month sentences with almost
    identical wording. Terminology changed over the sample: 2024-2025
    releases say "online retail sales" (total) and "online retail
    sales of physical goods"; 2026 releases say "online retail sales
    of goods and services" and "online retail sales of goods". Both
    wordings are mapped to the same two concepts.
    """
    out = {}
    m = re.search(
        r"From January to \w+(?: \d{4})?, the total retail sales of "
        r"consumer goods (?:reached|was) ([\d,]+\.?\d*) billion yuan, "
        r"up by ([\d.]+)\s*(?:%|percent)", text)
    if m:
        out["total_retail_cum_bn"] = num(m.group(1))
        out["total_retail_cum_yoy_pct"] = num(m.group(2))
    m = re.search(
        r"online retail sales of goods and services reached "
        r"([\d,]+\.?\d*) billion yuan, up by ([\d.]+)\s*(?:%|percent)", text)
    if not m:
        m = re.search(
            r"(?:national )?online retail sales(?: nationwide)? reached "
            r"([\d,]+\.?\d*) billion yuan, (?:up by|a year-on-year "
            r"increase of) ([\d.]+)\s*(?:%|percent)", text)
    if m:
        out["online_goods_services_cum_bn"] = num(m.group(1))
        out["online_goods_services_cum_yoy_pct"] = num(m.group(2))
    m = re.search(
        r"online retail sales of (?:physical )?goods (?:were|reached) "
        r"([\d,]+\.?\d*) billion yuan, (?:up by|up|a year-on-year increase "
        r"of) ([\d.]+)\s*(?:%|percent)(?: year on year| over the previous "
        r"year)?(?:, accounting for ([\d.]+)\s*(?:%|percent) of the total "
        r"retail sales)?", text)
    if m:
        out["online_goods_cum_bn"] = num(m.group(1))
        out["online_goods_cum_yoy_pct"] = num(m.group(2))
        if m.lastindex and m.lastindex >= 3 and m.group(3):
            out["online_share_published_pct"] = num(m.group(3))
    # Single-month total retail from the narrative ("In October, the
    # total retail sales of consumer goods reached 4,646.3 billion
    # yuan, up by 0.4%") - not published for the Jan-Feb release.
    m = re.search(
        r"In \w+, the total retail sales of consumer goods reached "
        r"([\d,]+\.?\d*) billion yuan, up by ([\d.]+)\s*(?:%|percent)", text)
    if m:
        out["total_retail_month_bn"] = num(m.group(1))
        out["total_retail_month_yoy_pct"] = num(m.group(2))
    # Table row fallback: "Total retail sales of consumer goods
    # 46463 0.4 416464 1.0" (month value, month YoY, cumulative value
    # in 100 million yuan, cumulative YoY).
    m = re.search(r"Total retail sales of consumer goods "
                  r"([\d,]+) (-?[\d.]+) ([\d,]+) (-?[\d.]+)", text)
    if m:
        out.setdefault("total_retail_month_bn", num(m.group(1)) / 10)
        out.setdefault("total_retail_month_yoy_pct", num(m.group(2)))
        out.setdefault("total_retail_cum_bn", num(m.group(3)) / 10)
        out.setdefault("total_retail_cum_yoy_pct", num(m.group(4)))
    m = re.search(r"Online retail sales of goods - - ([\d,]+) (-?[\d.]+)",
                  text)
    if m:
        out.setdefault("online_goods_cum_bn", num(m.group(1)) / 10)
        out.setdefault("online_goods_cum_yoy_pct", num(m.group(2)))
    return out


def main():
    rel = pd.read_csv(CUR / "nbs_releases.csv")
    rows = []
    for _, r in rel.iterrows():
        slug = r["period_end"].replace("-", "")
        vals = extract(to_text(fetch(r["url"], slug)))
        rows.append({"period_label": r["period_label"],
                     "period_end": r["period_end"], "source_url": r["url"],
                     **vals})
        print(r["period_label"], {k: v for k, v in vals.items()})
    df = pd.DataFrame(rows)
    df["online_share_of_total_pct"] = (
        df["online_goods_cum_bn"] / df["total_retail_cum_bn"] * 100).round(1)
    dest = PROC / "nbs_retail.csv"
    df.to_csv(dest, index=False)
    print("wrote", dest, len(df), "rows")

    # Derive monthly values by differencing cumulative figures within
    # each calendar year; record the span of each derived block.
    recs = []
    df["year"] = df["period_end"].str[:4]
    df["end_month"] = df["period_end"].str[5:7].astype(int)
    for year, g in df.sort_values("end_month").groupby("year"):
        prev_m, prev_t, prev_o = 0, 0.0, 0.0
        for _, r in g.iterrows():
            span = int(r["end_month"]) - prev_m
            recs.append({
                "year": year, "period_end": r["period_end"],
                "months_spanned": span,
                "total_retail_bn": round(r["total_retail_cum_bn"] - prev_t, 1),
                "online_goods_bn": round(r["online_goods_cum_bn"] - prev_o, 1),
            })
            prev_m, prev_t, prev_o = (int(r["end_month"]),
                                      r["total_retail_cum_bn"],
                                      r["online_goods_cum_bn"])
    md = pd.DataFrame(recs)
    md.to_csv(RES / "nbs_monthly_derived.csv", index=False)
    print(md.to_string(index=False))


if __name__ == "__main__":
    main()
