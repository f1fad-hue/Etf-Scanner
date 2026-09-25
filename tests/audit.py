#!/usr/bin/env python3
"""Static audit for index.html: data, arithmetic, stated claims, structure, contrast.

Run: python3 tests/audit.py   (exits non-zero on any failure)

The allocation model is re-implemented here from the documented assumptions,
independently of the page's JavaScript; every number the page states in prose
is then recomputed and matched against the text.
"""
import math, re, sys, pathlib

PAGE = pathlib.Path(__file__).resolve().parent.parent / "index.html"
s = PAGE.read_text(encoding="utf-8")
js = s[s.rfind("<script>"):]
style = s[:s.find("</style>")]
fails = []

def check(cond, msg):
    print(("  PASS  " if cond else "  FAIL  ") + msg)
    if not cond:
        fails.append(msg)

def block(name):
    """Source text of a top-level `var NAME = [ ... ];` array in the page script."""
    a = js.find("var %s = [" % name)
    assert a >= 0, name + " not found"
    return js[a:js.find("\n  ];", a)]

# ---------------------------------------------------------------- fund data
# documented inputs (sources on the page): fee, yield, J.P. Morgan forecast, worst crash
ER    = {"VTIP": .03, "RSP": .20, "VEA": .03, "XLV": .08, "ITA": .37}
YLD   = {"VTIP": 2.21, "RSP": 1.46, "VEA": 2.36, "XLV": 1.49, "ITA": 1.29}
EXP   = {"VTIP": 4.0, "RSP": 6.7, "VEA": 7.4, "XLV": 6.7, "ITA": 6.7}
CRASH = {"VTIP": 6.27, "RSP": 59.92, "VEA": 60.68, "XLV": 39.17, "ITA": 59.72}

FUNDS_SRC = block("FUNDS")
funds = []
for tk in re.findall(r'tk:"(\w+)"', FUNDS_SRC):
    blk = FUNDS_SRC[FUNDS_SRC.find('tk:"%s"' % tk):]
    blk = blk[:blk.find("} } }") + 5]
    m = re.search(r'asset:"(\w+)", er:([\d.]+), yld:([\d.]+), exp:([\d.]+), crash:([\d.]+)', blk)
    funds.append({
        "tk": tk, "asset": m.group(1), "er": float(m.group(2)), "yld": float(m.group(3)),
        "exp": float(m.group(4)), "crash": float(m.group(5)),
        "c": [int(x) for x in re.findall(r"\bc:(\d)", blk)],
        "b": re.findall(r'\bb:"([^"]+)"', blk),
        "prev": int(re.search(r"prev:(\d)", blk).group(1)),
        "stats": dict((k, v) for v, k in re.findall(r'\["([^"]+)","([^"]+)"\]', blk)),
    })
F = {f["tk"]: f for f in funds}

print("fund data")
check([f["tk"] for f in funds] == ["VTIP", "RSP", "VEA", "XLV", "ITA"], "five funds in display order")
for tk in ER:
    f = F[tk]
    check((f["er"], f["yld"], f["exp"], f["crash"]) == (ER[tk], YLD[tk], EXP[tk], CRASH[tk]),
          f"{tk}: fee {ER[tk]}, yield {YLD[tk]}, forecast {EXP[tk]}, crash {CRASH[tk]}")
    shown_fee = f["stats"].get("Fee"); shown_yld = f["stats"].get("Yield") or f["stats"].get("SEC yield")
    check(shown_fee == f"{ER[tk]:.2f}%" and shown_yld == f"{YLD[tk]:.2f}%", f"{tk}: card shows fee {shown_fee}, yield {shown_yld}")
check(F["VTIP"]["asset"] == "bond" and all(F[k]["asset"] == "stock" for k in ("RSP", "VEA", "XLV", "ITA")), "one bond fund, four stock funds")

print("fund scores and ranges")
for f in funds:
    check(len(f["c"]) == 4 and all(1 <= c <= 5 for c in f["c"]), f'{f["tk"]}: four scores 1-5 {f["c"]}')
