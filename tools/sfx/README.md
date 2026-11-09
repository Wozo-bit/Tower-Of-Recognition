# Sound effect scripts

The game's sound effects are synthesized by these Python scripts (no extra
packages needed) in a soft, modern style (Hayden 2026-11-09): glass chimes,
soft thuds, whooshes and a light reverb. They write WAV files into
`assets/audio/sfx/`, credited in `assets/credits.json` as "Own work".

    cd tools/sfx
    python sounds.py              # every sound, into assets/audio/sfx
    python sounds.py --preview    # into the current folder instead

- `chip.py`: notes, mixing, sequencing and the WAV writer.
- `soft.py`: FM bells, warm pads, sine glides, filtered noise, the reverb.
- `sounds.py`: the sound list (name, what it's for, how it's made) and loudness.
