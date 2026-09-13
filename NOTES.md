# Big Scary OST — 6 biome tracks (Minecraft-style)

Six MIDI sketches: 2 desert, 2 snow, 2 oak forest. Each is a fully arranged
multi-track MIDI file (melody / pad / bass / occasional bells or light
percussion) — a real starting point, not a loop of samples. Drag into Logic,
assign Software Instruments per the patch suggestions below, and shape from
there (these are deliberately sparse/ambient, in the C418/Lena Raine idiom:
lots of space, soft dynamics, slow harmonic rhythm).

**Each song's core phrase is 16 bars and the file repeats it twice (32 bars)
with fresh melodic variation each pass** (the generator re-walks the scale
each repeat) — the 16-bar point is a clean loop seam if you want a shorter
game loop, or use the full file for more variety before it repeats.

## How to bring into Logic Pro

1. New empty project → `File > Import > MIDI File...` → pick a `.mid` from `midi/`.
2. Logic creates one Software Instrument track per part, named (Piano Lead,
   Pad, Bass, etc.) — each already carries a General MIDI patch guess.
   Replace with the patches below (search by name in the Library).
3. Set each track's reverb send to a **Space Designer / ChromaVerb "Large
   Hall" or "Plate"** aux, fairly wet (20–35%) — that hall wash is a lot of
   what makes this genre read as "Minecraft."
4. Nudge a few notes' velocity/timing by hand if anything feels too grid-perfect —
   the melodies are generated on a strict beat grid; nothing kills this vibe
   like inhuman quantization on the lead line.
5. Low-pass the pads slightly (cut above ~4–6kHz) to keep them out of the
   melody's way and add warmth.

## If a track (e.g. Bass or Glockenspiel) is silent

MIDI import in Logic sometimes loads all parts into one shared, generic
**"GM Device"** fallback synth (each track just pointed at a different
channel/voice of it — 1 Grand Piano, 2 Warm Pad, 3 Acoustic Bs., 4
Glockenspiel, etc., visible in the Library browser's patch list on the left
when a track is selected) instead of giving each track its own real
instrument. That device can render some channels and not others. Two fixes:

1. **Regenerate from the latest files here** — I added an explicit MIDI
   channel-volume message to every part, which fixes silence caused by an
   unset channel defaulting to 0. Re-import the updated `.mid` files.
2. **Better fix — swap in a real instrument per track** (this is what the
   patch suggestions below assume anyway, and sounds far better than the
   generic GM fallback): click a track to select it, then in the Library
   browser on the left pick the real category/patch (e.g. Bass → Acoustic
   Bass, Mallet → Glockenspiel) and double-click it — this replaces that
   track's instrument entirely, independent of the other tracks.

## Your Sound Library — what's installed vs. what to grab

Checked your Logic install directly (Logic Pro menu → Sound Library →
Manage Packs → Instrument Packs). Already installed: Bass, Acoustic/Electronic
Drums, Percussion, Guitar, Acoustic Piano, Clavinet, Electric Piano, basic
Mellotron, Organ, basic Mallets (Glockenspiel/Vibraphone), Synthesizer,
Granular Alchemy, Bass Amp Boutique — this covers nearly everything below.

**Not installed** (no "Installed" tag): **Studio Strings** (real
strings/pizzicato), **Studio Horns** (real brass), **Keyboard Collection**
(extra celesta/harp/tubular-bells/music-box sounds), Vintage Mellotron,
Chinese/Japanese Traditional, Vintage/Modern/Cinematic Synths, Tone
Collection, Visions/Hybrid Textures (Alchemy expansions), Stereo IRs.

To get one: **Logic Pro menu → Sound Library... → Manage Packs**, search the
pack name, click **Get**. These can run several GB each, so I didn't trigger
any downloads myself — your call. Below, anything tagged **(needs pack)**
won't show in your Library browser until you download it; a **(built-in)**
alt is listed alongside so you can start today with nothing to download.

---

## Desert

