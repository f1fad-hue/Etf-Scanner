#!/usr/bin/env python3
"""Static audit for index.html: arithmetic, ranking method, structure, contrast.

Run: python3 tests/audit.py   (exits non-zero on any failure)

The blended fee and yield inputs below must match the fund stats shown on the
page; they live here because the page states the results, not the inputs.
"""
import re, sys, pathlib

PAGE = pathlib.Path(__file__).resolve().parent.parent / "index.html"
s = PAGE.read_text(encoding="utf-8")
js = s[s.rfind("<script>"):]
style = s[:s.find("</style>")]
fails = []

def check(cond, msg):
    print(("  PASS  " if cond else "  FAIL  ") + msg)
    if not cond:
        fails.append(msg)

# expense ratios and yields as displayed on the fund cards / cited in prose
ER = {"VTIP": .03, "RSP": .20, "VEA": .03, "XLV": .08, "ITA": .37}
YLD = {"VTIP": 2.21, "RSP": 1.46, "VEA": 2.36, "XLV": 1.49, "ITA": 1.29}

def block(name):
    """Source text of a top-level `var NAME = [ ... ];` array in the page script."""
    a = js.find("var %s = [" % name)
    assert a >= 0, name + " not found"
    return js[a:js.find("\n  ];", a)]

FUNDS_SRC = block("FUNDS")
funds = []
for tk in re.findall(r'tk:"(\w+)"', FUNDS_SRC):
    blk = FUNDS_SRC[FUNDS_SRC.find('tk:"%s"' % tk):]
    blk = blk[:blk.find("\n    },")]
    funds.append({
        "tk": tk,
        "w": int(re.search(r"\bw:(\d+)", blk).group(1)),
        "c": [int(x) for x in re.findall(r"\bc:(\d)", blk)],
        "prev": int(re.search(r"prev:(\d)", blk).group(1)),
    })

print("arithmetic")
w = {f["tk"]: f["w"] for f in funds}
check(sum(w.values()) == 100, f"weights sum to 100 (got {sum(w.values())})")
fee = sum(w[k] / 100 * ER[k] for k in w)
yld = sum(w[k] / 100 * YLD[k] for k in w)
m = re.search(r'fig-v">([\d.]+)%</div><div class="fig-k">Blended fee', s)
check(m and round(fee, 2) == float(m.group(1)), f"blended fee {fee:.4f}% rounds to page's {m and m.group(1)}%")
m = re.search(r'fig-v">~([\d.]+)%</div><div class="fig-k">Blended yield', s)
check(m and round(yld, 1) == float(m.group(1)), f"blended yield {yld:.4f}% rounds to page's ~{m and m.group(1)}%")
m = re.search(r'fig-v">(\d+)%</div><div class="fig-k">(\w+) \+ (\w+)', s)
if m:
    check(w[m.group(2)] + w[m.group(3)] == int(m.group(1)), f"{m.group(2)}+{m.group(3)} = {m.group(1)}%")

print("ranking follows the stated method (sum desc, 10y desc, previous order)")
for f in funds:
    check(len(f["c"]) == 4, f'{f["tk"]} has four horizon scores')
want = [f["tk"] for f in sorted(funds, key=lambda f: (-sum(f["c"]), -f["c"][3], f["prev"]))]
check(want == [f["tk"] for f in funds], f"order {[f['tk'] for f in funds]} == computed {want}")

print("structure")
for tag in ["div", "section", "article", "table", "tbody", "thead", "ul", "li", "p", "span", "header"]:
    o, c = len(re.findall(r"<%s[\s>]" % tag, s)), len(re.findall(r"</%s>" % tag, s))
    if o != c:
        check(False, f"<{tag}> balanced ({o} open / {c} close)")
defined = set(re.findall(r"(--[\w-]+)\s*:", s))
used = set(re.findall(r"var\((--[\w-]+)", s))
check(not (used - defined), f"no undefined CSS vars {sorted(used - defined) or ''}")
check(not (defined - used), f"no dead CSS vars {sorted(defined - used) or ''}")

