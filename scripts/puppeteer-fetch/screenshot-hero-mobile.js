#!/usr/bin/env node
const puppeteer = require('puppeteer');
(async () => {
  const url = process.argv[2];
  const out = process.argv[3];
  const browser = await puppeteer.launch({ headless: true, args: ['--no-sandbox'] });
  const page = await browser.newPage();
  await page.setViewport({ width: 390, height: 844, deviceScaleFactor: 2, isMobile: true });
  await page.goto(url, { waitUntil: 'networkidle2', timeout: 20000 });
  await new Promise(r => setTimeout(r, 1500));
  const hero = await page.$('.hero');
  await hero.screenshot({ path: out });
  await browser.close();
})();
