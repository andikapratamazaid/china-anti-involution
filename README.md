# China's Instant Retail Subsidy War and the Anti-Involution Turn

A business, policy and e-commerce analysis of the 2025 food-delivery subsidy war between JD.com, Meituan and Alibaba, the Chinese regulator's (SAMR) escalating response, and the financial aftermath through Q3 2026.

Every number in this project comes from a named source: company earnings releases filed on SEC EDGAR (Alibaba, JD.com, PDD Holdings) and HKEXnews (Meituan), daily prices from the Yahoo Finance chart API, and monthly retail releases from the National Bureau of Statistics of China (NBS). Nothing is estimated or interpolated; where a filing does not disclose a metric, the cell is left blank and the gap is documented.

## Headline findings

**1. The burn was enormous, and it peaked in late 2025.** The four companies in this study (Alibaba, JD.com, Meituan, PDD) spent a combined **RMB 540.0 billion on sales & marketing in calendar 2025**. Their combined quarterly S&M bill rose from RMB 95.3bn in Q1 2025 to RMB 163.4bn in Q4 2025, before falling back through 2026.

**2. Meituan, the incumbent, bled first and worst.** Its selling & marketing intensity jumped from 17.6% of revenue in Q1 2025 to **35.6% in Q3 2025**. Core local commerce (food delivery plus quick commerce) swung from an operating **profit of RMB 13.5bn in Q1 2025 to a loss of RMB 14.1bn in Q3 2025**, a RMB 27.6bn swing in two quarters. Meituan closed 2025 with a **net loss of RMB 23.4bn for the year**, against a RMB 35.8bn profit in 2024, and returned to segment profit in Q2 2026, holding it in Q3 2026: core local commerce earned **RMB 5.7bn (7.3% margin)**, S&M intensity fell to **23.4% of revenue** from 35.6% a year earlier, revenue rose 21.6% to **RMB 115.6bn**, and adjusted net profit was **RMB 1.9bn** — a second straight profitable quarter.

**3. JD.com's entry ticket was the most expensive, and it is still paying.** JD's "New businesses" segment, which contains JD Food Delivery, lost money in every quarter from Q2 2025 onward: a trough loss of **RMB 15.7bn in Q3 2025** and a cumulative operating loss of **RMB 76.5bn between Q1 2025 and Q3 2026**. Unlike Meituan and Alibaba, JD's front-line losses were still running at roughly RMB 9.6bn in Q3 2026.

**4. Alibaba's war was intense but brief, and its group results are confounded by AI.** Alibaba's S&M intensity peaked at **26.8% of revenue in Q3 2025** and was back to 15.2% by Q3 2026, exactly its pre-war level. China e-commerce adjusted EBITA recovered from RMB 10.5bn in Q3 2025 to **RMB 38.9bn in Q3 2026**. Group-level Alibaba numbers must be read with care: the same Q3 2026 release reports AI cloud revenue up 53%, and headline net income (RMB 64.4bn) includes large investment gains, so segment EBITA is the cleaner war gauge.

**5. The market's verdict on regulation was mixed, not uniformly negative.** Around JD's own launch (11 Feb 2025), JD fell (CAR [0,+5] of **-11.8%**, market-adjusted vs KWEB) while Alibaba rose (+7.8%), a window that overlaps Alibaba's AI-driven rally and its February earnings, so it cannot be read as a pure war effect. The January 2026 anti-monopoly investigation hit PDD hardest (**-12.6%**) while Alibaba rose (+6.6%). The June 2026 draft subsidy rules were followed by declines at all four names (Meituan **-6.8%**, PDD -5.3%, Alibaba -4.8%, JD -2.8% over [0,+5]). The July 2025 summons, by contrast, was followed by positive abnormal returns (PDD +8.4%), which is *consistent with* investors pricing an end to the burn, but the sign flips across events and firms, so this study claims association, not causation.

**6. The war was fought over a slowing pie.** NBS data: online retail of goods and services reached **RMB 16,981.1bn in Jan-Oct 2026 (+3.7% YoY)** and online goods RMB 10,727.4bn (+2.9%), about **25.8% of total retail sales**. But total retail growth slowed to +1.0% cumulative by Oct 2026 (October alone: **+0.4% YoY**), and online goods growth decelerated from +11.5% in Jan-May 2024 to +2.9% in Jan-Oct 2026. Subsidies were chasing share in a market whose growth had already faded.

## The war and the regulator: timeline

