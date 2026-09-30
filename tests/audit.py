#!/usr/bin/env python3
"""Static audit for index.html: data, arithmetic, stated claims, structure, contrast.

Run: python3 tests/audit.py   (exits non-zero on any failure)

The allocation model is re-implemented here from the documented assumptions,
independently of the page's JavaScript; every number the page states in prose
is then recomputed and matched against the text.
"""
import json, math, re, sys, pathlib

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
DATA  = json.loads((pathlib.Path(__file__).resolve().parent / "data.json").read_text(encoding="utf-8"))
ER, YLD, EXP, CRASH = ({k: v[f] for k, v in DATA["funds"].items()} for f in ("er", "yld", "exp", "crash"))

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
    w = [num(b)[1] - num(b)[0] for b in f["b"][:3]]      # 3m, 6m, 12m widths in points
    if f["asset"] == "stock":
        check(1.25 <= w[1] / w[0] <= 1.55 and 1.75 <= w[2] / w[0] <= 2.25,
              f'{f["tk"]}: range widths {w} widen with the square root of time (6m ≈ 1.4×, 12m ≈ 2× the 3-month width)')
    else:
        check(w[0] < w[1] < w[2], f'{f["tk"]}: range widths {w} widen with the horizon')
    lo, hi = num(f["b"][3])[:2]
    if f["tk"] == "XLV":
        others = [num(g["b"][2])[1] - num(g["b"][2])[0] for g in funds if g["asset"] == "stock" and g["tk"] != "XLV"]
        check(w[2] < min(others), f'XLV 12-month width {w[2]} is below every other stock fund {others}, as its 39% worst crash (vs about 60%) implies')
    check(lo <= f["exp"] <= hi, f'{f["tk"]} 10-yr range {lo}–{hi}% contains the {f["exp"]}% forecast the optimizer uses')


# ------------------------------------------------------------- market inputs
# tests/data.json holds the dated closes, keyed once from the cited sources. Everything
# below is checked against that table, and the page's own chart data is checked against it too.
# date: (S&P close, AP point change, 10-yr %, VIX close, reported VIX % change)
DAYS = {d: tuple(v) for d, v in DATA["days"].items() if not d.startswith("_")}
CHART_DATES = [d for d in DAYS if d >= "2026-09-17"]
SP24, SP29, TEN29 = DAYS["2026-09-24"][0], DAYS["2026-09-29"][0], DAYS["2026-09-29"][2]

print("market data table")
dates = list(DAYS)
for i in range(1, len(dates)):
    (sp0, _, _, v0, _), (sp1, chg, _, v1, vpct) = DAYS[dates[i - 1]], DAYS[dates[i]]
    if chg is not None:
        check(abs(sp0 + chg - sp1) < 0.005, f"{dates[i]}: S&P {sp0:,.2f} {chg:+.2f} = {sp1:,.2f}, as AP reports")
    if vpct is not None:
        check(abs((v1 / v0 - 1) * 100 - vpct) < 0.06, f"{dates[i]}: VIX {v0} -> {v1} = {(v1/v0-1)*100:+.2f}% (reported {vpct:+.2f}%)")
check(max(16.07, 16.11, 16.17) - min(16.07, 16.11, 16.17) <= 0.10 + 1e-9 and "up to about 0.1 (28 Sep VIX: 16.07 to 16.17)" in s,
      "the three 28 Sep VIX prints span 0.10, and the page says so")
check(abs((16.11 / 14.87 - 1) * 100 - 8.33) < 0.01 and abs((16.17 / 14.87 - 1) * 100 - 8.74) < 0.02, "the 16.11 (+8.33%) and 16.17 (+8.75%) reports share the 14.87 base with Saxo's 16.07")
ten = lambda d: DAYS[d][2]
check([round((ten(b) - ten(a)) * 100) for a, b in (("2026-09-22", "2026-09-23"), ("2026-09-23", "2026-09-24"), ("2026-09-25", "2026-09-28"))] == [15, 9, 6],
      "10-year moves match AP: +15bp (23 Sep), +9bp (24 Sep), +6bp (28 Sep)")

