import { connect, url, redact } from './lib.mjs';
const { b, p } = await connect();
await p.goto(await url('page=employee'), { waitUntil: 'domcontentloaded' });
await p.waitForTimeout(1200);
const t = await p.evaluate(() => (document.body.innerText||'').replace(/\s+/g,' '));
// print with any DSN/user tokens masked
console.log(redact(t).replace(/(uid|pwd|user|password|dsn|driver)\s*=\s*[^ ;,)]*/ig, '$1=<masked>').slice(0, 900));
await b.close().catch(()=>{});
