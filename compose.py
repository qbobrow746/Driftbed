"""
Big Scary OST generator — 6 Minecraft-style biome tracks.
Hand-composed harmony/key/chords per song; constrained seeded melodic
generator layered on top (chord-tone snapping on strong beats, stepwise
random walk otherwise) for idiomatic sparse/wandering melodic lines.

Run: python3 compose.py
Outputs .mid files into ./midi/
"""

import os
import random
import mido
from mido import Message, MetaMessage, MidiFile, MidiTrack, bpm2tempo

TICKS = 480  # ticks per quarter note
OUT_DIR = os.path.join(os.path.dirname(__file__), "midi")
os.makedirs(OUT_DIR, exist_ok=True)

NOTE_NAMES = ['C', 'C#', 'D', 'D#', 'E', 'F', 'F#', 'G', 'G#', 'A', 'A#', 'B']

def pc(name):
    return NOTE_NAMES.index(name)

def midi_note(pitch_class, octave):
    return 12 * (octave + 1) + pitch_class

SCALES = {
    'major':             [0, 2, 4, 5, 7, 9, 11],
    'minor':             [0, 2, 3, 5, 7, 8, 10],
    'lydian':            [0, 2, 4, 6, 7, 9, 11],
    'phrygian_dominant': [0, 1, 4, 5, 7, 8, 10],
    'harmonic_minor':    [0, 2, 3, 5, 7, 8, 11],
}

def scale_degree_to_midi(root_pc, scale_name, degree, octave_base):
    scale = SCALES[scale_name]
    n = len(scale)
    oct_shift, idx = divmod(degree, n)
    return root_pc + scale[idx] + 12 * (octave_base + oct_shift)

def nearest_scale_degree(root_pc, scale_name, target_midi, octave_base, low, high):
    """find the scale degree (within [low, high]) whose midi pitch is closest to target_midi"""
    best_d, best_dist = 0, 999
    for d in range(low, high + 1):
        m = scale_degree_to_midi(root_pc, scale_name, d, octave_base)
        dist = abs(m - target_midi)
        if dist < best_dist:
            best_dist, best_d = dist, d
    return best_d


# ---------------------------------------------------------------------------
# Track writers
# ---------------------------------------------------------------------------

def add_note_event(track, channel, notes, dur_ticks, vel, gate, lead_delta):
    """notes: list[int] (chord) or None (rest). Returns nothing; writes on/off."""
    on_len = max(1, int(dur_ticks * gate))
    off_len = dur_ticks - on_len
    if notes is None:
        return lead_delta + dur_ticks
    for i, p in enumerate(notes):
        track.append(Message('note_on', note=p, velocity=vel, channel=channel,
                              time=(lead_delta if i == 0 else 0)))
    for i, p in enumerate(notes):
        track.append(Message('note_off', note=p, velocity=0, channel=channel,
                              time=(on_len if i == 0 else 0)))
    return off_len


def write_voice(mid, channel, program, events, name):
    """events: list of dicts {notes: [int]|None, dur: beats(float), vel:int, gate:float}"""
    track = MidiTrack()
    track.append(MetaMessage('track_name', name=name, time=0))
    # Explicit channel volume/pan — some GM playback devices (e.g. Logic's
    # built-in "GM Device" fallback used on raw MIDI import) default an
    # unset channel to silence rather than the GM-spec default of 100.
    track.append(Message('control_change', control=7, value=100, channel=channel, time=0))
    track.append(Message('control_change', control=10, value=64, channel=channel, time=0))
    if program is not None:
        track.append(Message('program_change', program=program, channel=channel, time=0))
    mid.tracks.append(track)
    pending_delta = 0
    for ev in events:
        dur_ticks = round(ev['dur'] * TICKS)
        pending_delta = add_note_event(track, channel, ev['notes'], dur_ticks,
                                        ev.get('vel', 70), ev.get('gate', 0.85), pending_delta)


# ---------------------------------------------------------------------------
# Generative melody (seeded, chord-aware)
# ---------------------------------------------------------------------------

