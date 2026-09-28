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
YLD   = {"VTIP": 2.24, "RSP": 1.49, "VEA": 2.36, "XLV": 1.51, "ITA": 0.34}
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


# ------------------------------------------------------------- market inputs
# Keyed once, from the cited sources: S&P 500 close, AP-reported point change and 10-year
# close (AP "How major US stock indexes fared"); VIX cash close and reported percentage
# change (Saxo Options Briefs, Cboe-based reports). Everything below is checked against
# this table, and the page's own chart data is checked against it too.
# date: (S&P close, AP point change, 10-yr %, VIX close, reported VIX % change)
DAYS = {
    "2026-09-16": (7551.81, None,    None, 17.71, +2.97),
    "2026-09-17": (7637.76, +85.95,  4.93, 15.44, None),
    "2026-09-18": (7650.50, +12.74,  5.00, 14.81, -4.08),
    "2026-09-21": (7764.70, +114.20, 4.95, 14.87, +0.41),
    "2026-09-22": (7764.64, -0.06,   4.96, 14.21, None),
    "2026-09-23": (7706.03, -58.61,  5.11, 15.18, +6.83),
    "2026-09-24": (7704.13, -1.90,   5.20, 15.67, None),
    "2026-09-25": (7743.41, +39.28,  5.17, 14.87, -5.10),
    "2026-09-28": (7683.69, -59.72,  5.23, 16.11, +8.33),
}
CHART_DATES = [d for d in DAYS if d >= "2026-09-17"]
SP24, SP28, TEN28 = DAYS["2026-09-24"][0], DAYS["2026-09-28"][0], DAYS["2026-09-28"][2]

print("market data table")
dates = list(DAYS)
for i in range(1, len(dates)):
    (sp0, _, _, v0, _), (sp1, chg, _, v1, vpct) = DAYS[dates[i - 1]], DAYS[dates[i]]
    if chg is not None:
        check(abs(sp0 + chg - sp1) < 0.005, f"{dates[i]}: S&P {sp0:,.2f} {chg:+.2f} = {sp1:,.2f}, as AP reports")
    if vpct is not None:
        check(abs((v1 / v0 - 1) * 100 - vpct) < 0.06, f"{dates[i]}: VIX {v0} -> {v1} = {(v1/v0-1)*100:+.2f}% (reported {vpct:+.2f}%)")
check(abs(16.17 / 14.87 - 1 - 0.0875) < 0.0005, "the other 28 Sep VIX print, 16.17, is +8.75% from the same 14.87 base: sources differ by 0.06, the base agrees")
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
    check(pts == [(d, DAYS[d][col]) for d in CHART_DATES], f"{key}: the page's {len(pts)} plotted closes equal the keyed table, 17–28 Sep")
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
    (f"US large cap {EXP['RSP']}% a year (RSP, XLV, ITA), developed ex-US {EXP['VEA']}% (VEA)", "assumptions: forecasts"),
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
fs_hi, fs_lo = (SP28 / (SP24 / pe) for pe in (19.25, 19.15))      # FactSet P/E range at the 28 Sep close
pe_ss = SP28 / ss_eps
check(f"{fs_lo:.2f}" == "19.10" and f"{fs_hi:.2f}" == "19.20" and f"{pe_ss:.2f}" == "19.27"
      and "19.10–19.20 (FactSet, rounded) to 19.27 (StreetStats), re-priced to the 28 Sep close" in s,
      f"P/E at the 28 Sep close: FactSet {fs_lo:.3f}–{fs_hi:.3f}, StreetStats {pe_ss:.3f}")
ey_lo, ey_hi = 100 / pe_ss, 100 / fs_lo
check(f"{ey_lo:.2f}–{ey_hi:.2f}%" == "5.19–5.24%" and '<div class="v">5.19–5.24%</div>' in s, f"earnings yield {ey_lo:.3f}–{ey_hi:.3f}% -> 5.19–5.24%")
p_lo, p_hi = ey_lo - TEN28, ey_hi - TEN28
check(f"{p_lo:+.2f} to {p_hi:+.2f}" == "-0.04 to +0.01" and '<div class="v">−0.04 to +0.01 pts</div>' in s, f"premium {p_lo:+.3f} to {p_hi:+.3f} pts -> −0.04 to +0.01")
check(p_lo < 0 < p_hi and s.count("≈0 pt") >= 2 and "about zero" in s, "the range straddles zero, so the page says ≈0 rather than claiming a sign")
check(round(6.7 - 5.3, 1) == 1.4 and round(7.8 - 5.3, 1) == 2.5 and "by 1.4–2.5 points a year" in s, "J.P. Morgan stock-over-bond edge 1.4 (US) to 2.5 (EM)")
fc = re.findall(r'\{n:"[^"]+", v:([\d.]+)', block("FORECASTS"))
check([float(x) for x in fc] == [7.8, 7.4, 6.7, 5.3] and "lo:3.9, hi:5.9" in js, "forecast bars 7.8 / 7.4 / 6.7 / 5.3 and Vanguard 3.9–5.9")
check(abs(7 / 503 * 100 - 1.4) < 0.05 and '["~1.4%","Mag 7 weight"]' in s, f"RSP Mag 7 weight 7/503 = {7/503*100:.2f}%")
check(f"{(SP28 / DAYS['2026-09-25'][0] - 1) * 100:.2f}" == "-0.77" and '<div class="kpi-v">7,684</div>' in s and "−0.8% Monday" in s,
      "S&P 500 28 Sep: 7,683.69 = −0.77% on the day, shown as 7,684 / −0.8%")
