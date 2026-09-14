#!/usr/bin/env node
// Generates driftbed-standalone.html from index.html.
//
// index.html is the single source of truth. This script applies a
// deterministic, marker-based transform (never line-number-based, since
// index.html's <head>/<body> will keep changing) to produce a
// stand-alone single-file copy suitable for sharing without the PWA
// sibling assets (manifest.json, icon-*.png, sw.js).
//
// Usage:
//   node tools/build-standalone.mjs            # write driftbed-standalone.html
//   node tools/build-standalone.mjs --check     # (or --dry-run) report diff, exit non-zero if stale
//
// Exits non-zero with a clear message if any transform assertion fails,
// rather than ever emitting a broken file.

import { readFileSync, writeFileSync, existsSync } from 'node:fs';
import { fileURLToPath } from 'node:url';
import path from 'node:path';

const __dirname = path.dirname(fileURLToPath(import.meta.url));
const ROOT = path.resolve(__dirname, '..');
const SRC_PATH = path.join(ROOT, 'index.html');
const OUT_PATH = path.join(ROOT, 'driftbed-standalone.html');

const TITLE_FROM = '<title>Driftbed</title>';
const TITLE_TO = '<title>Driftbed (standalone)</title>';

// The PWA-only head block is delimited by a matched pair of comments in
// index.html. Paired delimiters (rather than matching the last expected tag)
// mean new PWA metadata can be added inside the block without touching this
// script, and no tag name can accidentally match early as a substring.
const PWA_BLOCK_START_MARKER = '<!-- installable app metadata -->';
const PWA_BLOCK_END_MARKER = '<!-- /installable app metadata -->';

function fail(message) {
  console.error(`build-standalone: FAIL — ${message}`);
  process.exit(1);
}

export function buildStandalone(src) {
  let out = src;

  // 1. Title.
  if (!out.includes(TITLE_FROM)) {
    fail(`title string not found: expected to see ${JSON.stringify(TITLE_FROM)} in index.html`);
  }
  out = out.replace(TITLE_FROM, TITLE_TO);

  // 2. Remove the PWA-install block delimited by the paired marker comments,
  //    inclusive of both delimiter lines.
  const lines = out.split('\n');
  const startIdx = lines.findIndex((l) => l.includes(PWA_BLOCK_START_MARKER));
  if (startIdx === -1) {
    fail(`PWA-install start marker not found: ${JSON.stringify(PWA_BLOCK_START_MARKER)}`);
  }
  let endIdx = -1;
  for (let i = startIdx + 1; i < lines.length; i++) {
    if (lines[i].includes(PWA_BLOCK_END_MARKER)) {
      endIdx = i;
      break;
    }
  }
  if (endIdx === -1) {
    fail(`PWA-install end marker ${JSON.stringify(PWA_BLOCK_END_MARKER)} not found after the start marker — the PWA head block in index.html must stay wrapped in both comments`);
  }
  lines.splice(startIdx, endIdx - startIdx + 1);
  out = lines.join('\n');

  // 3. Remove the service-worker registration <script>...</script> block.
  // Match individual (non-crossing) <script>...</script> blocks first, then
  // pick the one whose body contains the sw-registration call — a single
  // greedy/lazy regex spanning "<script>...navigator.serviceWorker.register...</script>"
  // would risk swallowing an earlier, unrelated <script> block too.
  const scriptBlockRe = /<script>[\s\S]*?<\/script>\n?/g;
  const scriptBlocks = out.match(scriptBlockRe) || [];
  const swBlock = scriptBlocks.find((b) => b.includes('navigator.serviceWorker.register'));
  if (!swBlock) {
    fail('service-worker registration <script> block not found (expected a block containing navigator.serviceWorker.register)');
  }
  out = out.replace(swBlock, '');

  // 4. Collapse any doubled blank line left behind by a removal.
  out = out.replace(/\n{3,}/g, '\n\n');

  // --- Output sanity assertions ---
  // Anything PWA-specific surviving into the output means the block delimiters
  // moved or a new install-related tag was added outside them.
  for (const leftover of ['manifest.json', 'sw.js', 'icon-', 'rel="manifest"',
                          'apple-touch-icon', 'mobile-web-app-capable',
                          'apple-mobile-web-app', 'serviceWorker']) {
    if (out.includes(leftover)) {
      fail(`output still contains leftover sibling-file reference: ${JSON.stringify(leftover)}`);
    }
  }
  for (const sentinel of ['function initAudio', '</html>']) {
    if (!out.includes(sentinel)) {
      fail(`output is missing sentinel string ${JSON.stringify(sentinel)} — refusing to write a possibly-mangled file`);
    }
  }

  return out;
}

function main() {
  const args = process.argv.slice(2);
  const checkMode = args.includes('--check') || args.includes('--dry-run');

  if (!existsSync(SRC_PATH)) {
    fail(`source file not found: ${SRC_PATH}`);
  }
  const src = readFileSync(SRC_PATH, 'utf8');
  const out = buildStandalone(src);

  const existing = existsSync(OUT_PATH) ? readFileSync(OUT_PATH, 'utf8') : null;
  const isStale = existing !== out;

  if (checkMode) {
    if (isStale) {
      console.error(`build-standalone --check: STALE — driftbed-standalone.html does not match index.html.`);
      console.error(`Run: node tools/build-standalone.mjs`);
      process.exit(1);
    } else {
      console.log('build-standalone --check: OK — driftbed-standalone.html is up to date.');
      process.exit(0);
    }
  }

  writeFileSync(OUT_PATH, out, 'utf8');
  const lineCount = out.split('\n').length;
  if (isStale) {
    console.log(`build-standalone: wrote ${OUT_PATH} (${lineCount} lines) — content changed.`);
  } else {
    console.log(`build-standalone: wrote ${OUT_PATH} (${lineCount} lines) — no change (already up to date).`);
  }
}

if (import.meta.url === `file://${process.argv[1]}`) {
  main();
}
