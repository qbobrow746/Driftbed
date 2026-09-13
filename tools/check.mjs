#!/usr/bin/env node
// The gate every agent editing this app must pass before claiming success.
//
// Runs three checks against pwa/index.html:
//   1. JS syntax     — every inline <script> (no src=) parses via `node --check`.
//   2. DOM id integrity — every id referenced from JS exists exactly once in the HTML.
//   3. Standalone in sync — driftbed-standalone.html matches what
//                            tools/build-standalone.mjs would generate.
//
// Usage: node tools/check.mjs
// Exits 0 only if all three checks pass.

import { readFileSync, writeFileSync, mkdtempSync, rmSync } from 'node:fs';
import { execFileSync } from 'node:child_process';
import { fileURLToPath } from 'node:url';
import path from 'node:path';
import os from 'node:os';

import { buildStandalone } from './build-standalone.mjs';

const __dirname = path.dirname(fileURLToPath(import.meta.url));
const ROOT = path.resolve(__dirname, '..');
const SRC_PATH = path.join(ROOT, 'pwa', 'index.html');
const STANDALONE_PATH = path.join(ROOT, 'driftbed-standalone.html');

const results = [];

function record(name, ok, detail) {
  results.push({ name, ok, detail });
}

// ---------------------------------------------------------------------
// Check 1 — JS syntax
// ---------------------------------------------------------------------
function checkJsSyntax(html) {
  const scriptRe = /<script\b([^>]*)>([\s\S]*?)<\/script>/gi;
  const blocks = [];
  let m;
  while ((m = scriptRe.exec(html)) !== null) {
    const attrs = m[1];
    if (/\bsrc\s*=/.test(attrs)) continue; // external script, skip
    blocks.push(m[2]);
  }

  if (blocks.length === 0) {
    record('1. JS syntax', false, 'no inline <script> blocks found (unexpected — check the extraction regex)');
    return;
  }

  const tmpDir = mkdtempSync(path.join(os.tmpdir(), 'driftbed-check-'));
  const failures = [];
  try {
    blocks.forEach((code, i) => {
      const tmpFile = path.join(tmpDir, `inline-script-${i}.js`);
      writeFileSync(tmpFile, code, 'utf8');
      try {
        execFileSync(process.execPath, ['--check', tmpFile], { stdio: ['ignore', 'pipe', 'pipe'] });
      } catch (err) {
        const stderr = (err.stderr || err.message || '').toString().trim();
        failures.push(`  block #${i}: ${stderr.split('\n').slice(0, 5).join('\n  ')}`);
      }
    });
  } finally {
    rmSync(tmpDir, { recursive: true, force: true });
  }

  if (failures.length > 0) {
    record('1. JS syntax', false, `${failures.length}/${blocks.length} inline script block(s) failed to parse:\n${failures.join('\n')}`);
  } else {
    record('1. JS syntax', true, `${blocks.length} inline script block(s) OK`);
  }
}

// ---------------------------------------------------------------------
// Check 2 — DOM id integrity
// ---------------------------------------------------------------------
function checkDomIds(html) {
  // Defined ids: id="..." or id='...'
  const definedIds = [];
  const idDefRe = /\bid\s*=\s*"([^"]+)"|\bid\s*=\s*'([^']+)'/g;
  let m;
  while ((m = idDefRe.exec(html)) !== null) {
    definedIds.push(m[1] ?? m[2]);
  }

  const definedCounts = new Map();
  for (const id of definedIds) {
    definedCounts.set(id, (definedCounts.get(id) || 0) + 1);
  }
  const duplicates = [...definedCounts.entries()].filter(([, count]) => count > 1);

  // Referenced ids from JS: getElementById('x'|"x"), querySelector('#x'|"#x")
  // Only plain single/double-quoted string literals — skip template literals
  // and anything not statically resolvable.
  const referenced = new Set();
  const getByIdRe = /getElementById\s*\(\s*(?:"([^"]+)"|'([^']+)')\s*\)/g;
  while ((m = getByIdRe.exec(html)) !== null) {
    referenced.add(m[1] ?? m[2]);
  }
  const qsRe = /querySelector(?:All)?\s*\(\s*(?:"(#[A-Za-z0-9_-]+)"|'(#[A-Za-z0-9_-]+)')\s*\)/g;
  while ((m = qsRe.exec(html)) !== null) {
    const sel = m[1] ?? m[2];
    referenced.add(sel.slice(1)); // strip leading '#'
  }

  const definedSet = new Set(definedIds);
  const missing = [...referenced].filter((id) => !definedSet.has(id));

  const problems = [];
  if (missing.length > 0) {
    problems.push(`referenced id(s) with no matching definition: ${missing.map((s) => JSON.stringify(s)).join(', ')}`);
  }
  if (duplicates.length > 0) {
    problems.push(`duplicate id definition(s): ${duplicates.map(([id, n]) => `${JSON.stringify(id)} (x${n})`).join(', ')}`);
  }

  if (problems.length > 0) {
    record('2. DOM id integrity', false, problems.join('; '));
  } else {
    record('2. DOM id integrity', true, `${definedSet.size} defined id(s), ${referenced.size} referenced id(s) all resolved`);
  }
}

// ---------------------------------------------------------------------
// Check 3 — standalone in sync
// ---------------------------------------------------------------------
function checkStandaloneSync(html) {
  let expected;
  try {
    expected = buildStandalone(html);
  } catch (err) {
    record('3. standalone in sync', false, `build-standalone transform threw: ${err.message}`);
    return;
  }
  let actual;
  try {
    actual = readFileSync(STANDALONE_PATH, 'utf8');
  } catch (err) {
    record('3. standalone in sync', false, `could not read ${STANDALONE_PATH}: ${err.message}`);
    return;
  }
  if (actual !== expected) {
    record('3. standalone in sync', false, 'driftbed-standalone.html is stale. Run: node tools/build-standalone.mjs');
  } else {
    record('3. standalone in sync', true, 'driftbed-standalone.html matches pwa/index.html');
  }
}

// ---------------------------------------------------------------------
// Main
// ---------------------------------------------------------------------
function main() {
  console.log('Driftbed checks — verifying pwa/index.html\n');

  const html = readFileSync(SRC_PATH, 'utf8');

  checkJsSyntax(html);
  checkDomIds(html);
  checkStandaloneSync(html);

  let allOk = true;
  for (const { name, ok, detail } of results) {
    const status = ok ? 'ok  ' : 'FAIL';
    console.log(`[${status}] ${name} — ${detail}`);
    if (!ok) allOk = false;
  }

  console.log('');
  if (allOk) {
    console.log(`Summary: ${results.length}/${results.length} checks passed.`);
    process.exit(0);
  } else {
    const failed = results.filter((r) => !r.ok).length;
    console.log(`Summary: ${failed}/${results.length} check(s) FAILED.`);
    process.exit(1);
  }
}

main();