def generate_melody(root_pc, scale_name, octave_base, chord_beats, total_beats,
                     seed, deg_low=-2, deg_high=9, rest_prob=0.32,
                     durations=(0.5, 1.0, 1.0, 1.0, 2.0), vel_range=(58, 78),
                     gate=0.92, max_step=2, phrase_bars=4, beats_per_bar=4):
    """
    chord_beats: list of (chord_root_degree, start_beat, end_beat) — used only to
    bias strong-beat notes toward the chord root/fifth/third for that window.
    """
    rng = random.Random(seed)
    events = []
    t = 0.0
    cur_degree = 0
    def chord_root_at(beat):
        for root_deg, s, e in chord_beats:
            if s <= beat < e:
                return root_deg
        return chord_beats[-1][0]

    while t < total_beats:
        dur = rng.choice(durations)
        dur = min(dur, total_beats - t)
        on_strong_beat = (t % beats_per_bar) < 1e-6
        if rng.random() < rest_prob and not on_strong_beat:
            events.append({'notes': None, 'dur': dur})
            t += dur
            continue
        if on_strong_beat and rng.random() < 0.55:
            root_deg = chord_root_at(t)
            choice = rng.choice([0, 2, 4])  # root, third, fifth (scale-step approx)
            cur_degree = max(deg_low, min(deg_high, root_deg + choice))
        else:
            step = rng.choice(range(-max_step, max_step + 1))
            cur_degree = max(deg_low, min(deg_high, cur_degree + step))
        midi_p = scale_degree_to_midi(root_pc, scale_name, cur_degree, octave_base)
        vel = rng.randint(*vel_range)
        events.append({'notes': [midi_p], 'dur': dur, 'vel': vel, 'gate': gate})
        t += dur
    return events


def generate_sparse_bells(root_pc, scale_name, octave_base, chord_beats, total_beats,
                           seed, density=0.15, beats_per_bar=4, grid=1.0,
                           deg_choices=(0, 2, 4, 7)):
    rng = random.Random(seed)
    events = []
    t = 0.0
    def chord_root_at(beat):
        for root_deg, s, e in chord_beats:
            if s <= beat < e:
                return root_deg
        return chord_beats[-1][0]
    while t < total_beats:
        dur = grid
        dur = min(dur, total_beats - t)
        if rng.random() < density:
            root_deg = chord_root_at(t)
            deg = root_deg + rng.choice(deg_choices)
            midi_p = scale_degree_to_midi(root_pc, scale_name, deg, octave_base)
            events.append({'notes': [midi_p], 'dur': dur, 'vel': rng.randint(50, 66), 'gate': 0.9})
        else:
            events.append({'notes': None, 'dur': dur})
        t += dur
    return events


def expand_chords(chord_list, bars_each, beats_per_bar=4, repeats=1):
    """chord_list: list of list[int] (explicit midi notes). Returns pad events + chord_beats map."""
    events = []
    chord_beats = []
    t = 0.0
    for _ in range(repeats):
        for notes in chord_list:
            dur = bars_each * beats_per_bar
            events.append({'notes': notes, 'dur': dur, 'vel': 46, 'gate': 1.0})
            root_deg = 0  # placeholder, real degree bias supplied separately per song
            chord_beats.append((t, t + dur))
            t += dur
    return events, t


def bass_from_chords(chord_roots_pc, octave_base, bars_each, beats_per_bar=4, repeats=1,
                      pulse=1, vel=52, gate=0.85):
    """chord_roots_pc: list of pitch classes (root of each chord)."""
    events = []
    for _ in range(repeats):
        for root in chord_roots_pc:
            bar_beats = bars_each * beats_per_bar
            n_pulses = max(1, int(bar_beats / pulse))
            dur = bar_beats / n_pulses
            for i in range(n_pulses):
                if i == 0:
                    events.append({'notes': [midi_note(root, octave_base)], 'dur': dur,
                                    'vel': vel, 'gate': gate})
                else:
                    events.append({'notes': None, 'dur': dur})
    return events


def light_percussion(total_beats, seed, beats_per_bar=4, note=70, density=0.5, vel=(30, 46)):
    """Soft shaker-ish pattern on channel 9 (GM drums), eighth-note grid, sparse."""
    rng = random.Random(seed)
    events = []
    t = 0.0
    grid = 0.5
    while t < total_beats:
        if rng.random() < density:
            events.append({'notes': [note], 'dur': grid, 'vel': rng.randint(*vel), 'gate': 0.5})
        else:
            events.append({'notes': None, 'dur': grid})
        t += grid
    return events


