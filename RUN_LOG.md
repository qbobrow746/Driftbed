# Driftbed unattended build run

Orchestrator: Opus 5 (plans + verifies + commits). Builders: Sonnet 5 agents, one at a time.

- **Started:** 2026-09-12 18:28 MDT
- **Stop dispatching at:** ~21:30 MDT (3h), then write the user a report
- **Baseline commit:** `71fb96b` — working app as deployed, before any agent edits

## Rules (also in AGENT_NOTES.md)

- Agents edit `pwa/index.html` only; `driftbed-standalone.html` is generated via `tools/build-standalone.mjs`.
- Agents never run git. Orchestrator commits one commit per verified feature.
- Nothing is pushed, deployed, or published. Shipping is the user's call.
- An agent may not claim success with `node tools/check.mjs` failing.
- Features touch the same file, so units run strictly sequentially.

## Status

| # | Unit | State | Commit |
|---|------|-------|--------|
| P1 | git baseline + .gitignore | done | `71fb96b` |
| P2 | tools/build-standalone.mjs, tools/check.mjs, AGENT_NOTES.md | done, adversarially verified | `b724a81` |
| 1 | Recorder hardening (on-demand taps, non-blocking encode, length cap) | done, browser-verified | `6ae4add` |
| 2 | Presets + shareable permalink (URL hash, localStorage, factory patches) | done, browser-verified | `98ba708` |
| 3 | Scale + root decoupled from biome | done, browser-verified | `cd44675` |
| 4 | Audio-reactive visuals (AnalyserNode) | done, browser-verified | `28c4692` |
| 5 | Generative auto-melodist | done, browser-verified | `2cd3c55` |
| 6 | Web MIDI input | done, browser-verified | `20ca3c5` |
| 7 | Freeze + tape character | done, browser-verified | `65a6f5a` |
| 8 | Three new biomes (rain/marsh, ocean/tide, void/nebula) | dispatched | — |
| 9 | Seamless loop export for game use | queued | — |
| 10 | Mobile + a11y polish pass + README | queued | — |

Stretch if time remains: granular texture layer, pad-ducks-under-melody sidechain, stereo
width control, "song mode" arc across biomes.

## Deferred to the polish unit (10)

- The generative performer (unit 5) plays pads without lighting them up: the `.active` class is
  only added by the pointer/keyboard handlers, so you can't see what it's playing. Same will apply
  to MIDI-input notes. Worth showing pad activity regardless of what triggered the note.
- Permalinks are ~1330 chars because the payload is plain JSON base64'd and includes chord edits
  for all five biomes. Works fine, but could be much shorter if it ever matters.

## Time budget

At 19:54 (86 min in) units P1-P2 and 1-7 were done and committed, with 8 dispatched. If everything
can't finish, prefer 9 (seamless loop export) over 10 (polish) — this folder exists to score a VR
game, so an export that loops cleanly in an engine is worth more than a polish pass. Report honestly
on whatever doesn't land rather than rushing it in unverified.

**Interruption:** at ~20:03 the account hit its session usage limit and the unit-8 agent was killed
mid-run. It had only been reading, so `pwa/index.html` was untouched and the tree stayed green at
`65a6f5a` — per-feature commits meant the failure cost nothing. Work resumed 23:01 with unit 8
re-dispatched from scratch. Total productive time before the outage: ~95 min.

## Notes / findings

- Known pre-existing landmine being fixed in unit 1: three `ScriptProcessorNode`s are created in
  `initAudio()` and run for the whole session even when not recording; long takes accumulate
  unbounded Float32 chunks across 3 stems and then encode 3 WAVs synchronously on the main thread.
- `pwa/index.html` and `driftbed-standalone.html` differed only by title, PWA head block, and the
  service-worker registration script — confirmed by diff before the run started.
- The harness's first cut silently leaked three PWA metas into the standalone: its end marker
  `mobile-web-app-capable` matched `apple-mobile-web-app-capable` as a substring. Fixed by wrapping
  the block in paired `<!-- installable app metadata -->` / `<!-- /... -->` comments. Lesson for
  later units: a "contains" match on an HTML attribute value can collide with a longer name.
- Orchestrator caught a real defect in unit 6 that the agent had self-reported but mis-classified
  as a taste decision: the MIDI anchor octave was copied from the pads (octave 4), but pads span
  one octave while a keyboard spans ~4 either side of middle C and compounds on top of the anchor,
  putting middle C at 1318Hz and an 88-key's top near 10kHz. Fixed to 2. General lesson: when an
  agent reports an odd number as "deliberate", check the arithmetic against a physical reference.
- Testing a device API with no device: stub it. Unit 6 was fully exercised by replacing
  `navigator.requestMIDIAccess` with a fake resolving to a Map holding a fake input object, then
  calling `fakeInput.onmidimessage({data:new Uint8Array([0x90,60,100])})` by hand. Same trick will
  work for any future hardware-dependent feature.
- Canvas/visual verification gotcha: `requestAnimationFrame` is throttled while the Browser pane is
  hidden, so the canvas reads as all-zero pixels and any promise that waits on rAF never settles
  (the JS tool then times out at 45s). Front the tab (`tabs_select`) and take a screenshot to force
  a paint before sampling `getImageData`. Audio keeps running while hidden; only rendering stalls.
- Useful objective test for visual work: sample mean canvas pixel brightness under two conditions
  rather than eyeballing screenshots. Unit 4 measured 10.02 (reactivity on) vs 8.27 (off).
- Verification trap hit during unit 2: assigning `location.href` to a URL whose path matches the
  current page only changes the hash — no reload, so boot never re-runs and a "restored" state is
  really just the state already on screen. Force a real boot (`location.hash = ...` then
  `location.reload()`), and make the test unambiguous by seeding localStorage with a *different*
  state than the permalink encodes.
- `applyStateToUI()` now exists (added in unit 2) as the single place that pushes `state` into every
  control. Any later unit adding a state field must extend it, plus `sanitizeState()` and the
  permalink payload, or the field silently won't survive a preset/permalink load.
- Browser verification recipe that worked well for unit 1, reuse it: serve with
  `cd pwa && python3 -m http.server 8743`, open `http://localhost:8743/index.html`, then drive the
  app by `document.getElementById('...').click()` from the JS console tool. To prove a node isn't
  being created, monkey-patch the constructor before acting (e.g. wrapping
  `AudioContext.prototype.createScriptProcessor` with a counter) — closure-private variables can't
  be read from outside, but constructor calls can be counted.
- The page always logs one console error in the browser pane: the service worker failing to fetch
  (`An unknown error occurred when fetching the script`). It is caught by the app's own `.catch()`,
  is sandbox-specific, and predates this run — not a regression, don't chase it.
- Harness is adversarially verified: deliberately introducing a syntax error, a `getElementById`
  pointing at a nonexistent id, a duplicate id, and a stale standalone each produce a non-zero exit.
  So a green `check.mjs` is meaningful, but it proves nothing about audio behavior — that needs the
  browser pass at milestones.
