import { connect, url, redact } from './lib.mjs';
const { b, p } = await connect();
for (const q of JSON.parse(process.argv[2])) {
  try {
    await p.goto(await url('page=' + q), { waitUntil: 'domcontentloaded' });
    await p.waitForTimeout(1200);
    const d = await p.evaluate(() => {
      const h = [...document.querySelectorAll('h1,h2,h3,legend,caption')].map(e => (e.innerText||'').replace(/\s+/g,' ').trim()).filter(Boolean).slice(0,3);
      const body = (document.body.innerText || '').replace(/\s+/g, ' ');
      const nav = body.indexOf('Quản lý khách ở');
      return { h, len: body.length, tail: body.slice(nav > 0 ? nav + 15 : 0, (nav > 0 ? nav + 15 : 0) + 180) };
    });
    console.log(redact(`${q.padEnd(28)} | ${d.len.toString().padStart(6)} | ${d.h.join(' / ').slice(0,60)} | ${d.tail.slice(0,120)}`));
  } catch (e) { console.log(`${q.padEnd(28)} | ERR`); }
}
await b.close().catch(()=>{});
