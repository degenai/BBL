#!/usr/bin/env node
/*
  puppeteer-fetch — Headless Chromium fetch helper for the BBL research agents.

  When curl-with-browser-UA hits a Cloudflare JS challenge (the "Just a
  moment..." page), this helper runs a real Chromium instance, lets the
  challenge resolve, and prints the rendered HTML to stdout.

  Usage:
    node fetch.js "<URL>"
    node fetch.js "<URL>" --text-only        (returns innerText, not HTML)
    node fetch.js "<URL>" --wait-for="<sel>" (wait for a specific selector)
    node fetch.js "<URL>" --timeout=20000    (override 30s default)

  Exit codes:
    0 = success (HTML/text on stdout)
    1 = bad args
    2 = navigation failed
    3 = timeout waiting for content
    4 = page returned non-2xx
*/

const puppeteer = require('puppeteer');

function parseArgs(argv) {
  const args = { url: null, textOnly: false, waitFor: null, timeoutMs: 30000 };
  for (const tok of argv.slice(2)) {
    if (tok === '--text-only') args.textOnly = true;
    else if (tok.startsWith('--wait-for=')) args.waitFor = tok.slice('--wait-for='.length);
    else if (tok.startsWith('--timeout=')) args.timeoutMs = parseInt(tok.slice('--timeout='.length), 10) || 30000;
    else if (!args.url) args.url = tok;
  }
  return args;
}

(async () => {
  const args = parseArgs(process.argv);
  if (!args.url) {
    console.error('usage: node fetch.js "<URL>" [--text-only] [--wait-for=<selector>] [--timeout=<ms>]');
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
        '--disable-blink-features=AutomationControlled',
      ],
    });
    const page = await browser.newPage();
    await page.setUserAgent(
      'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 ' +
      '(KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
    );
    await page.setViewport({ width: 1280, height: 800 });

    const resp = await page.goto(args.url, {
      waitUntil: 'networkidle2',
      timeout: args.timeoutMs,
    });

    if (!resp) {
      console.error(`[fetch] no response object for ${args.url}`);
      process.exit(2);
    }
    const status = resp.status();
    if (status >= 400) {
      console.error(`[fetch] HTTP ${status} on ${args.url}`);
      process.exit(4);
    }

    if (args.waitFor) {
      try {
        await page.waitForSelector(args.waitFor, { timeout: args.timeoutMs });
      } catch (e) {
        console.error(`[fetch] timeout waiting for selector "${args.waitFor}": ${e.message}`);
        process.exit(3);
      }
    } else {
      // Generic Cloudflare challenge resolver: if the page title or content
      // looks like the JS challenge, wait a few seconds for it to clear.
      try {
        const title = await page.title();
        if (/just a moment|attention required/i.test(title)) {
          await page.waitForFunction(
            () => !/just a moment|attention required/i.test(document.title),
            { timeout: args.timeoutMs }
          );
        }
      } catch (e) {
        // Non-fatal — proceed and let the caller see whatever was rendered.
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
    console.error(`[fetch] error: ${e.message}`);
    try { if (browser) await browser.close(); } catch (_) {}
    process.exit(2);
  }
})();