print("contrast (WCAG AA)")
def lum(h):
    c = [int(h[i:i + 2], 16) / 255 for i in (1, 3, 5)]
    c = [x / 12.92 if x <= .03928 else ((x + .055) / 1.055) ** 2.4 for x in c]
    return .2126 * c[0] + .7152 * c[1] + .0722 * c[2]
def ratio(a, b):
    x, y = sorted([lum(a), lum(b)], reverse=True)
    return (x + .05) / (y + .05)
tok = dict(re.findall(r"(--[\w-]+):(#[0-9A-Fa-f]{6})", style))
for t in ["--ink", "--ink-2", "--ink-3", "--accent", "--warn"]:
    for bg in ["--paper", "--surface", "--surface-sunk"]:
        r = ratio(tok[t], tok[bg])
        if r < 4.5:
            check(False, f"{t} on {bg} {r:.2f}:1")
check(True, "ink tokens >= 4.5:1 on all three surfaces")
for t in [k for k in tok if k.startswith("--t-")]:
    check(ratio(tok[t], tok["--surface"]) >= 4.5, f"chip text {t} {ratio(tok[t], tok['--surface']):.2f}:1")


print("sentiment & regions tab")
REG_SRC = block("REGIONS")
regions = []
for m in re.finditer(r'\{n:"([^"]+)", tk:"(\w+)"', REG_SRC):
    blk = REG_SRC[m.start():]
    blk = blk[:blk.find("}}}") + 3]
    regions.append({"n": m.group(1), "tk": m.group(2),
                    "c": {h: int(c) for h, c in re.findall(r'"(3m|6m|12m|10y)":\{c:(\d)', blk)}})
check(len(regions) == 8, f"8 regions ({len(regions)})")
for r in regions:
    check(set(r["c"]) == {"3m", "6m", "12m", "10y"} and all(1 <= v <= 5 for v in r["c"].values()),
          f'{r["n"]} scored 1-5 at all four horizons')

# the premium arithmetic shown on the page
ey = 100 / 19.26
check(f"{ey:.2f}" == "5.19", f"earnings yield 1/19.26 = {ey:.3f}% -> 5.19%")
check(f"{5.19 - 5.11:.2f}" == "0.08", "premium 5.19 - 5.11 = 0.08 pts")
check(round(6.7 - 5.3, 1) == 1.4 and round(7.8 - 5.3, 1) == 2.5, "JPM stock-over-bond edge 1.4 (US) to 2.5 (EM)")
lvl = 7706.03 * (1 - 0.0051)
check(abs(lvl / 7650.50 - 1) < 0.003, f"S&P {lvl:.1f} within 0.3% of 18 Sep 7,650.50 ({(lvl/7650.50-1)*100:+.2f}%)")
check(abs(14.21 / 1.0683 - 13.30) < 0.005, f"derived 22 Sep VIX 14.21/1.0683 = {14.21/1.0683:.3f}")
check(abs(4.96 + 0.04 - 5.00) < 1e-9, "derived 18 Sep 10-yr 4.96 + 0.04 = 5.00")
check(abs(5.11 - 4.75 - 0.36) < 1e-9, "4.75% threshold is 36bp under 5.11%")

# signal tallies: statuses in the markup must match every summary of them
st = re.findall(r'class="tr" data-status="(\w+)"', s)
met, part, no = st.count("met"), st.count("part"), st.count("not")
check(len(st) == 6, f"six signals ({len(st)})")
check(f'<div class="kpi-v">{met} of 6</div>' in s, f"KPI says {met} of 6 met")
check(f'<span class="tag">{met} met</span>' in s and f"◐ {part} partial" in s and f"○ {no} not met" in s,
      f"summary tags {met} met / {part} partial / {no} not met")
rung = {0: "0–1 met", 1: "0–1 met", 2: "2–3 met", 3: "2–3 met", 4: "4–5 met", 5: "4–5 met", 6: "All 6"}[met]
check(f'<div class="rung on"><div class="k">{rung}</div>' in s and s.count('class="rung on"') == 1,
      f'rule ladder highlights "{rung}" only')