| ID | Date | Event |
|---|---|---|
| E1 | 2025-02-11 | JD.com launches JD Takeaway with zero merchant commission (Reuters) |
| E2 | 2025-05-13 | SAMR and four other agencies summon JD, Meituan, Ele.me (SAMR) |
| E3 | 2025-07-18 | Second SAMR summons, after Taobao Instant Commerce's RMB 50bn subsidy pledge (SAMR via Caixin) |
| E4 | 2025-08-01 | All three platforms publicly pledge to curb irrational subsidies (China Daily / Xinhua) |
| E5 | 2026-01-09 | State Council anti-monopoly committee opens a competition investigation into food delivery (SAMR via Caixin) |
| E6 | 2026-02-13 | SAMR summons seven platforms on involution-style competition (Caixin) |
| E7 | 2026-04-17 | SAMR fines seven platforms a combined RMB 3.597bn in the "ghost shop" food-safety case (Reuters) |
| E8 | 2026-06-17 | SAMR publishes draft "Ten Provisions" on food-delivery subsidy behaviour for comment (SAMR via People's Daily / SCMP) |
| E9 | 2026-09-20 | SAMR pledges anti-involution "combination punches" at a State Council press conference (The Paper / CCTV) |

Each event date was verified against the cited reporting before inclusion. E7 is a food-safety enforcement case rather than a subsidy ruling; it is included because it was the campaign's largest financial penalty against the same platforms, and it is labelled as such in the data.

## Methods

**Subsidy-burn tracker (scripts/03).** Quarterly financials for the four companies were hand-transcribed from official earnings releases into `data/curated/financials_*.csv`, one row per company-quarter, each row carrying its filing source. The tracker computes sales & marketing as a percentage of revenue (only ever from the two disclosed inputs) and tracks the food-delivery front-line segment: Meituan core local commerce operating profit, JD New businesses operating profit, and Alibaba's China e-commerce adjusted EBITA. PDD does not fight in food delivery and discloses no segment operating result; its transaction-services revenue is tracked instead.

**Event study (scripts/01-02).** Daily adjusted closes for BABA, JD, PDD, 3690.HK and benchmarks (KWEB for the ADRs, 3067.HK Hang Seng TECH ETF for Meituan), Dec 2024 to Nov 2026. Day 0 is each stock's first trading day on or after the event date. Abnormal returns use a market model (alpha/beta estimated over trading days [-130, -11]) with market-adjusted returns alongside; for E1 the estimation window has fewer than 60 days, so only market-adjusted CARs are reported. Windows: [-1, +1] and [0, +5] trading days. Adjusted closes are used so dividend ex-dates do not masquerade as abnormal returns.

**Market context (script/04).** NBS monthly English press releases (26 releases, Jan-May 2024 to Jan-Oct 2026) are parsed for the cumulative figures NBS publishes: total retail sales, online retail of goods, and online retail of goods and services. Monthly values are derived only by differencing consecutive cumulative figures within a calendar year, and every derived row records how many months it spans (the Jan-Feb block spans two months because NBS does not publish January alone; the Apr-to-Jul 2026 block spans three because the May and June 2026 releases were not yet collected). As a parse check, the online share computed from the extracted values reproduces the share NBS itself publishes, exactly, at every point where NBS publishes one.

## Data honesty and limitations

- **Hand transcription, with sources.** Every financial figure was transcribed from the company's own release (SEC EDGAR Form 6-K Exhibit 99.1 for Alibaba, JD and PDD; HKEXnews results announcements for Meituan). The `source` column of `financials_quarterly.csv` names the filing for every row, and `tests/test_project.py` pins the headline anchors (for example Alibaba Q3 2026 revenue of RMB 271,519M and Meituan's FY2025 loss of RMB 23,354M) so any transcription drift fails the test suite.
- **Known gaps, left blank on purpose.** PDD's Q3 2026 release states no revenue YoY percentage (it gives the level against the same quarter of 2025), so that cell is empty rather than back-computed. Meituan's Q3 2026 results, announced 27 Nov 2026, are included, so all four companies now run through Q3 2026.
- **Segment definitions move.** Alibaba renamed and redefined its e-commerce segment twice in the sample (Taobao and Tmall Group, then Alibaba China E-commerce Group, then Alibaba E-commerce Group). Values are as originally reported in each quarter's release and are not strictly like-for-like across the renames; the Q3 2026 release, for instance, reports e-commerce EBITA growth of +243% against a restated comparative of RMB 11,336M, while the as-originally-reported Q3 2025 value in this dataset is RMB 10,497M. Meituan likewise revised its Q1-Q3 2025 revenue and S&M figures in its FY2025 announcement (an offsetting adjustment of roughly RMB 0.35-0.43bn per quarter); the revised figures are used and the originals are recorded in the notes column.
- **The adjusted-profit column is not one metric.** For Alibaba it holds adjusted EBITA, for Meituan adjusted EBITDA, and for JD and PDD non-GAAP operating profit, because that is what each company discloses. Each row's notes say which. Cross-company comparison of that column is indicative only; the S&M tracker and GAAP lines are the like-for-like measures.
- **JD's segment is an upper bound on food-delivery losses.** JD New businesses also contains JD Property, Jingxi and overseas businesses, so its losses overstate the pure food-delivery loss by an amount JD does not break out.
- **One secondary figure, labelled.** Tech-industry reporting (TechBuzz China, summarising Chinese financial media) puts the year-on-year *increase* in combined 2025 sales & marketing spend across the three warring platforms at roughly RMB 173bn. This dataset cannot reproduce that figure because its financial sample starts at Q4 2024, so it is cited here as secondary reporting, not as a result of this analysis.
- **Event-study caveats.** Abnormal returns measure repricing around an announcement, not proof that the announcement caused it. Windows overlap other news: Alibaba's February 2025 window coincides with its AI rally and earnings; sector-wide China tech moves are only partly removed by the benchmark; and the two benchmarks trade in different time zones from Meituan's listing (the Hang Seng TECH ETF is used precisely to keep Meituan on Hong Kong trading days). Findings are therefore phrased as "consistent with" throughout.
- **NBS caveats.** NBS cumulative figures are as published in each release and are occasionally revised in later releases; this dataset keeps the value from the release listed in `nbs_releases.csv`. The online-goods series is NBS's "online retail sales of physical goods" (2024-2025 wording) and "online retail sales of goods" (2026 wording), the same concept under both names. Collection starts with the Jan-May 2024 release; earlier 2024 cumulative points were not collected.

