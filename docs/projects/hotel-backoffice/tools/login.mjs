import { connect, describe, sec, log } from './lib.mjs';
const { b, p } = await connect();
await p.goto(sec.pub, { waitUntil: 'domcontentloaded' });
if (await p.$('input[name=user_id]')) {
  await p.fill('input[name=user_id]', sec.user);
  await p.fill('input[name=password]', sec.pass);
  await p.evaluate(() => document.querySelector('input[type=submit]').closest('form').submit()); // login POST must go through
  await p.waitForLoadState('networkidle').catch(() => {});
}
await p.waitForTimeout(1500);
log('now at', await p.evaluate(() => location.search));
await b.close().catch(() => {});
