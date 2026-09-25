// Browser regression suite for index.html.
// Run: node tests/browser.mjs   (needs Playwright; set PLAYWRIGHT_MODULE to its index.mjs if not resolvable)
import fs from 'fs';
import path from 'path';
import { fileURLToPath } from 'url';
const { chromium } = await import(process.env.PLAYWRIGHT_MODULE || 'playwright');
const PAGE = path.resolve(path.dirname(fileURLToPath(import.meta.url)), '..', 'index.html');
const raw = fs.readFileSync(PAGE,'utf8');
const PREV='/tmp/preview-test-'+process.pid+'.html';
fs.writeFileSync(PREV, `<!doctype html><html><head><meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1,viewport-fit=cover">
<style>:root{color-scheme:light;padding-top:env(safe-area-inset-top,0px);padding-bottom:env(safe-area-inset-bottom,0px)}
body{margin:0;font:14px system-ui;background:#fafaf9}img{max-width:100%}[hidden]{display:none!important}</style>
</head><body>${raw}</body></html>`);

const b = await chromium.launch();
let fail = 0;
const ok = (c,m)=>{ console.log((c?'  PASS  ':'  FAIL  ')+m); if(!c) fail++; };

for (const W of [320, 360, 412, 680]) {
  const p = await b.newPage({ viewport:{width:W,height:880} });
  const errs=[]; p.on('pageerror',e=>errs.push(e.message));
  await p.goto('file://'+PREV,{waitUntil:'domcontentloaded'});
  await p.waitForTimeout(600);
  const o = await p.evaluate(()=>[document.documentElement.scrollWidth, document.documentElement.clientWidth]);
  ok(o[0]<=o[1], `${W}px: no horizontal overflow (${o[0]}<=${o[1]})`);
  await p.click('#tab-regions'); await p.waitForTimeout(300);
  const o2 = await p.evaluate(()=>[document.documentElement.scrollWidth, document.documentElement.clientWidth]);
  ok(o2[0]<=o2[1], `${W}px tab 2: no horizontal overflow (${o2[0]}<=${o2[1]})`);
  ok(errs.length===0, `${W}px: no JS errors ${errs.join('|')}`);
  await p.close();
}

const p = await b.newPage({ viewport:{width:412,height:915} });
const errs=[]; p.on('pageerror',e=>errs.push('PAGEERROR '+e.message));
await p.goto('file://'+PREV,{waitUntil:'domcontentloaded'});
await p.waitForTimeout(700);

console.log('\n--- horizon switching ---');
const snap = async ()=> p.evaluate(()=>({
  band: document.querySelector('.band-v')?.textContent,
  note: document.querySelector('.band-n')?.textContent.slice(0,40),
  conv: document.querySelector('.conv-lbl')?.textContent,
  onHdr: document.querySelector('#matrix thead th.on')?.textContent,
  onCells: document.querySelectorAll('#matrix td.on').length,
  checked: document.querySelector('.seg button[aria-checked="true"]')?.textContent,
  status: document.getElementById('h-status')?.textContent,
  cards: document.querySelectorAll('.card').length
}));

const seen = new Set();
for (const h of ['3m','6m','12m','10y']) {
  await p.click(`#h-${h}`); await p.waitForTimeout(250);
  const s = await snap();
  seen.add(s.band);
  ok(s.cards===5, `${h}: 5 cards rendered`);
  ok(s.onCells===5, `${h}: 5 matrix cells highlighted (got ${s.onCells})`);
  ok(!!s.onHdr, `${h}: matrix header highlighted -> "${s.onHdr}"`);
  ok(/./.test(s.status), `${h}: live region -> "${s.status}"`);
  console.log(`         band=${s.band}  checked=${s.checked?.trim()}`);
}
ok(seen.size===4, `all 4 horizons produced distinct ranges (${seen.size}/4)`);

console.log('\n--- keyboard (roving tabindex + arrows) ---');
await p.click('#h-3m'); await p.waitForTimeout(150);
const tabIdx = await p.evaluate(()=>Array.from(document.querySelectorAll('.seg')).map(g=>Array.from(g.querySelectorAll('button')).filter(b=>b.tabIndex===0).length));
ok(tabIdx.every(n=>n===1), `exactly one tab stop per horizon group (${tabIdx})`);
await p.focus('#h-3m');
await p.keyboard.press('ArrowRight'); await p.waitForTimeout(200);
ok((await snap()).checked.trim()==='6 mo', 'ArrowRight advances 3mo -> 6mo');
await p.keyboard.press('End'); await p.waitForTimeout(200);
ok((await snap()).checked.trim()==='10 yr', 'End jumps to last (10 yr)');

