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

funds = []
for tk in re.findall(r'tk:"(\w+)"', js):
    blk = js[js.find('tk:"%s"' % tk):]
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

print()
print("ALL CHECKS PASSED" if not fails else f"{len(fails)} CHECK(S) FAILED")
sys.exit(1 if fails else 0)
