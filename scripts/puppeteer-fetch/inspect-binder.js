#!/usr/bin/env node
const puppeteer = require('puppeteer');

(async () => {
  const url = process.argv[2];
  const browser = await puppeteer.launch({ headless: true, args: ['--no-sandbox'] });
  const page = await browser.newPage();
  await page.setViewport({ width: 1280, height: 900, deviceScaleFactor: 2 });
  await page.goto(url, { waitUntil: 'networkidle2', timeout: 20000 });
  await new Promise(r => setTimeout(r, 1500));
  const info = await page.evaluate(() => {
    const pages = [...document.querySelectorAll('.michi-page')];
    return pages.map((p, i) => ({
      page: i + 1,
      slots: [...p.querySelectorAll('.michi-slot')].map(el => {
        const img = el.querySelector('img');
        return {
          cls: el.className,
          file: img?.src.split('/').slice(-2).join('/').split('?')[0],
          alt: (img?.alt || '').slice(0, 60),
        };
      }),
    }));
  });
  console.log(JSON.stringify(info, null, 2));
  await browser.close();
})();