# gauge markers and reference lines must sit inside their stated scales
for m in re.finditer(r'class="scale" data-min="([\d.]+)" data-max="([\d.]+)" data-v="([\d.]+)"(?: data-ref="([\d.]+)")?', s):
    lo, hi, v, ref = float(m.group(1)), float(m.group(2)), float(m.group(3)), m.group(4)
    check(lo <= v <= hi and (ref is None or lo <= float(ref) <= hi), f"gauge {v} (ref {ref}) inside {lo}-{hi}")

# chart points must fall inside their axes, or the SVG clips them silently
for key in ("vix", "ust"):
    blk = js[js.find("    %s: {el:" % key):]
    blk = blk[:blk.find("]}") + 2]
    y0, y1 = map(float, re.search(r"y:\[([\d.]+),([\d.]+)\]", blk).groups())
    vals = [float(v) for v in re.findall(r"v:([\d.]+)", blk)]
    dates = re.findall(r'd:"(2026-\d\d-\d\d)"', blk)
    check(all(y0 <= v <= y1 for v in vals), f"{key}: all {len(vals)} values (incl. ref) inside y {y0}-{y1}")
    check(all("2026-09-10" <= d <= "2026-09-24" for d in dates) and dates == sorted(dates), f"{key}: dates sorted and inside 10-24 Sep")


print("whole-portfolio allocation (max 10-yr growth within a worst-crash budget)")
import math
# the documented assumptions (sources on the page); the page's fund data must match them
EXP = {"VTIP": 4.0, "RSP": 6.7, "VEA": 7.4, "XLV": 6.7, "ITA": 6.7}
CRASH = {"VTIP": 6.27, "RSP": 59.92, "VEA": 60.68, "XLV": 39.17, "ITA": 59.72}
for tk in ER:
    m = re.search(r'tk:"%s", asset:"(\w+)", er:([\d.]+), yld:([\d.]+), exp:([\d.]+), crash:([\d.]+)' % tk, FUNDS_SRC)
    check(m and float(m.group(2)) == ER[tk] and float(m.group(3)) == YLD[tk], f"{tk} er/yld in page data match")
    check(m and float(m.group(4)) == EXP[tk] and float(m.group(5)) == CRASH[tk], f"{tk} forecast {EXP[tk]}% and crash {CRASH[tk]}% in page data")
for name, val in [("FLOOR", 5), ("CAP", 30), ("HORIZON", 10), ("STEP_BUDGET", 5)]:
    check(re.search(r"\b%s = %d\b" % (name, val), js) is not None, f"model constant {name} = {val}")
FLOOR, CAP, STEP = 5, 30, 5
STK = ["RSP", "VEA", "XLV", "ITA"]

def optimize(B):
    """Independent re-implementation: greedy fractional knapsack in whole points."""
    w = {k: FLOOR for k in STK}; w["VTIP"] = 100 - FLOOR * len(STK)
    tot = lambda: sum(w[k] * round(CRASH[k] * 100) for k in w)
    if tot() > B * 10000: return None
    eff = lambda k: (EXP[k] - EXP["VTIP"]) / (CRASH[k] - CRASH["VTIP"])
    for k in sorted(STK, key=lambda k: -eff(k)):
        while w[k] < CAP and w["VTIP"] > 0:
            w[k] += 1; w["VTIP"] -= 1
            if tot() > B * 10000: w[k] -= 1; w["VTIP"] += 1; break
    return w

def stats(w):
    r = sum(w[k] * EXP[k] for k in w) / 100; d = sum(w[k] * CRASH[k] for k in w) / 100
    return r, d, 10000 * (1 + r / 100) ** 10, math.log(1 / (1 - d / 100)) / math.log(1 + r / 100)

front, last = [], None
for B in range(1, 101):
    w = optimize(B)
    if not w: continue
    if w == last: break
    front.append((B, w, stats(w))); last = w
ok_all = all(sum(w.values()) == 100 and w["VTIP"] >= 0 and all(FLOOR <= w[k] <= CAP for k in STK) and st[1] <= B + 1e-9
             for B, w, st in front)
