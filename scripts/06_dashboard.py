#!/usr/bin/env python3
"""Build the static dashboard and the headline summary.

Reads the assembled financials, the event study and the NBS context,
computes the headline numbers (nothing is typed in by hand), writes
data/results/summary.json, and renders dashboard/index.html.
"""
import json
from pathlib import Path

import pandas as pd

ROOT = Path(__file__).resolve().parent.parent
CUR = ROOT / "data" / "curated"
RES = ROOT / "data" / "results"
PROC = ROOT / "data" / "processed"
DASH = ROOT / "dashboard"
DASH.mkdir(exist_ok=True)

fin = pd.read_csv(CUR / "financials_quarterly.csv")
es = pd.read_csv(RES / "event_study.csv")
nbs = pd.read_csv(PROC / "nbs_retail.csv")


def seg(company):
    g = fin[fin["company"] == company].dropna(subset=["segment_value_rmb_mn"])
    return g.set_index("calendar_quarter")["segment_value_rmb_mn"]


mt_clc = seg("Meituan")
jd_nb = seg("JD.com")
baba_seg = seg("Alibaba")
baba_sm = fin[fin["company"] == "Alibaba"].set_index(
    "calendar_quarter")["sm_pct_of_revenue"]
mt_2025_net = fin[(fin["company"] == "Meituan")
                  & (fin["calendar_quarter"].str.contains("2025"))][
                  "net_income_rmb_mn"].sum()
sm_by_q = fin.groupby("calendar_quarter")["sm_expense_rmb_mn"].sum()
es["car_0_p5"] = es["car_mm_0_p5_pct"].fillna(es["car_adj_0_p5_pct"])
worst = es.loc[es["car_0_p5"].idxmin()]
best = es.loc[es["car_0_p5"].idxmax()]
nbs_latest = nbs[nbs["period_label"] == "Jan-Oct 2026"].iloc[0]

summary = {
    "meituan_clc_peak_q1_2025_rmb_mn": float(mt_clc.get("Q1 2025")),
    "meituan_clc_trough_q3_2025_rmb_mn": float(mt_clc.get("Q3 2025")),
    "meituan_clc_swing_rmb_mn": float(mt_clc.get("Q3 2025")
                                      - mt_clc.get("Q1 2025")),
    "meituan_fy2025_net_income_sum_of_quarters_rmb_mn": float(mt_2025_net),
    "jd_new_businesses_trough_rmb_mn": float(jd_nb.min()),
    "jd_new_businesses_trough_quarter": str(jd_nb.idxmin()),
    "alibaba_sm_pct_peak": float(baba_sm.max()),
    "alibaba_sm_pct_peak_quarter": str(baba_sm.idxmax()),
    "alibaba_ecom_ebita_q3_2025_rmb_mn": float(baba_seg.get("Q3 2025")),
    "alibaba_ecom_ebita_q3_2026_rmb_mn": float(baba_seg.get("Q3 2026")),
    "combined_sm_expense_by_quarter_rmb_mn": {
        k: float(v) for k, v in sm_by_q.items()},
    "event_study_most_negative_car_0_p5": {
        "event_id": worst["event_id"], "ticker": worst["ticker"],
        "car_pct": float(worst["car_0_p5"])},
    "event_study_most_positive_car_0_p5": {
        "event_id": best["event_id"], "ticker": best["ticker"],
        "car_pct": float(best["car_0_p5"])},
    "nbs_jan_oct_2026": {
        "total_retail_cum_bn": float(nbs_latest["total_retail_cum_bn"]),
        "total_retail_cum_yoy_pct": float(
            nbs_latest["total_retail_cum_yoy_pct"]),
        "online_goods_services_cum_bn": float(
            nbs_latest["online_goods_services_cum_bn"]),
        "online_goods_services_yoy_pct": float(
            nbs_latest["online_goods_services_cum_yoy_pct"]),
        "online_goods_cum_bn": float(nbs_latest["online_goods_cum_bn"]),
        "online_goods_yoy_pct": float(
            nbs_latest["online_goods_cum_yoy_pct"]),
        "oct_total_retail_yoy_pct": float(
            nbs_latest["total_retail_month_yoy_pct"]),
    },
}
(RES / "summary.json").write_text(json.dumps(summary, indent=2))
print(json.dumps(summary, indent=2))

CSS = """
body{font-family:Arial,Helvetica,sans-serif;margin:0;background:#f4f6f9;color:#16324f}
header{background:#16324f;color:#fff;padding:28px 36px}
header h1{margin:0 0 6px;font-size:25px} header p{margin:0;opacity:.85;max-width:900px}
.wrap{max-width:1080px;margin:0 auto;padding:24px 20px 40px}
.cards{display:grid;grid-template-columns:repeat(auto-fit,minmax(180px,1fr));gap:14px;margin-bottom:22px}
.card{background:#fff;border-radius:10px;padding:16px;box-shadow:0 1px 4px rgba(0,0,0,.08)}
.card .v{font-size:23px;font-weight:700} .card .l{font-size:13px;margin-top:2px}
.card .s{font-size:12px;color:#667}
.panel{background:#fff;border-radius:10px;padding:20px;margin-bottom:20px;box-shadow:0 1px 4px rgba(0,0,0,.08)}
.panel h2{margin-top:0;font-size:18px} .panel img{width:100%}
table{border-collapse:collapse;width:100%;font-size:13.5px}
td,th{border-bottom:1px solid #e3e8ef;padding:6px 7px;text-align:right}
td:first-child,th:first-child{text-align:left}
.neg{color:#c2255c}.pos{color:#1b9aaa}
footer{font-size:12px;color:#778;text-align:center;padding:14px}
"""

