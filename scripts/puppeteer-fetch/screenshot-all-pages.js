#!/usr/bin/env node
const puppeteer = require('puppeteer');

(async () => {
  const url = process.argv[2];
  const outBase = process.argv[3] || 'page';
  const browser = await puppeteer.launch({ headless: true, args: ['--no-sandbox'] });
  const page = await browser.newPage();
  await page.setViewport({ width: 1400, height: 1100, deviceScaleFactor: 2 });
  await page.goto(url, { waitUntil: 'networkidle2', timeout: 20000 });
  await page.evaluate(() => {
    document.querySelectorAll('.michi-page img').forEach(img => img.loading = 'eager');
  });
  await new Promise(r => setTimeout(r, 3000));
  const pages = await page.$$('.michi-pages .michi-page');
  for (let i = 0; i < pages.length; i++) {
    await pages[i].screenshot({ path: `${outBase}-${i + 1}.png` });
  }
  console.error('wrote', pages.length, 'pages');
  await browser.close();
})();
