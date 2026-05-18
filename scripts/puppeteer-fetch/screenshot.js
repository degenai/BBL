#!/usr/bin/env node
const puppeteer = require('puppeteer');

(async () => {
  const url = process.argv[2];
  const out = process.argv[3] || 'screenshot.png';
  if (!url) { console.error('usage: screenshot.js <url> <out.png>'); process.exit(1); }
  const browser = await puppeteer.launch({
    headless: true,
    args: ['--no-sandbox', '--disable-setuid-sandbox'],
  });
  const page = await browser.newPage();
  await page.setViewport({ width: 1280, height: 900, deviceScaleFactor: 1 });
  page.on('console', m => console.error('[page]', m.type(), m.text()));
  page.on('pageerror', e => console.error('[pageerror]', e.message));
  page.on('requestfailed', r => console.error('[reqfail]', r.url(), r.failure().errorText));
  const resp = await page.goto(url, { waitUntil: 'networkidle2', timeout: 20000 });
  console.error('[status]', resp.status());
  // wait extra for michi inserts manifest fetch
  await new Promise(r => setTimeout(r, 2000));
  await page.screenshot({ path: out, fullPage: true });
  // dump michi-page count + slot details
  const info = await page.evaluate(() => {
    const pages = [...document.querySelectorAll('.michi-page')];
    return pages.map((p, i) => ({
      page: i,
      slot_count: p.children.length,
      slots: [...p.children].map(s => ({
        cls: s.className,
        img: s.querySelector('img')?.src.split('/').pop() || null,
        complete: s.querySelector('img')?.complete,
        natW: s.querySelector('img')?.naturalWidth,
      })),
    }));
  });
  console.error('[michi]', JSON.stringify(info, null, 2));
  await browser.close();
})();
