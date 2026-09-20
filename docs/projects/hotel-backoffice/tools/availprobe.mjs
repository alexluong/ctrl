import { connect, url, log } from './lib.mjs';
const q = process.argv[2];
const { b, p } = await connect();
await p.goto(await url(q), { waitUntil:'domcontentloaded' });
await p.waitForTimeout(2500);
const d = await p.evaluate(() => {
  const txt = e => (e.innerText||'').replace(/\s+/g,' ').trim();
  const f = n => document.querySelector(`[name="${n}"]`)?.value;
  const grid = [...document.querySelectorAll('table')].map(tb =>
    [...tb.querySelectorAll('tr')].map(r=>[...r.children].map(c=>txt(c)).join(' | ')).filter(Boolean)
  ).filter(rows => rows.some(r=>/Hạng phòng|Hiệu suất/.test(r)));
  return { dates:{ arrival:f('arrival_time'), departure:f('departure_time'), night:f('night') }, grid };
});
log(JSON.stringify(d,null,1));
await b.close().catch(()=>{});
