# Changelog

Each edition was fact-checked, recomputed and code-reviewed. Errors are listed
with the edition that fixed them.

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
