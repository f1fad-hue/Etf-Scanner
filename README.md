# ETF Scanner — September 2026 Brief

A mobile-first, light-theme market brief with two tabs:

- **Top 5 ETFs** — five ETFs ranked against the September 2026 regime, with
  conviction scored across 3-month, 6-month, 12-month and 10-year horizons.
- **Sentiment & regions** — when to move from bonds into stocks (six signals
  and a staged rule), volatility analysis, broad sentiment split by investor
  type, and eight regions ranked at each horizon.

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

### 25 Sep 2026 — whole-portfolio stock / bond allocation

The two tabs disagreed without saying so. The Top 5 sleeve is 27% bonds /
73% stocks, because it is five picks with one bond fund; the second tab says to
keep short-term money in short bonds. Adds one whole-portfolio model that both
tabs now use.

| Signals met | Stocks / bonds | VTIP | RSP | VEA | XLV | ITA |
|---|---|---|---|---|---|---|
| **0–1 (now)** | **45 / 55** | 55 | 15 | 14 | 9 | 7 |
| 2–3 | 50 / 50 | 50 | 16 | 16 | 10 | 8 |
| 4–5 | 55 / 45 | 45 | 18 | 18 | 11 | 8 |
| All 6 | 60 / 40 | 40 | 20 | 19 | 12 | 9 |

- Long-run mix 60 / 40 for a moderate-risk investor (stated as an assumption);
  today a 15-point bond overweight, unwound in 5-point steps as signals fire.
- The stock side keeps the Top 5 proportions (RSP + VEA are 64% of it); VTIP
  carries the bond side. Rounded by largest remainder so every row sums to 100.
- By horizon: 45 / 55 at 3 and 6 months, 45 → 60 over 12 months as signals
  fire, 60 / 40 target for decade money reached in 12 monthly steps of 1¼ points.
- Today's blended fee 0.08%, yield ~2.0%, 14% outside the US.
- Tab 1 shows the sleeve's 27 / 73 and links to the total allocation.

The page computes every weight from one set of constants and the fund data;
`tests/audit.py` recomputes them independently and checks that each place the
page states the mix (heading, KPI, thesis, tab-1 pointer, all four ladder
rungs) agrees, and that the page's numeric fee and yield fields match the
figures shown on the fund cards.

**Found and fixed**

| Defect | Fix |
|---|---|
| The two tabs gave conflicting allocation signals with no reconciliation | One model, stated on both tabs |
| Fund legends showed an empty grey cell after five items (tab 1 since v1) | Items grow to fill the last row |
| Steps table cut off two columns on phones | The Bonds column always equalled VTIP; merged into one "stocks / bonds" column. Fits at 360px and 412px |
| A 320px rule widened the table instead of narrowing it: an id-level `font-size` overrode the 10px header size | Font size applied to data cells only |

### 25 Sep 2026 — second tab: sentiment, volatility and regions

Adds a **Sentiment & regions** tab answering one question: when should money
move from bonds into stocks? Data through the 24 Sep close; surveys dated
individually. The Top 5 tab is unchanged apart from one correction below.

**The answer:** not yet for short-term money; gradually for decade money.

- *The arithmetic.* S&P forward earnings yield 5.19% (1 / 19.26) minus the
  10-year at 5.11% = **0.08 points** extra for owning stocks, at or near its
  thinnest since the dot-com bust against a historical 3–4 points.
- *The decade.* J.P. Morgan's 2026 LTCMA: EM stocks 7.8%, EAFE 7.4%, US large
  cap 6.7%, US aggregate bonds 5.3% — stocks ahead by 1.4 to 2.5 points a year.
  Vanguard's US range of 3.9–5.9% straddles that bond forecast, so the move
  into stocks favours international first.
- *Six signals*, each with today's reading: premium ≥ 2 pts (0.08); October hike
  odds < 30% (>70%); 10-year below 4.75% (5.11%); core CPI down three months
  running (one so far — partial); AAII bears > 55% **and** fund-manager cash > 5%
  (48.1% and 3.9%); VIX above 25 then back below 20 (14.21). **0 met, 1 partial.**
  A ladder moves a third of the bond overweight for every two signals.

**Volatility.** Two charts on the same dates, separate scales rather than a
dual axis: the VIX drifting toward 13 while the 10-year broke above 5%. Only
dated closes are plotted; two derived points are drawn hollow and explained,
and days without a confirmed close are left out rather than filled in.

**Sentiment, split three ways.** Retail is fearful (Fear & Greed 35; AAII bulls
32.7% after a 16-month low). Professionals are not (BofA cash 3.9%, under the
4.0% line that keeps BofA's own sell signal on; 49% net overweight stocks).
Credit is complacent (high-yield spread ≈270bp, tightest tenth of history).
That is why the capitulation signal requires retail and professionals together.

**Regional rankings.** Eight regions scored 1–5 at each horizon for a US-dollar
investor. Ties share a rank (standard competition ranking) instead of being
split arbitrarily. Four-horizon sums: Japan 15, Europe 14, EM 14, India 13,
Korea 11, Taiwan 11, US 10, China 10.

**Horizon state is shared** — changing it on either tab updates both.

**Errors found and fixed this round**

| Defect | Where | Fix |
|---|---|---|
| "Fear & Greed has not reached neutral once" this month — only a handful of September readings exist, not a daily series | Top 5 tab, since 21 Sep | Now "every September reading found has been in that zone" |
| A search returned the UK at +26.4% YTD — a **2025** figure | research | UK excluded, with the reason on the page |
| A search returned Hong Kong at +29% YTD — also 2025 | research | Not used; China uses MCHI −10.3% |
| Fund parser matched every `tk:` in the script, so regions would have been read as funds | `tests/audit.py` | Parsers scoped to their own arrays |
| Browser test expected 9 rows in the numbers table; the true union of dates is 8 | `tests/browser.mjs` | Test corrected — the page was right |
| Hover test moved the pointer over a chart 4,000px below the viewport | `tests/browser.mjs` | Scrolls first; added a tap test for phones |
| Region cards carried ~50px of dead space from a default paragraph margin | layout | Margin reset, now 13px |
| YTD line sat in different places on different region cards | layout | Fixed to its own line on every card |
| Double rule above the premium total | layout | One rule |
| Byline separators orphaned at the start of wrapped lines | both tabs, since 19 Sep v2 | Separators replaced by spacing |
| Four-tile stat rows split 3 + 1 on phones | both tabs | 2 × 2 on phones |

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
node tests/browser.mjs        # both tabs: overflow at 320/360/412/680px, JS errors,
                              # tabs + shared horizon, keyboard nav, ranking vs
                              # score table, charts, allocation, contrast
                              # (76 checks)
```

`browser.mjs` needs Playwright; set `PLAYWRIGHT_MODULE` to its `index.mjs` if
it is not resolvable. When fund weights, expense ratios or yields change, update
the `ER` and `YLD` tables in `audit.py` to match the page.

## Disclaimer

Educational summary of publicly reported market data. Not investment advice, not
a recommendation to buy or sell any security. Forecast ranges are scenario
estimates, not predictions. Verify current prices, yields and holdings before
trading.
