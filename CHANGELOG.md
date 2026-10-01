# Changelog

Each edition was fact-checked, recomputed and code-reviewed. Errors are listed
with the edition that fixed them.

## 1 Oct 2026: data to the 30 Sep close, top 5 re-ranked

Quarter-end data (S&P 500 7,651.54, 10-year 5.29%, VIX 16.3, MOVE 110.5) and
the August PCE report (core 3.0% against 3.3% expected; October hike odds fell
to about 35% from 71% a week earlier). The five funds were re-scored and
re-ranked, and candidates were screened.

**Top 5 update**

| Fund | Scores 3m/6m/12m/10y | Sum | Change |
|---|---|---|---|
| VTIP | 5/5/4/2 | 16 | unchanged, still first |
| XLV | 3/4/4/4 | 15 | up from fourth: 6-month score 3 → 4 (consumer confidence at a 12-year low, job openings at a five-month low) |
| VEA | 2/3/4/5 | 14 | unchanged |
| RSP | 2/3/4/4 | 13 | down from second: equal weight fell 5.0% in the month to 28 Sep while the S&P fell 0.4%; three in four stocks fell in September |
| ITA | 2/3/4/4 | 13 | stays fifth: 3-month score 3 → 2 (about −3% this year, 19% below its 52-week high) |

Screened and not added: SGOV (13; same job as VTIP without the inflation
link), EWJ (Japan ranks first of the regions, but VEA already holds it at a
fraction of the fee), QUAL and SPY (add back the concentration RSP hedges). The
allocation is unchanged at 35% stocks and 65% bonds, because no fund's fee,
forecast or worst crash changed.

**Errors found and fixed**

| # | Error | Fix |
|---|---|---|
| 1 | Re-ranking would have broken the allocation: the stage table wrote fund columns in the ranked order under a header hard-coded in the old order, so weights would have sat under the wrong tickers | One fixed allocation order (`ALLOC`) drives the optimizer, sums, bar, legend and the stage-table header, which is now generated. Tests check the header and legend agree |
| 2 | The stocks-and-yields correlation was stated as −0.78; with 30 Sep it is −0.7748, which rounds to −0.77 | Corrected; the audit computes it |
| 3 | Fear & Greed for 29 Sep was shown as 32, from a tracker site. Benzinga, which reports CNN's daily close, gives 29 | 29 on 29 Sep, 31 on 30 Sep |
| 4 | "Above all 60 prior readings" (24 Sep) and "above all 84" (30 Sep) for MOVE cannot both describe one history; Saxo's own store count changed | The page now says "a new high in Saxo's records" |
| 5 | The core-inflation signal did not name its measure, while core PCE was flat in August | It is core CPI (one decline so far); the page says core PCE was flat |
| 6 | SGOV's 3.67% SEC yield (a trailing 30-day figure) sat beside T-bills "at about 4.1%" | SGOV is quoted by yield to maturity, about 4.0% |
| 7 | The XLV note "up about 12% in three months" could not be confirmed against the September sector table, where every sector but technology fell | Replaced with the sourced sector fact |
| 8 | The ranking note said ITA fell to fifth; it was already fifth | Corrected |

**Updated:** the stock premium is now below zero on every estimate (−0.08 to
−0.03 points), so the Markets headline reads "Stocks pay less than bonds"; the
high-yield spread widened to 308bp (+40bp in a week); gold fell about 8.5% in
September; the MOVE index replaced Fear & Greed in the Markets KPIs. All six
signals are still unmet (one partial).

`audit.py` 282 checks; `browser.mjs` 84.

## 30 Sep 2026: data to the 29 Sep close, fund and region scrub

New data through Tuesday's close (S&P 500 7,670.84, 10-year 5.25%, VIX 16.0) and
the 30 Sep morning (October hike odds about 49%, down from 75%). Then every
fund, ETF, stock and region fact was re-checked against its source. The fund
scores and the 35% / 65% allocation are unchanged.

**Errors found and fixed**

| # | Error | Fix |
|---|---|---|
| 1 | VEA was treated as Europe and Japan. It holds South Korea (8.6%; Samsung 2.6% and SK Hynix 2.0%) and Canada (11.0%). J.P. Morgan's 7.4% forecast covers EAFE, which excludes both: 20% of the fund | VEA risk note added; the assumptions call the forecast a proxy |
| 2 | The emerging-markets region used VWO (FTSE), which excludes Korea and is 33% Taiwan, while J.P. Morgan's 7.8% is for MSCI EM (Taiwan 27%, Korea 24%) | Ticker EEM. EM was scored 4 at 12 months and 5 at 10 years while its four biggest markets (81% of the index) averaged 2.8 and 3.1; now 3 and 4, and the audit enforces a one-point limit |
| 3 | The 6- and 12-month ranges did not widen with the horizon (XLV and ITA were narrower at 12 months than at 6) | All widen with the square root of time, as the 3-month ranges implied. XLV, the calmer fund, is narrower than the rest |
| 4 | RSP's "Mag 7 weight ~1.4%" counted 7 lines. Alphabet has two share classes, so there are 8 | ~1.6% |
| 5 | VTIP duration 2.4 years | 2.3 (Vanguard, 31 Aug) |
| 6 | ITA: "demand written into treaties" and ReArm Europe "adds over €800bn". NATO's 5% is a pledge for 2035 (Spain excepted) and ReArm Europe aims to mobilise €800bn through 2029 | Reworded |
| 7 | October hike odds of 70–73% were stale: the New York Fed's Williams said "no need for urgency" and odds fell from 75% to about 49% | Updated and dated to 30 Sep morning |
| 8 | The high-yield spread (273bp, "credit is not scared") was stale. It widened to about 302bp, the most since April, and the "450bp median" reference could not be sourced | Gauge and text rewritten; reference line is the 241bp record low |
| 9 | The 28 Sep VIX close was 16.11. Saxo, the source of the rest of the series, has 16.07 (other prints: 16.11, 16.17) | 16.07, 29 Sep 16.04, and the page says the sources differ by up to 0.1 |
| 10 | 30-year yield "5.56%, highest since 2004"; Brent quoted without saying which contract | 5.61%, highest since 2002. Front-month Brent $102.59 (AP now quotes December, $96.16, in steep backwardation) |
| 11 | Smaller figures: Fear & Greed 34 → 32, earnings-yield premium −0.05 to −0.01 (every source now below zero), gold, USO note | Updated |