# the page's own chart data must equal the table
series = {}
for key, col in (("vix", 3), ("ust", 2)):
    blk = js[js.find("    %s: {el:" % key):]
    blk = blk[:blk.find("]}") + 2]
    y0, y1 = map(float, re.search(r"y:\[([\d.]+),([\d.]+)\]", blk).groups())
    ref = float(re.search(r"ref:\{v:([\d.]+)", blk).group(1))
    pts = [(d, float(v)) for d, v in re.findall(r'\{d:"(2026-\d\d-\d\d)",v:([\d.]+)\}', blk)]
    series[key] = (pts, ref)
    check(pts == [(d, DAYS[d][col]) for d in CHART_DATES], f"{key}: the page's {len(pts)} plotted closes equal the keyed table, 17–29 Sep")
    check(all(y0 <= v <= y1 for _, v in pts) and y0 <= ref <= y1, f"{key}: closes and reference line inside y {y0}–{y1}")
vix, vref = series["vix"]; ust, _ = series["ust"]
check(vref == 20 and "dashed line: 20, where signal 6 needs it back below" in s, "VIX reference line is the signal-6 level, 20")

# ----------------------------------------------------------------- allocation
print("allocation (max 10-yr growth within a worst-crash budget, net of fees)")
for name, val in [("FLOOR", 5), ("CAP", 30), ("HORIZON", 10), ("STEP_BUDGET", 5)]:
    check(re.search(r"\b%s = %d\b" % (name, val), js) is not None, f"model constant {name} = {val}")
check("RECOVER_WITHIN = HORIZON / 2" in js, "recovery target is half the horizon")
FLOOR, CAP, STEP = 5, 30, 5
STK = ["RSP", "VEA", "XLV", "ITA"]

def optimize(B, exp):
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

def stats(w, exp):
    r = sum(w[k] * (exp[k] - ER[k]) for k in w) / 100; d = sum(w[k] * CRASH[k] for k in w) / 100
    return r, d, 10000 * (1 + r / 100) ** 10, math.log(1 / (1 - d / 100)) / math.log(1 + r / 100)

def build_frontier(exp):
    """Distinct optimal mixes from the smallest feasible budget upward, as the page builds them."""
    out, last = [], None
    for B in range(1, 101):
        w = optimize(B, exp)
        if not w: continue
        if w == last: break
        out.append((B, w, stats(w, exp))); last = w
    return out

def recommended(front):
    """Most growth whose worst crash is recovered within five years."""
    return max((x for x in front if x[2][3] <= 5.0), key=lambda x: x[2][0])

front = build_frontier(EXP)
check(all(sum(w.values()) == 100 and all(FLOOR <= w[k] <= CAP for k in STK) and w["VTIP"] >= 0 and st[1] <= B + 1e-9
          for B, w, st in front), f"all {len(front)} frontier mixes sum to 100, respect 5–30% bounds and stay within budget")
check(all(front[i][2][0] < front[i + 1][2][0] for i in range(len(front) - 1)), "expected return rises with every budget step")

def brute(B):
    """Every whole-point mix: best net return, ties to the smaller crash."""
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
REC = recommended(front); REC_B = REC[0]
pt = lambda B: [x for x in front if x[0] <= B][-1]
for B in sorted({MIN_B, REC_B, REC_B + 5, REC_B + 10, REC_B + 15, MAX_B}):
    check(pt(B)[1] == brute(B), f"budget −{B}%: solver mix {pt(B)[1]} equals brute force over all mixes")
print(f"         (frontier −{MIN_B}% .. −{MAX_B}%, recommended −{REC_B}%: {REC[1]})")
nxt = [x for x in front if x[0] > REC_B][0]
check(nxt[2][3] > 5.0, f"next budget up (−{nxt[0]}%) would take {nxt[2][3]:.2f} yrs to recover, over 5")

