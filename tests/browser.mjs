// Browser regression suite for index.html.
// Run: node tests/browser.mjs   (needs Playwright; set PLAYWRIGHT_MODULE to its index.mjs if not resolvable)
import fs from 'fs';
import os from 'os';
import path from 'path';
import { fileURLToPath } from 'url';
const { chromium } = await import(process.env.PLAYWRIGHT_MODULE || 'playwright');
const PAGE = path.resolve(path.dirname(fileURLToPath(import.meta.url)), '..', 'index.html');
// the page is published as a fragment; wrap it the way the host does
const PREV = path.join(os.tmpdir(), `preview-test-${process.pid}.html`);
fs.writeFileSync(PREV, `<!doctype html><html><head><meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1,viewport-fit=cover">
<style>:root{color-scheme:light}body{margin:0;font:14px system-ui;background:#fafaf9}[hidden]{display:none!important}</style>
</head><body>${fs.readFileSync(PAGE, 'utf8')}</body></html>`);

const b = await chromium.launch();
let fail = 0;
const ok = (c, m) => { console.log((c ? '  PASS  ' : '  FAIL  ') + m); if (!c) fail++; };
const TABS = ['tab-top', 'tab-alloc', 'tab-markets'];

// ------------------------------------------------ independent allocation model
const ER = {VTIP:.03, RSP:.20, VEA:.03, XLV:.08, ITA:.37}, EX = {VTIP:4.0, RSP:6.7, VEA:7.4, XLV:6.7, ITA:6.7};
const CR = {VTIP:6.27, RSP:59.92, VEA:60.68, XLV:39.17, ITA:59.72};
const N = k => Math.round((EX[k] - ER[k]) * 100), C = k => Math.round(CR[k] * 100);
const brute = B => {   // every whole-point mix: best return, ties to the smaller crash
  let best = null;
  for (let a = 5; a <= 30; a++) for (let v = 5; v <= 30; v++) for (let x = 5; x <= 30; x++) for (let i = 5; i <= 30; i++) {
    const t = 100 - a - v - x - i; if (t < 0) continue;
    const c = a*C('RSP') + v*C('VEA') + x*C('XLV') + i*C('ITA') + t*C('VTIP'); if (c > B * 10000) continue;
    const r = a*N('RSP') + v*N('VEA') + x*N('XLV') + i*N('ITA') + t*N('VTIP');
    if (!best || r > best.r || (r === best.r && c < best.c)) best = {r, c, w:{VTIP:t, RSP:a, VEA:v, XLV:x, ITA:i}};
  }
  return best;
};

// ------------------------------------------------------------ phone widths
for (const W of [320, 360, 412, 680]) {
  const p = await b.newPage({ viewport:{width:W, height:880} });
  const errs = []; p.on('pageerror', e => errs.push(e.message));
  await p.goto('file://' + PREV, {waitUntil:'domcontentloaded'});
  await p.waitForTimeout(400);
  for (const t of TABS) {
    await p.click('#' + t); await p.waitForTimeout(250);
    const o = await p.evaluate(() => [document.documentElement.scrollWidth, document.documentElement.clientWidth]);
    ok(o[0] <= o[1], `${W}px ${t}: no horizontal overflow (${o[0]}<=${o[1]})`);
  }
  ok(errs.length === 0, `${W}px: no JS errors ${errs.join('|')}`);
  await p.evaluate(() => { try { localStorage.clear(); } catch (e) {} });
  await p.close();
}

const p = await b.newPage({ viewport:{width:412, height:915} });
const errs = []; p.on('pageerror', e => errs.push(e.message));
await p.goto('file://' + PREV, {waitUntil:'domcontentloaded'});
await p.waitForTimeout(500);

const contrast = sel => p.evaluate(sel => {
  const rgb = c => c.match(/\d+(\.\d+)?/g).slice(0, 3).map(Number);
  const L = v => { const a = v.map(x => { x /= 255; return x <= 0.03928 ? x / 12.92 : Math.pow((x + 0.055) / 1.055, 2.4); }); return 0.2126*a[0] + 0.7152*a[1] + 0.0722*a[2]; };
  const ratio = (f, g) => { const x = L(f), y = L(g); return (Math.max(x, y) + 0.05) / (Math.min(x, y) + 0.05); };
  const bg = el => { while (el) { const c = getComputedStyle(el).backgroundColor; if (c && !/rgba\(0, 0, 0, 0\)|transparent/.test(c)) return c; el = el.parentElement; } return 'rgb(255,255,255)'; };
  return Array.from(document.querySelectorAll(sel)).filter(el => el.offsetParent)
    .map(el => ({t:el.textContent.trim().slice(0, 24), r:+ratio(rgb(getComputedStyle(el).color), rgb(bg(el))).toFixed(2)}));
}, sel);
const lowest = list => list.reduce((a, c) => a.r < c.r ? a : c, {r:99, t:''});

