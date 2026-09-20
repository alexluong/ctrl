import { connect, url, redact } from './lib.mjs';
const { b, p } = await connect();
await p.goto(await url('page=reservation&status=INHOUSE'), { waitUntil: 'domcontentloaded' });
await p.waitForTimeout(2500);
const out = await p.evaluate(() => {
  const rows = [...document.querySelectorAll('tr')].filter(r => /\b\d{4}\b/.test(r.innerText) && r.children.length > 8);
  const r = rows[0];
  if (!r) return 'no row';
  return { cells: [...r.children].map(c => (c.innerText||'').replace(/\s+/g,' ').trim().slice(0,40)),
    html: r.outerHTML.slice(0, 2500) };
});
console.log(redact(JSON.stringify(out, null, 1)));
await b.close().catch(() => {});