S = lambda B: 100 - pt(B)[1]["VTIP"]
r0, d0, g0, rc0 = REC[2]; mx = pt(MAX_B)
xlv_share = round(100 * REC[1]["XLV"] / S(REC_B))
# sensitivity 1: Schwab's lower US large-cap forecast, same crash budget
alt = dict(EXP); alt.update({"RSP": 5.9, "XLV": 5.9, "ITA": 5.9})
wa = optimize(REC_B, alt); alt_s = 100 - wa["VTIP"]
check(max(STK, key=lambda k: wa[k]) == "VEA", f"Schwab case tilts to VEA ({wa})")
# sensitivity 2: VTIP at 4.9% (about the two-year Treasury yield); the whole recovery rule is re-run
exp49 = dict(EXP); exp49["VTIP"] = 4.9
rec49 = recommended(build_frontier(exp49)); s49 = 100 - rec49[1]["VTIP"]
check(mx[2][3] > 10, f"all-stock mix takes {mx[2][3]:.1f} yrs to recover — longer than the 10-yr horizon, as stated")

claims = [
    (f"<h1>{S(REC_B)}% stocks, {100-S(REC_B)}% bonds</h1>", "Allocation headline"),
    (f"The default, a {REC_B}% worst case", "Allocation standfirst"),
    (f"<b>All stocks</b> ends about ${mx[2][2]-g0:,.0f} ahead over ten years", "max vs recommended gap"),
    (f"its {mx[2][1]:.0f}% worst case would take about {mx[2][3]:.1f} years to recover", "max crash and recovery"),
    (f"({xlv_share}% of the stock side)", "XLV share of stocks"),
    (f"the same {REC_B}% budget would hold only {alt_s}% in stocks, tilted to VEA", "Schwab sensitivity"),
    (f"Re-running the recovery rule with VTIP at 4.9%, about the two-year Treasury yield, would allow {s49}% in stocks", "VTIP sensitivity"),
    ("J.P. Morgan's forecasts date from October 2025 and Schwab's from January 2026, before yields rose to 5.2%.", "assumptions: forecast dates"),
    (f"thin against a {mx[2][1]:.0f}% worst case", "10-yr stance"),
    (f"RSP {CRASH['RSP']:.1f}%, VEA {CRASH['VEA']:.1f}%, ITA {CRASH['ITA']:.1f}%, XLV {CRASH['XLV']:.1f}%", "assumptions: crash depths"),
    (f"its worst, {CRASH['VTIP']:.1f}% in March 2020", "assumptions: VTIP crash"),
    (f"US large cap {EXP['RSP']}% a year (RSP, XLV, ITA), developed ex-US {EXP['VEA']}% (VEA, a proxy: the forecast covers EAFE, which leaves out Canada and South Korea, 20% of VEA)", "assumptions: forecasts"),
    (f"VTIP {EXP['VTIP']}% is an assumption", "assumptions: VTIP forecast"),
    (f"Every fund at least {FLOOR}%, no stock fund above {CAP}%", "assumptions: bounds"),
    (f"Each two of the six signals on the Markets tab raise the budget {STEP} points", "signal step"),
]
for txt, why in claims:
    check(txt in s, f'{why}: "{txt[:70]}"')

# ----------------------------------------------------------------- markets
print("markets arithmetic")
# earnings yield: FactSet quotes forward P/E 19.2 (rounded, so 19.15–19.25) on the 24 Sep close;
# StreetStats quotes 19.32 from forward EPS $398.74. Both are re-priced to the 28 Sep close.
ss_eps = 398.74
check(abs(SP24 / ss_eps - 19.32) < 0.005, f"StreetStats P/E {SP24/ss_eps:.3f} = reported 19.32")
fs_hi, fs_lo = (SP29 / (SP24 / pe) for pe in (19.25, 19.15))      # FactSet P/E range at the 29 Sep close
pe_ss = SP29 / ss_eps
check(f"{fs_lo:.2f}" == "19.07" and f"{fs_hi:.2f}" == "19.17" and f"{pe_ss:.2f}" == "19.24"
      and "19.07–19.17 (FactSet, rounded) to 19.24 (StreetStats), re-priced to the 29 Sep close" in s,
      f"P/E at the 29 Sep close: FactSet {fs_lo:.3f}–{fs_hi:.3f}, StreetStats {pe_ss:.3f}")
