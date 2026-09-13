# big-scary-ost

This folder holds two independent, unrelated tools for the same ambient
game-music project: **Driftbed**, a playable instrument, and a **MIDI sketch
generator**. They don't share code or data — see "How the two halves relate"
below for why they live together.

## Driftbed

Driftbed is a single-file, self-contained ambient music instrument that runs
entirely in the browser (Web Audio + canvas, no build step, no server-side
code, no dependencies). It layers a generative ambient bed (noise, drone,
slowly-advancing chords, reverb tuned per biome) under a melody you can play
yourself, and it doubles as an installable PWA.

What it can currently do:

- **8 biomes** (desert, snow, oak forest, cave, aurora, rain, ocean, void),
  each with its own scale, chord progression, reverb character, noise color,
  and canvas motion style.
- A **root/scale (tuning) override**, decoupled from biome, so you can play
  any biome in any key/mode.
- **Melody pads** (5, mapped to keys A S D F G) in three modes — notes, arp,
  or full chord voicings — always tracking whichever chord is currently
  playing, with per-degree chord editing and optional 7ths.
- **Audio-reactive visuals**: the canvas field can respond to the actual
  output level/tone (the "pulse" chip), not just the Presence slider.
- A **generative performer** ("auto" chip) that plays the melody pads itself,
  chord-aware and phrase-structured, and a **performance looper** that
  records a short played performance and replays it hands-free.
- **Web MIDI input**: any class-compliant controller plays the instrument,
  every note folded onto the current scale, with sustain-pedal and mod-wheel
  support.
- **Freeze** (pin the current chord) and **tape character** (saturation +
  wow/flutter on the master output).
- **Presets**: factory patches, user-saved presets (localStorage), and
  shareable URL-hash permalinks that encode the full sound.
- **Recording**: captures the live mix to an uncompressed `.wav` (and a
  `.mid` of whatever you played), with opt-in separate bed/melody stems, a
  15-minute cap, and Int16 on-demand taps so idle playback costs nothing.
- **Seamless loop export**: captures a fixed-length take that crosshatches
  its own tail back over its head so it repeats with no audible seam —
  freezes the chord for the capture, since a chord change mid-loop can't be
  hidden.

Everything lives behind one panel: totems (biome), a breathe/presence core,
the melody block, an intensity fader, a utility row (fades, freeze, loop,
record, stems, loop export), four secondary dials (density/air/warmth/key),
and a collapsible layers row of toggle chips (accents, wind, echo, drift,
pulse, breathe, auto, tape). Four side-tab popovers (blend, tuning, midi,
presets) and two melody-block popovers (chords, tone) hold the deeper
controls.

### Single-source rule

**`pwa/index.html` is the only file you ever hand-edit for app changes.** It
is the entire app — markup, CSS, and JS in one file, served as an installable
PWA (`pwa/manifest.json`, `pwa/sw.js`, icons alongside it).

**`driftbed-standalone.html` at the project root is GENERATED — never
hand-edit it.** It's the same app minus the PWA-install `<head>` block and
service-worker registration, for dropping into a context where install/SW
semantics aren't wanted (e.g. attaching as a single file). After any change
to `pwa/index.html`, regenerate it:

```
node tools/build-standalone.mjs
```

### Running it locally

No build step, so any static file server works:

```
cd pwa && python3 -m http.server 8743
```

then open `http://localhost:8743`. Opening `pwa/index.html` directly via
`file://` mostly works too, except the clipboard API (used by "copy link")
requires a secure context — the presets popover falls back to a selectable
text field in that case.

### Tooling workflow

Two scripts live in `tools/`:

- **`node tools/build-standalone.mjs`** — regenerates
  `driftbed-standalone.html` from `pwa/index.html` via a marker-based
  transform (swap the `<title>`, strip the PWA-install head block and the
  service-worker registration script, copy everything else verbatim). Run
  this after every edit to `pwa/index.html`.