// ------------------------------------------------------------------ Top 5
console.log('\n--- Top 5: horizon switching ---');
const snap = () => p.evaluate(() => ({
  band: document.querySelector('.band-v')?.textContent,
  onHdr: document.querySelector('#matrix thead th.on')?.textContent,
  onCells: document.querySelectorAll('#matrix td.on').length,
  checked: document.querySelector('#panel-top .seg button[aria-checked="true"]')?.textContent,
  status: document.getElementById('h-status')?.textContent,
  cards: Array.from(document.querySelectorAll('.card .tick')).map(e => e.textContent)
}));
const seen = new Set();
for (const h of ['3m', '6m', '12m', '10y']) {
  await p.click(`#h-${h}`); await p.waitForTimeout(150);
  const s = await snap(); seen.add(s.band);
  ok(s.cards.join() === 'VTIP,RSP,VEA,XLV,ITA', `${h}: five cards in rank order`);
  ok(s.onCells === 5 && !!s.onHdr, `${h}: matrix column "${s.onHdr}" highlighted (${s.onCells} cells)`);
  ok(/horizon/.test(s.status), `${h}: live region says "${s.status}"`);
}
ok(seen.size === 4, `each horizon shows a different range (${seen.size}/4)`);

await p.click('#h-3m'); await p.focus('#h-3m');
const stops = await p.evaluate(() => Array.from(document.querySelectorAll('.seg')).map(g => Array.from(g.querySelectorAll('button')).filter(x => x.tabIndex === 0).length));
ok(stops.every(n => n === 1), `one tab stop per horizon group (${stops})`);
await p.keyboard.press('ArrowRight'); ok((await snap()).checked.trim() === '6 mo', 'ArrowRight: 3 mo -> 6 mo');
await p.keyboard.press('End'); ok((await snap()).checked.trim() === '10 yr', 'End: -> 10 yr');
await p.keyboard.press('ArrowRight'); ok((await snap()).checked.trim() === '3 mo', 'ArrowRight wraps to 3 mo');

const chips = await contrast('.role, .kpi-d, .sec-note, .stat-k, .band-n, .risk');
ok(chips.every(c => c.r >= 4.5), `Top 5 small text >= 4.5:1 across ${chips.length} elements (lowest "${lowest(chips).t}" ${lowest(chips).r}:1)`);

console.log('\n--- sticky bars ---');
for (const panel of ['top', 'markets']) {
  await p.click('#tab-' + panel); await p.waitForTimeout(200);
  await p.evaluate(sel => { const hz = document.querySelector(sel); window.scrollTo(0, hz.getBoundingClientRect().top + scrollY + 900); }, `#panel-${panel} .horizon`);
  await p.waitForTimeout(250);
  const g = await p.evaluate(sel => {
    const hz = document.querySelector(sel).getBoundingClientRect(), tb = document.querySelector('.topbar').getBoundingClientRect();
    const under = document.elementFromPoint(innerWidth / 2, hz.bottom + 4);
    return {gap:+(hz.top - tb.bottom).toFixed(2), under:under ? String(under.className) : ''};
  }, `#panel-${panel} .horizon`);
  ok(Math.abs(g.gap) < 1.5 && !g.under.includes('horizon'), `${panel}: horizon bar docks under the top bar (gap ${g.gap}px)`);
  const y0 = await p.evaluate(() => scrollY);
  await p.click(`#panel-${panel} .seg button[data-h="12m"]`); await p.waitForTimeout(200);
  ok(Math.abs(y0 - await p.evaluate(() => scrollY)) < 5, `${panel}: changing horizon keeps the scroll position`);
}