console.log('\n--- sticky bars do not cover content ---');
// scroll far enough that the horizon bar is genuinely stuck, whatever the page length
await p.evaluate(()=>{
  const hz=document.querySelector('.horizon');
  window.scrollTo(0, hz.getBoundingClientRect().top + window.scrollY + 900);
});
await p.waitForTimeout(400);
const cover = await p.evaluate(()=>{
  const hz=document.querySelector('.horizon').getBoundingClientRect();
  const tb=document.querySelector('.topbar').getBoundingClientRect();
  // sample the strip just under the horizon bar: what element is on top?
  const el=document.elementFromPoint(window.innerWidth/2, hz.bottom+4);
  return {gap:+(hz.top-tb.bottom).toFixed(2), under: el?el.className||el.tagName:'none'};
});
ok(Math.abs(cover.gap)<1.5, `no seam between sticky bars (gap ${cover.gap}px)`);
ok(!String(cover.under).includes('horizon'), `content below bar is not overpainted (got "${cover.under}")`);

console.log('\n--- scroll stability on horizon change ---');
const before = await p.evaluate(()=>window.scrollY);
await p.click('#h-3m'); await p.waitForTimeout(350);
const after = await p.evaluate(()=>window.scrollY);
ok(Math.abs(before-after)<5, `scroll position held (${before} -> ${after})`);

console.log('\n--- rendered text contrast of role chips + rank tags (>=4.5:1) ---');
const chip = await p.evaluate(()=>{
  const toRGB=c=>c.match(/\d+(\.\d+)?/g).slice(0,3).map(Number);
  const L=rgb=>{const a=rgb.map(v=>{v/=255;return v<=0.03928?v/12.92:Math.pow((v+0.055)/1.055,2.4)});return 0.2126*a[0]+0.7152*a[1]+0.0722*a[2]};
  const ratio=(f,b)=>{const x=L(f),y=L(b);return (Math.max(x,y)+0.05)/(Math.min(x,y)+0.05)};
  const bgOf=el=>{while(el){const c=getComputedStyle(el).backgroundColor;if(c&&!/rgba\(0, 0, 0, 0\)|transparent/.test(c))return c;el=el.parentElement}return 'rgb(255,255,255)'};
  return Array.from(document.querySelectorAll('.role,.newflag')).map(el=>({t:el.textContent.trim(),r:+ratio(toRGB(getComputedStyle(el).color),toRGB(bgOf(el))).toFixed(2)}));
});
for(const c of chip) ok(c.r>=4.5, `"${c.t}" ${c.r}:1`);

console.log('\n=== Sentiment & regions tab ===');
await p.evaluate(()=>window.scrollTo(0,0));
await p.click('#tab-regions'); await p.waitForTimeout(350);
const tabs = await p.evaluate(()=>({
  sel: document.getElementById('tab-regions').getAttribute('aria-selected'),
  p1: document.getElementById('panel-etfs').hidden, p2: document.getElementById('panel-regions').hidden,
  stops: Array.from(document.querySelectorAll('[role=tab]')).filter(b=>b.tabIndex===0).map(b=>b.id)
}));
ok(tabs.sel==='true' && tabs.p1 && !tabs.p2, 'clicking the tab shows panel 2 and hides panel 1');
ok(tabs.stops.length===1 && tabs.stops[0]==='tab-regions', `one tab stop in the tab bar (${tabs.stops})`);

await p.focus('#tab-regions'); await p.keyboard.press('ArrowLeft'); await p.waitForTimeout(200);
ok(await p.evaluate(()=>document.activeElement.id==='tab-etfs' && !document.getElementById('panel-etfs').hidden), 'ArrowLeft moves to Top 5 and shows it');
await p.keyboard.press('End'); await p.waitForTimeout(250);
ok(await p.evaluate(()=>document.activeElement.id==='tab-regions' && !document.getElementById('panel-regions').hidden), 'End moves to the last tab');

