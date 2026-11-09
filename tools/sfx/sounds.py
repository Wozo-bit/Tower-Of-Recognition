"""The game's core sound effects (Hayden 2026-11-09: "soft modern UI": rounded
chimes, glassy clicks, whooshes and thumps, not beeps). Own work.

    python sounds.py               # writes every sound into assets/audio/sfx
    python sounds.py --preview     # writes them into the current folder instead

Each entry: file name (assets/audio/sfx/<name>.wav) -> (what it's for, how to make it).
"""
import os
import random
import sys
from chip import mix, note, save, seq
from soft import air, bell, chord, glide, pad, sweeten

OUT = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "..", "assets", "audio", "sfx")


def thump(f0=140, f1=55, dur=0.18, vol=0.6):
    return glide(f0, f1, dur, vol, attack=0.002, curve=2.6)


def impact(body=0.6, bright=2200, dur=0.14):
    """A soft hit: a low thump plus a short, filtered smack."""
    return mix(thump(170, 60, dur + 0.05, body), air(dur, bright, 300, 0.55, attack=0.001, curve=3.0, seed=7))


def static(dur, vol=0.5, seed=11, crush=6):
    """Radio static: bit-crushed, sample-held noise that cuts in and out."""
    rng = random.Random(seed)
    n = int(dur * 22050)
    out, held, hold, gate, gate_left = [], 0.0, 0, 1.0, 0
    for i in range(n):
        if hold <= 0:                                   # sample-and-hold: grainy, lo-fi
            held = rng.uniform(-1, 1)
            hold = rng.choice((1, 1, 2, 3, crush))
        hold -= 1
        if gate_left <= 0:                              # chop it into bursts
            gate = rng.choice((1.0, 1.0, 0.6, 0.0))
            gate_left = rng.randint(80, 600)
        gate_left -= 1
        q = round(held * 6) / 6                         # bit-crush
        fade = min(1.0, i / 150) * min(1.0, (n - i) / 400)
        out.append(q * gate * fade * vol)
    return out


def crack(dur=0.03, vol=0.6):
    """A sharp, bright crack: the very start of a big hit."""
    return air(dur, 9000, 4000, vol, attack=0.0005, curve=4.0, seed=19, band=True)