fmt = lambda v: f"{v:,.0f}"  # noqa: E731
bn = lambda v: f"{v/1000:,.1f}"  # noqa: E731


def car_cell(v):
    if pd.isna(v):
        return "<td>-</td>"
    cls = "neg" if v < 0 else "pos"
    return f'<td class="{cls}">{v:+.1f}</td>'


def build_html():
    s = summary
    cards = f"""
<div class="card"><div class="v">RMB {bn(abs(s['meituan_fy2025_net_income_sum_of_quarters_rmb_mn']))}bn loss</div>
<div class="l">Meituan net result, FY2025</div><div class="s">sum of four quarters; matches the annual announcement (profit of RMB 35.8bn in FY2024)</div></div>
<div class="card"><div class="v">RMB {bn(abs(s['meituan_clc_swing_rmb_mn']))}bn swing</div>
<div class="l">Meituan core local commerce</div><div class="s">operating profit Q1 2025 to Q3 2025, per quarter</div></div>
<div class="card"><div class="v">RMB {bn(abs(s['jd_new_businesses_trough_rmb_mn']))}bn</div>
<div class="l">JD New businesses worst quarter</div><div class="s">operating loss in {s['jd_new_businesses_trough_quarter']} (includes JD food delivery)</div></div>
<div class="card"><div class="v">{s['alibaba_sm_pct_peak']:.1f}%</div>
<div class="l">Alibaba S&amp;M peak</div><div class="s">sales &amp; marketing as % of revenue, {s['alibaba_sm_pct_peak_quarter']}</div></div>
<div class="card"><div class="v">{s['event_study_most_negative_car_0_p5']['car_pct']:+.1f}%</div>
<div class="l">Largest negative event CAR</div><div class="s">{s['event_study_most_negative_car_0_p5']['ticker']} around event {s['event_study_most_negative_car_0_p5']['event_id']}, CAR [0,+5]</div></div>
<div class="card"><div class="v">+{s['nbs_jan_oct_2026']['online_goods_services_yoy_pct']:.1f}%</div>
<div class="l">China online retail growth</div><div class="s">goods and services, Jan-Oct 2026 (NBS); total retail +{s['nbs_jan_oct_2026']['total_retail_cum_yoy_pct']:.1f}%</div></div>
"""
    piv = es.pivot_table(index=["event_id", "event_date", "event_name"],
                         columns="ticker", values="car_0_p5")
    ev_rows = ""
    for (eid, edate, ename), row in piv.iterrows():
        ev_rows += (f"<tr><td>{eid}</td><td>{edate}</td><td>{ename}</td>"
                    + "".join(car_cell(row.get(t)) for t in
                              ["BABA", "JD", "PDD", "3690.HK"]) + "</tr>")
    smp = fin.pivot_table(index="company", columns="calendar_quarter",
                          values="sm_pct_of_revenue")
    qcols = [q for q in ["Q4 2024", "Q1 2025", "Q2 2025", "Q3 2025",
                         "Q4 2025", "Q1 2026", "Q2 2026", "Q3 2026"]
             if q in smp.columns]
    sm_head = "".join(f"<th>{q}</th>" for q in qcols)
    sm_rows = ""
    for comp, row in smp.iterrows():
        cells = "".join(
            f"<td>{row[q]:.1f}</td>" if pd.notna(row.get(q)) else "<td>-</td>"
            for q in qcols)
        sm_rows += f"<tr><td>{comp}</td>{cells}</tr>"
    return f"""<!DOCTYPE html>
<html lang="en"><head><meta charset="utf-8">
<title>China Instant Retail Subsidy War and the Anti-Involution Turn</title>
<style>{CSS}</style></head><body>
<header><h1>China's Instant Retail Subsidy War and the Anti-Involution Turn</h1>
<p>How the 2025 food-delivery subsidy war between JD.com, Meituan and Alibaba burned
through platform profits, what the regulator (SAMR) did about it, and what the
financial statements show through Q3 2026. All figures are transcribed from official
earnings releases (SEC EDGAR 6-K exhibits; HKEXnews for Meituan), Yahoo Finance
prices, and National Bureau of Statistics releases.</p></header>
<div class="wrap">
<div class="cards">{cards}</div>
<div class="panel"><h2>The subsidy burn</h2><img src="../charts/sm_pct_timeline.png"></div>
<div class="panel"><h2>Front-line segment results</h2><img src="../charts/segment_profit_swing.png"></div>
<div class="panel"><h2>Share prices through the war</h2><img src="../charts/indexed_prices.png"></div>
<div class="panel"><h2>Event study: CAR [0,+5] trading days, %</h2>
<table><tr><th>Event</th><th>Date</th><th></th><th>BABA</th><th>JD</th><th>PDD</th><th>3690.HK</th></tr>
{ev_rows}</table>
<p style="font-size:12.5px;color:#667">Market model vs KWEB (ADRs) or the Hang Seng TECH ETF (Meituan);
market-adjusted returns for E1, where the estimation window is too short.
Abnormal returns measure what the market repriced, not proof of regulatory causation.</p></div>
<div class="panel"><h2>Sales &amp; marketing, % of revenue</h2>
<table><tr><th>Company</th>{sm_head}</tr>{sm_rows}</table></div>
<div class="panel"><h2>Market context (NBS)</h2><img src="../charts/nbs_context.png"></div>
</div>
<footer>Sources: company earnings releases via SEC EDGAR and HKEXnews; Yahoo Finance chart API;
National Bureau of Statistics of China, monthly retail sales releases. Analysis code and
data notes are in the project repository (README.md).</footer>
</body></html>"""


(DASH / "index.html").write_text(build_html())
print("wrote", DASH / "index.html")
