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
| 4 | Audio-reactive visuals (AnalyserNode) | dispatched | — |
| 5 | Generative auto-melodist | queued | — |
| 6 | Web MIDI input | queued | — |
| 7 | Freeze + tape character | queued | — |
| 8 | Three new biomes (rain/marsh, ocean/tide, void/nebula) | queued | — |
| 9 | Seamless loop export for game use | queued | — |
| 10 | Mobile + a11y polish pass + README | queued | — |

Stretch if time remains: granular texture layer, pad-ducks-under-melody sidechain, stereo
width control, "song mode" arc across biomes.

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