def build_song(filename, bpm, time_sig, beats_per_bar, tracks_spec):
    """tracks_spec: list of (channel, program_or_None, events, name)"""
    mid = MidiFile(ticks_per_beat=TICKS)
    tempo_track = MidiTrack()
    tempo_track.append(MetaMessage('set_tempo', tempo=bpm2tempo(bpm), time=0))
    tempo_track.append(MetaMessage('time_signature', numerator=time_sig[0],
                                    denominator=time_sig[1], time=0))
    mid.tracks.append(tempo_track)
    for channel, program, events, name in tracks_spec:
        write_voice(mid, channel, program, events, name)
    path = os.path.join(OUT_DIR, filename)
    mid.save(path)
    print(f"wrote {path}  ({mid.length:.1f}s)")


# ===========================================================================
# SONG 1 — Desert: "Dune Drift"  (sparse ambient, E harmonic minor)
# ===========================================================================
def song_dune_drift():
    root = pc('E'); scale = 'harmonic_minor'
    bpb = 4
    pad_chords = [
        [midi_note(pc('E'), 3), midi_note(pc('B'), 3)],
        [midi_note(pc('C'), 4), midi_note(pc('E'), 4), midi_note(pc('G'), 4)],
        [midi_note(pc('E'), 3), midi_note(pc('B'), 3)],
        [midi_note(pc('B'), 3), midi_note(pc('D#'), 4), midi_note(pc('F#'), 4)],
    ]
    bars_each = 4
    pad_events, total_beats = expand_chords(pad_chords, bars_each, bpb, repeats=2)
    chord_beats = []
    t = 0
    degree_roots = [0, 5, 0, 4]  # Em(i, deg0), C(VI, deg5), Em(i, deg0), B(V, deg4) in E harmonic minor
    for _ in range(2):
        for rd in degree_roots:
            chord_beats.append((rd, t, t + bars_each * bpb))
            t += bars_each * bpb

    bass = bass_from_chords([pc('E'), pc('C'), pc('E'), pc('B')], 2, bars_each, bpb,
                             repeats=2, pulse=4, vel=44, gate=0.95)
    melody = generate_melody(root, scale, 4, chord_beats, total_beats, seed=42,
                              deg_low=-2, deg_high=9, rest_prob=0.38,
                              durations=(0.5, 1, 1, 1.5, 2), vel_range=(52, 72), gate=0.9)
    bells = generate_sparse_bells(root, scale, 6, chord_beats, total_beats, seed=142,
                                   density=0.12)
    build_song('01_desert_dune_drift.mid', 64, (4, 4), bpb, [
        (0, 0, melody, 'Piano Lead (soft)'),
        (1, 89, pad_events, 'Pad Drone (warm)'),
        (2, 32, bass, 'Bass (sparse)'),
        (3, 9, bells, 'Glockenspiel (sparkle)'),
    ])


# ===========================================================================
# SONG 2 — Desert: "Sunbaked Trail" (walking pace, A harmonic minor)
# ===========================================================================
def song_sunbaked_trail():
    root = pc('A'); scale = 'harmonic_minor'
    bpb = 4
    pad_chords = [
        [midi_note(pc('A'), 3), midi_note(pc('C'), 4), midi_note(pc('E'), 4)],
        [midi_note(pc('D'), 3), midi_note(pc('F'), 3), midi_note(pc('A'), 3)],
        [midi_note(pc('F'), 3), midi_note(pc('A'), 3), midi_note(pc('C'), 4)],
        [midi_note(pc('E'), 3), midi_note(pc('G#'), 3), midi_note(pc('B'), 3)],
    ]
    bars_each = 2
    pad_events, total_beats = expand_chords(pad_chords, bars_each, bpb, repeats=4)
    chord_beats = []
    t = 0
    degree_roots = [0, 3, 5, 4]  # Am(i, deg0), Dm(iv, deg3), F(VI, deg5), E(V, deg4) in A harmonic minor
    for _ in range(4):
        for rd in degree_roots:
            chord_beats.append((rd, t, t + bars_each * bpb))
            t += bars_each * bpb

    bass = bass_from_chords([pc('A'), pc('D'), pc('F'), pc('E')], 2, bars_each, bpb,
                             repeats=4, pulse=2, vel=56, gate=0.9)
    melody = generate_melody(root, scale, 4, chord_beats, total_beats, seed=7,
                              deg_low=-2, deg_high=9, rest_prob=0.22,
                              durations=(0.5, 0.5, 1, 1, 1), vel_range=(60, 82), gate=0.92)
    perc = light_percussion(total_beats, seed=707, note=70, density=0.35)
    build_song('02_desert_sunbaked_trail.mid', 92, (4, 4), bpb, [
        (0, 24, melody, 'Nylon Guitar Lead'),
        (1, 50, pad_events, 'Pad (soft strings)'),
        (2, 32, bass, 'Acoustic Bass'),
        (9, None, perc, 'Shaker (light)'),
    ])


