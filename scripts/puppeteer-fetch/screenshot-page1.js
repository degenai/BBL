#!/usr/bin/env node
const puppeteer = require('puppeteer');

(async () => {
  const url = process.argv[2];
  const out = process.argv[3];
  const browser = await puppeteer.launch({ headless: true, args: ['--no-sandbox'] });
  const page = await browser.newPage();
  await page.setViewport({ width: 1400, height: 1100, deviceScaleFactor: 2 });
  await page.goto(url, { waitUntil: 'networkidle2', timeout: 20000 });
  await page.evaluate(() => {
    document.querySelectorAll('.michi-page img').forEach(img => img.loading = 'eager');
  });
  await new Promise(r => setTimeout(r, 2500));
  const page1 = await page.$('.michi-pages .michi-page:first-child');
  await page1.screenshot({ path: out });
  await browser.close();
  console.error('done', out);
})();
