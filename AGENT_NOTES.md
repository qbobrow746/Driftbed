# Agent notes — Driftbed

Read this before touching anything in this repo.

## Source of truth

- **`index.html` is the ONLY file you edit for app changes.** It is a
  single self-contained HTML file (no build step) served as a PWA.
- **`driftbed-standalone.html` is GENERATED. Never hand-edit it.** After any
  change to `index.html`, run:

  ```
  node tools/build-standalone.mjs
  ```

  This regenerates the standalone copy (marker-based transform: swaps the
  `<title>`, strips the PWA-install `<head>` block and the service-worker
  registration script — everything else is copied verbatim).

## Before you report success

You **must** run:

```
node tools/check.mjs
```

and it **must exit 0**. It checks (1) inline `<script>` blocks still parse,
(2) every DOM id referenced from JS has a matching `id="..."` in the HTML
(and no duplicate ids), and (3) `driftbed-standalone.html` is in sync with
`index.html`. If check 3 fails, run `node tools/build-standalone.mjs`
and re-check.

## Hard limits

- **Do NOT run any `git` command**, for any reason — not commit, not reset,
  not stash, not checkout. Version control is handled outside your session.
- **Do NOT push, deploy, publish, upload, or touch anything network-facing.**
  The live site is not yours to update.
- **Do not delete files.** Off-limits paths: `compose.py`, `midi/`,
  `NOTES.md`, and anything outside this project directory.
- `driftbed-pwa.zip` is a stale local upload artifact (gitignored). Don't
  wire it into the build; regenerate it by hand if you ever need it.

## Architecture orientation

Driftbed is a single self-contained HTML file: CSS custom properties plus a
`.panel` UI live in `<head>`/`<body>`, and the app logic is one big IIFE
containing a `BIOMES` data table (per-biome scale, chords, reverb, noise,
and visual-motion settings), a Web Audio graph assembled in `initAudio()`
(pad voices feed `bedBus`, played notes feed `melodyBus`, both feed
`voiceBus` → a brightness lowpass → dry signal + convolver reverb →
`masterGain`), melody pads that always track whichever chord is currently
playing, and a `requestAnimationFrame` canvas loop rendering a field of
drifting "motes" at the end of the file.