# ===========================================================================
# SONG 3 — Snow: "Frostlight" (sparse ambient, C lydian)
# ===========================================================================
def song_frostlight():
    root = pc('C'); scale = 'lydian'
    bpb = 4
    pad_chords = [
        [midi_note(pc('C'), 3), midi_note(pc('E'), 3), midi_note(pc('B'), 3), midi_note(pc('D'), 4)],
        [midi_note(pc('D'), 3), midi_note(pc('F#'), 3), midi_note(pc('A'), 3), midi_note(pc('C'), 4)],
        [midi_note(pc('C'), 3), midi_note(pc('E'), 3), midi_note(pc('B'), 3), midi_note(pc('D'), 4)],
        [midi_note(pc('G'), 3), midi_note(pc('B'), 3), midi_note(pc('D'), 4)],
    ]
    bars_each = 4
    pad_events, total_beats = expand_chords(pad_chords, bars_each, bpb, repeats=2)
    chord_beats = []
    t = 0
    degree_roots = [0, 1, 0, 4]  # C(0) D(deg1) C(0) G(deg4) in C lydian
    for _ in range(2):
        for rd in degree_roots:
            chord_beats.append((rd, t, t + bars_each * bpb))
            t += bars_each * bpb

    bass = bass_from_chords([pc('C'), pc('D'), pc('C'), pc('G')], 2, bars_each, bpb,
                             repeats=2, pulse=4, vel=40, gate=0.97)
    melody = generate_melody(root, scale, 5, chord_beats, total_beats, seed=18,
                              deg_low=-2, deg_high=9, rest_prob=0.42,
                              durations=(0.5, 1, 1, 1.5, 2), vel_range=(48, 68), gate=0.88)
    bells = generate_sparse_bells(root, scale, 6, chord_beats, total_beats, seed=118,
                                   density=0.18)
    build_song('03_snow_frostlight.mid', 58, (4, 4), bpb, [
        (0, 8, melody, 'Celesta Lead'),
        (1, 89, pad_events, 'Pad (icy strings)'),
        (2, 32, bass, 'Sub Bass (soft)'),
        (3, 14, bells, 'Tubular Bells (rare chime)'),
    ])


# ===========================================================================
# SONG 4 — Snow: "Hearth & Snowfall" (cozy, melodic, F major)
# ===========================================================================
def song_hearth_snowfall():
    root = pc('F'); scale = 'major'
    bpb = 4
    pad_chords = [
        [midi_note(pc('F'), 3), midi_note(pc('A'), 3), midi_note(pc('C'), 4)],
        [midi_note(pc('D'), 3), midi_note(pc('F'), 3), midi_note(pc('A'), 3), midi_note(pc('C'), 4)],
        [midi_note(pc('A#'), 3), midi_note(pc('D'), 4), midi_note(pc('F'), 4), midi_note(pc('A'), 4)],
        [midi_note(pc('C'), 4), midi_note(pc('E'), 4), midi_note(pc('G'), 4)],
    ]
    bars_each = 2
    pad_events, total_beats = expand_chords(pad_chords, bars_each, bpb, repeats=4)
    chord_beats = []
    t = 0
    degree_roots = [0, 5, 3, 4]  # F(0) Dm(deg5) Bb(deg3) C(deg4) in F major
    for _ in range(4):
        for rd in degree_roots:
            chord_beats.append((rd, t, t + bars_each * bpb))
            t += bars_each * bpb

    bass = bass_from_chords([pc('F'), pc('D'), pc('A#'), pc('C')], 2, bars_each, bpb,
                             repeats=4, pulse=2, vel=48, gate=0.9)
    melody = generate_melody(root, scale, 5, chord_beats, total_beats, seed=99,
                              deg_low=-2, deg_high=9, rest_prob=0.3,
                              durations=(0.5, 1, 1, 1, 2), vel_range=(56, 76), gate=0.9)
    bells = generate_sparse_bells(root, scale, 6, chord_beats, total_beats, seed=199,
                                   density=0.16)
    build_song('04_snow_hearth_and_snowfall.mid', 76, (4, 4), bpb, [
        (0, 10, melody, 'Music Box Lead'),
        (1, 89, pad_events, 'Pad (warm strings)'),
        (2, 32, bass, 'Upright Bass'),
        (3, 9, bells, 'Glockenspiel (sparkle)'),
    ])


