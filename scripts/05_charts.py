#!/usr/bin/env python3
"""Render all charts from the result files, so every visual is a real
output of the analysis (no hand-drawn numbers)."""
from pathlib import Path

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import pandas as pd

ROOT = Path(__file__).resolve().parent.parent
RES = ROOT / "data" / "results"
PROC = ROOT / "data" / "processed"
CUR = ROOT / "data" / "curated"
CH = ROOT / "charts"
CH.mkdir(exist_ok=True)
NAVY, TEAL, ORANGE, GREY = "#16324f", "#1b9aaa", "#ef476f", "#8d99ae"
COLORS = {"Alibaba": NAVY, "JD.com": ORANGE, "Meituan": TEAL,
          "PDD Holdings": "#e0a458"}
plt.rcParams.update({"font.size": 10, "axes.edgecolor": "#cccccc",
                     "axes.labelcolor": NAVY, "text.color": NAVY,
                     "xtick.color": "#444444", "ytick.color": "#444444"})
QUARTERS = ["Q4 2024", "Q1 2025", "Q2 2025", "Q3 2025", "Q4 2025",
            "Q1 2026", "Q2 2026", "Q3 2026"]


def save(fig, name):
    fig.tight_layout()
    fig.savefig(CH / name, dpi=150)
    plt.close(fig)
    print(name)