// shared horizon: set on tab 2, read back from tab 1's control
await p.click('#r-3m'); await p.waitForTimeout(250);
const sync = await p.evaluate(()=>({
  t1: document.getElementById('h-3m').getAttribute('aria-checked'),
  on: Array.from(document.querySelectorAll('.st.on')).map(e=>e.dataset.h),
  hdr: document.querySelector('#rmatrix thead th.on')?.textContent
}));
ok(sync.t1==='true', 'horizon chosen on tab 2 is mirrored on tab 1');
ok(sync.on.length===2 && sync.on.every(h=>h==='3m'), `stance + volatility rows highlight 3m (${sync.on})`);
ok(sync.hdr==='3 mo', 'region matrix highlights the 3-month column');

// the ranked list must agree with the score table, under the stated rule
for (const h of ['3m','6m','12m','10y']) {
  await p.click('#r-'+h); await p.waitForTimeout(200);
  const r = await p.evaluate((h)=>{
    const col = {'3m':1,'6m':2,'12m':3,'10y':4}[h];
    const table = Array.from(document.querySelectorAll('#rmatrix tbody tr')).map(tr=>{
      const td = tr.querySelectorAll('td'); return {n:td[0].textContent, c:+td[col].textContent, sum:+td[5].textContent};
    });
    table.sort((a,b)=>(b.c-a.c)||(b.sum-a.sum)||(a.n<b.n?-1:a.n>b.n?1:0));
    let rank=0, prev=null; table.forEach((x,i)=>{ if(x.c!==prev){rank=i+1;prev=x.c;} x.rank=rank; x.tie=table.filter(y=>y.c===x.c).length>1; });
    const shown = Array.from(document.querySelectorAll('#rlist .reg')).map(el=>({n:el.querySelector('.reg-n').textContent, lbl:el.querySelector('.reg-rank').textContent}));
    return {want: table.map(x=>x.n+':'+(x.tie?'T':'')+x.rank), got: shown.map(x=>x.n+':'+x.lbl)};
  }, h);
  ok(JSON.stringify(r.want)===JSON.stringify(r.got), `${h}: ranked list matches score table + tie rule`);
  if (JSON.stringify(r.want)!==JSON.stringify(r.got)) console.log('   want', r.want, '\n   got ', r.got);
}

// charts: drawn, correct point counts, nothing outside the drawing
const ch = await p.evaluate(()=>['vc-vix','vc-ust'].map(id=>{
  const box=document.getElementById(id), svg=box.querySelector('svg'); if(!svg) return {id, drawn:false};
  const b=svg.getBoundingClientRect();
  const pts=Array.from(svg.querySelectorAll('circle.pt'));
  const inside=pts.every(c=>{const r=c.getBoundingClientRect();return r.left>=b.left-1&&r.right<=b.right+1&&r.top>=b.top-1&&r.bottom<=b.bottom+1;});
  const texts=Array.from(svg.querySelectorAll('text')).every(t=>{const r=t.getBoundingClientRect();return r.left>=b.left-2&&r.right<=b.right+2;});
  return {id, drawn:true, n:pts.length, derived:svg.querySelectorAll('circle.derived').length, inside, texts, label:!!box.getAttribute('aria-label')};
}));
ok(ch[0].drawn && ch[0].n===6 && ch[0].derived===1, `VIX chart: 6 points, 1 derived (${ch[0].n}/${ch[0].derived})`);
ok(ch[1].drawn && ch[1].n===7 && ch[1].derived===1, `10-yr chart: 7 points, 1 derived (${ch[1].n}/${ch[1].derived})`);
ok(ch.every(c=>c.inside && c.texts), 'chart points and labels stay inside their drawings');
ok(ch.every(c=>c.label), 'charts carry a text description');

// the chart sits far below the fold; move the pointer only once it is on screen
await p.evaluate(()=>document.getElementById('vc-vix').scrollIntoView({block:'center'})); await p.waitForTimeout(200);
const vb = await p.$('#vc-vix'); const bb = await vb.boundingBox();
await p.mouse.move(bb.x + bb.width - 20, bb.y + 60); await p.waitForTimeout(150);
const tip = await p.evaluate(()=>{const t=document.querySelector('#vc-vix .vtip');return t.hidden?null:t.textContent;});
ok(tip && /23 Sep/.test(tip) && /14\.21/.test(tip), `hover snaps to nearest point ("${tip}")`);
// a tap is how phone users read the chart: pointerdown must show the value too
await p.evaluate(()=>document.getElementById('vc-ust').scrollIntoView({block:'center'})); await p.waitForTimeout(150);
const ub = await (await p.$('#vc-ust')).boundingBox();
await p.mouse.move(ub.x + 45, ub.y + 70); await p.mouse.down(); await p.mouse.up(); await p.waitForTimeout(150);
const tap = await p.evaluate(()=>{const t=document.querySelector('#vc-ust .vtip');return t.hidden?null:t.textContent;});
ok(tap && /16 Sep/.test(tap) && /5\.01%/.test(tap), `tap near the left edge shows the first yield ("${tap}")`);
// union of dated observations across both series: 10,16,17,18,21,22,23,24 Sep
const rows = await p.evaluate(()=>document.querySelectorAll('#vtable tbody tr').length);
ok(rows===8, `numbers table lists every dated observation once (${rows})`);