check(ok_all, f"all {len(front)} frontier mixes sum to 100, respect 5-30% bounds and stay within budget")
check(all(front[i][2][0] <= front[i + 1][2][0] for i in range(len(front) - 1)), "expected return never falls as the budget rises")
MIN_B, MAX_B = front[0][0], front[-1][0]
REC = max((x for x in front if x[2][3] <= 5.0), key=lambda x: x[2][0])
REC_B = REC[0]
print(f"         (frontier -{MIN_B}% .. -{MAX_B}%, recommended -{REC_B}%: {REC[1]})")
pt = lambda B: [x for x in front if x[0] <= B][-1]
S = lambda B: 100 - pt(B)[1]["VTIP"]
r0, d0, g0, rc0 = REC[2]; mn, mx = pt(MIN_B), pt(MAX_B)
rungs = [REC_B + STEP * i for i in range(4)]
xlv_share = round(100 * REC[1]["XLV"] / S(REC_B))

# Schwab sensitivity: same budget with US stocks at 5.9%
_e = dict(EXP)
for k in ("RSP", "XLV", "ITA"): EXP[k] = 5.9
alt_s = 100 - optimize(REC_B)["VTIP"]
EXP.update(_e)

claims = [
    (f'<div class="kpi-v">{S(REC_B)} / {100-S(REC_B)}</div>', "tab 2 KPI split"),
    (f"worst case −{REC_B}%</div>", "tab 2 KPI budget"),
    (f"puts {S(REC_B)}% in stocks and {100-S(REC_B)}% in bonds today", "tab 2 thesis"),
    (f"is {100-S(REC_B)}% bonds and {S(REC_B)}% stocks", "tab 1 pointer"),
    (f"The default, a {REC_B}% worst case", "section intro"),
    (f"Worst-case budget {rungs[0]}%: {S(rungs[0])}% stocks / {100-S(rungs[0])}% bonds.", "ladder rung 1"),
    (f"Budget {rungs[1]}%: {S(rungs[1])} / {100-S(rungs[1])}.", "ladder rung 2"),
    (f"Budget {rungs[2]}%: {S(rungs[2])} / {100-S(rungs[2])}.", "ladder rung 3"),
    (f"Budget {rungs[3]}%: {S(rungs[3])} / {100-S(rungs[3])}.", "ladder rung 4"),
    (f"{S(REC_B)}% stocks · {100-S(REC_B)}% bonds</div>", "horizon rows 3m/6m"),
    (f"rises to {rungs[1]}% — {S(rungs[1])}% stocks", "horizon row 6m"),
    (f"{S(REC_B)}% → {S(rungs[3])}% stocks", "horizon row 12m"),
    (f"from {rungs[0]}% toward {rungs[3]}%", "horizon row 12m budgets"),
    (f"Why {REC_B}%, not the maximum", "why heading"),
    (f"about ${mx[2][2]:,.0f} in ten years", "max-growth ending value"),
    (f"${mx[2][2]-g0:,.0f} more than the recommended mix", "max vs recommended gap"),
    (f"about {mx[2][1]:.0f}%, would take roughly {mx[2][3]:.1f} years", "max-growth crash and recovery"),
    (f"{mn[1]['VTIP']}% in VTIP — holds the worst case near {mn[2][1]:.0f}%, but ends near ${mn[2][2]:,.0f}", "least-drawdown line"),
    (f"a {REC_B}% worst case — ends near ${g0:,.0f} and would recover from its worst crash in about {rc0:.1f} years", "recommended line"),
    (f"XLV at {xlv_share}% of the stock side", "XLV share"),
    (f"would hold only {alt_s}% in stocks", "Schwab sensitivity"),
    (f"thin against a {mx[2][1]:.0f}% worst case", "10-yr stance crash"),
    ("RSP 59.9%, VEA 60.7%, ITA 59.7% and XLV 39.2%", "assumptions: crash depths"),
    ("its worst fall, 6.3% in March 2020", "assumptions: VTIP crash"),
]
for txt, why in claims:
    check(txt in s, f"{why}: \"{txt[:60]}\"")

print()
print("ALL CHECKS PASSED" if not fails else f"{len(fails)} CHECK(S) FAILED")
sys.exit(1 if fails else 0)
