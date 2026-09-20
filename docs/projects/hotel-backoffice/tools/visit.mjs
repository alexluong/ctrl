import { connect, describe, url, log } from './lib.mjs';
const [slug, q] = process.argv.slice(2);
const { b, p } = await connect();
await p.goto(await url(q), { waitUntil: 'domcontentloaded' });
await p.waitForTimeout(2500);
await describe(p, slug);
await b.close().catch(() => {});