want = [f["tk"] for f in sorted(funds, key=lambda f: (-sum(f["c"]), -f["c"][3], f["prev"]))]
check(want == [f["tk"] for f in funds], f"order follows the stated method (sum, then 10-yr, then last order): {want}")
num = lambda t: [float(x.replace("−", "-")) for x in re.findall(r"[−+-]?\d+(?:\.\d+)?", t)]
for f in funds:
    for label, band in zip(("3m", "6m", "12m", "10y"), f["b"]):
        lo, hi = num(band)[:2]
        check(lo < hi, f'{f["tk"]} {label} range "{band}" is low-to-high')
    lo, hi = num(f["b"][3])[:2]
    check(lo <= f["exp"] <= hi, f'{f["tk"]} 10-yr range {lo}–{hi}% contains the {f["exp"]}% forecast the optimizer uses')

# ------------------------------------------------------------- allocation
print("allocation (max 10-yr growth within a worst-crash budget, net of fees)")
for name, val in [("FLOOR", 5), ("CAP", 30), ("HORIZON", 10), ("STEP_BUDGET", 5)]:
    check(re.search(r"\b%s = %d\b" % (name, val), js) is not None, f"model constant {name} = {val}")
check("RECOVER_WITHIN = HORIZON / 2" in js, "recovery target is half the horizon")
FLOOR, CAP, STEP = 5, 30, 5
STK = ["RSP", "VEA", "XLV", "ITA"]

