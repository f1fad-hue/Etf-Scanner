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
const tabIdx = await p.evaluate(()=>Array.from(document.querySelectorAll('.seg button')).map(b=>b.tabIndex));
ok(tabIdx.filter(t=>t===0).length===1, `exactly one tab stop in group (${tabIdx})`);
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
console.log('\nJS errors: '+(errs.length?errs.join(' | '):'none'));
console.log(fail===0 ? '\n>>> ALL CHECKS PASSED' : `\n>>> ${fail} CHECK(S) FAILED`);
await b.close();
process.exit(fail===0?0:1);