**Added:** consumer confidence (81.9, lowest since 2014); the correlation between
daily S&P 500 moves and 10-year yield changes over eight sessions (−0.78; stocks
and bonds fell together, so long bonds were no hedge); the MOVE reading for 28 Sep.

**Checked and unchanged:** all five worst-crash figures, VTIP's inception and
6.27% drawdown, RSP's 251% against 207% over ten years over SPY, XLV's 0.08% fee,
J.P. Morgan, Schwab and Vanguard forecasts, and the allocation frontier.

**Cleanup:** keyed inputs moved to `tests/data.json` with their sources;
`.gitignore` added; older changelog entries condensed. `audit.py` has 260 checks,
`browser.mjs` 83.

## 28 Sep 2026: data to the 28 Sep close, second scrub

Errors fixed: the 24 Sep 10-year close (5.20%, not 5.11%); a yield chart that
mixed intraday snapshots with closes; VEA "at parity" from comparing a trailing
P/E with a forward one; ITA's stale "+34% 1-year" and 1.29% yield; an
unverifiable semiconductor claim; a stock premium built on mismatched dates;
stale region notes (Taiwan, Korea, India, Japan, Europe, China); Iran and oil
text. The MOVE index and a second allocation sensitivity (VTIP at 4.9% allows
44% stocks) were added, and forecast dates were stated. `audit.py` gained a
keyed table of dated closes and AP's point-change chain.

## 25 Sep 2026: concise edition

Three tabs (Top 5 ETFs, Allocation, Markets); text cut from about 4,700 to 1,600
words. Removed duplicated and conflicting content, including a 27/73 sleeve that
contradicted the 35/65 allocation.

Errors fixed: an intraday S&P figure and a false "within 0.3%" claim; VIX dates
off by a day; oil described as falling on an up day; an optimizer that ignored
fees and, at whole-point steps, missed the best mix at 10 of 39 budgets (now an
exact solver checked against brute force); a 5.16% earnings yield that was
5.15%; AAII's bearish average (31.0%, not the 31.5% neutral one); ITA's 10-year
range above its own forecast; a double screen-reader announcement on the slider;
a steps table cut off at 360px.

## 25 Sep 2026: allocation optimized for 10-year growth within a worst-crash limit

- Replaced an assumed 60/40 with an optimizer. You choose the worst fall you can
  accept, and the page finds the mix with the most expected growth inside it.
- The default is the most growth whose crash is recovered within five years:
  35% stocks, 65% bonds. Signals raise the budget in 5-point steps.

**Fixed**
- The stock/bond bar drew 35% as 36.7%, because flex-grow added the label padding.
- Frontier labels collided with the axis.
- Test identifiers clashed.

## 25 Sep 2026: whole-portfolio allocation

- One stock/bond model is now shared by both tabs. Before, the tabs gave
  conflicting signals.

**Fixed**
- An empty legend cell appeared after five items.
- The steps table was cut off on phones.
- A 320px rule widened the table instead of narrowing it.

## 25 Sep 2026: second tab for sentiment, volatility and regions

- Answers when to move from bonds to stocks, with six signals, volatility charts
  on separate scales, sentiment split by investor type, and eight regions ranked.

**Fixed**
- A 2025 UK year-to-date figure was excluded.
- A 2025 Hong Kong figure was not used.
- The fund parser read regions as funds.
- A test expected 9 dates when there are 8.
- Hover tests ran off-screen.
- Several layout gaps.

## 24 Sep 2026: thesis corrected and re-ranked

- The PMIs showed the economy running hot, not slowing. The 10-year hit 5.11%,
  its highest since 2007.
- Re-ranked: VTIP, RSP, VEA, XLV, ITA. XLE stays out.

**Fixed**
- The VTIP chip had 3.92:1 contrast, below AA. Text-safe `--t-*` tokens were added.
- Both earlier editions had one pair out of rank order. The order is now
  computed from the scores and tested.
- RSP was compared with the S&P using mismatched dates.
- The shared test preview file was replaced with one per run.

## 21 Sep 2026: data refresh

- XLE was dropped under its own exit rule as oil fell and Hormuz reopened. XLV
  was added.
- Core CPI of 2.4% reframed the thesis.
- RSP's year-to-date figure was corrected to +15.46% through 31 Aug.

## 19 Sep 2026: first edition and audit

Twenty-six defects were fixed. They included:
- VEA's "12× earnings", which was EFV's figure;
- ITA's fee: 0.37%, not 0.40%;
- XLE's yield: about 2.4%, not 3.12%;
- VEA compared on total return against the S&P's price return;
- wrong ARIA roles on the horizon control;
- `--ink-3` contrast at 2.86:1;
- a sticky-bar shadow painted over content.
