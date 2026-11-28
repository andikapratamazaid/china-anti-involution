"""Consistency tests for the China anti-involution project.

The financial anchors below are taken from the companies' official
earnings releases (the same filings the curated CSV was transcribed
from), so the tests fail if the transcription or assembly drifts.
"""
import json
from pathlib import Path

import pandas as pd
import pytest

ROOT = Path(__file__).resolve().parent.parent
CUR = ROOT / "data" / "curated"
PROC = ROOT / "data" / "processed"
RES = ROOT / "data" / "results"

ALL_QUARTERS = ["Q4 2024", "Q1 2025", "Q2 2025", "Q3 2025", "Q4 2025",
                "Q1 2026", "Q2 2026", "Q3 2026"]


@pytest.fixture(scope="module")
def fin():
    return pd.read_csv(CUR / "financials_quarterly.csv")


def test_quarters_present(fin):
    for comp in ("Alibaba", "JD.com", "PDD Holdings", "Meituan"):
        qs = set(fin[fin["company"] == comp]["calendar_quarter"])
        assert qs == set(ALL_QUARTERS), comp


def test_every_row_has_a_source(fin):
    assert fin["source"].notna().all()
    assert (fin["source"].str.len() > 10).all()
    assert fin["revenue_rmb_mn"].notna().all()


def test_sm_pct_recomputation(fin):
    recomputed = (fin["sm_expense_rmb_mn"] / fin["revenue_rmb_mn"]
                  * 100).round(2)
    assert (abs(recomputed - fin["sm_pct_of_revenue"]) < 0.011).all()


def test_alibaba_anchor_q3_2026(fin):
    r = fin[(fin["company"] == "Alibaba")
            & (fin["calendar_quarter"] == "Q3 2026")].iloc[0]
    assert r["revenue_rmb_mn"] == 271519
    assert r["revenue_yoy_pct"] == 10
    assert r["segment_value_rmb_mn"] == 38851  # e-commerce adj. EBITA


def test_meituan_fy2025_anchor(fin):
    mt = fin[fin["company"] == "Meituan"]
    fy_net = mt[mt["calendar_quarter"].str.contains("2025")][
        "net_income_rmb_mn"].sum()
    # FY2025 annual announcement: loss for the year RMB 23,354M.
    assert abs(fy_net - (-23354)) <= 3
    clc = mt.set_index("calendar_quarter")["segment_value_rmb_mn"]
    assert clc["Q1 2025"] == 13491
    assert clc["Q3 2025"] == -14071


def test_meituan_q3_2026_anchor(fin):
    r = fin[(fin["company"] == "Meituan")
            & (fin["calendar_quarter"] == "Q3 2026")].iloc[0]
    # Announcement of the Results for the Three Months Ended
    # September 30 2026 (HKEXnews filing) - 2026-11-27. Filing figures
    # are in RMB thousands and are rounded to the nearest RMB million.
    assert r["revenue_rmb_mn"] == 115556
    assert r["revenue_yoy_pct"] == 21.6
    assert r["sm_expense_rmb_mn"] == 27023
    assert r["operating_profit_rmb_mn"] == 2741
    assert r["adj_ebita_rmb_mn"] == 4581  # Adjusted EBITDA, Non-IFRS
    assert r["net_income_rmb_mn"] == 2071
    assert r["segment_value_rmb_mn"] == 5704  # Core local commerce
    # S&M was 23.4% of revenue, down from 35.6% in Q3 2025.
    assert abs(r["sm_pct_of_revenue"] - 23.39) < 0.011


def test_jd_new_businesses_anchor(fin):
    jd = fin[fin["company"] == "JD.com"].set_index("calendar_quarter")
    assert jd.loc["Q4 2024", "segment_value_rmb_mn"] == -885
    assert jd.loc["Q3 2025", "segment_value_rmb_mn"] == -15736
    assert jd["segment_value_rmb_mn"].idxmin() == "Q3 2025"


def test_pdd_q3_2026_anchor(fin):
    r = fin[(fin["company"] == "PDD Holdings")
            & (fin["calendar_quarter"] == "Q3 2026")].iloc[0]
    assert r["revenue_rmb_mn"] == 108341
    assert r["operating_profit_rmb_mn"] == 31164
    # The release states no revenue YoY % for this quarter (it gives
    # the level vs the same quarter of 2025 instead); the cell must
    # stay empty rather than carry an estimate.
    assert pd.isna(r["revenue_yoy_pct"])


def test_event_study_windows():
    es = pd.read_csv(RES / "event_study.csv", parse_dates=["event_date",
                                                          "day0_date"])
    assert len(es) == 36  # 9 events x 4 stocks
    assert es["car_adj_0_p5_pct"].notna().all()
    assert es["car_adj_m1_p1_pct"].notna().all()
    gap = (es["day0_date"] - es["event_date"]).dt.days
    assert (gap >= 0).all() and (gap <= 4).all()
    px = pd.read_csv(PROC / "prices_daily.csv", parse_dates=["date"])
    trading = {(t, d) for t, d in zip(px["ticker"], px["date"])}
    for _, r in es.iterrows():
        assert (r["ticker"], r["day0_date"]) in trading


def test_prices_coverage():
    px = pd.read_csv(PROC / "prices_daily.csv", parse_dates=["date"])
    counts = px.groupby("ticker").size()
    for t in ("BABA", "JD", "PDD", "3690.HK", "KWEB", "3067.HK"):
        assert counts[t] >= 480, t
    assert px["date"].min() <= pd.Timestamp("2024-12-05")
    assert px["date"].max() >= pd.Timestamp("2026-11-20")
    assert px["close"].notna().all() and (px["close"] > 0).all()


def test_nbs_anchors_and_consistency():
    nbs = pd.read_csv(PROC / "nbs_retail.csv")
    latest = nbs[nbs["period_label"] == "Jan-Oct 2026"].iloc[0]
    assert latest["total_retail_cum_bn"] == 41646.4
    assert latest["online_goods_services_cum_bn"] == 16981.1
    assert latest["online_goods_services_cum_yoy_pct"] == 3.7
    assert latest["online_goods_cum_bn"] == 10727.4
    assert latest["total_retail_month_yoy_pct"] == 0.4
    # Computed online share must agree with the share NBS publishes.
    sub = nbs.dropna(subset=["online_share_published_pct"])
    assert len(sub) >= 15
    diff = (sub["online_share_of_total_pct"]
            - sub["online_share_published_pct"]).abs()
    assert (diff < 0.15).all()
    # Cumulative totals rise monotonically inside each calendar year.
    nbs["year"] = nbs["period_end"].str[:4]
    for _, g in nbs.groupby("year"):
        assert g["total_retail_cum_bn"].is_monotonic_increasing


def test_summary_and_outputs_exist():
    s = json.loads((RES / "summary.json").read_text())
    assert s["meituan_clc_trough_q3_2025_rmb_mn"] == -14071
    assert s["jd_new_businesses_trough_rmb_mn"] == -15736
    assert abs(s["meituan_fy2025_net_income_sum_of_quarters_rmb_mn"]
               - (-23354)) <= 3
    for name in ("sm_pct_timeline.png", "segment_profit_swing.png",
                 "event_study_car.png", "nbs_context.png",
                 "indexed_prices.png"):
        p = ROOT / "charts" / name
        assert p.exists() and p.stat().st_size > 10000, name
    assert (ROOT / "dashboard" / "index.html").exists()
    tr = pd.read_csv(RES / "sm_tracker.csv")
    assert len(tr) == 32  # 8 quarters x 4 companies