ey_lo, ey_hi = 100 / pe_ss, 100 / fs_lo
check(f"{ey_lo:.2f}–{ey_hi:.2f}%" == "5.20–5.24%" and '<div class="v">5.20–5.24%</div>' in s, f"earnings yield {ey_lo:.3f}–{ey_hi:.3f}% -> 5.20–5.24%")
p_lo, p_hi = ey_lo - TEN29, ey_hi - TEN29
check(f"{p_lo:+.2f} to {p_hi:+.2f}" == "-0.05 to -0.01" and '<div class="v">−0.05 to −0.01 pts</div>' in s, f"premium {p_lo:+.3f} to {p_hi:+.3f} pts -> −0.05 to −0.01")
check(max(abs(p_lo), abs(p_hi)) < 0.1 and s.count("≈0 pt") >= 2 and "about zero" in s, "the whole range sits within 0.1 point of zero, so the page says ≈0")
check(round(6.7 - 5.3, 1) == 1.4 and round(7.8 - 5.3, 1) == 2.5 and "by 1.4–2.5 points a year" in s, "J.P. Morgan stock-over-bond edge 1.4 (US) to 2.5 (EM)")
fc = re.findall(r'\{n:"[^"]+", v:([\d.]+)', block("FORECASTS"))
check([float(x) for x in fc] == [7.8, 7.4, 6.7, 5.3] and "lo:3.9, hi:5.9" in js, "forecast bars 7.8 / 7.4 / 6.7 / 5.3 and Vanguard 3.9–5.9")
check(abs(8 / 503 * 100 - 1.6) < 0.05 and '["~1.6%","Mag 7 weight"]' in s and "about 1.6% here" in s,
      f"RSP Mag 7 weight: 7 companies but 8 lines (Alphabet A and C), 8/503 = {8/503*100:.2f}%")
check(round(11.02 + 8.64) == 20 and "South Korea is 8.6% of the fund and Samsung and SK Hynix 4.6%" in s and abs(2.60 + 2.00 - 4.6) < 1e-9,
      "VEA: Canada 11.02% + South Korea 8.64% = 20%; Samsung 2.60% + SK Hynix 2.00% = 4.6%")
check(round(15.31) == 15 and "Eli Lilly alone is 15% of the fund" in s, "XLV: Eli Lilly 15.31% of the fund")
check(f"{(SP29 / DAYS['2026-09-28'][0] - 1) * 100:.2f}" == "-0.17", "S&P 500 29 Sep: 7,670.84 = −0.17% on the day (AP: −0.2%)")
check(round((SP29 / DAYS["2026-09-21"][0] - 1) * 100, 1) == -1.2 and "(7,671) is 1.2% below its 21 Sep close" in s, "S&P is 1.2% below its 21 Sep close")
check(round((1 - 17.97 / 19.2) * 100) == 6 and "about 18× forward earnings against 19.2× for the S&amp;P" in s and '["18.0×","EAFE fwd P/E"]' in s,
      "EAFE forward P/E 17.97 (18.0×) vs S&P 19.2: a 6% discount, stated on the same forward basis in the tile and the prose")
check(abs(572.68 / 655.95 - 1 + 0.127) < 0.001 and "SOXX is 13% below its 52-week high" in s, "SOXX 572.68 vs 52-week high 655.95: 12.7% below")
check(abs(52.62 / 67.37 - 1 + 0.219) < 0.001 and "MCHI sits 22% below its 52-week high" in s, "MCHI 52.62 vs 52-week high 67.37: 21.9% below")
check(round((48157.29 / 45511.49 - 1) * 100, 1) == 5.8 and "5.8% rise in six sessions" in s, "TAIEX 45,511.49 (15 Sep) -> 48,157.29 (23 Sep) = +5.8%")
check(round(20.51 + 16.13 + 8.40) == 45 and round(20.42 + 16.38 + 7.72) == 45 and "about 45% of the fund" in s, "ITA: GE Aerospace + RTX + Boeing = 45% of the fund on both holdings snapshots")
check(round(52617 / 17131, 1) == 3.1 and "about three times what foreigners sold" in s, "India: domestic ₹52,617cr vs foreign ₹17,131cr = 3.1×")
check(round((6889.74 / (6889.74 + 191.18) - 1) * 100, 1) == -2.7 and "KOSPI fell 2.7% to 6,890" in s, "KOSPI 6,889.74, −191.18 pts = −2.7%")
check(302 - 241 == 61 and "only 61bp above the 2007 record low" in s and 'data-v="302" data-ref="241"' in s, "high-yield spread 302bp is 61bp above the 241bp record low")
check(round((102.59 / 105.28 - 1) * 100, 1) == -2.6 and round((102.59 / 99.25 - 1) * 100) == 3 and "down 2.6% on the day but 3% above its $99.25 close on 22 Sep" in s,
      "Brent front month: 105.28 -> 102.59 = −2.6% (29 Sep); 3% above the 99.25 close of 22 Sep")
