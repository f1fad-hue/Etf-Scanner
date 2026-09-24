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
- `tests/` — static audit and browser regression suite (see Tests).

## Edition log

### 24 Sep 2026 — thesis corrected, re-ranked, three latent bugs fixed

**The 21 Sep thesis was wrong.** It said the Fed was tightening into a
slowdown, making policy error the live risk. Wednesday's S&P Global PMIs showed
the opposite: services 58.7 (~5-year high), manufacturing 56.7, with input and
output price inflation at multi-year highs. Governor Barr said "further policy
adjustments are likely to be needed" and named AI investment demand as an
inflation source. The 10-year rose ~15bp to ~5.11% (5.135% intraday), its
highest since July 2007; the 5-year crossed 5% for the first time since 2007;
October hike odds went from 49% to 70%.

Restated regime: **the economy is running hot, and the bond market has taken over.**

| Rank | Fund | Scores 3m/6m/12m/10y | Sum | Moved |
|---|---|---|---|---|
| 1 | VTIP | 5/5/4/2 | 16 | up from #3 — the 10-yr breakout is what short duration is for |
| 2 | RSP | 3/4/4/4 | 15 | — hot surveys broaden earnings; lead over SPY narrowing |
| 3 | VEA | 2/3/4/5 | 14 | down from #1 — dollar index 100.6, a two-month high |
| 4 | XLV | 3/3/4/4 | 14 | — reframed as low-beta diversifier, not policy-error hedge |
| 5 | ITA | 3/3/4/4 | 14 | — 3m upgraded; talks opened a channel but no deal |

**XLE stays out.** Its re-entry condition (talks collapse) did not fire: envoys
met for ~3 hours on 22 Sep and Iran offered to reopen Hormuz within seven days.
A demand-led energy case from the hot PMIs was weighed and rejected as
headline-chasing three sessions after removal.

**Data conflicts handled rather than papered over**

- Oil on 23 Sep: sources ranged from below $99 (sixth straight decline) to above
  $103, and one reported $114.89 for 22 Sep. No single figure is printed; the
  Brent KPI tile was replaced with four figures that are cleanly sourced.
- Fear & Greed on 23 Sep: three sources say 35, one says 71. 35 used; the
  outlier is named on the page.
- VIX: 14.21 on 23 Sep after +6.83% implies ~13.3 on 22 Sep, confirming that
  the 14.81 shown for 21 Sep was a stale quote, as that edition had cautioned.
- Futures pricing of ~4.6% by late 2027 dates from 17 Sep, before this week's
  repricing, and is now labelled as such.

**Latent errors found in earlier editions**

| Defect | Present since | Fix |
|---|---|---|
| VTIP's "Ballast" chip rendered teal at **3.92:1**, failing AA for 10px text. Earlier audits checked ink tokens only, never series colours used as text. | 19 Sep (v1) | Added `--t-*` text-safe tokens; teal `#00847F` 4.56:1, amber `#A36908` 4.58:1 |
| Both prior editions claimed to rank by summed conviction but had one pair inverted each (RSP > ITA on 19 Sep, VTIP > XLV on 21 Sep). Order was partly set by hand. | 19 Sep (v1) | Order now computed from scores with a stated tiebreak, and verified by `tests/audit.py` |
| RSP compared through 31 Aug against the S&P through 18 Sep — mismatched dates. | 21 Sep | Same-date comparison: ~16% vs ~13% in late Aug, narrowed to ~1pt since |
| The dropped-XLE heading used RSP's identity colour. | 21 Sep | Uses the caution token |
| Test harness: all scripts shared `/tmp/preview.html`, so testing an old file silently changed what the screenshot tool showed. | this session | Each run writes its own preview |

Palette re-validated for the new display order (indigo beside plum fails, so
XLV takes amber and ITA plum): worst CVD ΔE 12.6, normal-vision ΔE 27.3.

Blended fee 0.1157%, yield 1.8553%, VTIP + XLV 42% — all re-derived.

### 21 Sep 2026 — data refresh and one pick changed

Re-ran the full pipeline against current data. Two trading sessions had passed
and the picture moved materially.

| Moved | From (18 Sep) | To (21 Sep) |
|---|---|---|
| S&P 500 | 7,650.50 | 7,764.70 (+1.49%, Nasdaq record close) |
| Brent | ~$109 (14 Sep) | $100.34 (4th straight decline) |
| 10-yr UST | 4.93% | 4.96% (peaked 5.014% on 14 Sep) |
| Fear & Greed | 29 | 29 (unchanged — now against a record Nasdaq) |

**New facts that changed the thesis**

- **Core CPI is 2.4% and easing** (from 2.5%). The whole gap to the 3.4%
  headline is energy — and energy is now falling. The previous edition framed
  the regime as inflation re-acceleration; that framing was too simple.
- Fed Chair **Warsh**; the hike was **12–0**; October hike odds **49%**, at
  least one more in 2026 at **87%**; next FOMC **27–28 October**.
- Washington signalled openness to meeting Iran's president at the UN;
  Hormuz flows back to ~80% of pre-war levels.

Regime restated: **the Fed is tightening into an energy shock that is already
deflating**, which makes policy error — not inflation — the live risk.

**XLE dropped, XLV added.** The 19 Sep edition scored XLE 2/5 at 12 months and
10 years with an explicit rule: hold for a reason, sell when the reason ends.
Brent down four sessions, restored Hormuz flows and possible US–Iran talks mean
the reason is ending, so the rule was followed rather than the pick defended.
XLV replaces it as the defensive sleeve: not a bond proxy (unlike XLU), lagging
at +9.7% YTD, with the drug-pricing overhang largely resolved.

Also corrected: RSP's YTD is **+15.46% through 31 Aug**, ahead of the
cap-weighted index — the 9.67% figure used earlier came from a June-dated
article and understated it.

Weights re-struck (VEA 28 / RSP 24 / VTIP 22 / XLV 15 / ITA 11); blended fee
0.1157% and yield 1.8628% both re-derived. Palette re-validated for the new
ordering — indigo↔plum failed the normal-vision floor when adjacent, so the
assignment was re-searched across all 120 permutations and
`indigo · red · teal · plum · amber` chosen (worst CVD ΔE 12.1, normal ΔE 22.4),
which also preserves VEA, VTIP and ITA on their existing colours.

Verification: 30 browser checks passing, zero JS errors, no overflow at
320/360/412/680px.

### Audit log (19 Sep 2026)

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

## Tests

Both run from the repo root and exit non-zero on failure.

```sh
python3 tests/audit.py        # arithmetic, ranking method, structure, contrast
node tests/browser.mjs        # overflow at 320/360/412/680px, JS errors, horizon
                              # switching, keyboard nav, sticky bars, rendered
                              # chip contrast (38 checks)
```

`browser.mjs` needs Playwright; set `PLAYWRIGHT_MODULE` to its `index.mjs` if
it is not resolvable. When fund weights, expense ratios or yields change, update
the `ER` and `YLD` tables in `audit.py` to match the page.

## Disclaimer

Educational summary of publicly reported market data. Not investment advice, not
a recommendation to buy or sell any security. Forecast ranges are scenario
estimates, not predictions. Verify current prices, yields and holdings before
trading.
