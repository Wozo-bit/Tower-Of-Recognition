"""A tiny chiptune sound synthesizer (no extra packages): square, triangle,
saw and noise voices with pitch slides, vibrato and envelopes, mixed and
written as 16-bit mono WAV. Own work.

    python sounds.py               # writes every sound into assets/audio/sfx
    python sounds.py --preview     # writes them here, plus listen.html
"""
import math
import random
import struct
import wave

RATE = 22050


def note(n):
    """Frequency of a note name like "C5", "F#4", "Bb3"."""
    names = {"C": 0, "D": 2, "E": 4, "F": 5, "G": 7, "A": 9, "B": 11}
    k = names[n[0]]
    rest = n[1:]
    if rest and rest[0] in "#b":
        k += 1 if rest[0] == "#" else -1
        rest = rest[1:]
    midi = 12 * (int(rest) + 1) + k
    return 440.0 * 2 ** ((midi - 69) / 12)


def tone(dur, f0, f1=None, wave_="square", vol=0.5, attack=0.004, decay=None, duty=0.5,
         vibrato=0.0, vib_rate=6.0, slide="exp", seed=1):
    """One voice: a pitch from f0 to f1 over `dur` seconds, with an envelope."""
    f1 = f0 if f1 is None else f1
    n = int(dur * RATE)
    out = [0.0] * n
    phase = 0.0
    rng = random.Random(seed)
    noise_val, noise_ctr = 0.0, 0.0
    decay = dur if decay is None else decay
    for i in range(n):
        t = i / RATE
        k = i / max(1, n - 1)
        f = f0 * (f1 / f0) ** k if slide == "exp" and f0 > 0 and f1 > 0 else f0 + (f1 - f0) * k
        if vibrato:
            f *= 1 + vibrato * math.sin(2 * math.pi * vib_rate * t)
        phase = (phase + f / RATE) % 1.0
        if wave_ == "square":
            s = 1.0 if phase < duty else -1.0
        elif wave_ == "triangle":
            s = 4 * abs(phase - 0.5) - 1
        elif wave_ == "saw":
            s = 2 * phase - 1
        elif wave_ == "sine":
            s = math.sin(2 * math.pi * phase)
        else:   # noise: sample-and-hold at the given "pitch"
            noise_ctr += f / RATE
            if noise_ctr >= 1.0 or i == 0:
                noise_ctr %= 1.0
                noise_val = rng.uniform(-1, 1)
            s = noise_val
        env = min(1.0, t / attack) if attack > 0 else 1.0
        env *= max(0.0, 1 - t / decay) ** 1.6 if t < decay else 0.0
        out[i] = s * env * vol
    return out


def seq(*parts, gap=0.0):
    """Plays parts one after another."""
    out = []
    for p in parts:
        out += p + [0.0] * int(gap * RATE)
    return out


def mix(*parts, offsets=None):
    """Plays parts at the same time (or at offsets in seconds)."""
    offsets = offsets or [0.0] * len(parts)
    n = max(int(o * RATE) + len(p) for p, o in zip(parts, offsets))
    out = [0.0] * n
    for p, o in zip(parts, offsets):
        s = int(o * RATE)
        for i, v in enumerate(p):
            out[s + i] += v
    return out


def arp(notes, step, wave_="square", vol=0.35, tail=None, duty=0.5):
    """A quick run of notes."""
    parts = []
    for k, nm in enumerate(notes):
        d = tail if (tail and k == len(notes) - 1) else step
        parts.append(tone(d, note(nm), wave_=wave_, vol=vol, decay=d, duty=duty))
    return seq(*parts)


def save(samples, path, gain=0.9):
    peak = max(1e-6, max(abs(v) for v in samples))
    scale = gain / peak if peak > gain else 1.0
    fade = int(0.004 * RATE)                       # no click at the end
    for i in range(min(fade, len(samples))):
        samples[-1 - i] *= i / fade
    with wave.open(path, "wb") as w:
        w.setnchannels(1)
        w.setsampwidth(2)
        w.setframerate(RATE)
        w.writeframes(b"".join(struct.pack("<h", int(max(-1, min(1, v * scale)) * 32767)) for v in samples))