// ------------------------------------------------------------------- tabs
console.log('\n--- tabs ---');
await p.evaluate(() => scrollTo(0, 0));
await p.click('#tab-alloc'); await p.waitForTimeout(200);
const tabState = () => p.evaluate(ids => ids.map(id => {
  const t = document.getElementById(id);
  return [t.getAttribute('aria-selected'), t.tabIndex, document.getElementById(t.getAttribute('aria-controls')).hidden].join('/');
}), TABS);
ok(JSON.stringify(await tabState()) === JSON.stringify(['false/-1/true', 'true/0/false', 'false/-1/true']), 'click shows one panel, one tab stop');
await p.focus('#tab-alloc');
await p.keyboard.press('ArrowRight'); ok(await p.evaluate(() => document.activeElement.id) === 'tab-markets', 'ArrowRight -> Markets');
await p.keyboard.press('ArrowRight'); ok(await p.evaluate(() => document.activeElement.id === 'tab-top' && !document.getElementById('panel-top').hidden), 'ArrowRight wraps to Top 5');
await p.keyboard.press('End'); ok(await p.evaluate(() => document.activeElement.id) === 'tab-markets', 'End -> last tab');
await p.keyboard.press('Home'); ok(await p.evaluate(() => document.activeElement.id) === 'tab-top', 'Home -> first tab');

// horizon is shared: set it on Markets, read it back on Top 5
await p.click('#tab-markets'); await p.click('#m-3m'); await p.waitForTimeout(150);
const sync = await p.evaluate(() => ({
  top: document.getElementById('h-3m').getAttribute('aria-checked'),
  on: Array.from(document.querySelectorAll('.st.on')).map(e => e.dataset.h),
  hdr: document.querySelector('#rmatrix thead th.on')?.textContent
}));
ok(sync.top === 'true' && sync.on.join() === '3m' && sync.hdr === '3 mo', `horizon shared across tabs (${JSON.stringify(sync)})`);

// jump links open the named tab at its top and move focus to that tab
await p.click('#tab-top'); await p.waitForTimeout(150);
for (const [from, to] of [['top', 'tab-markets'], ['alloc', 'tab-markets'], ['markets', 'tab-alloc']]) {
  await p.click('#tab-' + from); await p.waitForTimeout(150);
  await p.evaluate(sel => document.querySelector(sel).scrollIntoView({block:'center'}), `#panel-${from} [data-goto]`);
  await p.click(`#panel-${from} [data-goto]`); await p.waitForTimeout(250);
  const j = await p.evaluate(to => ({shown:!document.getElementById(document.getElementById(to).getAttribute('aria-controls')).hidden, y:scrollY, focus:document.activeElement.id}), to);
  ok(j.shown && j.y === 0 && j.focus === to, `${from} link opens ${to} at the top with focus (${JSON.stringify(j)})`);
}

// ------------------------------------------------------------- allocation
console.log('\n--- allocation: max 10-yr growth within a worst-crash budget ---');
await p.click('#tab-alloc'); await p.waitForTimeout(250);
const readAlloc = () => p.evaluate(() => ({
  readout: document.getElementById('dd-readout').textContent,
  w: Object.fromEntries(Array.from(document.querySelectorAll('#total-legend div')).map(d => [d.querySelector('b').textContent, parseInt(d.querySelector('em').textContent)])),
  figs: Array.from(document.querySelectorAll('#total-figs .fig-v')).map(x => x.textContent),
  costs: document.getElementById('total-costs').textContent,
  pressed: Array.from(document.querySelectorAll('[data-preset][aria-pressed="true"]')).map(x => x.dataset.preset).join(),
  stk: (() => { const t = document.querySelector('#mix-bar .mix-track').getBoundingClientRect(), s = document.querySelector('#mix-bar .mix-seg.stk'); return s ? s.getBoundingClientRect().width / t.width * 100 : 0; })()
}));
let A = await readAlloc();
ok(A.readout === '−21%' && A.pressed === 'rec', `default is the recommended −21% budget (${A.readout}, ${A.pressed})`);
ok(JSON.stringify(A.w) === JSON.stringify(brute(21).w), `recommended weights ${JSON.stringify(A.w)} equal brute force`);
ok(JSON.stringify(A.figs) === JSON.stringify(['$16,157', '4.91%', '−20.9%', '4.9 yrs']), `recommended figures ${A.figs}`);
const fee = Object.keys(A.w).reduce((a, k) => a + A.w[k] * ER[k], 0) / 100;
const YL = {VTIP:2.21, RSP:1.46, VEA:2.36, XLV:1.49, ITA:1.29}, yl = Object.keys(A.w).reduce((a, k) => a + A.w[k] * YL[k], 0) / 100;
ok(A.costs.includes(`Fee ${fee.toFixed(2)}%`) && A.costs.includes(`yield ~${yl.toFixed(1)}%`), `blended fee ${fee.toFixed(4)} and yield ${yl.toFixed(3)} match "${A.costs}"`);
ok(Math.abs(A.stk - 35) < 0.5, `stock segment drawn to scale at 35% (${A.stk.toFixed(2)})`);