def optimize(B, exp=EXP):
    """Independent exact solver, decomposed differently from the page: enumerate
    RSP, XLV and ITA in whole points, then give VEA the most the budget allows."""
    net = {k: round((exp[k] - ER[k]) * 100) for k in exp}; C = {k: round(CRASH[k] * 100) for k in CRASH}
    best = None
    for a in range(FLOOR, CAP + 1):
        for c in range(FLOOR, CAP + 1):
            for d in range(FLOOR, CAP + 1):
                rest = 100 - a - c - d
                crash = a * C["RSP"] + c * C["XLV"] + d * C["ITA"]
                y = min(CAP, rest, (B * 10000 - crash - rest * C["VTIP"]) // (C["VEA"] - C["VTIP"]))
                if y < FLOOR: continue
                w = {"RSP": a, "VEA": y, "XLV": c, "ITA": d, "VTIP": rest - y}
                key = (sum(w[k] * net[k] for k in w), -sum(w[k] * C[k] for k in w))
                if best is None or key > best[0]: best = (key, w)
    return best and best[1]

def stats(w):
    r = sum(w[k] * (EXP[k] - ER[k]) for k in w) / 100; d = sum(w[k] * CRASH[k] for k in w) / 100
    return r, d, 10000 * (1 + r / 100) ** 10, math.log(1 / (1 - d / 100)) / math.log(1 + r / 100)

front, last = [], None
for B in range(1, 101):
    w = optimize(B)
    if not w: continue
    if w == last: break
    front.append((B, w, stats(w))); last = w
check(all(sum(w.values()) == 100 and all(FLOOR <= w[k] <= CAP for k in STK) and w["VTIP"] >= 0 and st[1] <= B + 1e-9
          for B, w, st in front), f"all {len(front)} frontier mixes sum to 100, respect 5–30% bounds and stay within budget")
check(all(front[i][2][0] < front[i + 1][2][0] for i in range(len(front) - 1)), "expected return rises with every budget step")

# brute force over every whole-point mix: the solver must match it exactly
def brute(B):
    best = None
    for a in range(FLOOR, CAP + 1):
        for b in range(FLOOR, CAP + 1):
            for c in range(FLOOR, CAP + 1):
                for d in range(FLOOR, CAP + 1):
                    v = 100 - a - b - c - d
                    if v < 0: continue
                    w = {"RSP": a, "VEA": b, "XLV": c, "ITA": d, "VTIP": v}
                    cr = sum(w[k] * round(CRASH[k] * 100) for k in w)
                    if cr > B * 10000: continue
                    key = (sum(w[k] * round((EXP[k] - ER[k]) * 100) for k in w), -cr)
                    if best is None or key > best[0]: best = (key, w)
    return best[1]
MIN_B, MAX_B = front[0][0], front[-1][0]
REC = max((x for x in front if x[2][3] <= 5.0), key=lambda x: x[2][0]); REC_B = REC[0]
pt = lambda B: [x for x in front if x[0] <= B][-1]
for B in sorted({MIN_B, REC_B, REC_B + 5, REC_B + 10, REC_B + 15, MAX_B}):
    check(pt(B)[1] == brute(B), f"budget −{B}%: solver mix {pt(B)[1]} equals brute force over all mixes")
print(f"         (frontier −{MIN_B}% .. −{MAX_B}%, recommended −{REC_B}%: {REC[1]})")
nxt = [x for x in front if x[0] > REC_B][0]
check(nxt[2][3] > 5.0, f"next budget up (−{nxt[0]}%) would take {nxt[2][3]:.2f} yrs to recover, over 5")

S = lambda B: 100 - pt(B)[1]["VTIP"]
r0, d0, g0, rc0 = REC[2]; mx = pt(MAX_B)
xlv_share = round(100 * REC[1]["XLV"] / S(REC_B))
alt = dict(EXP); alt.update({"RSP": 5.9, "XLV": 5.9, "ITA": 5.9})
wa = optimize(REC_B, alt); alt_s = 100 - wa["VTIP"]
check(max(STK, key=lambda k: wa[k]) == "VEA", f"Schwab case tilts to VEA ({wa})")
check(mx[2][3] > 10, f"all-stock mix takes {mx[2][3]:.1f} yrs to recover — longer than the 10-yr horizon, as stated")

claims = [
    (f"<h1>{S(REC_B)}% stocks, {100-S(REC_B)}% bonds</h1>", "Allocation headline"),
    (f"The default, a {REC_B}% worst case", "Allocation standfirst"),
    (f"<b>All stocks</b> ends about ${mx[2][2]-g0:,.0f} ahead over ten years", "max vs recommended gap"),
    (f"its {mx[2][1]:.0f}% worst case would take about {mx[2][3]:.1f} years to recover", "max crash and recovery"),
    (f"({xlv_share}% of the stock side)", "XLV share of stocks"),
    (f"the same {REC_B}% budget would hold only {alt_s}% in stocks, tilted to VEA", "Schwab sensitivity"),
    (f"thin against a {mx[2][1]:.0f}% worst case", "10-yr stance"),
    (f"RSP {CRASH['RSP']:.1f}%, VEA {CRASH['VEA']:.1f}%, ITA {CRASH['ITA']:.1f}%, XLV {CRASH['XLV']:.1f}%", "assumptions: crash depths"),
    (f"its worst, {CRASH['VTIP']:.1f}% in March 2020", "assumptions: VTIP crash"),
    (f"US large cap {EXP['RSP']}% a year (RSP, XLV, ITA), developed ex-US {EXP['VEA']}% (VEA)", "assumptions: forecasts"),
    (f"VTIP {EXP['VTIP']}% is an assumption", "assumptions: VTIP forecast"),
    (f"Every fund at least {FLOOR}%, no stock fund above {CAP}%", "assumptions: bounds"),
    (f"Each two of the six signals on the Markets tab raise the budget {STEP} points", "signal step"),
]
for txt, why in claims:
    check(txt in s, f'{why}: "{txt[:70]}"')

# ----------------------------------------------------------------- markets
print("markets arithmetic")
lo_pe, hi_pe = 19.1, 19.4
check("19.1 (FactSet) to 19.4 (StreetStats" in s, "premium box cites P/E 19.1 and 19.4")
check(f"{100/hi_pe:.2f}–{100/lo_pe:.2f}%" == "5.15–5.24%" and '<div class="v">5.15–5.24%</div>' in s,
      f"earnings yield 1/19.4–1/19.1 = {100/hi_pe:.3f}–{100/lo_pe:.3f}% -> 5.15–5.24%")
check(abs(397.02 / 7704.13 * 100 - 100 / hi_pe) < 0.01, f"StreetStats EPS $397.02 / S&P 7,704.13 = {397.02/7704.13*100:.3f}% (≈ 1/19.4)")
p_lo, p_hi = 100 / hi_pe - 5.11, 100 / lo_pe - 5.11
check(f"{p_lo:.2f}–{p_hi:.2f} pts" == "0.04–0.13 pts" and '<div class="v">0.04–0.13 pts</div>' in s,
      f"premium {p_lo:.3f}–{p_hi:.3f} pts -> 0.04–0.13")
check(round((p_lo + p_hi) / 2, 1) == 0.1 and s.count("≈0.1 pt") >= 2, "headline ≈0.1 pt is the rounded midpoint")
check(round(6.7 - 5.3, 1) == 1.4 and round(7.8 - 5.3, 1) == 2.5 and "by 1.4–2.5 points a year" in s,
      "J.P. Morgan stock-over-bond edge 1.4 (US) to 2.5 (EM)")
fc = re.findall(r'\{n:"[^"]+", v:([\d.]+)', block("FORECASTS"))
check([float(x) for x in fc] == [7.8, 7.4, 6.7, 5.3] and "lo:3.9, hi:5.9" in js, "forecast bars 7.8 / 7.4 / 6.7 / 5.3 and Vanguard 3.9–5.9")
check(abs(-1.90 / (7704.13 + 1.90)) < 0.001 and '<div class="kpi-v">7,704</div>' in s and "flat Thursday" in s,
      f"S&P 7,704.13, −1.90 pts ({-1.90/7706.03*100:+.3f}%) shown as 7,704, flat")
check(abs(7 / 503 * 100 - 1.4) < 0.05 and '["~1.4%","Mag 7 weight"]' in s, f"RSP Mag 7 weight 7/503 = {7/503*100:.2f}%")

print("signals")
st = re.findall(r'class="sig" data-status="(\w+)"', s)
met, part = st.count("met"), st.count("part")
check(len(st) == 6, f"six signals ({len(st)})")
check(f'<div class="kpi-v">{met} of 6</div>' in s and f"◐ {part} partial" in s, f"KPI: {met} of 6 met, {part} partial")

print("charts and gauges")
series = {}
for key in ("vix", "ust"):
    blk = js[js.find("    %s: {el:" % key):]
    blk = blk[:blk.find("]}") + 2]
    y0, y1 = map(float, re.search(r"y:\[([\d.]+),([\d.]+)\]", blk).groups())
    ref = float(re.search(r"ref:\{v:([\d.]+)", blk).group(1))
    pts = [(d, float(v)) for d, v in re.findall(r'\{d:"(2026-\d\d-\d\d)",v:([\d.]+)\}', blk)]
    series[key] = (pts, ref)
    vals = [v for _, v in pts] + [ref]
    dates = [d for d, _ in pts]
    check(all(y0 <= v <= y1 for v in vals), f"{key}: {len(pts)} closes and ref inside y {y0}–{y1}")
    check(dates == sorted(set(dates)) and "2026-09-10" <= dates[0] and dates[-1] == "2026-09-24", f"{key}: dates unique, sorted, ending 24 Sep")
vix, vref = series["vix"]; ust, _ = series["ust"]
check(vref >= max(v for _, v in vix), f"VIX one-month high {vref} is at least every plotted close")
v = [x for _, x in vix]
check(v[-3] < v[-2] < v[-1] and v[-4] > v[-3], f"VIX 'up two days running': {v[-4]} > {v[-3]} < {v[-2]} < {v[-1]}")
check(f'<div class="kpi-v">{v[-1]:.2f}</div>' in s and f'<div class="sig-now">{v[-1]:.2f}</div>' in s and f"VIX {v[-1]:.2f}" in s,
      f"VIX {v[-1]:.2f} consistent in KPI, signal and summary")
u = [x for _, x in ust]
check(round((u[-2] - u[-3]) * 100) == 15 and "about 15bp in a day" in s, f"10-year jump {u[-3]} -> {u[-2]} = 15bp")
check(f'<div class="kpi-v">{u[-1]:.2f}%</div>' in s and f'<div class="sig-now">{u[-1]:.2f}%</div>' in s, f"10-year {u[-1]:.2f}% consistent")
for m in re.finditer(r'class="scale" data-min="([\d.]+)" data-max="([\d.]+)" data-v="([\d.]+)"(?: data-ref="([\d.]+)")?', s):
    lo, hi, val, ref = float(m.group(1)), float(m.group(2)), float(m.group(3)), m.group(4)
    check(lo <= val <= hi and (ref is None or lo <= float(ref) <= hi), f"gauge {val} (ref {ref}) inside {lo}–{hi}")
check("Bears 48.1% vs a 31.0% average" in s and 'data-ref="37.5"' in s, "AAII long-run averages: bulls 37.5%, bears 31.0%")

print("regions")
REG_SRC = block("REGIONS")
regions = []
for m in re.finditer(r'\{n:"([^"]+)", tk:"(\w+)"', REG_SRC):
    blk = REG_SRC[m.start():]
    blk = blk[:blk.find("}}}") + 3]
    regions.append({"n": m.group(1), "c": {h: int(c) for h, c in re.findall(r'"(3m|6m|12m|10y)":\{c:(\d)', blk)}})
check(len(regions) == 8, f"8 regions ({len(regions)})")
for r in regions:
    check(set(r["c"]) == {"3m", "6m", "12m", "10y"} and all(1 <= x <= 5 for x in r["c"].values()), f'{r["n"]} scored 1–5 at all four horizons')

# ------------------------------------------------------------ consistency
print("consistency and stale text")
for phrase in ["70–78%", "33.9%", "5.11%"]:
    check(s.count(phrase) >= 2, f'"{phrase}" repeated consistently ({s.count(phrase)}×)')
for stale in ["within 0.3%", "−0.51%", "13.30", "long-run 60", "third daily rise", "31.5% average",
              "5.16–", "0.05–0.13", "level with the S&amp;P", "0.08 points", "1 / 19.26"]:
    check(stale not in s, f'stale text "{stale}" is gone')
hrefs = re.findall(r'href="([^"]+)"', s)
dups = sorted({h for h in hrefs if hrefs.count(h) > 1 and h.startswith("http")})
check(not dups, f"no duplicate source links {dups or ''}")
check(all(h.startswith("https://") for h in hrefs if h.startswith("http")), "every source link is https")

# --------------------------------------------------------------- structure
print("structure")
for tag in ["div", "section", "article", "table", "tbody", "thead", "ul", "li", "p", "span", "details", "footer", "button"]:
    o, c = len(re.findall(r"<%s[\s>]" % tag, s)), len(re.findall(r"</%s>" % tag, s))
    check(o == c, f"<{tag}> balanced ({o} open / {c} close)")
ids = re.findall(r'\bid="([\w-]+)"', s)
check(len(ids) == len(set(ids)), "element ids unique")
for i in set(re.findall(r'getElementById\("([\w-]+)"\)', js)):
    check(i in ids, f"script target #{i} exists")
for a in re.findall(r'aria-controls="([\w-]+)"', s) + re.findall(r'data-goto="([\w-]+)"', s):
    check(a in ids, f"reference #{a} exists")
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
        check(r >= 4.5, f"{t} on {bg} {r:.2f}:1")
for t in [k for k in tok if k.startswith("--t-")]:
    check(ratio(tok[t], tok["--surface"]) >= 4.5, f"chip text {t} {ratio(tok[t], tok['--surface']):.2f}:1")

print()
print("ALL CHECKS PASSED" if not fails else f"{len(fails)} CHECK(S) FAILED")
sys.exit(1 if fails else 0)
