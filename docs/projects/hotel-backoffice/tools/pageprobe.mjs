import { connect, url, log } from './lib.mjs';
const pages = process.argv.slice(2);
const { b, p } = await connect();
for (const q of pages) {
  try {
    await p.goto(await url('page=' + q), { waitUntil:'domcontentloaded' });
    await p.waitForTimeout(1200);
    const d = await p.evaluate(() => {
      const body = (document.body.innerText||'').replace(/\s+/g,' ').trim();
      const heads = [...document.querySelectorAll('h1,h2,h3,legend,.title,.panel-title,b')].map(e=>(e.innerText||'').trim()).filter(Boolean).slice(0,4);
      const rows = [...document.querySelectorAll('table tr')].length;
      const denied = /không có quyền|no permission|access denied|bạn không được/i.test(body);
      const err = /ORA-|Fatal error|Warning:|Notice:/i.test(body);
      return { len: body.length, heads, rows, denied, err, head: body.slice(0,110) };
    });
    log(`${q.padEnd(28)} len=${String(d.len).padEnd(6)} rows=${String(d.rows).padEnd(4)} ${d.denied?'DENIED':d.err?'ERROR ':'ok    '} ${JSON.stringify(d.heads).slice(0,70)} :: ${d.head.slice(0,80)}`);
  } catch (e) { log(`${q.padEnd(28)} EXC ${String(e).slice(0,60)}`); }
}
await b.close().catch(()=>{});