const ladder = await p.evaluate(() => Array.from(document.querySelectorAll('#stage-table tbody tr')).map(tr => ({c:Array.from(tr.cells).map(td => td.textContent), on:tr.classList.contains('on')})));
ok(ladder.map(r => r.c[1]).join() === '35,48,57,66' && ladder.every(r => +r.c[1] + +r.c[2] === 100), `signal rows: stocks ${ladder.map(r => r.c[1])}, VTIP the rest`);
ok(ladder.map(r => r.c[0].match(/−\d+%/)[0]).join() === '−21%,−26%,−31%,−36%', 'each row names its budget');
ladder.forEach((r, i) => {
  const want = brute(21 + 5 * i).w;
  ok(r.c.slice(2).map(Number).join() === ['VTIP', 'RSP', 'VEA', 'XLV', 'ITA'].map(k => want[k]).join(), `row −${21 + 5 * i}%: ${r.c.slice(2)} equals brute force`);
});
const metNow = await p.evaluate(() => document.querySelectorAll('.sig[data-status="met"]').length);
ok(ladder.filter(r => r.on).length === 1 && ladder[metNow <= 1 ? 0 : metNow <= 3 ? 1 : metNow <= 5 ? 2 : 3].on && /\(current\)/.test(ladder.find(r => r.on).c[0]), `current row (${metNow} signals met) highlighted with a text marker`);

// every slider position equals the brute-force optimum
const sweep = await p.evaluate(() => {
  const sl = document.getElementById('dd-budget'), out = [];
  for (let v = +sl.min; v <= +sl.max; v++) {
    sl.value = v; sl.dispatchEvent(new Event('input', {bubbles:true}));
    out.push({v, w:Object.fromEntries(Array.from(document.querySelectorAll('#total-legend div')).map(d => [d.querySelector('b').textContent, parseInt(d.querySelector('em').textContent)]))});
  }
  return {min:+sl.min, max:+sl.max, out};
});
ok(sweep.min === 16 && sweep.max === 54, `slider spans −${sweep.min}% to −${sweep.max}%`);
const bad = sweep.out.filter(({v, w}) => JSON.stringify(w) !== JSON.stringify(brute(v).w));
ok(bad.length === 0, `all ${sweep.out.length} slider positions equal the brute-force optimum ${bad.map(x => x.v)}`);

await p.click('[data-preset="max"]'); await p.waitForTimeout(100); A = await readAlloc();
ok(A.readout === '−54%' && JSON.stringify(A.w) === JSON.stringify({VTIP:0, RSP:30, VEA:30, XLV:30, ITA:10}) && A.figs.join() === '$19,271,6.78%,−53.9%,11.8 yrs', `most growth: ${JSON.stringify(A.w)} ${A.figs}`);
await p.click('[data-preset="min"]'); await p.waitForTimeout(100); A = await readAlloc();
ok(A.readout === '−16%' && A.w.VTIP === 80 && A.pressed === 'min', `least drawdown: VTIP ${A.w.VTIP}%`);

await p.evaluate(() => document.getElementById('frontier').scrollIntoView({block:'center'})); await p.waitForTimeout(150);
const fr = await p.evaluate(() => { const svg = document.querySelector('#frontier svg'), r = svg.getBoundingClientRect();
  return {n:svg.querySelectorAll('circle').length, inside:Array.from(svg.querySelectorAll('circle,text')).every(e => { const q = e.getBoundingClientRect(); return q.left >= r.left - 2 && q.right <= r.right + 2 && q.top >= r.top - 2 && q.bottom <= r.bottom + 2; })}; });
