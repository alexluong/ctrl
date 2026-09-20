import { connect, url, redact } from './lib.mjs';
const [q, pat] = process.argv.slice(2);
const { b, p } = await connect();
await p.goto(await url(q), { waitUntil: 'domcontentloaded' });
await p.waitForTimeout(2500);
const out = await p.evaluate(() => {
  const seen = new Set(), res = [];
  for (const e of document.querySelectorAll('a,[onclick],[href]')) {
    const h = e.getAttribute('href') || '', o = (e.getAttribute('onclick') || '').slice(0, 160);
    const t = (e.innerText || '').replace(/\s+/g, ' ').trim().slice(0, 40);
    const k = h + '|' + o;
    if ((h && !h.startsWith('#') && !h.startsWith('javascript:void')) || o) { if (!seen.has(k)) { seen.add(k); res.push([t, h, o].join(' :: ')); } }
  }
  return res;
});
const re = pat ? new RegExp(pat, 'i') : null;
console.log(redact(out.filter(l => !re || re.test(l)).slice(0, 60).join('\n')));
await b.close().catch(() => {});