- **`node tools/check.mjs`** — the gate to pass before considering any change
  to Driftbed done. Must exit 0. It checks three things against
  `pwa/index.html`:
  1. **JS syntax** — every inline `<script>` block (no `src=`) parses via
     `node --check`.
  2. **DOM id integrity** — every DOM id referenced from JS
     (`getElementById`, `querySelector('#...')`, etc.) exists exactly once
     in the HTML, and no id is duplicated.
  3. **Standalone in sync** — `driftbed-standalone.html` matches what
     `tools/build-standalone.mjs` would produce right now. If this fails,
     run the build script and re-check.

### Orientation to the code

`pwa/index.html` is organized top to bottom as:

1. `<head>` — PWA install metadata, then a `<style>` block: CSS custom
   properties (`--accent`, `--panel`, etc., swapped per biome) followed by
   the `.panel` UI's styles, with narrow-viewport (`max-width:480px`) and
   `prefers-reduced-motion` media queries at the end.
2. `<body>` markup — the canvas (`#field`), the fixed corner labels, and the
   `.panel` itself with every control described above.
3. One big IIFE `<script>` containing the app logic, roughly in this order:
   - Music theory helpers (`noteFreq`, scale tables) and the `BIOMES` data
     table (per-biome scale, chords, reverb, noise, and visual-motion
     settings).
   - The Web Audio graph, assembled lazily in `initAudio()` on first
     interaction: pad voices feed `bedBus`, played melody notes feed
     `melodyBus`, both feed `voiceBus` → a brightness lowpass → dry signal +
     convolver reverb → `masterGain` (with a tape-character stage and an
     analyser tap for the reactive visuals along the way).
   - Melody note lifecycle (`startMelodyNote`/`stopMelodyNote`,
     `padHoldStart`/`padHoldEnd` for the pad `.active` highlight, which is
     owned by the lifecycle rather than by each input source so pointer,
     keyboard, the generative performer, MIDI, and the looper all agree on
     what's currently lit), the arpeggiator, MIDI input handling, the
     performance looper, and the generative performer.
   - Recording/export: on-demand recorder taps, WAV encoding, stem export,
     and the seamless loop-export capture path.
   - Presets, permalink hash encode/decode, and state persistence
     (localStorage).
   - UI wiring: every control's event listener, plus `applyStateToUI()`
     which pushes restored state into the DOM and audio graph.
   - The `requestAnimationFrame` canvas loop at the end, rendering a field
     of drifting "motes" whose motion style/color/reactivity depend on the
     current biome and (if enabled) the live audio analyser.

`tools/build-standalone.mjs` and `tools/check.mjs` are small, independent
Node scripts with no dependencies beyond the Node standard library.

## MIDI sketch generator

`compose.py` (plus the pre-generated output in `midi/`) is a separate,
unrelated tool: a Python script that generates fully-arranged multi-track
MIDI sketches (melody/pad/bass/etc.) in the same ambient/biome idiom as
Driftbed, meant as starting points to import into a DAW (Logic, etc.) and
hand-finish. See **`NOTES.md`** for the full writeup — bringing the files
into Logic, patch suggestions per track, and a fix for a common
silent-track import issue.

## How the two halves relate

Driftbed and the MIDI generator are two independent takes on the same
"ambient/biome game music" idea — one is a live, playable instrument; the
other produces static arrangements to finish by hand in a DAW. They don't
import each other's code and don't share a runtime, so treat them as
separate projects that happen to share a folder and a musical language
(scales, chord vocabulary, the biome concept). If you're only working on
one, the other's files are safe to ignore.

## Repository layout

```
pwa/index.html            Driftbed — the only file to edit for app changes
pwa/manifest.json, sw.js  PWA install metadata / service worker
pwa/icon-*.png            App icons
driftbed-standalone.html  GENERATED from pwa/index.html — do not hand-edit
tools/build-standalone.mjs  Regenerates driftbed-standalone.html
tools/check.mjs           Verification gate (must exit 0)
AGENT_NOTES.md            Operating rules for agents editing this repo
compose.py                MIDI sketch generator (Python)
midi/                     Pre-generated .mid output from compose.py
NOTES.md                  Writeup for the MIDI sketches (Logic import, patches)
```

## For agents

Read **`AGENT_NOTES.md`** before making any change in this repository — it
has the hard rules (single-source file, generated-file handling, no git
commands, no network-facing actions) that apply regardless of what's asked.