ok(fr.n === 4 && fr.inside, `frontier: 3 preset points + selection, all inside the drawing (${fr.n})`);
const key = await p.evaluate(() => document.getElementById('frontier-key').textContent);
ok(key.includes('Least drawdown: −16% · 4.52%/yr') && key.includes('Recommended: −21% · 4.91%/yr') && key.includes('Most growth: −54% · 6.78%/yr'), 'frontier key names the presets with their values');
const fb = await (await p.$('#frontier')).boundingBox();
await p.mouse.click(fb.x + fb.width - 16, fb.y + 40); await p.waitForTimeout(150);
ok((await readAlloc()).readout === '−54%', 'tapping the right end of the frontier selects most growth');
await p.click('[data-preset="rec"]'); await p.waitForTimeout(100);
const ac = await contrast('#panel-alloc .fig-k, #panel-alloc .note-line, #panel-alloc .fchart-s, #panel-alloc .sec-note, #panel-alloc .mix-seg, #panel-alloc .budget-ends span');
ok(ac.every(c => c.r >= 4.5), `Allocation small text >= 4.5:1 across ${ac.length} elements (lowest "${lowest(ac).t}" ${lowest(ac).r}:1)`);

// ---------------------------------------------------------------- markets
console.log('\n--- markets ---');
await p.click('#tab-markets'); await p.waitForTimeout(300);
for (const h of ['3m', '6m', '12m', '10y']) {
  await p.click('#m-' + h); await p.waitForTimeout(120);
  const r = await p.evaluate(h => {
    const col = {'3m':1, '6m':2, '12m':3, '10y':4}[h];
    const t = Array.from(document.querySelectorAll('#rmatrix tbody tr')).map(tr => { const d = tr.cells; return {n:d[0].textContent, c:+d[col].textContent, sum:+d[5].textContent}; });
    t.sort((a, b) => (b.c - a.c) || (b.sum - a.sum) || (a.n < b.n ? -1 : a.n > b.n ? 1 : 0));
    let rank = 0, prev = null; t.forEach((x, i) => { if (x.c !== prev) { rank = i + 1; prev = x.c; } x.lbl = (t.filter(y => y.c === x.c).length > 1 ? 'T' : '') + rank; });
    return {want:t.map(x => x.n + ':' + x.lbl).join(), got:Array.from(document.querySelectorAll('#rlist .reg')).map(el => el.querySelector('.reg-n').textContent + ':' + el.querySelector('.reg-rank').textContent).join(),
            st:Array.from(document.querySelectorAll('.st.on')).map(e => e.dataset.h).join()};
  }, h);
  ok(r.want === r.got && r.st === h, `${h}: ranked list matches the score table under competition ranking; stance row ${r.st}`);
}
const ch = await p.evaluate(() => ['vc-vix', 'vc-ust'].map(id => {
  const box = document.getElementById(id), svg = box.querySelector('svg'), r = svg.getBoundingClientRect();
  const inside = Array.from(svg.querySelectorAll('circle.pt, text')).every(e => { const q = e.getBoundingClientRect(); return q.left >= r.left - 2 && q.right <= r.right + 2 && q.top >= r.top - 2 && q.bottom <= r.bottom + 2; });
  return {n:svg.querySelectorAll('circle.pt').length, inside, label:box.getAttribute('aria-label') || ''};
}));
ok(ch[0].n === 7 && ch[1].n === 6, `VIX 7 and 10-yr 6 reported closes plotted (${ch[0].n}/${ch[1].n})`);
ok(ch.every(c => c.inside) && ch.every(c => c.label.length > 20), 'chart points and labels inside the drawing; charts described in text');
const overlaps = await p.evaluate(() => ['vc-vix', 'vc-ust'].map(id => {
  const t = Array.from(document.querySelectorAll('#' + id + ' svg text')).map(e => e.getBoundingClientRect()); let n = 0;
  for (let i = 0; i < t.length; i++) for (let j = i + 1; j < t.length; j++) { const a = t[i], c = t[j]; if (a.left < c.right - 1 && c.left < a.right - 1 && a.top < c.bottom - 1 && c.top < a.bottom - 1) n++; }
  return n; }));