check(round(88.6 - 6.7, 1) == 81.9 and "Down 6.7 points to its lowest since 2014" in s and round(74.6 - 49.4, 1) == 25.2 and "from 75% (30 Sep a.m.)" in s,
      "consumer confidence 88.6 - 6.7 = 81.9; October hike odds 74.6% -> 49.4%")
check(round(46.94) == 47 and "nearly half of the index (47% in May)" in s, "Samsung 26.04% + SK Hynix 20.90% = 46.94% of KOSPI")

print("signals")
st = re.findall(r'class="sig" data-status="(\w+)"', s)
met, part = st.count("met"), st.count("part")
check(len(st) == 6, f"six signals ({len(st)})")
check(f'<div class="kpi-v">{met} of 6</div>' in s and f"◐ {part} partial" in s, f"KPI: {met} of 6 met, {part} partial")

print("charts and gauges")
v28, v25, v29 = DAYS["2026-09-28"][3], DAYS["2026-09-25"][3], DAYS["2026-09-29"][3]
check(round((v28 / v25 - 1) * 100, 1) == 8.1 and "■ +8% Monday, flat Tuesday" in s and abs(v29 / v28 - 1) < 0.005, f"VIX {v25} -> {v28} = {(v28/v25-1)*100:+.2f}% Monday, then {v29}")
check(f'<div class="kpi-v">{v29:.1f}</div>' in s and f'<div class="sig-now">{v29:.1f}</div>' in s and f"VIX {v29:.1f}" in s, f"VIX {v29:.1f} consistent in KPI, signal and summary")
u21, u29 = ten("2026-09-21"), ten("2026-09-29")
check(round((u29 - u21) * 100) == 30 and "up 30bp in six sessions" in s, f"10-year {u21} (21 Sep) -> {u29} (29 Sep) = 30bp")
check(f'<div class="kpi-v">{u29:.2f}%</div>' in s and f'<div class="sig-now">{u29:.2f}%</div>' in s, f"10-year {u29:.2f}% consistent")
check(u29 == max(ten(d) for d in CHART_DATES) and ten("2026-09-24") == 5.20, "10-year closed 29 Sep at 5.25%, the highest close in the window (5.20% on 24 Sep)")
# stocks against yields: correlation of daily moves, last eight sessions
sp = [DAYS[d][0] for d in CHART_DATES]; tn = [ten(d) for d in CHART_DATES]
ret = [(b / a - 1) * 100 for a, b in zip(sp, sp[1:])]; dy = [(b - a) * 100 for a, b in zip(tn, tn[1:])]
def corr(x, y):
    n = len(x); mx, my = sum(x) / n, sum(y) / n
    return sum((i - mx) * (j - my) for i, j in zip(x, y)) / math.sqrt(sum((i - mx) ** 2 for i in x) * sum((j - my) ** 2 for j in y))
opp = sum(1 for r, d in zip(ret, dy) if r * d < 0)      # strict signs; 22 Sep (−0.06 pts) counts
check(len(ret) == 8 and round(corr(ret, dy), 2) == -0.78 and opp == 7 and "In seven of the last eight sessions" in s and "correlation of daily moves is −0.78" in s,
      f"S&P return vs 10-year change: correlation {corr(ret, dy):.3f} over {len(ret)} sessions, opposite moves on {opp}")
