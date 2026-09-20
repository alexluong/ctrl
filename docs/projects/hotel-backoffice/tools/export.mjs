import { connect, url, redact } from './lib.mjs';
import path from 'path';
const [slug, q] = process.argv.slice(2);
const OUT = path.join(import.meta.dirname, '..', 'exports');
const { b, p } = await connect();
await p.goto(await url(q), { waitUntil: 'domcontentloaded' });
await p.waitForTimeout(2500);
const search = p.locator('[name=do_search],[name=search],[id=do_search]').first();
if (await search.count()) { await search.click().catch(()=>{}); await p.waitForTimeout(4000); }
const [dl] = await Promise.all([
  p.waitForEvent('download', { timeout: 30000 }),
  p.locator('[id=btnExport],[name=btnExport]').first().click(),
]);
const name = dl.suggestedFilename();
const dest = path.join(OUT, slug + '-' + name);
await dl.saveAs(dest);
console.log(redact('saved: ' + dest + ' (suggested: ' + name + ')'));
await b.close().catch(() => {});
