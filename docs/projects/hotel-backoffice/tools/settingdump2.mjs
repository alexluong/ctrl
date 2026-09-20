import { connect, url, redact } from './lib.mjs';
const { b, p } = await connect();
await p.goto(await url('page=setting'), { waitUntil: 'domcontentloaded' });
await p.waitForTimeout(3000);
const d = await p.evaluate(() => {
  const grab = (kw) => {
    for (const e of document.querySelectorAll('legend,h3,td,div')) {
      const t = (e.innerText || '').trim();
      if (t.startsWith(kw) && t.length < 4000) return t.replace(/\s*\n\s*/g, ' | ').slice(0, 1500);
    }
    return null;
  };
  return { cms: grab('Cấu hình kết nối ezCMS'), price: grab('Chính sách giá'), conn: grab('Thông tin kết nối') };
});
console.log(redact(JSON.stringify(d, null, 1)));
await b.close().catch(()=>{});
