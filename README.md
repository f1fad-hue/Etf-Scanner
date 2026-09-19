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

## Disclaimer

Educational summary of publicly reported market data. Not investment advice, not
a recommendation to buy or sell any security. Forecast ranges are scenario
estimates, not predictions. Verify current prices, yields and holdings before
trading.
