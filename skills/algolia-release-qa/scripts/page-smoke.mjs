#!/usr/bin/env node
// Page-startup smoke gate for an Algolia search UI.
//
// Loads the page in a real browser and asserts the things that "I re-read my
// edits" cannot prove: no uncaught errors, every <script src> resolved, search
// requests actually fired, hit cards rendered with text, the Insights client
// really loaded (not a queued stub), and — optionally — a typed query reaches
// the results and a click emits an Insights event.
//
// Requires Playwright:  npm i -D playwright   (uses installed Google Chrome
// when present; otherwise run `npx playwright install chromium` once).
// --dir serves the folder with `python3 -m http.server`; pass --url instead
// if a server is already running.
//
// Usage:
//   node page-smoke.mjs --url http://localhost:8000/index.html
//   node page-smoke.mjs --dir ./storefront [--file index.html]
//   options: --query "yoga mat"   type into the search input, press Enter,
//                                 assert the results request carries the query
//            --click              click the first hit, assert an Insights request
//            --hit-selector CSS   override hit-card selector
//            --input-selector CSS override search-input selector
//            --min-hits N         default 1
//            --mobile             also load at 375px and check horizontal overflow
//            --json               machine-readable output
//
// Exit code 0 = every gate passed, 1 = at least one gate failed, 2 = setup error.

import { spawn } from 'node:child_process';
import { createRequire } from 'node:module';
import path from 'node:path';

const args = parseArgs(process.argv.slice(2));
if (!args.url && !args.dir) {
  console.error('usage: page-smoke.mjs --url <url> | --dir <folder> [--query q] [--click] [--mobile] [--json]');
  process.exit(2);
}

const HIT_SEL = args['hit-selector'] || '.ais-Hits-item, .ais-InfiniteHits-item, [data-hit], .hit, .product-card, article';
// Tried in order: the main search input must win over facet-search inputs that may precede it in the DOM.
const INPUT_SELS = (args['input-selector'] || '.ais-SearchBox-input, .aa-Input, input[type="search"], input[type="text"]').split(',').map(s => s.trim());
const INPUT_SEL = INPUT_SELS.join(', ');
const MIN_HITS = Number(args['min-hits'] || 1);
async function findInput(p) { for (const s of INPUT_SELS) { const el = await p.$(s); if (el) return el; } return null; }

// Resolve Playwright from the project under test (cwd), not from wherever this
// script is installed - skills usually live outside the project tree.
let chromium;
try {
  ({ chromium } = createRequire(path.join(process.cwd(), 'package.json'))('playwright'));
} catch {
  try { ({ chromium } = await import('playwright')); }
  catch {
    console.error('Playwright not found. Run: npm i -D playwright   (then, if no Google Chrome is installed: npx playwright install chromium)');
    process.exit(2);
  }
}

let server = null;
let url = args.url;
if (args.dir) {
  const port = 8765 + Math.floor(Math.random() * 200);
  server = spawn('python3', ['-m', 'http.server', String(port), '--directory', args.dir], { stdio: 'ignore' });
  await new Promise(r => setTimeout(r, 700));
  url = `http://localhost:${port}/${args.file || 'index.html'}`;
}

const results = [];
const gate = (name, pass, evidence) => results.push({ name, pass, evidence });

let browser;
try {
  try { browser = await chromium.launch({ channel: 'chrome', headless: true }); }
  catch { browser = await chromium.launch({ headless: true }); }
} catch (e) {
  console.error('Could not launch a browser: ' + e.message);
  cleanup(); process.exit(2);
}