ok(overlaps.every(n => n === 0), `no overlapping chart labels (${overlaps})`);
await p.evaluate(() => document.getElementById('vc-vix').scrollIntoView({block:'center'})); await p.waitForTimeout(150);
const vb = await (await p.$('#vc-vix')).boundingBox();
await p.mouse.move(vb.x + vb.width - 14, vb.y + 60); await p.waitForTimeout(100);
const tip = await p.evaluate(() => { const t = document.querySelector('#vc-vix .vtip'); return t.hidden ? null : t.textContent; });
ok(tip === '24 Sep · 15.67', `hover snaps to the nearest close ("${tip}")`);
await p.evaluate(() => document.getElementById('vc-ust').scrollIntoView({block:'center'})); await p.waitForTimeout(150);
const ub = await (await p.$('#vc-ust')).boundingBox();
await p.mouse.move(ub.x + 45, ub.y + 70); await p.mouse.down(); await p.mouse.up(); await p.waitForTimeout(100);
const tap = await p.evaluate(() => { const t = document.querySelector('#vc-ust .vtip'); return t.hidden ? null : t.textContent; });
ok(tap === '16 Sep · 5.01%', `a tap shows the value ("${tap}")`);
ok(await p.evaluate(() => document.querySelectorAll('#vtable tbody tr').length) === 8, 'numbers table lists each of the 8 dates once');

const bars = await p.evaluate(() => Array.from(document.querySelectorAll('.fbar')).map(el => {
  const t = el.querySelector('.fbar-track').getBoundingClientRect(), f = el.querySelector('.fbar-fill').getBoundingClientRect();
  return {n:el.querySelector('.n').textContent, lo:(f.left - t.left) / t.width * 9, hi:(f.right - t.left) / t.width * 9};
}));
const want = {'Emerging-market stocks':[0, 7.8], 'Developed ex-US stocks':[0, 7.4], 'US large-cap stocks':[0, 6.7], 'US aggregate bonds':[0, 5.3], 'US stocks, Vanguard':[3.9, 5.9]};
ok(bars.length === 5 && bars.every(x => Math.abs(x.lo - want[x.n][0]) < 0.08 && Math.abs(x.hi - want[x.n][1]) < 0.08), `forecast bars drawn to one 0–9% scale (${bars.map(x => x.hi.toFixed(2)).join(', ')})`);
const gauges = await p.evaluate(() => Array.from(document.querySelectorAll('.scale[data-v]')).map(el => {
  const r = el.getBoundingClientRect(), d = el.querySelector('.dot').getBoundingClientRect();
  const lo = +el.dataset.min, hi = +el.dataset.max;
  return Math.abs(((d.left + d.width / 2) - r.left) / r.width - (+el.dataset.v - lo) / (hi - lo)) < 0.02;
}));
ok(gauges.length === 4 && gauges.every(Boolean), `gauge dots sit at their values (${gauges.length})`);
const met = await p.evaluate(() => ({kpi:Array.from(document.querySelectorAll('#panel-markets .kpi')).find(k => /Signals/.test(k.textContent)).querySelector('.kpi-v').textContent,
  n:document.querySelectorAll('.sig[data-status="met"]').length}));
ok(met.kpi === `${met.n} of 6`, `Signals KPI "${met.kpi}" matches the list`);
const mc = await contrast('#panel-markets .tag, #panel-markets .reg-rank, #panel-markets .st.on .st-h, #panel-markets .scale-lbl, #panel-markets .g-note, #panel-markets .sig-t span, #panel-markets .sig-now, #panel-markets .erp-row small, #panel-markets .kpi-d, #panel-markets .reg-tk');
ok(mc.every(c => c.r >= 4.5), `Markets small text >= 4.5:1 across ${mc.length} elements (lowest "${lowest(mc).t}" ${lowest(mc).r}:1)`);

// remembered tab survives a reload
await p.reload({waitUntil:'domcontentloaded'}); await p.waitForTimeout(400);
ok(await p.evaluate(() => !document.getElementById('panel-markets').hidden), 'selected tab is remembered across reload');

console.log('\nJS errors: ' + (errs.length ? errs.join(' | ') : 'none'));
ok(errs.length === 0, 'no JS errors in the main run');
console.log(fail === 0 ? '\n>>> ALL CHECKS PASSED' : `\n>>> ${fail} CHECK(S) FAILED`);
await b.close();
fs.unlinkSync(PREV);
process.exit(fail === 0 ? 0 : 1);
