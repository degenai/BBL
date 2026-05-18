#!/usr/bin/env node
const puppeteer = require('puppeteer');
(async () => {
  const url = process.argv[2];
  const out = process.argv[3];
  const browser = await puppeteer.launch({ headless: true, args: ['--no-sandbox'] });
  const page = await browser.newPage();
  page.on('console', m => console.error('[page]', m.type(), m.text()));
  page.on('pageerror', e => console.error('[pageerror]', e.message));
  page.on('requestfailed', r => console.error('[reqfail]', r.url(), r.failure().errorText));
  await page.setViewport({ width: 1280, height: 1400, deviceScaleFactor: 2 });
  await page.goto(url, { waitUntil: 'networkidle2', timeout: 20000 });
  await new Promise(r => setTimeout(r, 2500));
  const el = await page.$('#constellation-section');
  if (el) await el.screenshot({ path: out });
  else console.error('No constellation element');
  await browser.close();
})();
