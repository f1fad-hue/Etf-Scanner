# ETF Scanner — September 2026 Brief

A single-page, mobile-first market brief that ranks five ETFs against the
September 2026 regime, with conviction scored across four horizons
(3-month, 6-month, 12-month, 10-year).

**Live page:** https://claude.ai/artifact/D1jcssxQKUavM9MQ9W7YE9

> Private artifact — only the owner and people they share it with can open it.
> Share it from the page's Share menu.

## What it covers

Three analytical lenses, each built from reported data through 18 Sep 2026:

| Lens | Headline reading |
|---|---|
| Market trend | S&P 500 at 7,650.50, +11.7% YTD, but only ~33% of members above their 50-DMA |
| Broad sentiment | CNN Fear & Greed at 29 ("Fear") within a few percent of the index high |
| Volatility | VIX 14.81 while the 10-year touched 5.01% — risk repriced in rates, not equities |

The five picks — VEA, VTIP, RSP, ITA, XLE — are ranked by blended conviction
across all four horizons, with a worked sleeve allocation, a conviction matrix,
and a section on what was deliberately excluded (SMH/SOXX, GLD, XLU, TLT, USO)
and why.

## Design notes

- **Light theme, committed.** Tokens are defined once on `:root` with
  `color-scheme: light`; no dark-mode block, so the page holds its intended
  appearance on either host ground.
- **Android-first.** Single column, 18px gutter, no horizontal page scroll at
  412px; the matrix table scrolls inside its own container. Both sticky bars
  clear `env(safe-area-inset-top)`.
- **Chart palette is validated, not eyeballed.** The five categorical series
  colours pass the lightness band, chroma floor, CVD separation, normal-vision
  floor, and contrast checks against a white surface. The plum↔teal pair sits in
  the tritan floor band (ΔE 7.5), so every allocation segment carries a direct
  ticker label as secondary encoding.
- **KPI deltas are direction-only.** Rising yields aren't "good" and a falling
  VIX isn't "bad", so the deltas use glyphs on neutral ink rather than
  green/red status colour.

## Files

- `index.html` — the whole page; no build step, no runtime dependencies beyond
  Google Fonts (Newsreader, IBM Plex Sans, IBM Plex Mono).

## Audit log (19 Sep 2026)

A full fact-check, math revalidation and code review was run over v1. Twenty-six
defects were found and fixed.

**Data errors**

| # | Defect | Resolution |
|---|---|---|
| D1 | "International value trades near 12x earnings" applied to VEA | EFV's figure, misapplied. VEA is ~19.9x vs S&P fwd 19.3x — **parity, not a discount**. Thesis rewritten. |
| D2 | Headline "The cheapest leadership in the market" | False once D1 corrected; rewritten to "Leadership and diversification — but not a discount" |
| D3 | ITA expense ratio 0.40% | 0.37% |
| D4 | XLE yield 3.12% | ~2.4% — the figure was pre-rally; a 47% gain compressed it |
| D5 | RSP yield 1.6% (unsourced assumption) | 1.46% |
| D6 | ITA yield 0.6% (unsourced assumption) | 1.29% |
| D7 | "~85bp priced by Sep 2027" | ~70bp (3.875% midpoint to 4.6%) |
| D8 | "Beating the S&P by roughly five points" compared VEA total return to S&P *price* return | ~4 points like-for-like (16.5% TR vs 12.3% TR) |
| D9 | "+16.2% YTD" attributed to XLU | It is the S&P 500 utilities *index*; reattributed |
| D10 | XLE "3% yield" in two further places | ~2.4% |
| D11 | Concentration/HHI data undated | Stamped April 2026 |
| D12 | "35% in hedges" contradicted RSP's own "Concentration hedge" label (would be 57%) | Relabelled "VTIP + XLE" |
| D20 | "Cheapest way to own the other side" (fee sense) read as valuation | "lowest-cost" |
| D21 | Trend lens still claimed international leads on "cheaper multiples" | Corrected with real multiples |

Verified correct and left unchanged: VTIP 2.4yr duration, 10-year touching 5.014%
on 14 Sep, CPI 3.4%, Fed 3.75-4.00%, S&P 7,650.50, VIX 14.81, Fear & Greed 29,
gold flows, SMH/SOXX/USO/GLD figures, NATO and ReArm Europe figures.

Both blended statistics survived recalculation with corrected inputs
(fee 0.1176% -> 0.12%, yield 1.9932% -> ~2.0%); the input errors happened to offset.

**Code and accessibility**

| # | Defect | Resolution |
|---|---|---|
| D13 | Dead `.eyebrow` rule | Removed |
| D14 | `--pos`/`--neg` orphaned after the KPI colour fix | Removed; `--topbar-h` declared |
| D15 | `box-shadow: 0 0 0 18px` spread painted over the first 18px of the card beneath the sticky bar | Replaced with negative inline margin + padding |
| D16 | `role="tablist"`/`role="tab"` with no tabpanels and no arrow-key handling — wrong ARIA contract | Converted to `radiogroup`/`radio` with roving tabindex, arrow/Home/End keys |
| D17 | Allocation bar `aria-label` hardcoded, duplicating the JS weights | Generated from the same data that draws the bar |
| D18 | No announcement on horizon change | Added `role="status"` live region |
| D22 | `--ink-3` #8A94A2 at 2.86:1 failed contrast for the 9.5px uppercase labels | #686F7A — 4.51:1 minimum across all three surfaces |

**Verification run:** 30 automated browser checks — no horizontal overflow at
320/360/412/680px, zero JS errors, all four horizons producing distinct content,
matrix highlight tracking, keyboard navigation, sticky-bar seam at -0.05px,
scroll position held across re-render. Palette re-validated (all six checks pass).
Every text token re-audited to WCAG AA.

## Disclaimer

Educational summary of publicly reported market data. Not investment advice, not
a recommendation to buy or sell any security. Forecast ranges are scenario
estimates, not predictions. Verify current prices, yields and holdings before
trading.