// forecast bars drawn to one 0-9% scale
const fb = await p.evaluate(()=>Array.from(document.querySelectorAll('.fbar')).map(el=>{
  const t=el.querySelector('.fbar-track').getBoundingClientRect(), f=el.querySelector('.fbar-fill').getBoundingClientRect();
  return {n:el.querySelector('.n').textContent, left:(f.left-t.left)/t.width*9, w:f.width/t.width*9};
}));
const em = fb.find(x=>/Emerging/.test(x.n)), rg = fb.find(x=>/Vanguard/.test(x.n));
ok(Math.abs(em.w-7.8)<0.08, `EM bar drawn to 7.8% (${em.w.toFixed(2)})`);
ok(Math.abs(rg.left-3.9)<0.08 && Math.abs(rg.left+rg.w-5.9)<0.08, `Vanguard range spans 3.9-5.9% (${rg.left.toFixed(2)}-${(rg.left+rg.w).toFixed(2)})`);

// sticky seam on this tab too
await p.evaluate(()=>{ const hz=document.querySelector('#panel-regions .horizon'); window.scrollTo(0, hz.getBoundingClientRect().top + window.scrollY + 1200); });
await p.waitForTimeout(300);
const seam2 = await p.evaluate(()=>{ const hz=document.querySelector('#panel-regions .horizon').getBoundingClientRect(), tb=document.querySelector('.topbar').getBoundingClientRect(); return +(hz.top-tb.bottom).toFixed(2); });
ok(Math.abs(seam2)<1.5, `tab 2: no seam between sticky bars (${seam2}px)`);

const c2 = await p.evaluate(()=>{
  const toRGB=c=>c.match(/\d+(\.\d+)?/g).slice(0,3).map(Number);
  const L=rgb=>{const a=rgb.map(v=>{v/=255;return v<=0.03928?v/12.92:Math.pow((v+0.055)/1.055,2.4)});return 0.2126*a[0]+0.7152*a[1]+0.0722*a[2]};
  const ratio=(f,b)=>{const x=L(f),y=L(b);return (Math.max(x,y)+0.05)/(Math.min(x,y)+0.05)};
  const bgOf=el=>{while(el){const c=getComputedStyle(el).backgroundColor;if(c&&!/rgba\(0, 0, 0, 0\)|transparent/.test(c))return c;el=el.parentElement}return 'rgb(255,255,255)'};
  return Array.from(document.querySelectorAll('#panel-regions .tag, #panel-regions .reg-rank, #panel-regions .rung .here, #panel-regions .st.on .st-h, #panel-regions .scale-lbl, #panel-regions .g-date, #panel-regions .reg-ytd'))
    .map(el=>({t:el.textContent.trim().slice(0,22), r:+ratio(toRGB(getComputedStyle(el).color),toRGB(bgOf(el))).toFixed(2)}));
});
const worst = c2.reduce((a,b)=>a.r<b.r?a:b);
ok(c2.every(c=>c.r>=4.5), `tab 2 small text all >=4.5:1 across ${c2.length} elements (lowest "${worst.t}" ${worst.r}:1)`);

// remembered tab survives a reload
await p.reload({waitUntil:'domcontentloaded'}); await p.waitForTimeout(500);
ok(await p.evaluate(()=>!document.getElementById('panel-regions').hidden), 'selected tab is remembered across reload');
console.log('\nJS errors: '+(errs.length?errs.join(' | '):'none'));
console.log(fail===0 ? '\n>>> ALL CHECKS PASSED' : `\n>>> ${fail} CHECK(S) FAILED`);
await b.close();
process.exit(fail===0?0:1);
