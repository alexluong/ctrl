import { connect, url, redact } from './lib.mjs';
const { b, p } = await connect();
await p.goto(await url('page=room_map'), { waitUntil: 'domcontentloaded' });
await p.waitForTimeout(3500);
const out = await p.evaluate(() => {
  const res = [];
  for (const e of document.querySelectorAll('*')) {
    const t = (e.innerText || '').trim();
    if (t === '110' || t === '101') res.push(e.outerHTML.slice(0, 400) + ' >>PARENT>> ' + (e.parentElement?.outerHTML || '').slice(0, 600));
    if (res.length >= 3) break;
  }
  const fns = Object.keys(window).filter(k => /room|detail|popup|folio|book/i.test(k) && typeof window[k] === 'function').slice(0, 30);
  return { res, fns };
});
console.log(redact(JSON.stringify(out, null, 1)).slice(0, 4000));
await b.close().catch(() => {});
