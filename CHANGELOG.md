# Changelog

Each edition was fact-checked, recomputed and code-reviewed. Errors are listed
with the edition that fixed them.

## 28 Sep 2026: data refresh to the 28 Sep close, second scrub

Fresh data through Monday's close (S&P 500 7,683.69, 10-year 5.23%, VIX 16.1),
then every figure, calculation and claim on the page was re-checked. Scores and
the allocation are unchanged: the evidence moved the notes, not the rankings.

**Errors found in the 25 Sep edition and fixed**

| # | Error | Fix |
|---|---|---|
| 1 | The 10-year close for 24 Sep was shown as 5.11%, which was the 23 Sep close repeated. AP reported 5.20%. The chart drew a flat step where the yield jumped 9bp | Series rebuilt from AP closes |
| 2 | The yield chart, titled "reported daily closes", mixed CNBC mid-session snapshots (5.01, 4.93, 4.96, 4.96) with closes | Both charts now plot only AP (10-year) and Saxo/Cboe-based (VIX) closes for 17–28 Sep. The VIX series also lacked 21 Sep (14.87) |
| 3 | VEA was called "level with the S&P" by comparing a trailing P/E (19.9×) with the S&P's forward P/E. The error dates from the 19 Sep audit | Like for like, EAFE is on 18.0× forward against 19.2×: a 6% discount, not parity |
| 4 | ITA was shown as "+34% 1-year" and a 1.29% yield. It is about flat this year, and iShares' SEC yield is 0.34% | Corrected. The risk note now says defence shares fell 3% on 22 Sep on a Hormuz reopening report, so they are not immune to oil news |
| 5 | Semiconductors were "up 82% and 113% in the first half", which cannot be squared with SOXX's 52-week high of 655.95 | Replaced with a checkable figure: SOXX is 13% below that high |
| 6 | The stock premium of 0.04–0.13 points combined 5.15–5.24% with a 24 Sep yield of 5.11% | Re-priced to the 28 Sep close: 5.19–5.24% against 5.23%, so −0.04 to +0.01. The page now says "≈0" because the range straddles zero. FactSet's P/E is rounded to 0.1, and the range says so |
| 7 | Region notes were stale or unsourced: Taiwan "hit directly by AI selling" (it closed at a record on 23 Sep), Korea "back above 7,000" (6,890 on 28 Sep), India "P/E near 19.6", Japan "up 22% in dollars", Europe "banks and cyclicals lead", China "down about 10%" | Rewritten from dated facts. Samsung and SK Hynix are 47% of KOSPI, not "over 40%" |
| 8 | Iran and oil: "a phased Hormuz deal is being discussed; Brent $106.60" | Trump rejected Iran's offer on 26 Sep but expects talks to resume, so the XLE re-entry rule has not fired. Brent settled at $105.28 |
| 9 | Smaller figures: hike odds 70–78% (now 70–73%; FedWatch 70.3% from 64.2%), Fear & Greed 35 (34), high-yield spread 270bp (273), breadth "about 33%" (31%, dated), "tightest tenth" (softened), VTIP yield 2.24%, RSP 1.49%, XLV 1.51% and 20.5× | Updated and dated |
| 10 | The "history 3–4 pts" comparison had no source | Sourced: the 1871–2026 average of earnings yield minus the 10-year |

**Added:** the MOVE index (bond volatility, 104.6 on 24 Sep, above all 60 prior
readings) beside the VIX, and a second allocation sensitivity: with VTIP at
4.9%, about the two-year Treasury yield, the recovery rule would allow 44% in
stocks instead of 35%. The 4.0% assumption stays because it is the conservative
one, and the forecasts are now dated (J.P. Morgan October 2025, Schwab January
2026, both before yields rose).

**Code review findings applied:** the sensitivity wording, forecast dates, the
VEA tile and prose on one basis, restored RSP sources, and the MOVE claim
restated from the readings shown.

**Tests:** `audit.py` (230 checks) now holds one keyed table of dated closes
and checks the page's chart data against it, chains AP's reported point changes
from close to close, and checks reported VIX percentage moves. `browser.mjs`
(83 checks) is unchanged in scope apart from the new chart values and a stricter numbers-table check.

**Checked and left alone:** a 21 Sep and a 25 Sep VIX close that are both
14.87. Percentage moves reported on 22 Sep (+0.41%) and 28 Sep (+8.33% and
+8.75%) both start from that same base, so they agree.

## 25 Sep 2026: concise edition, data to the 24 Sep close

The page is now three tabs: Top 5 ETFs, Allocation and Markets. The static text
went from about 4,700 words to 1,600, and the file from 124 KB to 80 KB. The
sources list is deduplicated and collapsed.

**Removed as duplicate or conflicting**
- The edition-history box.
- The Top 5 tab's "three lenses", which repeated the Markets tab.
- The Top 5 tab's own 27/73 sleeve, which contradicted the optimized 35/65
  allocation.
- Horizon rows that were repeated three times.
- Rank-movement tags.
- Region year-to-date figures taken from different dates.

**Errors found and fixed**

| # | Error | Fix |
|---|---|---|
| 1 | S&P 500 on 24 Sep shown as −0.51%, an intraday figure | Close was 7,704.13, down 1.90 points: flat |
| 2 | The claim that the S&P was "within 0.3% of 18 Sep" was false (it was +0.70%) | Removed |
| 3 | VIX dates were shifted by one day, and a derived 13.30 point was plotted | Series re-dated. Only the 7 reported closes are plotted |
| 4 | "VIX third daily rise" was not supported by the data | "Up two days running" (14.21 → 15.18 → 15.67) |
| 5 | Oil on 23 Sep was described as falling | It rose, ending a five-day losing streak. Brent was $106.60 on 24 Sep |
| 6 | The optimizer ignored fund fees | Returns are net of fees. The recommended mix is unchanged, and at maximum growth RSP overtakes ITA |
| 7 | The one-point greedy optimizer was short of the optimum at 10 of 39 budgets (by up to 0.015 pt/yr), because it rounded to whole points | Replaced with an exact whole-point solver that matches brute force at every budget. The −31% and −36% signal rows changed (XLV 29, VEA 18 / 27) |
| 8 | The low end of the earnings yield was 5.16%, but 1 ÷ 19.4 = 5.155% (and 397.02 ÷ 7,704.13 = 5.153%) | 5.15–5.24%. The premium is 0.04–0.13 pts, not 0.05–0.13 |
| 9 | AAII bears were compared with a "31.5% average", which is the neutral average | The bearish average is 31.0% |
| 10 | VEA was called "19.9×, level with the S&P", comparing a trailing P/E with a forward one | Now "19.9× trailing earnings" |
| 11 | ITA's 10-year range (7–10%) sat above the 6.7% forecast the optimizer uses | 5.5–8.5% a year. The tests now require every 10-year range to contain its forecast |
| 12 | The budget readout had its own live region on top of the slider's value text, so screen readers announced each change twice | Readout's live region removed |
| 13 | The signal-steps table cut off the XLV and ITA columns on a 360px phone | "Stocks / bonds" became "Stocks", because VTIP is the bond side, and the budget moved under the signal count. Fits at 320px |
| 14 | README described two tabs, data to 18 Sep, and XLE as a pick | Rewritten. History moved here |

**Tests**
- `audit.py` has 182 checks. It includes an independent exact solver, brute
  force at six budgets, every stated number, and stale-text and duplicate-source
  checks.
- `browser.mjs` has 84 checks. It compares every slider position with brute
  force.

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
