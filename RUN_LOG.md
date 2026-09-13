# Driftbed build runs

Orchestrator: Opus 5 (plans + verifies + commits). Builders: Sonnet 5 agents, one at a time.

## Rules (also in AGENT_NOTES.md)

- Agents edit `pwa/index.html` only; `driftbed-standalone.html` is generated via `tools/build-standalone.mjs`.
- Agents never run git. Orchestrator commits one commit per verified unit.
- Nothing is pushed, deployed, or published. Shipping is the user's call.
- An agent may not claim success with `node tools/check.mjs` failing.
- Units touch the same file, so they run strictly sequentially.

---

# Run 2 — look and feel (90 minutes)

- **Started:** 2026-09-13 12:08 MDT · **stop dispatching:** ~13:38
- **Baseline:** `2105141`

Purely form, clarity and feel. No new features — if a unit starts adding capability it has drifted.

Measured before the run, at 1280x900: panel is 560x1082, so it **scrolls on a full desktop** while
**720px of horizontal space is empty**, holding **89 controls** in one flat column at uniform
visual weight.

| # | Unit | State | Commit |
|---|------|-------|--------|
| 1 | Responsive two-column layout on wide viewports | dispatched | — |
| 2 | Visual hierarchy + craft pass (type, spacing, states, transitions) | queued | — |
| 3 | First-run guidance + honest labels (Presence = volume) | queued | — |
| 4 | The canvas field: depth, per-biome signature, grading | queued | — |
| 5 | Stretch: now-playing state + micro-interactions | queued | — |

## Notes for this run

- The six popovers are `position:absolute; left:100%` anchored to `.totems-row` / `.melody-block`
  (both `position:relative`), with a `@media (max-width:900px)` fallback to a fixed bottom sheet.
  A two-column layout can push them across or off screen — the likeliest breakage in unit 1.
- Verify visually at 1280x900, 768 and 375. Front the Browser pane before sampling the canvas;
  `requestAnimationFrame` is throttled while it's hidden.
- Real labelling failure confirmed by the user this session: Presence is the master volume and
  nothing said so, which is why the instrument seemed silent and then too quiet.

---

# Run 1 — features (complete)

All 10 units plus prerequisites landed. `pwa/index.html` went 2,174 → ~3,990 lines. Commits:
`71fb96b` baseline · `b724a81` harness · `6ae4add` recording · `98ba708` presets/permalinks ·
`cd44675` key+scale · `28c4692` audio-reactive visuals · `2cd3c55` generative melodist ·
`20ca3c5` Web MIDI · `65a6f5a` freeze+tape · `90211fe` three new biomes · `8fe9229` loop export ·
`6ba5744` polish+README.

Follow-up fixes after the user tried it on real hardware:
- `be4dccd` — played notes were inaudible unless Play was pressed (masterGain parked at 0.0001).
- `4a8a2a1` — raised levels ~11dB on played notes and added a safety limiter.
- `1f50f82` — MIDI keyboard level slider, independent of Presence.
- `2105141` — **service worker served a permanently frozen app**: same-origin requests were
  cache-first against a cache name that never changed, so a returning visitor kept the
  `index.html` from their first visit and no update could ever reach them. Now network-first for
  the document. This is why the user couldn't see new features until a hard reload.

## Lessons worth keeping

- Verify the agent's claim, not its summary. Real defects caught by orchestrator review: a build
  script whose end-marker matched a longer attribute name as a substring; a MIDI anchor octave
  putting middle C at 1318Hz; freeze that left the blended biome advancing; a pad that could sit
  lit but silent; a phone-layout claim whose arithmetic forgot the panel padding.
- Test device APIs by stubbing them (`navigator.requestMIDIAccess` → fake input, then dispatch
  real MIDI byte arrays).
- Measure audio objectively by patching constructors (`createGain`, `createDynamicsCompressor`)
  to capture nodes, then attaching your own AnalyserNode and reading `getFloatTimeDomainData`.
- `location.href` to the same path only changes the hash — no reload, so boot never re-runs.
- Per-unit commits meant an agent dying mid-run (session limit) cost nothing.
