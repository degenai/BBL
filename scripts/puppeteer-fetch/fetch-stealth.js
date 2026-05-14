#!/usr/bin/env node
/*
  puppeteer-fetch-stealth — Cloudflare-fingerprint-resistant fetch.

  Uses puppeteer-extra + puppeteer-extra-plugin-stealth to defeat sites
  that detect headless Chrome via browser fingerprinting (Cardmarket etc).
  Slower than vanilla fetch.js — only use when fetch.js gets HTTP 403.

  Usage:
    node fetch-stealth.js "<URL>"
    node fetch-stealth.js "<URL>" --text-only
    node fetch-stealth.js "<URL>" --wait-for="<selector>"
    node fetch-stealth.js "<URL>" --timeout=45000

  Exit codes:
    0 = success (HTML/text on stdout)
    1 = bad args
    2 = navigation failed
    3 = timeout waiting for content
    4 = page returned non-2xx
*/

const puppeteer = require('puppeteer-extra');
const StealthPlugin = require('puppeteer-extra-plugin-stealth');
puppeteer.use(StealthPlugin());

function parseArgs(argv) {
  const args = { url: null, textOnly: false, waitFor: null, timeoutMs: 45000 };
  for (const tok of argv.slice(2)) {
    if (tok === '--text-only') args.textOnly = true;
    else if (tok.startsWith('--wait-for=')) args.waitFor = tok.slice('--wait-for='.length);
    else if (tok.startsWith('--timeout=')) args.timeoutMs = parseInt(tok.slice('--timeout='.length), 10) || 45000;
    else if (!args.url) args.url = tok;
  }
  return args;
}

(async () => {
  const args = parseArgs(process.argv);
  if (!args.url) {
    console.error('usage: node fetch-stealth.js "<URL>" [--text-only] [--wait-for=<sel>] [--timeout=<ms>]');
    process.exit(1);
  }

  let browser;
  try {
    browser = await puppeteer.launch({
      headless: true,
      args: [
        '--no-sandbox',
        '--disable-setuid-sandbox',
        '--disable-dev-shm-usage',
      ],
    });
    const page = await browser.newPage();
    await page.setViewport({ width: 1280, height: 800 });
    // Stealth plugin handles UA + fingerprint cleanup; setUserAgent is unnecessary.

    const resp = await page.goto(args.url, {
      waitUntil: 'networkidle2',
      timeout: args.timeoutMs,
    });

    if (!resp) {
      console.error(`[stealth] no response object for ${args.url}`);
      process.exit(2);
    }
    const status = resp.status();
    if (status >= 400) {
      console.error(`[stealth] HTTP ${status} on ${args.url}`);
      process.exit(4);
    }

    if (args.waitFor) {
      try {
        await page.waitForSelector(args.waitFor, { timeout: args.timeoutMs });
      } catch (e) {
        console.error(`[stealth] timeout waiting for selector "${args.waitFor}": ${e.message}`);
        process.exit(3);
      }
    } else {
      try {
        const title = await page.title();
        if (/just a moment|attention required/i.test(title)) {
          await page.waitForFunction(
            () => !/just a moment|attention required/i.test(document.title),
            { timeout: args.timeoutMs }
          );
        }
      } catch (e) {
        // Non-fatal — proceed.
      }
    }

    if (args.textOnly) {
      const text = await page.evaluate(() => document.body && document.body.innerText || '');
      process.stdout.write(text);
    } else {
      const html = await page.content();
      process.stdout.write(html);
    }
    await browser.close();
    process.exit(0);
  } catch (e) {
    console.error(`[stealth] error: ${e.message}`);
    try { if (browser) await browser.close(); } catch (_) {}
    process.exit(2);
  }
})();
