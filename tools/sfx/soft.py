"""Soft modern sound building blocks (Hayden 2026-11-09: "soft modern UI"):
rounded sine and FM-bell tones, filtered-noise whooshes and impacts, and a
light room reverb. Builds on chip.py's mixing and WAV writing. Own work.
"""
import math
import random
from chip import RATE, mix, note, seq


def env(n, attack, decay, curve=2.2):
    """Smooth attack, then an exponential-ish fall over `decay` seconds."""
    out = []
    a = max(1, int(attack * RATE))
    for i in range(n):
        t = i / RATE
        rise = 0.5 - 0.5 * math.cos(math.pi * min(1.0, i / a))
        fall = max(0.0, 1 - t / decay) ** curve if decay > 0 else 1.0
        out.append(rise * fall)
    return out


def bell(f, dur=0.6, vol=0.4, ratio=2.0, index=1.6, attack=0.003, bright=1.0):
    """An FM bell: a sine carrier with a decaying sine modulator (glassy chime)."""
    n = int(dur * RATE)
    e = env(n, attack, dur)
    out = []
    for i in range(n):
        t = i / RATE
        mod_depth = index * bright * math.exp(-t * 7)
        s = math.sin(2 * math.pi * f * t + mod_depth * math.sin(2 * math.pi * f * ratio * t))
        out.append(s * e[i] * vol)
    return out


def pad(f, dur=0.5, vol=0.3, attack=0.02, detune=0.004, harmonics=(1.0, 0.25, 0.08)):
    """A warm sine tone with a little detune and soft harmonics."""
    n = int(dur * RATE)
    e = env(n, attack, dur, 1.6)
    out = []
    for i in range(n):
        t = i / RATE
        s = 0.0
        for h, amp in enumerate(harmonics, start=1):
            s += amp * (math.sin(2 * math.pi * f * h * t) + math.sin(2 * math.pi * f * h * (1 + detune) * t)) * 0.5
        out.append(s * e[i] * vol)
    return out


def glide(f0, f1, dur, vol=0.35, attack=0.005, curve=2.0):
    """A sine sliding from f0 to f1 (thumps, swells, drops)."""
    n = int(dur * RATE)
    e = env(n, attack, dur, curve)
    out, phase = [], 0.0
    for i in range(n):
        k = i / max(1, n - 1)
        f = f0 * (f1 / f0) ** k
        phase += f / RATE
        out.append(math.sin(2 * math.pi * phase) * e[i] * vol)
    return out


def air(dur, cutoff0=800.0, cutoff1=4000.0, vol=0.3, attack=0.01, curve=1.8, seed=3, band=False):
    """Filtered noise with a moving cutoff: whooshes, swishes, soft impacts."""
    rng = random.Random(seed)
    n = int(dur * RATE)
    e = env(n, attack, dur, curve)
    out, lp, lp2 = [], 0.0, 0.0
    for i in range(n):
        k = i / max(1, n - 1)
        fc = cutoff0 * (cutoff1 / cutoff0) ** k
        a = 1 - math.exp(-2 * math.pi * fc / RATE)
        x = rng.uniform(-1, 1)
        lp += a * (x - lp)
        lp2 += a * (lp - lp2)
        s = (lp - lp2) * 2.2 if band else lp2
        out.append(s * e[i] * vol)
    return out


def chord(names, dur=0.7, vol=0.22, spread=0.0, fn=None):
    """Several bells at once (or rolled, `spread` seconds apart)."""
    fn = fn or (lambda f: bell(f, dur, vol))
    return mix(*[fn(note(nm)) for nm in names], offsets=[k * spread for k in range(len(names))])


def reverb(x, room=0.32, damp=0.4, tail=0.5):
    """A light, airy room: a few damped feedback delays mixed back in."""
    delays = [int(RATE * d) for d in (0.0297, 0.0371, 0.0411, 0.0437)]
    out = x + [0.0] * int(tail * RATE)
    wet = [0.0] * len(out)
    for d in delays:
        buf = [0.0] * len(out)
        lp = 0.0
        for i in range(len(out)):
            src = out[i] if i < len(x) else 0.0
            fb = buf[i - d] if i >= d else 0.0
            lp = lp + (1 - damp) * (fb - lp)
            buf[i] = src + lp * 0.62
            wet[i] += buf[i] * 0.25
    return [out[i] + wet[i] * room for i in range(len(out))]


def sweeten(x, room=0.25, tail=0.4):
    return reverb(x, room=room, tail=tail)