check(round((SP28 / DAYS["2026-09-21"][0] - 1) * 100, 1) == -1.0, "S&P is 1.0% below its 21 Sep close")
check(round((1 - 17.97 / 19.2) * 100) == 6 and "about 18× forward earnings against 19.2× for the S&amp;P" in s and '["18.0×","EAFE fwd P/E"]' in s,
      "EAFE forward P/E 17.97 (18.0×) vs S&P 19.2: a 6% discount, stated on the same forward basis in the tile and the prose")
check(abs(572.68 / 655.95 - 1 + 0.127) < 0.001 and "SOXX is 13% below its 52-week high" in s, "SOXX 572.68 vs 52-week high 655.95: 12.7% below")
check(abs(52.62 / 67.37 - 1 + 0.219) < 0.001 and "MCHI sits 22% below its 52-week high" in s, "MCHI 52.62 vs 52-week high 67.37: 21.9% below")
check(round((48157.29 / 45511.49 - 1) * 100, 1) == 5.8 and "5.8% rise in six sessions" in s, "TAIEX 45,511.49 (15 Sep) -> 48,157.29 (23 Sep) = +5.8%")
check(round(20.51 + 16.13 + 8.40) == 45 and round(20.42 + 16.38 + 7.72) == 45 and "about 45% of the fund" in s, "ITA: GE Aerospace + RTX + Boeing = 45% of the fund on both holdings snapshots")
check(round(52617 / 17131, 1) == 3.1 and "about three times what foreigners sold" in s, "India: domestic ₹52,617cr vs foreign ₹17,131cr = 3.1×")
check(round((6889.74 / (6889.74 + 191.18) - 1) * 100, 1) == -2.7 and "KOSPI fell 2.7% to 6,890" in s, "KOSPI 6,889.74, −191.18 pts = −2.7%")
check(round(46.94) == 47 and "nearly half of the index (47% in May)" in s, "Samsung 26.04% + SK Hynix 20.90% = 46.94% of KOSPI")

print("signals")
st = re.findall(r'class="sig" data-status="(\w+)"', s)
met, part = st.count("met"), st.count("part")
check(len(st) == 6, f"six signals ({len(st)})")
check(f'<div class="kpi-v">{met} of 6</div>' in s and f"◐ {part} partial" in s, f"KPI: {met} of 6 met, {part} partial")

print("charts and gauges")
v28, v25 = DAYS["2026-09-28"][3], DAYS["2026-09-25"][3]
check(round((v28 / v25 - 1) * 100, 1) == 8.3 and "▲ +8% on Monday" in s and "rose 8% on Monday" in s, f"VIX {v25} -> {v28} = {(v28/v25-1)*100:+.2f}%")
check(f'<div class="kpi-v">{v28:.1f}</div>' in s and f'<div class="sig-now">{v28:.1f}</div>' in s and f"VIX {v28:.1f}" in s, f"VIX {v28:.1f} consistent in KPI, signal and summary")
u21, u28 = ten("2026-09-21"), ten("2026-09-28")
check(round((u28 - u21) * 100) == 28 and "up 28bp in five sessions" in s, f"10-year {u21} (21 Sep) -> {u28} (28 Sep) = 28bp")
check(f'<div class="kpi-v">{u28:.2f}%</div>' in s and f'<div class="sig-now">{u28:.2f}%</div>' in s, f"10-year {u28:.2f}% consistent")
check(u28 == max(ten(d) for d in CHART_DATES) and ten("2026-09-24") == 5.20, "10-year hit 5.20% on 24 Sep and closed 28 Sep at 5.23%, the highest close in the window")
# MOVE (bond volatility) figures quoted on the page: Saxo Options Briefs
check(abs(80.73 * (1 - .0559) - 76.22) < 0.01 and abs(95.45 * 1.0956 - 104.58) < 0.02,
      "MOVE 80.73 (16 Sep) -> 76.22 (17 Sep, −5.59%); 95.45 (23 Sep, +21.5%) -> 104.58 (24 Sep, +9.56%)")
check("rose 21.5% on 23 Sep and 9.6% on 24 Sep to 104.6" in s and "76.2 on 17 Sep, 95.5 on 23 Sep (+21.5%), 104.6 on 24 Sep (+9.6%)" in s, "MOVE figures as stated on the page")
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
want_sum = {"Japan": 15, "Europe": 14, "Emerging markets": 14, "India": 13, "South Korea": 11, "Taiwan": 11, "United States": 10, "China": 10}
check({r["n"]: sum(r["c"].values()) for r in regions} == want_sum, f"region score sums unchanged {want_sum}")

# ------------------------------------------------------------ consistency
print("consistency and stale text")
for phrase in ["70–73%", "33.9%", "5.23%"]:
    check(s.count(phrase) >= 2, f'"{phrase}" repeated consistently ({s.count(phrase)}×)')
for stale in ["within 0.3%", "−0.51%", "13.30", "long-run 60", "third daily rise", "31.5% average",
              "5.16–", "0.05–0.13", "level with the S&amp;P", "0.08 points", "1 / 19.26",
              "70–78%", "5.15–5.24%", "0.04–0.13", "≈0.1 pt", "+34%", "19.9×", "trailing earnings", "up two days running",
              "1-mo high", "Tightest tenth", "82% and 113%", "Fear &amp; Greed 35", "hit directly by AI selling", "phased Hormuz deal",
              "5.11%", "2.21%", "1.29%", "Data to 24 Sep"]:
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
