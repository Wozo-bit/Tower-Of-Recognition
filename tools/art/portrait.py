"""64x64 pixel-art portraits (busts, facing the viewer, lit from the upper left).

    python portrait.py            # writes every portrait into assets/art/portraits
    python portrait.py --preview  # also writes 4x previews and a contact sheet here

Each portrait is a dict of parts (skin, hair style, eyes, clothes, extras);
the drawing code below turns it into pixels. Own work: credited in
assets/credits.json.
"""
import os
import sys
from pixpng import Canvas, hexc

S = 64
OUT = os.path.join(os.path.dirname(__file__), "..", "..", "assets", "art", "portraits")
OUTLINE = "#14111c"


def shade(hex_col, f):
    r, g, b, a = hexc(hex_col)
    if f < 1:
        return (int(r * f), int(g * f), int(b * f), a)
    return (min(255, int(r + (255 - r) * (f - 1))), min(255, int(g + (255 - g) * (f - 1))),
            min(255, int(b + (255 - b) * (f - 1))), a)


SKINS = {
    "fair": "#f1c7a1", "light": "#e8b48c", "tan": "#c98e62", "brown": "#9a6440", "deep": "#6e4329",
    "pale": "#efd9c8", "grey": "#d8c2ae",
}


class Portrait:
    def __init__(self, p):
        self.p = p
        self.cv = Canvas(S, S)

    # --- helpers -------------------------------------------------------------
    def px(self, x, y, c):
        self.cv.put(x, y, c)

    def rect(self, x, y, w, h, c):
        self.cv.rect(x, y, w, h, c)

    def ell(self, cx, cy, rx, ry, c):
        self.cv.ellipse(cx, cy, rx, ry, c)

    def poly(self, pts, c):
        self.cv.poly(pts, c)

    # --- body ------------------------------------------------------------------
    def body(self):
        p = self.p
        top = p.get("top", "hoodie")
        col = p.get("top_color", "#556088")
        dark, light = shade(col, 0.72), shade(col, 1.18)
        if p.get("sword"):   # on the back: hilt over the right shoulder, blade hidden behind it
            self.rect(50, 26, 4, 2, "#d9be7c")                            # pommel
            self.rect(51, 28, 2, 8, "#6b4a2a")                            # grip
            self.rect(52, 29, 1, 6, "#8a6a40")
            self.rect(47, 36, 10, 2, "#c9b07a")                           # guard
            self.rect(51, 38, 2, 12, "#9aa8c8")                           # blade, mostly behind the shoulder
        if p.get("hair") == "ponytail":   # the tail hangs down behind the head and shoulder
            hc = p.get("hair_color", "#2a2230")
            self.poly([(45, 14), (52, 21), (53, 34), (51, 42), (49, 36), (48, 24)], hc)   # stops above the shoulder
            self.poly([(50, 24), (52, 33), (51, 39)], shade(hc, 0.7))
        # Shoulders.
        self.poly([(5, 64), (9, 52), (18, 47), (46, 47), (55, 52), (59, 64)], col)
        self.poly([(5, 64), (9, 52), (18, 47), (24, 47), (16, 54), (13, 64)], light)
        self.poly([(46, 47), (55, 52), (59, 64), (50, 64), (49, 54)], dark)
        # Neck.
        skin = SKINS[p.get("skin", "fair")]
        self.rect(27, 40, 10, 9, skin)
        self.rect(32, 40, 5, 9, shade(skin, 0.82))
        self.rect(27, 46, 10, 2, shade(skin, 0.7))
        if top == "hoodie":
            self.poly([(16, 49), (24, 45), (32, 51), (40, 45), (48, 49), (40, 55), (32, 56), (24, 55)], dark)
            self.poly([(24, 47), (32, 53), (40, 47), (38, 51), (32, 54), (26, 51)], shade(col, 0.55))
            self.rect(27, 55, 1, 7, light)       # drawstrings
            self.rect(36, 55, 1, 6, light)
            self.rect(23, 60, 18, 1, dark)       # pocket seam
        elif top == "flannel":
            for x in range(6, 59):
                for y in range(47, 64):
                    if self.cv.get(x, y)[3] and (x // 4 + y // 4) % 2 == 0 and self.cv.get(x, y)[:3] in (hexc(col)[:3], light[:3], dark[:3]):
                        self.px(x, y, shade(col, 0.82))
            for y in range(47, 64, 4):
                for x in range(6, 59):
                    if self.cv.get(x, y)[3] and abs(x - 32) > 5:
                        self.px(x, y, shade("#e8dcc8", 0.9))
            self.poly([(26, 47), (32, 56), (38, 47)], "#e8dcc8")     # t-shirt under the open shirt
            self.poly([(24, 47), (31, 57), (27, 64), (22, 64)], shade(col, 1.1))
            self.poly([(40, 47), (33, 57), (37, 64), (42, 64)], dark)
        elif top == "bomber":
            self.rect(24, 46, 16, 4, shade(col, 0.6))                  # ribbed collar
            for x in range(24, 40, 2):
                self.px(x, 47, shade(col, 0.5))
            self.rect(32, 50, 1, 14, "#c9b07a")                         # zip
            self.rect(12, 56, 6, 1, dark)
            self.rect(46, 56, 6, 1, dark)
            self.px(14, 52, "#d0413a")                                   # a little patch
            self.px(15, 52, "#d0413a")
        elif top == "tshirt":
            self.poly([(25, 47), (32, 52), (39, 47)], shade(skin, 0.8))
            self.rect(24, 47, 16, 1, shade(col, 1.35))
        elif top == "coat":
            self.poly([(20, 47), (32, 64), (44, 47)], shade(col, 0.6))   # open front
            self.poly([(24, 47), (32, 58), (40, 47)], "#d9cfb6")          # shirt
            self.rect(10, 56, 5, 4, shade(col, 1.25))                     # patches
            self.rect(11, 57, 3, 2, "#8a6a4a")
            self.px(11, 56, OUTLINE)
            self.rect(48, 59, 4, 3, "#6a5a7a")
        # Scarf (the friend's): wraps the neck and trails off one shoulder.
        if p.get("scarf"):
            sc = p["scarf"]
            self.poly([(22, 44), (42, 44), (44, 50), (32, 52), (20, 50)], sc)
            self.poly([(22, 44), (42, 44), (42, 46), (22, 46)], shade(sc, 1.2))
            self.poly([(36, 50), (44, 49), (46, 64), (39, 64)], shade(sc, 0.85))
            for y in range(53, 64, 3):
                self.rect(39 + (y - 53) // 4, y, 6, 1, shade(sc, 0.65))

    # --- head ------------------------------------------------------------------
    def head(self):
        p = self.p
        skin = SKINS[p.get("skin", "fair")]
        sd = shade(skin, 0.82)
        # Ears.
        self.ell(18, 29, 3, 4, skin)
        self.ell(46, 29, 3, 4, sd)
        self.px(18, 29, shade(skin, 0.7))
        self.px(46, 29, shade(skin, 0.65))
        # Face: a soft rounded shape with a narrower chin.
        self.ell(32, 26, 13, 14, skin)
        self.poly([(21, 30), (43, 30), (39, 39), (32, 42), (25, 39)], skin)
        # Shade the right side and under the chin.
        for y in range(12, 43):
            for x in range(32, 47):
                c = self.cv.get(x, y)
                if c[:3] == hexc(skin)[:3] and (x - 32) * 1.0 + (y - 26) * 0.35 > 8:
                    self.px(x, y, sd)
        self.rect(28, 41, 8, 1, sd)
        # Cheeks.
        if p.get("blush", True):
            self.rect(23, 33, 3, 1, shade(skin, 0.9) if p.get("skin") in ("brown", "deep") else "#e9a28a")
            self.rect(38, 33, 3, 1, shade(skin, 0.78) if p.get("skin") in ("brown", "deep") else "#d98f78")
        if p.get("freckles"):
            for x, y in ((24, 31), (26, 32), (28, 31), (36, 31), (38, 32), (40, 31)):
                self.px(x, y, shade(skin, 0.7))
        # Nose: a highlight and a shadow.
        self.px(32, 31, shade(skin, 1.1))
        self.rect(33, 32, 1, 2, shade(skin, 0.72))
        self.px(32, 34, shade(skin, 0.78))

    def eyes(self):
        p = self.p
        iris = p.get("eyes", "#3a2a22")
        y = 28
        for cx in (26, 38):
            self.rect(cx - 2, y, 5, 3, "#f4f1e6")
            self.rect(cx - 1, y, 3, 3, iris)
            self.px(cx, y + 1, OUTLINE)
            self.px(cx - 1, y, shade(iris, 1.5))                           # catch-light
            self.rect(cx - 2, y - 1, 5, 1, OUTLINE)                         # upper lid
        if p.get("tired"):
            for cx in (26, 38):
                self.rect(cx - 2, y + 3, 5, 1, shade(SKINS[p.get("skin", "fair")], 0.7))
        # Brows.
        bc = shade(p.get("hair_color", "#2a2230"), 0.8)
        lift = -1 if p.get("brow") == "raised" else 0
        self.rect(23, y - 4 + lift, 6, 1, bc)
        self.rect(35, y - 4 + lift, 6, 1, bc)
        if p.get("brow") == "worried":
            self.px(28, y - 5, bc)
            self.px(35, y - 5, bc)
        if p.get("scar_brow"):
            self.rect(37, y - 6, 1, 4, "#c98a7a")
            self.px(38, y - 2, "#c98a7a")
        if p.get("glasses"):
            gc = p["glasses"]
            for cx in (26, 38):
                for dx in range(-4, 5):
                    for dy in range(-3, 4):
                        if 13 <= dx * dx + dy * dy * 1.6 <= 21:
                            self.px(cx + dx, y + 1 + dy, gc)
            self.rect(30, y, 4, 1, gc)
        if p.get("eyepatch"):
            self.rect(35, y - 1, 7, 6, "#1c1a24")
            self.rect(36, y, 5, 4, "#2c2a36")
            for x in range(20, 46):
                yy = y - 3 + (x - 20) // 6
                if not (35 <= x <= 41):
                    self.px(x, yy, "#1c1a24")

    def mouth(self):
        kind = self.p.get("mouth", "neutral")
        m = "#7a3a32"
        if kind == "grin":
            self.rect(28, 36, 9, 1, m)
            self.rect(29, 37, 7, 1, "#f4f1e6")
            self.rect(30, 38, 5, 1, m)
            self.px(27, 35, m)
            self.px(37, 35, m)
        elif kind == "smile":
            self.rect(29, 37, 7, 1, m)
            self.px(28, 36, m)
            self.px(36, 36, m)
        elif kind == "flat":
            self.rect(29, 37, 6, 1, m)
        elif kind == "frown":
            self.rect(29, 37, 6, 1, m)
            self.px(28, 38, m)
            self.px(35, 38, m)
        else:
            self.rect(30, 37, 5, 1, m)
            self.px(35, 36, m)
        if self.p.get("plaster"):
            self.rect(29, 31, 6, 2, "#e8d2b0")
            self.px(31, 31, "#c9b07a")
            self.px(33, 32, "#c9b07a")

    # --- hair (drawn in front of the head) -------------------------------------
    def hair(self):
        p = self.p
        style = p.get("hair", "short")
        hc = p.get("hair_color", "#2a2230")
        hl, hd = shade(hc, 1.35), shade(hc, 0.7)
        if style == "short":            # short and a bit messy, fringe to the brows
            self.ell(32, 18, 15, 10, hc)
            self.poly([(17, 22), (19, 14), (25, 25), (29, 21), (33, 26), (37, 21), (41, 25), (45, 14), (47, 22), (46, 30), (44, 22), (20, 22), (18, 30)], hc)
            self.poly([(20, 14), (30, 9), (26, 14)], hl)
            self.rect(23, 12, 8, 1, hl)
            self.poly([(40, 12), (47, 20), (45, 26)], hd)
        elif style == "messy":          # the friend's: spiky, falling every way
            self.ell(32, 18, 16, 11, hc)
            for (x, y) in ((16, 26), (20, 23), (24, 27), (29, 23), (34, 27), (38, 23), (43, 27), (47, 24)):
                self.poly([(x - 3, 18), (x + 3, 18), (x, y)], hc)
            for (x, y) in ((22, 6), (30, 4), (38, 5), (45, 9)):
                self.poly([(x - 4, 12), (x + 4, 12), (x, y)], hc)
            self.poly([(20, 12), (28, 7), (25, 13)], hl)
            self.rect(30, 9, 5, 1, hl)
            self.poly([(42, 12), (48, 19), (46, 25)], hd)
        elif style == "ponytail":       # pulled back, with a tail over one shoulder
            self.ell(32, 18, 14, 10, hc)
            self.poly([(18, 22), (20, 13), (32, 11), (44, 13), (46, 22), (44, 18), (36, 16), (28, 16), (20, 18)], hc)
            self.poly([(42, 14), (49, 16), (50, 33), (46, 34), (44, 24)], hc)  # hair down the side, into the tail
            self.poly([(46, 18), (49, 18), (49, 32), (47, 32)], hd)
            # The right ear in front of that hair: a mirror of the left one, outline and all.
            skin = SKINS[p.get("skin", "fair")]
            self.ell(46, 29, 3, 4, shade(skin, 0.82))
            self.px(46, 29, shade(skin, 0.65))
            for y in range(25, 34):
                for x in range(43, 51):
                    inside = ((x - 46) / 3) ** 2 + ((y - 29) / 4) ** 2 <= 1.0
                    outside_next = ((x + 1 - 46) / 3) ** 2 + ((y - 29) / 4) ** 2 > 1.0 or                         ((x - 46) / 3) ** 2 + ((y + 1 - 29) / 4) ** 2 > 1.0 or ((x - 46) / 3) ** 2 + ((y - 1 - 29) / 4) ** 2 > 1.0
                    if not inside and x > 46 and ((x - 1 - 46) / 3) ** 2 + ((y - 29) / 4) ** 2 <= 1.0:
                        self.px(x, y, OUTLINE)
            self.px(46, 24, OUTLINE)
            self.px(47, 25, OUTLINE)
            self.px(46, 34, OUTLINE)
            self.px(47, 33, OUTLINE)
            self.rect(44, 15, 3, 3, "#c0392b")                           # hair tie (the tail hangs behind)
            self.rect(23, 12, 9, 1, hl)
        elif style == "curly":          # a full crown of curls
            for (x, y, r) in ((20, 18, 5), (24, 12, 6), (31, 9, 6), (38, 11, 6), (44, 17, 5), (18, 24, 4), (46, 24, 4), (27, 16, 5), (36, 16, 5)):
                self.cv.disc(x, y, r, hc)
            for (x, y) in ((22, 11), (29, 7), (36, 9), (42, 14), (19, 19), (25, 15)):
                self.px(x, y, hl)
                self.px(x + 1, y, hl)
            for (x, y) in ((44, 20), (40, 15), (46, 26)):
                self.px(x, y, hd)
        elif style == "buzz":           # close-cropped: just a shadow of hair
            for y in range(10, 22):
                for x in range(18, 47):
                    c = self.cv.get(x, y)
                    if c[3] and ((x - 32) ** 2 / 196 + (y - 22) ** 2 / 144 <= 1) and y < 21 - max(0, abs(x - 32) - 10) // 3:
                        self.px(x, y, hc if (x + y) % 3 else hd)
        elif style == "braid":          # long black braid over the shoulder
            self.ell(32, 18, 15, 10, hc)
            self.poly([(17, 24), (19, 13), (32, 10), (45, 13), (47, 24), (44, 18), (34, 15), (24, 17), (20, 20)], hc)
            self.poly([(42, 22), (47, 30), (46, 36), (43, 30)], hc)
            for k in range(6):
                self.ell(46, 38 + k * 4, 3, 2, hc if k % 2 else hl)
            self.rect(44, 61, 5, 2, "#d0413a")
            self.rect(24, 12, 8, 1, hl)
        elif style == "bob":            # chin-length, with a side fringe (Tess)
            self.ell(32, 19, 16, 11, hc)
            self.poly([(16, 20), (21, 13), (21, 38), (16, 36)], hc)
            self.poly([(48, 20), (43, 13), (43, 38), (48, 36)], shade(hc, 0.8))
            self.poly([(19, 16), (40, 12), (34, 24), (26, 21), (21, 25)], hc)
            self.rect(23, 13, 9, 1, hl)
            self.poly([(16, 36), (21, 38), (21, 40), (16, 38)], hd)
        elif style == "caesar":         # short, cropped; a straight fringe high on the forehead
            self.ell(32, 16, 15, 7, hc)
            self.rect(19, 15, 26, 3, hc)
            self.rect(18, 17, 3, 8, hc)                                   # short sides
            self.rect(43, 17, 3, 8, hd)
            for x in range(20, 45, 2):                                    # cropped texture
                self.px(x, 12 + (x % 4 == 0), hl)
            self.rect(20, 17, 24, 1, hd)                                  # the straight fringe edge
        elif style == "slick":          # swept straight back, forehead clear
            self.ell(32, 15, 15, 7, hc)
            self.poly([(17, 24), (18, 15), (24, 11), (40, 11), (46, 15), (47, 24), (44, 17), (32, 15), (20, 17)], hc)
            for k, y in enumerate((11, 13, 15)):                         # comb lines sweeping back
                self.rect(22 + k * 2, y, 12 - k * 2, 1, hl)
            self.poly([(40, 11), (47, 17), (46, 24), (43, 16)], hd)
        elif style == "slick_messy":    # the friend's: swept back, but it won't stay down
            self.ell(32, 15, 16, 8, hc)
            self.poly([(16, 24), (17, 15), (24, 10), (40, 10), (47, 15), (48, 24), (44, 17), (32, 15), (20, 17)], hc)
            for (x, y) in ((20, 5), (27, 3), (35, 3), (42, 6), (47, 10)):
                self.poly([(x - 4, 11), (x + 3, 11), (x + 1, y)], hc)
            self.rect(23, 11, 9, 1, hl)
            self.rect(25, 13, 6, 1, hl)
            self.poly([(41, 10), (48, 17), (47, 24), (44, 16)], hd)
            self.px(30, 16, hc)                                           # one strand that escaped
            self.px(29, 17, hc)
        elif style == "slick_undercut": # shaved sides, the top slicked back
            self.ell(32, 14, 13, 6, hc)
            self.poly([(20, 16), (24, 9), (40, 9), (44, 16), (32, 14)], hc)
            self.rect(24, 10, 12, 1, hl)
            self.rect(26, 12, 8, 1, hl)
        elif style == "bob_back":       # Tess: a bob tucked back, forehead clear
            self.ell(32, 16, 16, 8, hc)
            self.poly([(16, 18), (20, 12), (21, 38), (16, 36)], hc)
            self.poly([(48, 18), (44, 12), (43, 38), (48, 36)], shade(hc, 0.8))
            self.poly([(20, 16), (26, 12), (38, 12), (44, 16), (32, 15)], hc)
            self.rect(24, 11, 10, 1, hl)
            self.rect(26, 13, 6, 1, hl)
            self.poly([(16, 36), (21, 38), (21, 40), (16, 38)], hd)
            self.rect(20, 18, 1, 6, hl)                                   # tucked behind the ear
        elif style == "undercut":       # long on top, swept to one side; shaved sides
            self.ell(32, 17, 14, 8, hc)
            self.poly([(18, 18), (24, 9), (40, 8), (47, 14), (46, 21), (36, 17), (22, 21)], hc)
            self.poly([(24, 9), (36, 7), (30, 12)], hl)
            for y in range(18, 27):
                self.px(18, y, hd)
                self.px(46, y, hd)
        elif style == "silver_short":   # short and neat, swept back
            self.ell(32, 17, 15, 9, hc)
            self.poly([(17, 23), (18, 14), (32, 9), (46, 14), (47, 23), (44, 18), (32, 15), (20, 18)], hc)
            for x in range(21, 44, 4):
                self.rect(x, 11, 2, 1, hl)
            self.poly([(41, 12), (47, 18), (46, 24)], hd)
        elif style == "bald_grey":      # Marn: thinning grey hair and stubble
            self.poly([(17, 25), (19, 17), (23, 21), (21, 29)], hc)
            self.poly([(47, 25), (45, 17), (41, 21), (43, 29)], hd)
            self.rect(26, 13, 12, 1, hl)
        if p.get("stubble"):
            for y in range(33, 42):
                for x in range(22, 43):
                    c = self.cv.get(x, y)
                    if c[3] and (x * 3 + y * 7) % 4 == 0 and y > 34 + (0 if 26 < x < 38 else 2):
                        if c[:3] in (hexc(SKINS[p["skin"]])[:3], shade(SKINS[p["skin"]], 0.82)[:3]):
                            self.px(x, y, shade(p["hair_color"], 0.9))
        if p.get("broken_nose"):
            self.px(31, 30, shade(SKINS[p["skin"]], 0.72))
            self.px(33, 30, shade(SKINS[p["skin"]], 0.72))
        if p.get("cloudy_eye"):
            self.rect(37, 28, 3, 3, "#b8c0c8")
            self.px(38, 29, "#d8dee4")
        if p.get("bandage"):
            self.rect(22, 34, 5, 2, "#efe6d2")                            # on the cheek, below the eye
            self.px(24, 34, "#d8c8a8")
        if p.get("helmet_dent"):
            pass

    def fill_holes(self):
        """Gaps enclosed by the figure (e.g. between hair and head) become skin,
        so the outline pass only traces the outside edge, never little black holes."""
        seen = [[False] * S for _ in range(S)]
        stack = [(x, y) for x in range(S) for y in (0, S - 1)] + [(x, y) for y in range(S) for x in (0, S - 1)]
        while stack:
            x, y = stack.pop()
            if not (0 <= x < S and 0 <= y < S) or seen[y][x] or self.cv.get(x, y)[3]:
                continue
            seen[y][x] = True
            stack += [(x + 1, y), (x - 1, y), (x, y + 1), (x, y - 1)]
        skin = SKINS[self.p.get("skin", "fair")]
        behind = shade(self.p.get("hair_color", "#2a2230"), 0.6)   # low gaps (behind the neck) read as shadow
        for y in range(S):
            for x in range(S):
                if not seen[y][x] and not self.cv.get(x, y)[3]:
                    self.px(x, y, skin if y < 30 else behind)

    def draw(self):
        self.body()
        self.head()
        self.eyes()
        self.mouth()
        self.hair()
        self.fill_holes()
        self.cv.outline(OUTLINE)
        return self.cv


# ---------------------------------------------------------------------------
# The cast (Hayden 2026-11-09). Ids are the art file names.
# ---------------------------------------------------------------------------
PORTRAITS = {
    "player_0": {"skin": "fair", "hair": "caesar", "hair_color": "#2a2230", "eyes": "#4a3a30", "tired": True,
                 "top": "hoodie", "top_color": "#556088", "mouth": "neutral"},
    "player_1": {"skin": "light", "hair": "ponytail", "hair_color": "#5a3a24", "eyes": "#3a5a3a", "glasses": "#2a2a36",
                 "top": "flannel", "top_color": "#9a3a34", "mouth": "smile"},
    "player_2": {"skin": "deep", "hair": "curly", "hair_color": "#1c1418", "eyes": "#2a1a14", "top": "bomber",
                 "top_color": "#3d5a3a", "mouth": "flat"},
    "player_3": {"skin": "tan", "hair": "buzz", "hair_color": "#2a2018", "eyes": "#3a2a1a", "scar_brow": True,
                 "top": "tshirt", "top_color": "#22212c", "mouth": "flat", "brow": "flat"},
    "childhood_friend_0": {"skin": "fair", "hair": "slick_messy", "hair_color": "#6b3e26", "eyes": "#3a6a4a", "freckles": True,
                           "top": "coat", "top_color": "#3b6fb6", "scarf": "#d0413a", "sword": True, "mouth": "grin"},
    "childhood_friend_1": {"skin": "brown", "hair": "braid", "hair_color": "#14121a", "eyes": "#3a2418",
                           "top": "coat", "top_color": "#3b6fb6", "scarf": "#d0413a", "sword": True, "mouth": "grin"},
    "childhood_friend_2": {"skin": "light", "hair": "undercut", "hair_color": "#e0c070", "eyes": "#3a5a8a", "plaster": True,
                           "top": "coat", "top_color": "#3b6fb6", "scarf": "#d0413a", "sword": True, "mouth": "grin"},
    "childhood_friend_3": {"skin": "pale", "hair": "silver_short", "hair_color": "#c8ccd8", "eyes": "#6a4a8a", "eyepatch": True,
                           "top": "coat", "top_color": "#3b6fb6", "scarf": "#d0413a", "sword": True, "mouth": "grin"},
    "tess": {"skin": "fair", "hair": "bob_back", "hair_color": "#a8542a", "eyes": "#4a3a24", 
             "top": "coat", "top_color": "#6a5a44", "scarf": "#e0392b", "mouth": "grin", "brow": "raised"},
    "marn": {"skin": "grey", "hair": "bald_grey", "hair_color": "#9a9aa4", "eyes": "#3a3a44", "stubble": True,
             "broken_nose": True, "cloudy_eye": True, "top": "coat", "top_color": "#4a4038", "mouth": "frown",
             "brow": "worried", "blush": False},
}


def main():
    preview = "--preview" in sys.argv
    only = [a for a in sys.argv[1:] if not a.startswith("--")]
    os.makedirs(OUT, exist_ok=True)
    done = []
    for pid, spec in PORTRAITS.items():
        if only and pid not in only:
            continue
        cv = Portrait(spec).draw()
        if preview:
            cv.scaled(4).save("preview_%s.png" % pid)
        else:
            cv.save(os.path.join(OUT, pid + ".png"))
        done.append((pid, cv))
    if preview and done:
        sheet = Canvas(len(done) * 68 + 4, 72, hexc("#22304a"))
        for k, (_, cv) in enumerate(done):
            for y in range(S):
                for x in range(S):
                    c = cv.get(x, y)
                    if c[3]:
                        sheet.put(4 + k * 68 + x, 4 + y, c)
        sheet.scaled(3).save("preview_sheet.png")
    print("drew", [d[0] for d in done])


if __name__ == "__main__":
    main()
