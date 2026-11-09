"""Title screen: the tower at night (640x360, shown at 3x = 1920x1080)."""
import random
import sys
from pixpng import Canvas, hexc, text, text_width

W, H = 640, 360
rng = random.Random(41)
cv = Canvas(W, H, hexc("#0b1022"))

# Sky: banded night gradient with ordered dithering between bands.
bands = ["#070b1a", "#0b1022", "#10173a", "#16204a", "#1c2a58", "#243566"]
BAYER = [[0, 8, 2, 10], [12, 4, 14, 6], [3, 11, 1, 9], [15, 7, 13, 5]]
for y in range(H):
    t = y / (H * 0.78)
    f = min(t, 0.999) * (len(bands) - 1)
    i, frac = int(f), f - int(f)
    for x in range(W):
        use = bands[min(i + 1, len(bands) - 1)] if frac * 16 > BAYER[y % 4][x % 4] else bands[i]
        cv.put(x, y, use)

# Stars, a few bright ones with a cross glint.
for _ in range(260):
    x, y = rng.randrange(W), rng.randrange(int(H * 0.7))
    cv.put(x, y, rng.choice(["#3a4a80", "#5d6fae", "#9aa8d8", "#cfd8ff"]))
for _ in range(9):
    x, y = rng.randrange(20, W - 20), rng.randrange(10, 170)
    cv.put(x, y, "#ffffff")
    for dx, dy in ((1, 0), (-1, 0), (0, 1), (0, -1)):
        cv.put(x + dx, y + dy, "#9aa8d8")

# Moon, low and to the left: one soft halo, a clean disc, a few craters.
mx, my = 132, 92
cv.disc(mx, my, 27, "#1a2552")
cv.disc(mx, my, 23, "#22306a")
cv.disc(mx, my, 19, "#f2edd4")
for j in range(my - 19, my + 20):          # shade the lower-right edge
    for i in range(mx - 19, mx + 20):
        d2 = (i - mx) ** 2 + (j - my) ** 2
        if 15 ** 2 < d2 <= 19 ** 2 + 11 and (i - mx) + (j - my) > 6:
            cv.put(i, j, "#d9d2b2")
for cx, cy, r in ((mx - 6, my - 5, 4), (mx + 6, my + 4, 3), (mx - 2, my + 9, 2), (mx + 9, my - 8, 2)):
    cv.disc(cx, cy, r, "#e2dbbd")
    cv.put(cx - r + 1, cy - r + 1, "#d2cba9")

# Distant hills / city of the tower's foot.
def ridge(base, amp, col, seed, step=6):
    r = random.Random(seed)
    h = base
    for x in range(W):
        if x % step == 0:
            h = base + r.randint(-amp, amp)
        cv.rect(x, h, 1, H - h, col)

ridge(232, 10, "#121a3c", 3, 9)
ridge(252, 7, "#0d1430", 5, 5)