def main():
    fin = pd.read_csv(CUR / "financials_quarterly.csv")
    fin["qi"] = fin["calendar_quarter"].map(
        {q: i for i, q in enumerate(QUARTERS)})

    # 1. Subsidy-burn tracker: S&M as % of revenue
    fig, ax = plt.subplots(figsize=(10, 4.4))
    for comp, g in fin.groupby("company"):
        g = g.sort_values("qi")
        ax.plot(g["qi"], g["sm_pct_of_revenue"], "o-", lw=2,
                color=COLORS.get(comp), label=comp)
    ax.axvspan(1.5, 4.5, color=ORANGE, alpha=0.07)
    ax.text(3.0, ax.get_ylim()[0] + 0.4, "peak subsidy war\n2025",
            ha="center", fontsize=8.5, color="#b03a5b")
    ax.set_xticks(range(len(QUARTERS)))
    ax.set_xticklabels(QUARTERS, rotation=30, ha="left", fontsize=8.5)
    ax.set_ylabel("Sales & marketing, % of revenue")
    ax.set_title("The subsidy burn: sales & marketing intensity by quarter")
    ax.legend(frameon=False, ncol=4, fontsize=9)
    save(fig, "sm_pct_timeline.png")

    # 2. Segment profit swing (food-delivery front lines)
    seg = fin.dropna(subset=["segment_value_rmb_mn"]).copy()
    seg["bn"] = seg["segment_value_rmb_mn"] / 1000
    panels = [("Meituan", "Core local commerce operating profit"),
              ("JD.com", "New businesses operating profit"),
              ("Alibaba", "China e-commerce adj. EBITA")]
    fig, axes = plt.subplots(1, 3, figsize=(11, 3.8), sharex=True)
    for ax, (comp, title) in zip(axes, panels):
        g = seg[seg["company"] == comp].sort_values("qi")
        cols = [ORANGE if v < 0 else TEAL for v in g["bn"]]
        ax.bar(g["qi"], g["bn"], color=cols, width=0.65)
        ax.axhline(0, color=NAVY, lw=0.8)
        ax.set_title(title, fontsize=9.5)
        ax.set_xticks(range(len(QUARTERS)))
        ax.set_xticklabels([q.replace(" 20", "\n") for q in QUARTERS],
                           fontsize=7.5)
    axes[0].set_ylabel("RMB billion per quarter")
    fig.suptitle("Front-line segment results: the swing into loss and back",
                 fontsize=11, color=NAVY)
    save(fig, "segment_profit_swing.png")

    # 3. Event study CARs [0,+5]
    es = pd.read_csv(RES / "event_study.csv")
    es["car"] = es["car_mm_0_p5_pct"].fillna(es["car_adj_0_p5_pct"])
    piv = es.pivot_table(index="event_id", columns="ticker", values="car")
    order = ["BABA", "JD", "PDD", "3690.HK"]
    piv = piv[order]
    fig, ax = plt.subplots(figsize=(10, 4.6))
    x = range(len(piv))
    w = 0.2
    for i, t in enumerate(order):
        ax.bar([v + (i - 1.5) * w for v in x], piv[t], width=w,
               label=t, color=[NAVY, ORANGE, "#e0a458", TEAL][i])
    ax.axhline(0, color=NAVY, lw=0.8)
    ax.set_xticks(list(x))
    ax.set_xticklabels([f"{e}\n{d[5:]}" for e, d in
                        zip(es.drop_duplicates('event_id')['event_id'],
                            es.drop_duplicates('event_id')['event_date'])],
                       fontsize=8)
    ax.set_ylabel("CAR [0,+5] trading days, %")
    ax.set_title("Event study: cumulative abnormal returns around policy events\n"
                 "(market model vs KWEB / Hang Seng TECH ETF; market-adjusted for E1)")
    ax.legend(frameon=False, ncol=4, fontsize=9)
    save(fig, "event_study_car.png")

    # 4. NBS context: growth and online share
    nbs = pd.read_csv(PROC / "nbs_retail.csv", parse_dates=["period_end"])
    nbs = nbs.sort_values("period_end")
    fig, axes = plt.subplots(1, 2, figsize=(11, 3.9))
    axes[0].plot(nbs["period_end"], nbs["online_goods_cum_yoy_pct"], "o-",
                 color=TEAL, lw=2, label="Online retail, goods")
    axes[0].plot(nbs["period_end"], nbs["total_retail_cum_yoy_pct"], "o-",
                 color=NAVY, lw=2, label="Total retail sales")
    axes[0].set_title("Cumulative YoY growth, % (NBS)", fontsize=10)
    axes[0].legend(frameon=False, fontsize=8.5)
    share = nbs["online_share_published_pct"].fillna(
        nbs["online_share_of_total_pct"])
    axes[1].plot(nbs["period_end"], share, "o-", color=ORANGE, lw=2)
    axes[1].set_title("Online goods share of total retail, % (NBS)",
                      fontsize=10)
    for ax in axes:
        ax.tick_params(axis="x", labelsize=8, rotation=0)
    fig.suptitle("Market context: online kept outgrowing a slowing high street",
                 fontsize=11, color=NAVY)
    save(fig, "nbs_context.png")

    # 5. Indexed share prices with key events
    px = pd.read_csv(PROC / "prices_daily.csv", parse_dates=["date"])
    fig, ax = plt.subplots(figsize=(11, 4.4))
    labels = {"BABA": "Alibaba (BABA)", "JD": "JD.com (JD)",
              "PDD": "PDD (PDD)", "3690.HK": "Meituan (3690.HK)"}
    cols = {"BABA": NAVY, "JD": ORANGE, "PDD": "#e0a458", "3690.HK": TEAL}
    base_date = pd.Timestamp("2024-12-31")
    for t, lab in labels.items():
        g = px[px["ticker"] == t].sort_values("date")
        g = g[g["date"] >= "2024-12-20"]
        base = g[g["date"] <= base_date]["close"].iloc[-1]
        ax.plot(g["date"], g["close"] / base * 100, lw=1.4,
                color=cols[t], label=lab)
    for d, lab in [("2025-02-11", "E1 JD launch"),
                   ("2025-08-01", "E4 pledge"),
                   ("2026-04-17", "E7 fines"),
                   ("2026-06-17", "E8 draft rules")]:
        ax.axvline(pd.Timestamp(d), color=GREY, lw=0.8, ls="--")
        ax.text(pd.Timestamp(d), ax.get_ylim()[1] * 0.99, " " + lab,
                fontsize=8, color="#555555", va="top")
    ax.set_ylabel("Indexed close, 31 Dec 2024 = 100")
    ax.set_title("Share prices through the subsidy war (indexed)")
    ax.legend(frameon=False, ncol=4, fontsize=9)
    save(fig, "indexed_prices.png")


if __name__ == "__main__":
    main()