## File guide

```
scripts/
  01_collect_prices.py    Yahoo Finance chart API -> data/processed/prices_daily.csv
  02_event_study.py       CARs for 9 events x 4 stocks -> data/results/event_study.csv
  03_financials.py        assembles the curated filings -> financials_quarterly.csv, sm_tracker.csv
  04_context_nbs.py       parses 26 NBS releases -> nbs_retail.csv, nbs_monthly_derived.csv
  05_charts.py            renders the five charts from the result files
  06_dashboard.py         computes summary.json and renders dashboard/index.html
data/curated/
  financials_baba.csv / financials_jd.csv / financials_pdd.csv / financials_meituan.csv
                          hand-transcribed filings, one row per company-quarter, with sources
  financials_quarterly.csv  the four files combined, with S&M % of revenue computed
  events.csv              the nine verified events, with sources
  nbs_releases.csv        the 26 NBS release URLs parsed by script 04
data/processed/           prices_daily.csv, nbs_retail.csv
data/results/             event_study.csv, sm_tracker.csv, nbs_monthly_derived.csv, summary.json
data/raw/                 cached Yahoo JSON and NBS HTML (excluded from the zip where large)
charts/                   sm_pct_timeline, segment_profit_swing, event_study_car,
                          nbs_context, indexed_prices (all rendered by script 05)
dashboard/index.html      static dashboard generated by script 06
tests/test_project.py     12 consistency tests (anchors, recomputation, windows, coverage)
```

## Running it

```bash
python3 -m venv .venv && .venv/bin/pip install -r requirements.txt
.venv/bin/python scripts/01_collect_prices.py
.venv/bin/python scripts/02_event_study.py
.venv/bin/python scripts/03_financials.py
.venv/bin/python scripts/04_context_nbs.py
.venv/bin/python scripts/05_charts.py
.venv/bin/python scripts/06_dashboard.py
.venv/bin/python -m pytest tests/ -q
```

## Sources

- Alibaba, JD.com, PDD Holdings earnings releases: SEC EDGAR, Form 6-K Exhibit 99.1 (CIK 1577552, 1549802, 1737806), quarters ended Dec 2024 to Sep 2026.
- Meituan results announcements: HKEXnews (stock code 3690), quarters ended Dec 2024 to Sep 2026, including the FY2025 annual results announcement of 26 Mar 2026 and the Q3 2026 results announcement of 27 Nov 2026.
- Prices: Yahoo Finance chart API (query1.finance.yahoo.com), tickers BABA, JD, PDD, 3690.HK, KWEB, 3067.HK.
- Market context: National Bureau of Statistics of China, "Total Retail Sales of Consumer Goods" English press releases, stats.gov.cn, Jan-May 2024 to Jan-Oct 2026.
- Event verification: Reuters (11 Feb 2025; 17 Apr 2026), SAMR notices and disclosures (samr.gov.cn; english.samr.gov.cn), Caixin Global (Jul 2025; Jan-Feb 2026), China Daily / Xinhua (Aug 2025), People's Daily and South China Morning Post (Jun 2026), The Paper / CCTV (Sep 2026).
