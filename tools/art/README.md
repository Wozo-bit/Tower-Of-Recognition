# Pixel art scripts

The game's own pixel art is drawn by these Python scripts (no extra packages
needed). Each one writes a PNG straight into `assets/art/`, and is credited in
`assets/credits.json` as "Own work". Edit a script and run it again to change
the picture.

    cd tools/art
    python title.py ../../assets/art/backgrounds/title.png

- `pixpng.py`: the tiny canvas, shapes, 5x7 pixel font and PNG writer.
- `title.py`: the title screen (640x360, shown at 3x): the tower at night.
