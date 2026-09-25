# ETF Scanner

A light-theme, phone-first market brief: five ETFs for a hiking-cycle market,
an allocation that maximises 10-year growth within a worst-crash limit, and a
market view across 3-month, 6-month, 12-month and 10-year horizons.
Data to the 24 Sep 2026 close.

**Live page:** https://claude.ai/artifact/D1jcssxQKUavM9MQ9W7YE9
(private: open it from the owner's account, or share it from the page's Share menu)

## The page

| Tab | What it answers |
|---|---|
| **Top 5 ETFs** | VTIP, RSP, VEA, XLV, ITA, each scored 1–5 at four horizons, plus what was left out and why |
| **Allocation** | How much in stocks versus bonds: pick the worst crash you can accept and get the mix with the most expected growth. Today: 35% stocks, 65% bonds |
| **Markets** | When to move from bonds to stocks: the stock premium, six signals, volatility, sentiment and eight regions ranked |

## Method

**Ranking.** Funds are ordered by the sum of their four horizon scores (ties go
to the 10-year score, then the previous order). Regions are ranked by the score
at the chosen horizon, and tied regions share a rank.

**Allocation.** This finds the mix with the highest expected return, net of
fees, whose worst historical crash stays within the chosen budget.
- **Forecasts:** J.P. Morgan 2026 LTCMA, which gives US large cap 6.7% (used for
  RSP, XLV and ITA) and developed ex-US 7.4% (VEA). VTIP's 4.0% is an
  assumption between Schwab's 3.3% for cash and J.P. Morgan's 5.3% for bonds.
- **Crash depths:** each fund's actual fall. The stock funds are RSP 59.92%,
  VEA 60.68%, ITA 59.72% and XLV 39.17%, and all four bottomed on 9 Mar 2009.
  VTIP launched in 2012, so its worst fall, 6.27% in March 2020, is used.
- **Bounds:** every fund holds at least 5%, and no stock fund holds more than 30%.
- **Solver:** weights move in whole points. The first three stock funds are
  enumerated, and the last one is solved directly. The tests confirm that this
  matches a brute-force search at every budget.
- **Default budget:** the one with the most growth whose worst crash would be
  recovered within five years (half the horizon), assuming expected returns.
- **Signals:** every two signals that are met raise the budget by 5 points.

| Preset | Worst crash | Stocks | Net %/yr | $10k in 10 yrs | Recovery |
|---|---|---|---|---|---|
| Least drawdown | 16.0% | 20% | 4.52 | $15,555 | 3.9 yrs |
| **Recommended** | **20.9%** | **35%** | **4.91** | **$16,157** | **4.9 yrs** |
| Most growth | 53.9% | 100% | 6.78 | $19,271 | 11.8 yrs |

**Data policy.**
- Charts plot reported closes only, and days without a confirmed close are left out.
- Where sources conflict, the page shows a range (for example, October hike
  odds of 70–78%).
- Every survey reading carries its date.

## Design

- **Light theme:** set with `color-scheme: light`, with tokens on `:root`.
- **Phone layout:** a single column with no horizontal scroll at
  320/360/412/680px. Sticky bars clear the safe area.
- **Colours:** the five fund colours are validated for colour-vision deficiency,
  and text versions (`--t-*`) meet WCAG AA. All ink tokens meet AA on every surface.
- **Accessibility:** the tabs follow the ARIA tabs pattern, the horizon
  switches are radiogroups with arrow keys, and a single live region announces
  changes.

## Files

- `index.html` is the whole page. There is no build step, and the only external
  dependency is Google Fonts.
- `tests/audit.py` is a static audit. It re-implements the optimizer, recomputes
  every number the page states, and checks for stale text, duplicate sources,
  structure and contrast.
- `tests/browser.mjs` runs Playwright checks:
  - overflow at four widths, the tabs, the keyboard and the shared horizon;
  - every slider position against brute force;
  - the charts, label overlap and contrast.
- `CHANGELOG.md` holds the edition history and every error found and fixed.

## Tests

```sh
python3 tests/audit.py
PLAYWRIGHT_MODULE=/path/to/playwright/index.mjs node tests/browser.mjs
```

Both exit non-zero on failure.

## Network note

This cloud environment blocks portfolioslab.com, am.jpmorgan.com, schwab.com,
stooq.com, query1.finance.yahoo.com, cnbc.com, ishares.com, ssga.com and
morningstar.com. As a result, figures were checked through search results
instead of primary tables. Allowing these hosts (cloud environment → Edit →
Network access) would let a future run compute drawdowns and correlations
from daily prices.

## Disclaimer

This is an educational summary of publicly reported data. It is not investment
advice or a recommendation to buy or sell any security. The ten-year figures
are model forecasts.