# MOVE (bond volatility) figures quoted on the page: Saxo Options Briefs
check(abs(80.73 * (1 - .0559) - 76.22) < 0.01 and abs(95.45 * 1.0956 - 104.58) < 0.02,
      "MOVE 80.73 (16 Sep) -> 76.22 (17 Sep, −5.59%); 95.45 (23 Sep, +21.5%) -> 104.58 (24 Sep, +9.56%)")
check(abs(101.82 / 1.0606 - 96.0) < 0.01 and "was still 101.8 on 28 Sep" in s, "MOVE 101.82 on 28 Sep (+6.06%) implies 96.0 on 25 Sep; the page quotes 101.8")
check("rose 21.5% on 23 Sep and 9.6% on 24 Sep to 104.6" in s and "76.2 on 17 Sep, 95.5 on 23 Sep (+21.5%), 104.6 on 24 Sep (+9.6%), 101.8 on 28 Sep (+6.1%)" in s, "MOVE figures as stated on the page")
for m in re.finditer(r'class="scale" data-min="([\d.]+)" data-max="([\d.]+)" data-v="([\d.]+)"(?: data-ref="([\d.]+)")?', s):
    lo, hi, val, ref = float(m.group(1)), float(m.group(2)), float(m.group(3)), m.group(4)
    check(lo <= val <= hi and (ref is None or lo <= float(ref) <= hi), f"gauge {val} (ref {ref}) inside {lo}–{hi}")
check("Bears 48.1% vs a 31.0% average" in s and 'data-ref="37.5"' in s, "AAII long-run averages: bulls 37.5%, bears 31.0%")
check(abs(32.7 + 19.2 + 48.1 - 100) < 1e-9 and round(32.7 - 3.9, 1) == 28.8, "AAII 32.7 bull + 19.2 neutral + 48.1 bear = 100; prior week bulls 28.8")

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
want_sum = {"Japan": 15, "Europe": 14, "India": 13, "Emerging markets": 12, "South Korea": 11, "Taiwan": 11, "United States": 10, "China": 10}
check({r["n"]: sum(r["c"].values()) for r in regions} == want_sum, f"region score sums {want_sum}")
# consistency: MSCI EM is 81% Taiwan, Korea, China and India (iShares EEM fact sheet, 30 Jun 2026);
# its score must stay within one point of their weighted average at every horizon
W = {k: v for k, v in DATA["em_weights"].items() if not k.startswith("_")}
R = {r["n"]: r["c"] for r in regions}
for h in ("3m", "6m", "12m", "10y"):
    avg = sum(W[k] * R[k][h] for k in W) / sum(W.values())
    check(abs(R["Emerging markets"][h] - avg) <= 1, f"EM {h} score {R['Emerging markets'][h]} is within 1 of its four biggest markets' weighted average {avg:.2f}")
check(round(27.28 + 23.67) == 51 and "Taiwan and Korea are half the index" in s and "half the index is Taiwan and Korea" in s, "Taiwan 27.28% + Korea 23.67% = 51% of MSCI EM, as the notes say")

# ------------------------------------------------------------ consistency
print("consistency and stale text")
for phrase in ["33.9%", "5.25%", "~49%"]:
    check(s.count(phrase) >= 2, f'"{phrase}" repeated consistently ({s.count(phrase)}×)')
for stale in ["within 0.3%", "−0.51%", "13.30", "long-run 60", "third daily rise", "31.5% average",
              "5.16–", "0.05–0.13", "level with the S&amp;P", "0.08 points", "1 / 19.26",
              "70–78%", "5.15–5.24%", "0.04–0.13", "≈0.1 pt", "+34%", "19.9×", "trailing earnings", "up two days running",
              "1-mo high", "Tightest tenth", "82% and 113%", "Fear &amp; Greed 35", "hit directly by AI selling", "phased Hormuz deal",
              "5.11%", "2.21%", "1.29%", "still tight against a 2008 peak", "Data to 24 Sep", "Data to 28 Sep", "70–73%", "Fear &amp; Greed 34", "~1.4%", "2.4 years of duration",
              "Demand written into treaties", "adds over €800bn", "VWO", "450bp median", "1 ÷ forward P/E of 19.10"]:
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