# ===========================================================================
# SONG 5 — Oak Forest: "Green Canopy" (pastoral, walking, G major)
# ===========================================================================
def song_green_canopy():
    root = pc('G'); scale = 'major'
    bpb = 4
    pad_chords = [
        [midi_note(pc('G'), 3), midi_note(pc('B'), 3), midi_note(pc('D'), 4)],
        [midi_note(pc('E'), 3), midi_note(pc('G'), 3), midi_note(pc('B'), 3), midi_note(pc('D'), 4)],
        [midi_note(pc('C'), 3), midi_note(pc('E'), 3), midi_note(pc('G'), 3)],
        [midi_note(pc('D'), 3), midi_note(pc('F#'), 3), midi_note(pc('A'), 3)],
    ]
    bars_each = 2
    pad_events, total_beats = expand_chords(pad_chords, bars_each, bpb, repeats=4)
    chord_beats = []
    t = 0
    degree_roots = [0, 5, 3, 4]  # G(0) Em(deg5) C(deg3) D(deg4) in G major
    for _ in range(4):
        for rd in degree_roots:
            chord_beats.append((rd, t, t + bars_each * bpb))
            t += bars_each * bpb

    bass = bass_from_chords([pc('G'), pc('E'), pc('C'), pc('D')], 2, bars_each, bpb,
                             repeats=4, pulse=1, vel=50, gate=0.85)
    melody = generate_melody(root, scale, 4, chord_beats, total_beats, seed=55,
                              deg_low=-2, deg_high=9, rest_prob=0.24,
                              durations=(0.5, 0.5, 1, 1, 1), vel_range=(60, 80), gate=0.92)
    build_song('05_oak_forest_green_canopy.mid', 84, (4, 4), bpb, [
        (0, 71, melody, 'Clarinet Lead'),
        (1, 25, pad_events, 'Acoustic Guitar Arp / Pad'),
        (2, 32, bass, 'Acoustic Bass'),
    ])


# ===========================================================================
# SONG 6 — Oak Forest: "Meadow Skip" (playful waltz, 3/4, D major)
# ===========================================================================
def song_meadow_skip():
    root = pc('D'); scale = 'major'
    bpb = 3
    pad_chords = [
        [midi_note(pc('D'), 4), midi_note(pc('F#'), 4), midi_note(pc('A'), 4)],
        [midi_note(pc('C#'), 4), midi_note(pc('E'), 4), midi_note(pc('A'), 4)],
        [midi_note(pc('B'), 3), midi_note(pc('D'), 4), midi_note(pc('F#'), 4)],
        [midi_note(pc('G'), 3), midi_note(pc('B'), 3), midi_note(pc('D'), 4)],
    ]
    bars_each = 2
    pad_events, total_beats = expand_chords(pad_chords, bars_each, bpb, repeats=4)
    chord_beats = []
    t = 0
    degree_roots = [0, 5, 6, 3]  # D(0) A/C#(deg5~A) Bm(deg6) G(deg3) in D major
    for _ in range(4):
        for rd in degree_roots:
            chord_beats.append((rd, t, t + bars_each * bpb))
            t += bars_each * bpb

    bass = bass_from_chords([pc('D'), pc('C#'), pc('B'), pc('G')], 3, bars_each, bpb,
                             repeats=4, pulse=1, vel=48, gate=0.85)
    melody = generate_melody(root, scale, 5, chord_beats, total_beats, seed=63,
                              deg_low=-2, deg_high=9, rest_prob=0.2,
                              durations=(0.5, 0.5, 1, 1), vel_range=(62, 84), gate=0.9,
                              beats_per_bar=bpb)
    perc = light_percussion(total_beats, seed=606, note=54, density=0.3)
    build_song('06_oak_forest_meadow_skip.mid', 116, (3, 4), bpb, [
        (0, 12, melody, 'Vibraphone/Xylophone Lead'),
        (1, 46, pad_events, 'Harp Arpeggio / Pad'),
        (2, 32, bass, 'Pizzicato Bass'),
        (9, None, perc, 'Tambourine (light)'),
    ])


if __name__ == '__main__':
    song_dune_drift()
    song_sunbaked_trail()
    song_frostlight()
    song_hearth_snowfall()
    song_green_canopy()
    song_meadow_skip()
    print("done.")