### 1. `01_desert_dune_drift.mid` — sparse ambient
- **Key/scale:** E Harmonic Minor (E–F#–G–A–B–C–D#) — the raised 7th (D#) is what gives harmonic minor its exotic/desert pull
- **Tempo:** 64 BPM, 4/4
- **Chords (4 bars each):** Em(i, drone) → Cmaj(VI) → Em(i, drone) → Bmaj(V) — that final V→i (B→Em) is the classic harmonic-minor "authentic cadence" snap, built entirely from the raised leading tone
- **Instruments:** soft Grand/Felt Piano (lead), warm Pad synth (Alchemy "Ancient Winds" or similar), very sparse low bass, rare Glockenspiel chimes
- **Vibe:** heat-shimmer stillness, wide open space, night-desert calm with a darker/more exotic pull than before

### 2. `02_desert_sunbaked_trail.mid` — walking exploration
- **Key/scale:** A Harmonic Minor (A–B–C–D–E–F–G#)
- **Tempo:** 92 BPM, 4/4
- **Chords (2 bars each, loops):** Am(i) → Dm(iv) → F(VI) → E(V, major — raised leading tone G#)
- **Instruments:** Nylon Guitar (lead, plucked), soft string Pad, Acoustic Bass, light Shaker
- **Vibe:** trudging across dunes; the major V chord resolving to Am each loop gives it a caravan/maqam-adjacent pull instead of the previous straight natural-minor descent

## Snow

### 3. `03_snow_frostlight.mid` — sparse ambient, icy
- **Key/scale:** C Lydian (the #4 is the "sparkle/crystalline" color)
- **Tempo:** 58 BPM, 4/4
- **Chords (4 bars each):** Cmaj9(drone) → Dmaj(add9) → Cmaj9(drone) → Gmaj(add9)
- **Instruments:** Celesta (lead) **(needs Keyboard Collection)** — built-in alt: Glockenspiel or a soft Sampler/Alchemy bell patch; icy string Pad **(built-in: Alchemy/ES2 pad, since Studio Strings isn't installed)**; soft sub Bass **(built-in)**; rare Tubular Bells chime **(needs Keyboard Collection; built-in alt: Vibraphone)**
- **Vibe:** stark, cold, wide — the "alone at night on a glacier" track

### 4. `04_snow_hearth_and_snowfall.mid` — cozy, melodic
- **Key/scale:** F major
- **Tempo:** 76 BPM, 4/4
- **Chords (2 bars each):** F → Dm7 → Bb → C
- **Instruments:** Music Box (lead) **(built-in — check Mallet/Electric Piano category; if not found, use Glockenspiel)**; warm string Pad **(built-in: Alchemy/ES2 pad)**; Upright Bass **(built-in)**; Glockenspiel sparkle **(built-in)**
- **Vibe:** cabin fireplace, warmer/friendlier than Frostlight — pairs well as its "B-side"

## Oak Forest

### 5. `05_oak_forest_green_canopy.mid` — pastoral walking theme
- **Key/scale:** G major
- **Tempo:** 84 BPM, 4/4
- **Chords (2 bars each):** G → Em7 → C → D
- **Instruments:** Clarinet or Flute (lead) **(needs Studio Horns for real winds; built-in alt: a Woodwind/Flute patch under Synthesizer, or Electric Piano for the lead instead)**; Acoustic Guitar arpeggio **(built-in)**; Acoustic Bass **(built-in)**
- **Vibe:** dappled sunlight, classic "Sweden"-adjacent pastoral overworld theme

### 6. `06_oak_forest_meadow_skip.mid` — playful waltz
- **Key/scale:** D major
- **Tempo:** 116 BPM, **3/4**
- **Chords (2 bars each):** D → A/C# → Bm → G
- **Instruments:** Vibraphone/Xylophone (lead) **(built-in)**; Harp arpeggio **(needs Keyboard Collection or Studio Strings; built-in alt: Nylon Guitar or a plucked Alchemy patch)**; Pizzicato Bass **(needs Studio Strings for true pizzicato; built-in alt: Acoustic Bass with a short/staccato patch)**; light Tambourine **(built-in — GM drum kit)**
- **Vibe:** the lightest/most whimsical of the six — good for a friendly forest clearing or village-adjacent area

---

## Regenerating / tweaking

`compose.py` hand-defines the key, chords, tempo, and instrumentation per
song, and generates the melodic lines with a seeded random walk that snaps to
chord tones on strong beats. To get a different melody for the same harmony,
change that song's `seed=` value and rerun:

```bash
python3 compose.py
```

Everything else (harmony, structure, instrumentation) is deterministic and
won't change unless you edit the song function directly.
