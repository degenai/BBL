#!/usr/bin/env node
const puppeteer = require('puppeteer');

(async () => {
  const url = process.argv[2];
  const out = process.argv[3] || 'binder.png';
  const browser = await puppeteer.launch({
    headless: true,
    args: ['--no-sandbox', '--disable-setuid-sandbox'],
  });
  const page = await browser.newPage();
  await page.setViewport({ width: 1280, height: 900, deviceScaleFactor: 2 });
  page.on('requestfailed', r => console.error('[reqfail]', r.url(), r.failure().errorText));
  await page.goto(url, { waitUntil: 'networkidle2', timeout: 20000 });
  await page.evaluate(() => {
    // force any lazy images in the binder to load
    document.querySelectorAll('.michi-page img').forEach(img => img.loading = 'eager');
  });
  await new Promise(r => setTimeout(r, 2500));
  const el = await page.$('#michi-section');
  await el.screenshot({ path: out });
  await browser.close();
  console.error('done', out);
})();