SOUNDS = {
    # --- Interface ---
    "ui_click": ("Every button: a soft glassy tick",
                 lambda: mix(bell(note("E6"), 0.08, 0.22, ratio=3.5, index=0.8), air(0.03, 6000, 3000, 0.12, attack=0.001))),
    "system": ("A System notice: a two-note glass chime",
               lambda: sweeten(seq(bell(note("E6"), 0.12, 0.3), bell(note("B6"), 0.5, 0.3)), 0.35, 0.6)),
    "notice": ("A System line in dialogue: one soft chime", lambda: sweeten(bell(note("A6"), 0.35, 0.22, index=1.0), 0.3)),
    "system_glitch": ("The System slipping: a burst of static with the chime breaking up inside it",
                      lambda: mix(static(0.55, 0.55),
                                  seq(bell(note("A6"), 0.05, 0.22), static(0.04, 0.0), bell(note("A6") * 0.94, 0.04, 0.18),
                                      static(0.06, 0.0), glide(note("A6"), note("A5"), 0.18, 0.12)),
                                  static(0.12, 0.35, seed=29, crush=12), offsets=[0, 0.05, 0.45])),
    "system_tip": ("A tutorial tip window: a rising three-note chime",
                   lambda: sweeten(chord(["C6", "E6", "G6"], 0.6, 0.18, spread=0.06), 0.35, 0.6)),
    "talk": ("Starting a conversation: a soft pop", lambda: mix(glide(500, 820, 0.07, 0.3), air(0.04, 3000, 1200, 0.08))),
    # --- Battle ---
    "encounter": ("A fight starts: a whoosh into a low swell",
                  lambda: sweeten(mix(air(0.35, 400, 6000, 0.4, attack=0.15, curve=1.2), pad(note("A2"), 0.6, 0.35, attack=0.08),
                                      bell(note("E5"), 0.5, 0.15), offsets=[0, 0.2, 0.3]), 0.3)),
    "encounter_boss": ("A boss fight starts: a deep boom and a dark swell",
                       lambda: sweeten(mix(thump(90, 35, 0.9, 0.8), air(0.7, 200, 1200, 0.35, attack=0.02),
                                           pad(note("D2"), 1.2, 0.3, attack=0.2), pad(note("Ab2"), 1.2, 0.18, attack=0.3),
                                           offsets=[0, 0, 0.1, 0.25]), 0.4, 0.8)),
    "encounter_flash": ("The floor flashes before a fight: a quick rising swish",
                        lambda: air(0.22, 600, 9000, 0.35, attack=0.12, curve=1.0, band=True)),
    "hit": ("A normal hit: a soft thud", lambda: impact()),
    "crit": ("A critical hit: a sharp crack, a heavy boom and a metallic ring",
             lambda: sweeten(mix(crack(0.035, 0.7), thump(130, 38, 0.4, 0.85), air(0.2, 3000, 250, 0.5, attack=0.001, curve=2.4, seed=5),
                                 bell(note("D7"), 0.45, 0.14, ratio=3.47, index=3.0), offsets=[0, 0.004, 0.004, 0.01]), 0.3, 0.5)),
    "weak": ("Hitting a weakness: a light thud and a rising three-note chime",
             lambda: sweeten(mix(impact(0.45, 2000, 0.1),
                                 seq(bell(note("E5"), 0.07, 0.17, index=1.0), bell(note("B5"), 0.07, 0.17, index=1.0),
                                     bell(note("E6"), 0.35, 0.18, index=1.0)), offsets=[0, 0.05]), 0.3)),
    "stagger": ("An enemy is staggered: a thud and a wobbling ring",
                lambda: sweeten(mix(impact(0.7, 2400, 0.16),
                                    mix(bell(note("G5"), 0.5, 0.15), bell(note("G5") * 1.02, 0.5, 0.15)), offsets=[0, 0.05]), 0.3)),
    "resist": ("A resisted hit: a dull knock", lambda: mix(thump(220, 160, 0.12, 0.45), air(0.06, 900, 400, 0.2))),
    "miss": ("An attack misses: a quick swish", lambda: air(0.18, 2500, 700, 0.3, attack=0.03, curve=1.4, band=True)),
    "heal": ("Healing: a warm rising shimmer",
             lambda: sweeten(mix(chord(["C5", "E5", "G5", "C6"], 0.7, 0.14, spread=0.05,
                                       fn=lambda f: bell(f, 0.7, 0.14, ratio=1.0, index=0.6)),
                                 air(0.5, 3000, 8000, 0.05, attack=0.2)), 0.4, 0.7)),
    "status": ("A status effect lands: a low wavering tone",
               lambda: sweeten(mix(pad(note("C4"), 0.4, 0.22, attack=0.03), pad(note("C#4"), 0.4, 0.14, attack=0.05)), 0.3)),
    "defend": ("Defending: a soft shield hum", lambda: sweeten(mix(pad(note("G3"), 0.35, 0.3, attack=0.03), air(0.1, 2000, 800, 0.08)), 0.25)),
    "item": ("Using an item: a quick bright bloop", lambda: mix(glide(600, 1000, 0.08, 0.25), bell(note("E6"), 0.25, 0.12))),
    "down_enemy": ("An enemy is defeated: a falling thump that fades",
                   lambda: sweeten(mix(thump(200, 45, 0.45, 0.6), air(0.4, 1500, 200, 0.25, attack=0.005)), 0.3)),
    "down_ally": ("A party member falls: a low, sad two-note fall",
                  lambda: sweeten(seq(pad(note("E4"), 0.25, 0.28, attack=0.01), pad(note("A3"), 0.7, 0.28, attack=0.01)), 0.4, 0.7)),
    "victory": ("Winning a fight: a bright rolled chord",
                lambda: sweeten(mix(chord(["C5", "E5", "G5", "C6", "E6"], 1.0, 0.16, spread=0.07),
                                    pad(note("C3"), 1.0, 0.2, attack=0.05)), 0.4, 0.9)),
    "defeat": ("Losing a fight: a slow, low, falling chord",
               lambda: sweeten(mix(chord(["G4", "D4", "Bb3"], 1.4, 0.14, spread=0.18, fn=lambda f: pad(f, 1.4, 0.14, attack=0.08)),
                                   glide(note("G2"), note("D2"), 1.4, 0.25, attack=0.1)), 0.5, 1.0)),
    "flee": ("Running away: a quick double swish", lambda: seq(air(0.1, 1200, 4000, 0.25, band=True), air(0.12, 1400, 5000, 0.22, band=True))),
    "level_up": ("Level up: a sparkling rising arpeggio",
                 lambda: sweeten(mix(chord(["C5", "E5", "G5", "C6", "E6", "G6"], 0.8, 0.14, spread=0.06),
                                     air(0.6, 4000, 10000, 0.05, attack=0.3)), 0.4, 0.9)),
    "cutin": ("A cut-in splash: a big whoosh with a ring",
              lambda: sweeten(mix(air(0.45, 300, 8000, 0.45, attack=0.25, curve=1.0), thump(120, 50, 0.4, 0.5),
                                  bell(note("A5"), 0.6, 0.15), offsets=[0, 0.3, 0.32]), 0.35, 0.6)),
    # --- Floor ---
    "stairs": ("Taking the stairs: soft rising steps",
               lambda: sweeten(seq(*[mix(thump(160, 90, 0.07, 0.3), bell(note(n), 0.09, 0.08)) for n in ("C5", "E5", "G5", "C6")]), 0.3)),
    "campfire": ("Resting at a campfire: a warm chord and a soft crackle",
                 lambda: sweeten(mix(chord(["G4", "B4", "D5"], 1.2, 0.12, spread=0.12, fn=lambda f: pad(f, 1.2, 0.12, attack=0.1)),
                                     air(1.0, 3000, 2000, 0.04, attack=0.2)), 0.4, 0.8)),
    # --- Shop ---
    "coin": ("Buying or selling: two clinking coins",
             lambda: sweeten(seq(bell(note("B6"), 0.07, 0.2, ratio=3.7, index=2.0), bell(note("E7"), 0.3, 0.2, ratio=3.7, index=2.0)), 0.2)),
    "steal": ("A successful steal: a quick, sly swipe", lambda: mix(air(0.12, 1500, 6000, 0.25, band=True), bell(note("G6"), 0.2, 0.12), offsets=[0, 0.08])),
    "caught": ("Caught stealing: a short alarm chime",
               lambda: sweeten(seq(*[bell(note("E6") if k % 2 == 0 else note("C6"), 0.11, 0.25, index=2.2) for k in range(4)]), 0.25)),
}


## Peak level per sound (everything else 0.7): small interface sounds sit quieter.
QUIET = {"system_glitch": 0.4, "ui_click": 0.4, "talk": 0.4, "notice": 0.5, "item": 0.55, "miss": 0.55, "flee": 0.55, "encounter_flash": 0.5,
         "coin": 0.55, "steal": 0.55}


def main():
    preview = "--preview" in sys.argv
    out = os.getcwd() if preview else OUT
    os.makedirs(out, exist_ok=True)
    for name, (_, make) in SOUNDS.items():
        x = make()
        peak = max(1e-6, max(abs(v) for v in x))
        target = QUIET.get(name, 0.7)              # consistent loudness across the set
        save([v * target / peak for v in x], os.path.join(out, name + ".wav"))
    print("made %d sounds in %s" % (len(SOUNDS), out))


if __name__ == "__main__":
    main()