# Clouds drifting across the tower's middle.
def cloud(cx, cy, w, col, shade):
    for k in range(0, w, 9):
        r = 6 + (k * 7919) % 6
        cv.ellipse(cx + k, cy, r + 4, r // 2 + 3, col)
    cv.rect(cx - 6, cy + 2, w + 8, 4, shade)

# The tower: a tall, slightly tapering stone spire into the clouds.
tx = 320
def tower_half_width(y):
    # Wide base, tapering, with ledges.
    return int(26 + (y / H) * 30)

TOP = 18
stone = ["#2a3150", "#323a5e", "#3a446c"]
for y in range(TOP, 262):
    hw = tower_half_width(y)
    for x in range(tx - hw, tx + hw):
        # Brick courses: lighter left face, darker right face, mortar lines.
        side = (x - (tx - hw)) / (2 * hw)
        col = stone[2] if side < 0.25 else stone[1] if side < 0.7 else stone[0]
        if y % 6 == 0:
            col = "#20263f"
        elif (x + (6 if (y // 6) % 2 else 0)) % 12 == 0:
            col = "#232a46"
        cv.put(x, y, col)
    # Moonlit rim on the left edge.
    cv.put(tx - hw, y, "#5a6a9e")

# Ledges every 40 floors-ish.
for ly in range(70, 262, 38):
    hw = tower_half_width(ly) + 4
    cv.rect(tx - hw, ly, hw * 2, 3, "#454f7a")
    cv.rect(tx - hw, ly + 3, hw * 2, 1, "#161b30")

# Dark windows up the tower, and ONE lit window near the top.
# No other windows: only the one lit window near the top (Hayden).
lit = (tx - 2, 52)
cv.rect(lit[0] - 3, lit[1] - 3, 10, 13, "#3a3010")
cv.rect(lit[0] - 1, lit[1] - 1, 6, 9, "#7a5a18")
cv.rect(lit[0], lit[1], 4, 7, "#ffd36b")
cv.rect(lit[0] + 1, lit[1] + 1, 2, 3, "#fff2b8")

# Spire tip pierces a cloud bank.
cv.poly([(tx - 18, TOP + 1), (tx, 0), (tx + 18, TOP + 1)], "#2a3150")
cv.poly([(tx - 18, TOP + 1), (tx, 0), (tx - 6, TOP + 1)], "#3a446c")
for cx in range(150, 500, 34):
    cloud(cx, 14 + (cx * 7) % 13, 60, "#2b3768", "#222c58")
cloud(230, 40, 60, "#24305f", "#1d2752")
cloud(360, 34, 56, "#24305f", "#1d2752")
cloud(470, 128, 90, "#1f2a58", "#19224a")
cloud(90, 170, 80, "#1f2a58", "#19224a")

# The tower stands on a rocky hill that runs down to the ground (no floating).
hill = [(tx - 210, 304), (tx - 150, 276), (tx - 96, 258), (tx - 60, 250), (tx + 60, 250),
        (tx + 100, 258), (tx + 160, 278), (tx + 220, 304)]
cv.poly(hill, "#161c38")
for x in range(tx - 210, tx + 221):          # moonlit rim along the hill's top edge
    for y in range(240, 305):
        c = cv.get(x, y) if 0 <= x < W else None
        if c and c[:3] == (0x16, 0x1c, 0x38):
            cv.put(x, y, "#2a3360" if x < tx else "#1f2648")
            break
for _ in range(70):                           # rocks and grass tufts on the hill
    x = rng.randrange(tx - 190, tx + 200)
    y = rng.randrange(262, 300)
    c = cv.get(x, y)
    if c[:3] in ((0x16, 0x1c, 0x38),):
        cv.rect(x, y, rng.choice((2, 3)), 1, rng.choice(("#20284c", "#11162c", "#26305a")))
# A wide stone foundation under the tower, flush with the hill.
fhw = tower_half_width(261) + 8
cv.rect(tx - fhw, 250, fhw * 2, 12, "#2a3150")
cv.rect(tx - fhw, 250, fhw * 2, 2, "#4a5584")
cv.rect(tx - fhw, 250, 2, 12, "#4a5584")
for bx in range(tx - fhw + 10, tx + fhw, 14):
    cv.rect(bx, 253, 1, 9, "#1e243e")
cv.rect(tx - fhw, 261, fhw * 2, 1, "#10142a")
# Soft shadow where the foundation meets the hill.
cv.rect(tx - fhw - 6, 262, fhw * 2 + 12, 2, "#10142a")

# --- Filling the sides ---
# Lit windows in the distant town behind the hill.
for _ in range(46):
    x = rng.randrange(0, W)
    if tx - 70 < x < tx + 70:
        continue
    y = rng.randrange(238, 262)
    c = cv.get(x, y)
    if c[:3] in ((0x12, 0x1a, 0x3c), (0x0d, 0x14, 0x30)):
        cv.rect(x, y, 1, 2 if rng.random() < 0.4 else 1, rng.choice(("#ffd36b", "#e0a84a", "#9aa8d8")))

# Left: a climbers' camp on the hillside (tents, a fire, two figures).
def tent(x, y, w, h, col, shade, open_col="#0b0e1c"):
    cv.poly([(x, y + h), (x + w // 2, y), (x + w, y + h)], col)
    cv.poly([(x + w // 2, y), (x + w, y + h), (x + w // 2 + 2, y + h)], shade)
    cv.poly([(x + w // 2 - 3, y + h), (x + w // 2, y + h - 7), (x + w // 2 + 3, y + h)], open_col)
    cv.put(x + w // 2, y - 1, "#9aa8d8")

def glow(cx, cy, r, cols):
    for k, col in enumerate(cols):
        rr = r - k * (r // len(cols))
        for j in range(cy - rr, cy + rr + 1):
            for i in range(cx - rr, cx + rr + 1):
                if (i - cx) ** 2 + ((j - cy) * 1.6) ** 2 <= rr * rr and (i + j) % (len(cols) - k + 1) == 0:
                    cv.put(i, j, col)

cv.poly([(0, 304), (0, 292), (30, 288), (80, 286), (150, 288), (196, 296), (214, 304)], "#161c38")
for x in range(0, 214):                       # moonlit rim on the rise
    for y in range(282, 305):
        if cv.get(x, y)[:3] == (0x16, 0x1c, 0x38):
            cv.put(x, y, "#2a3360")
            break
glow(96, 296, 40, ["#1c2240", "#2a2a46", "#3d3448", "#5a3e3e"])
tent(40, 263, 36, 26, "#5a4670", "#41325a")
tent(124, 268, 30, 20, "#46587e", "#344466")
cv.rect(36, 289, 44, 1, "#10142a")            # tent shadows on the ground
cv.rect(121, 288, 36, 1, "#10142a")
cv.rect(90, 296, 14, 2, "#3a2418")          # logs
cv.rect(93, 290, 2, 6, "#ff8a3d")             # fire
cv.rect(96, 287, 2, 9, "#ffd36b")
cv.rect(99, 291, 2, 5, "#ff8a3d")
cv.put(96, 285, "#fff2b8")
for (x, y) in ((80, 288), (108, 289)):         # two climbers sitting by it
    cv.rect(x, y, 4, 3, "#1a1f36")
    cv.rect(x, y + 3, 5, 4, "#232a46")
    cv.put(x + 3 if x < 96 else x, y + 4, "#e0a84a")   # firelit side
cv.rect(40, 298, 1, 1, "#e0a84a")             # a dropped lantern
cv.rect(120, 299, 6, 1, "#26305a")            # a pack

# Right: an old bare tree, a broken pillar and lanterns along the path.
def branch(x, y, dx, dy, n, col):
    for k in range(n):
        cv.put(x + (dx * k) // 3, y + (dy * k) // 3, col)

TREE, RIM = "#141a30", "#2f3a6a"
def line(x0, y0, x1, y1, w, col, rim=None):
    n = max(abs(x1 - x0), abs(y1 - y0), 1)
    for k in range(n + 1):
        x = round(x0 + (x1 - x0) * k / n)
        y = round(y0 + (y1 - y0) * k / n)
        ww = max(1, round(w * (1 - k / (n + 1))))   # taper toward the tip
        cv.rect(x - ww // 2, y, ww, 1, col)
        cv.rect(x, y - ww // 2, 1, ww, col)
        if rim and x1 < x0:
            cv.put(x - ww // 2 - 1, y, rim)
    return (x1, y1)

def grow(x, y, angle_deg, length, width, depth):
    import math
    if depth == 0 or length < 4:
        return
    x1 = x + round(math.cos(math.radians(angle_deg)) * length)
    y1 = y - round(math.sin(math.radians(angle_deg)) * length)
    line(x, y, x1, y1, width, TREE, RIM)
    for turn in (-28, 24):
        grow(x1, y1, angle_deg + turn + (7 if depth % 2 else -6), int(length * 0.7), max(1, width - 1), depth - 1)

cv.rect(565, 226, 6, 76, TREE)                # trunk, wider at the base
cv.rect(563, 286, 10, 16, TREE)
cv.rect(565, 226, 1, 76, RIM)
cv.rect(560, 299, 17, 3, TREE)                # roots
grow(568, 230, 128, 34, 4, 4)                 # main limbs, left and right
grow(568, 236, 52, 36, 4, 4)
grow(567, 252, 158, 22, 3, 3)
grow(570, 258, 20, 20, 3, 3)
grow(568, 228, 92, 22, 3, 3)
cv.rect(482, 270, 9, 30, "#2a3150")           # broken pillar
cv.rect(482, 270, 2, 30, "#4a5584")
cv.poly([(482, 270), (486, 263), (489, 268), (491, 266), (491, 270)], "#2a3150")
cv.rect(478, 299, 17, 2, "#1e243e")
cv.rect(497, 296, 5, 3, "#2a3150")            # fallen chunk
for lx in (402, 430, 458):                    # lantern posts beside the stairs
    cv.rect(lx, 268 + (lx - 402) // 5, 1, 30, "#10142a")
    ly = 266 + (lx - 402) // 5
    cv.rect(lx - 1, ly, 3, 3, "#e0a84a")
    cv.put(lx, ly + 1, "#fff2b8")
for lx in (238, 210, 182):
    cv.rect(lx, 268 + (238 - lx) // 5, 1, 30, "#10142a")
    ly = 266 + (238 - lx) // 5
    cv.rect(lx - 1, ly, 3, 3, "#e0a84a")
    cv.put(lx, ly + 1, "#fff2b8")
# A few birds crossing the moonlit sky.
for bx, by in ((200, 140), (212, 134), (226, 146), (540, 70), (552, 64)):
    cv.put(bx, by, "#0b0e1c"); cv.put(bx - 1, by - 1, "#0b0e1c"); cv.put(bx + 1, by - 1, "#0b0e1c")

# The great stairs up to the door.
door_y = 262
for k in range(8):
    y = door_y + k * 5
    hw = 30 + k * 12
    cv.rect(tx - hw, y, hw * 2, 5, "#2f3758" if k % 2 == 0 else "#2a3150")
    cv.rect(tx - hw, y, hw * 2, 1, "#4a5584")
cv.rect(0, 302, W, H - 302, "#0a0f22")
# Door with a faint glow.
cv.rect(tx - 9, 240, 18, 22, "#0b0e1c")
cv.poly([(tx - 9, 240), (tx, 232), (tx + 9, 240)], "#0b0e1c")
cv.rect(tx - 7, 244, 14, 18, "#1a1530")
cv.rect(tx - 2, 256, 4, 6, "#3a3060")

# You and the friend at the foot of the stairs, seen from behind, walking up.
PAL = {
    "k": "#0b0e1c", "H": "#2a2230", "h": "#556088", "d": "#3f4970", "s": "#e8c4a0",
    "p": "#252c48", "b": "#151a2e",
    "f": "#7a4a2c", "F": "#5a3420", "c": "#3b6fb6", "C": "#2c5490", "r": "#d0413a", "R": "#8e2a20",
    "g": "#d9be7c", "m": "#9aa8c8",
}
YOU = [
    "...kkk...",
    "..kHHHk..",
    ".kHHHHHk.",
    ".kHHHHHk.",
    "..kHHHk..",
    ".kdhhhdk.",
    "khhdddhhk",
    "khhhhhhhk",
    "khhhdhhhk",
    "kdhhhhhdk",
    "kshhhhhsk",
    ".khhhhhk.",
    ".kppkppk.",
    ".kppkppk.",
    ".kppkppk.",
    ".kbbkbbk.",
    ".kkk.kkk.",
]
FRIEND = [
    "........g..",
    "...kkk..g..",
    "..kfffk.m..",
    ".kffFffkm..",
    ".kfffffkm..",
    "..kfffkm...",
    ".krrrrrkRR.",
    "kcrrrrrcRRR",
    "kcccmcccR.R",
    "kcccmCcck..",
    "kCccmccCk..",
    "kscccmccsk.",
    ".kccccck...",
    ".kppkppk...",
    ".kppkppk...",
    ".kppkppk...",
    ".kbbkbbk...",
    ".kkk.kkk...",
]
def sprite(rows, x, y):
    for j, row in enumerate(rows):
        for i, ch in enumerate(row):
            if ch in PAL:
                cv.put(x + i, y + j, PAL[ch])

# Standing on the steps: you on the bottom step, the friend one step ahead.
cv.rect(300, 298, 10, 1, "#1a2038")           # shadows on the step treads
cv.rect(311, 293, 10, 1, "#1a2038")
sprite(YOU, 300, 281)                          # feet on the bottom step (top at y 297)
sprite(FRIEND, 311, 275)                       # feet on the next step up (top at y 292)
# Logo: TOWER OF RECOGNITION, with one glitched letter.
title = "TOWER OF RECOGNITION"
scale = 3
tw = text_width(title, scale)
x0, y0 = (W - tw) // 2, 318
# Shadow plate behind the logo for readability.
cv.rect(x0 - 10, y0 - 7, tw + 20, 7 * scale + 14, (6, 9, 22, 255))
cv.rect(x0 - 10, y0 - 7, tw + 20, 1, "#6ee7ff")
cv.rect(x0 - 10, y0 + 7 * scale + 6, tw + 20, 1, "#6ee7ff")
text(cv, title, x0 + scale, y0 + scale, "#1c2a58", scale)   # drop shadow
glitch = title.index("G")  # the G in RECOGNITION flickers
text(cv, title, x0, y0, "#e8ecff", scale,
     per_char=lambda n, ch: "#ff4d6d" if n == glitch else "#e8ecff")
# Glitch: a displaced slice of the G.
gx = x0 + glitch * 6 * scale
cv.rect(gx + 2, y0 + 3 * scale, 5 * scale, scale, "#6ee7ff")

out = sys.argv[1] if len(sys.argv) > 1 else "title.png"
cv.save(out)
cv.scaled(2).save(out.replace(".png", "_preview2x.png"))
print("saved", out)
