"""Tiny pixel canvas + PNG writer (no Pillow needed)."""
import struct
import zlib


def hexc(h, a=255):
    h = h.lstrip("#")
    return (int(h[0:2], 16), int(h[2:4], 16), int(h[4:6], 16), a)


class Canvas:
    def __init__(self, w, h, bg=(0, 0, 0, 0)):
        self.w, self.h = w, h
        self.px = [[bg for _ in range(w)] for _ in range(h)]

    def put(self, x, y, c):
        if 0 <= x < self.w and 0 <= y < self.h and c is not None:
            if isinstance(c, str):
                c = hexc(c)
            self.px[y][x] = c

    def get(self, x, y):
        return self.px[y][x]

    def rect(self, x, y, w, h, c):
        for j in range(y, y + h):
            for i in range(x, x + w):
                self.put(i, j, c)

    def disc(self, cx, cy, r, c):
        for j in range(cy - r, cy + r + 1):
            for i in range(cx - r, cx + r + 1):
                if (i - cx) ** 2 + (j - cy) ** 2 <= r * r + r * 0.6:
                    self.put(i, j, c)

    def ellipse(self, cx, cy, rx, ry, c):
        for j in range(cy - ry, cy + ry + 1):
            for i in range(cx - rx, cx + rx + 1):
                if ((i - cx) / max(rx, 0.5)) ** 2 + ((j - cy) / max(ry, 0.5)) ** 2 <= 1.0:
                    self.put(i, j, c)

    def poly(self, pts, c):
        ys = [p[1] for p in pts]
        for y in range(int(min(ys)), int(max(ys)) + 1):
            xs = []
            n = len(pts)
            for k in range(n):
                (x1, y1), (x2, y2) = pts[k], pts[(k + 1) % n]
                if (y1 <= y < y2) or (y2 <= y < y1):
                    xs.append(x1 + (y - y1) * (x2 - x1) / (y2 - y1))
            xs.sort()
            for a, b in zip(xs[0::2], xs[1::2]):
                for x in range(int(round(a)), int(round(b))):
                    self.put(x, y, c)

    def outline(self, c, inside=None):
        """Draws `c` around every opaque pixel (on transparent neighbours)."""
        if isinstance(c, str):
            c = hexc(c)
        mark = []
        for y in range(self.h):
            for x in range(self.w):
                if self.px[y][x][3] == 0:
                    for dx, dy in ((1, 0), (-1, 0), (0, 1), (0, -1)):
                        X, Y = x + dx, y + dy
                        if 0 <= X < self.w and 0 <= Y < self.h and self.px[Y][X][3] > 0 and self.px[Y][X] != c:
                            mark.append((x, y))
                            break
        for x, y in mark:
            self.px[y][x] = c

    def scaled(self, k):
        out = Canvas(self.w * k, self.h * k)
        for y in range(self.h):
            for x in range(self.w):
                for j in range(k):
                    for i in range(k):
                        out.px[y * k + j][x * k + i] = self.px[y][x]
        return out

    def save(self, path):
        raw = b"".join(b"\x00" + b"".join(struct.pack("BBBB", *p) for p in row) for row in self.px)

        def chunk(t, d):
            return struct.pack(">I", len(d)) + t + d + struct.pack(">I", zlib.crc32(t + d) & 0xFFFFFFFF)

        with open(path, "wb") as f:
            f.write(b"\x89PNG\r\n\x1a\n")
            f.write(chunk(b"IHDR", struct.pack(">IIBBBBB", self.w, self.h, 8, 6, 0, 0, 0)))
            f.write(chunk(b"IDAT", zlib.compress(raw, 9)))
            f.write(chunk(b"IEND", b""))


# 5x7 pixel font, caps only (what the logo needs, plus a few spares).
FONT = {
    "A": ["01110", "10001", "10001", "11111", "10001", "10001", "10001"],
    "C": ["01111", "10000", "10000", "10000", "10000", "10000", "01111"],
    "E": ["11111", "10000", "10000", "11110", "10000", "10000", "11111"],
    "F": ["11111", "10000", "10000", "11110", "10000", "10000", "10000"],
    "G": ["01111", "10000", "10000", "10011", "10001", "10001", "01111"],
    "I": ["11111", "00100", "00100", "00100", "00100", "00100", "11111"],
    "N": ["10001", "11001", "10101", "10011", "10001", "10001", "10001"],
    "O": ["01110", "10001", "10001", "10001", "10001", "10001", "01110"],
    "R": ["11110", "10001", "10001", "11110", "10100", "10010", "10001"],
    "T": ["11111", "00100", "00100", "00100", "00100", "00100", "00100"],
    "W": ["10001", "10001", "10001", "10101", "10101", "11011", "10001"],
    " ": ["00000"] * 7,
}


def text_width(s, scale=1, gap=1):
    return len(s) * (5 + gap) * scale - gap * scale


def text(cv, s, x, y, c, scale=1, gap=1, per_char=None):
    for n, ch in enumerate(s):
        glyph = FONT[ch]
        col = per_char(n, ch) if per_char else c
        for j, row in enumerate(glyph):
            for i, b in enumerate(row):
                if b == "1":
                    cv.rect(x + i * scale, y + j * scale, scale, scale, col)
        x += (5 + gap) * scale
