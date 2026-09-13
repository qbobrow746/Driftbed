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
| P2 | tools/build-standalone.mjs, tools/check.mjs, AGENT_NOTES.md | dispatched | — |
| 1 | Recorder hardening (on-demand taps, non-blocking encode, length cap) | queued | — |
| 2 | Presets + shareable permalink (URL hash, localStorage, factory patches) | queued | — |
| 3 | Scale + root decoupled from biome | queued | — |
| 4 | Audio-reactive visuals (AnalyserNode) | queued | — |
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