try {
  const page = await browser.newPage({ viewport: { width: 1280, height: 900 } });
  const pageErrors = [], consoleErrors = [], failedScripts = [], searchReqs = [], insightsReqs = [];
  page.on('pageerror', e => pageErrors.push(String(e.message || e)));
  // "Failed to load resource" console lines are covered by the asset gates below; favicon 404s are noise.
  page.on('console', m => { if (m.type() === 'error' && !/Failed to load resource/.test(m.text())) consoleErrors.push(m.text().slice(0, 200)); });
  const failedAssets = [];
  page.on('response', r => {
    const u = r.url(), t = r.request().resourceType();
    if (r.status() < 400 || /favicon\.ico$/.test(u)) return;
    if (t === 'script') failedScripts.push(`${r.status()} ${u}`); else failedAssets.push(`${r.status()} ${u}`);
  });
  page.on('requestfailed', r => { if (r.resourceType() === 'script') failedScripts.push(`FAILED ${r.url()}`); });
  page.on('request', r => {
    const u = r.url();
    if (/algolia(net\.com|\.net)\/1\/indexes/.test(u)) searchReqs.push({ url: u, body: r.postData() || '' });
    if (/insights\.algolia\.io/.test(u)) insightsReqs.push({ url: u, body: r.postData() || '' });
  });

  await page.goto(url, { waitUntil: 'load', timeout: 30000 });
  await page.waitForTimeout(2500);

  gate('No uncaught errors', pageErrors.length === 0, pageErrors.length ? pageErrors.slice(0, 3).join(' | ') : 'clean');
  gate('No console errors', consoleErrors.length === 0, consoleErrors.length ? consoleErrors.slice(0, 3).join(' | ') : 'clean');
  gate('Every <script src> resolved', failedScripts.length === 0, failedScripts.length ? failedScripts.join(' | ') : 'all 2xx');
  gate('Every stylesheet/image/XHR resolved', failedAssets.length === 0, failedAssets.length ? failedAssets.slice(0, 3).join(' | ') : 'all 2xx (favicon ignored)');
  gate('Search request fired on load', searchReqs.length > 0, `${searchReqs.length} request(s) to the Algolia search API`);

  const hits = await page.$$eval(HIT_SEL, els => els.map(e => (e.innerText || '').trim()));
  const textless = hits.filter(t => t.length < 8 || /^div$/i.test(t)).length;
  gate(`At least ${MIN_HITS} hit card(s) rendered`, hits.length >= MIN_HITS, `${hits.length} matched "${HIT_SEL}"`);
  gate('Hit cards carry text (name/price), not a bare image', hits.length > 0 && textless === 0,
    hits.length ? `${textless} of ${hits.length} cards have no readable text` : 'no cards');

  // The loader shim keeps `aa.queue` even after the library drains it, so queue length proves
  // nothing. A live client answers `getVersion`; a stub swallows the call forever.
  const aa = await page.evaluate(async () => {
    const f = window.aa;
    if (typeof f !== 'function') return { state: 'absent', lib: typeof window.AlgoliaAnalytics };
    const answered = await new Promise(res => { try { f('getVersion', v => res(v || true)); } catch { res(false); } setTimeout(() => res(false), 1000); });
    return { state: answered ? 'loaded' : 'stub', version: answered, queued: Array.isArray(f.queue) ? f.queue.length : 0, lib: typeof window.AlgoliaAnalytics };
  });
  gate('Insights client loaded (not a queued stub)', aa.state === 'loaded',
    aa.state === 'absent' ? `window.aa is undefined (search-insights library ${aa.lib === 'object' ? 'loaded but never bound — set window.AlgoliaAnalyticsObject = "aa" before the script' : 'not loaded'})`
      : aa.state === 'loaded' ? `window.aa answers getVersion (${aa.version})`
      : `window.aa never answers getVersion — it is the loader shim with ${aa.queued} queued call(s); the script 404'd or window.AlgoliaAnalyticsObject was not set`);

  if (args.query) {
    const before = searchReqs.length;
    const input = await findInput(page);
    if (!input) gate('Typed query reaches the results', false, `no input matched "${INPUT_SEL}"`);
    else {
      await input.click(); await input.fill(''); await input.type(String(args.query), { delay: 40 });
      await page.keyboard.press('Enter'); await page.waitForTimeout(1800);
      const after = searchReqs.slice(before);
      const needle = String(args.query).toLowerCase();
      const carried = after.some(r => (r.body + r.url).toLowerCase().includes(encodeURIComponent(needle)) || (r.body + r.url).toLowerCase().includes(needle));
      const hitsAfter = await page.$$eval(HIT_SEL, els => els.map(e => (e.innerText || '').trim().slice(0, 60)));
      const changed = JSON.stringify(hitsAfter) !== JSON.stringify(hits.map(t => t.slice(0, 60)));
      gate('Typed query reaches the results', carried && changed,
        `${after.length} search request(s) after Enter; query in request: ${carried}; results changed: ${changed}`);
    }
  }

  if (args.click) {
    const before = insightsReqs.length;
    const first = await page.$(HIT_SEL);
    if (!first) gate('Click emits an Insights event', false, 'no hit to click');
    else {
      const target = (await first.$('a, button')) || first;
      await target.click({ timeout: 5000 }).catch(() => {});
      await page.waitForTimeout(1800);
      const evs = insightsReqs.slice(before);
      const ok = evs.some(e => /queryID/.test(e.body) && /objectIDs/.test(e.body));
      gate('Click emits an attributed Insights event', ok,
        evs.length ? `${evs.length} Insights request(s); attributed (queryID+objectIDs): ${ok}` : 'no request to insights.algolia.io after click');
    }
  }

  if (args.mobile) {
    const m = await browser.newPage({ viewport: { width: 375, height: 740 } });
    await m.goto(url, { waitUntil: 'load', timeout: 30000 }); await m.waitForTimeout(1500);
    const over = await m.evaluate(() => document.documentElement.scrollWidth - window.innerWidth);
    const mInput = await findInput(m);
    const inputVisible = mInput ? await mInput.evaluate(el => { const r = el.getBoundingClientRect(); return r.width > 0 && r.top >= 0 && r.top < window.innerHeight; }).catch(() => false) : false;
    gate('375px: no horizontal overflow', over <= 0, `scrollWidth exceeds viewport by ${Math.max(0, over)}px`);
    gate('375px: search input visible without scrolling', inputVisible, inputVisible ? 'visible' : 'not in first viewport');
    await m.close();
  }
} catch (e) {
  gate('Page loaded', false, e.message);
} finally {
  await browser.close();
  cleanup();
}

const failed = results.filter(r => !r.pass);
if (args.json) console.log(JSON.stringify({ url, passed: results.length - failed.length, failed: failed.length, gates: results }, null, 2));
else {
  for (const r of results) console.log(`${r.pass ? 'PASS' : 'FAIL'}  ${r.name} — ${r.evidence}`);
  console.log(`\n${results.length - failed.length}/${results.length} gates passed${failed.length ? ' — NOT launch-ready' : ''}`);
}
process.exit(failed.length ? 1 : 0);

function cleanup() { if (server) server.kill(); }
function parseArgs(a) {
  const o = {};
  for (let i = 0; i < a.length; i++) {
    if (!a[i].startsWith('--')) continue;
    const k = a[i].slice(2), v = a[i + 1];
    if (v === undefined || v.startsWith('--')) o[k] = true; else { o[k] = v; i++; }
  }
  return o;
}
