#!/usr/bin/env python3
"""Ionity Sticker & Emoji Pack generator  -  v2.0  (transparent / die-cut edition)

Every sticker is drawn procedurally at 1024 px with 2x super-sampled shapes
(effective 4x at 512), on a fully TRANSPARENT canvas, then exported as:

  stickers-512-whatsapp/   animated WebP, die-cut, <= 500 KB  (+ tray-96.png)
  stickers-512-telegram/   WEBM VP9 + alpha, die-cut, <= 256 KB, <= 3 s
  stickers-320-discord/    APNG + GIF, die-cut, <= 512 KB
  web-800/                 WebP (clean, full-alpha neon glow) + GIF (die-cut)
  static-png-512/          static PNG, die-cut (best frame)
  emoji-128/               GIF, die-cut, <= 128 KB (Slack / Discord)
  emoji-128-png/           static PNG, die-cut
  emoji-100-telegram/      WEBM VP9 + alpha, <= 64 KB (Telegram custom emoji)
  preview/                 contact sheets on dark, light and checkerboard

"Die-cut" = artwork sits on a dark #0B0C10 sticker silhouette with a cyan rim,
everything outside the silhouette is 100 % transparent - readable on light AND
dark chat themes, and gives clean edges in 1-bit-alpha GIF.

Usage:  python3 gen.py <assets-dir> <out-dir> [sticker-names...]
Needs:  Pillow >= 10, numpy, ffmpeg (libvpx-vp9) on PATH.

(c) 2018-2026 Antwerp Designs | Ionity (Pty) Ltd - All Rights Reserved - TM2
Governance: Policy 986 AED | License: AED 900 | www.ionity.co.za | www.ionity.today
"""
import math, os, random, shutil, subprocess, sys, tempfile
from multiprocessing import Pool
import numpy as np
from PIL import Image, ImageDraw, ImageFilter, ImageFont, ImageChops

VERSION = "2.0"
ASSETS = sys.argv[1] if len(sys.argv) > 1 else "assets"
OUT = sys.argv[2] if len(sys.argv) > 2 else "out"
S = 1024          # master render size
SS = 2            # shape super-sampling factor (shapes drawn at S*SS)

# ---------------------------------------------------------------- palette
CYAN = (0, 210, 255)
BLUE = (51, 102, 255)
LOGO_BLUE = (33, 96, 174)
RED = (255, 40, 40)
WHITE = (255, 255, 255)
DARK = (11, 12, 16)
DARK2 = (7, 8, 13)
GREEN = (0, 235, 150)
AMBER = (255, 190, 40)
DIM = (18, 58, 104)
ICE = (200, 245, 255)

FD = "/usr/share/fonts/truetype"
MONO = f"{FD}/liberation/LiberationMono-Bold.ttf"        # metric clone of Courier New (site font)
MONO_R = f"{FD}/liberation/LiberationMono-Regular.ttf"
SANS = f"{FD}/google-fonts/Poppins-Bold.ttf"
for _p in (MONO, MONO_R, SANS):
    if not os.path.exists(_p):
        sys.exit(f"missing font: {_p}")

_FONTS = {}
def font(path, size):
    k = (path, int(size))
    if k not in _FONTS:
        _FONTS[k] = ImageFont.truetype(path, int(size))
    return _FONTS[k]

# ---------------------------------------------------------------- assets
def _alpha(path):
    im = Image.open(path).convert("RGBA")
    a = im.getchannel("A")
    return a.crop(a.getbbox())

AI_A = _alpha(os.path.join(ASSETS, "ai-mark-white.png"))
_wm_hi = os.path.join(ASSETS, "ionity-logo-edited.png")
WM_A = _alpha(_wm_hi if os.path.exists(_wm_hi) else os.path.join(ASSETS, "wordmark.png"))

YY, XX = np.mgrid[0:S, 0:S].astype(np.float32)

# ---------------------------------------------------------------- math
def ease(t):            return 0.5 - 0.5 * math.cos(math.pi * max(0.0, min(1.0, t)))
def ease_out(t):        t = max(0.0, min(1.0, t)); return 1 - (1 - t) ** 3
def back_out(t, s=1.7):
    t = max(0.0, min(1.0, t)) - 1
    return 1 + (s + 1) * t ** 3 + s * t ** 2
def seg(t, a, b):       return max(0.0, min(1.0, (t - a) / (b - a)))
def lerp(a, b, t):      return tuple(int(a[i] + (b[i] - a[i]) * t) for i in range(3))
def wave(t, k=1, ph=0): return math.sin(2 * math.pi * (t * k + ph))

# ---------------------------------------------------------------- canvas
def blank():
    return Image.new("RGBA", (S, S), (0, 0, 0, 0))

def L():
    return Image.new("L", (S, S), 0)

def arr(m):
    return np.asarray(m, dtype=np.float32) / 255.0

def to_L(a):
    return Image.fromarray(np.clip(a * 255.0 + 0.5, 0, 255).astype(np.uint8), "L")

class Pen:
    """Anti-aliased shape painter: draws on an SS-times larger L mask, returns S x S."""
    def __init__(self, scale=1.0, center=(S / 2, S / 2), dx=0, dy=0):
        self.m = Image.new("L", (S * SS, S * SS), 0)
        self.d = ImageDraw.Draw(self.m)
        self.sc, self.c, self.dx, self.dy = scale, center, dx, dy

    def P(self, x, y):
        return ((self.c[0] + (x - self.c[0]) * self.sc + self.dx) * SS,
                (self.c[1] + (y - self.c[1]) * self.sc + self.dy) * SS)

    def W(self, w):
        return max(1, int(round(w * self.sc * SS)))

    def circle(self, cx, cy, r, fill=255):
        x, y = self.P(cx, cy); r = r * self.sc * SS
        self.d.ellipse((x - r, y - r, x + r, y + r), fill=fill)

    def ellipse(self, cx, cy, rx, ry, fill=255):
        x, y = self.P(cx, cy); rx *= self.sc * SS; ry *= self.sc * SS
        self.d.ellipse((x - rx, y - ry, x + rx, y + ry), fill=fill)

    def ring(self, cx, cy, r, w, fill=255):
        x, y = self.P(cx, cy); r = r * self.sc * SS
        self.d.ellipse((x - r, y - r, x + r, y + r), outline=fill, width=self.W(w))

    def poly(self, pts, fill=255):
        self.d.polygon([self.P(*p) for p in pts], fill=fill)

    def line(self, pts, w, fill=255, caps=True):
        q = [self.P(*p) for p in pts]
        if len(q) > 1:
            self.d.line(q, fill=fill, width=self.W(w), joint="curve")
        if caps:
            r = w * self.sc * SS / 2
            for (x, y) in (q[0], q[-1]):
                self.d.ellipse((x - r, y - r, x + r, y + r), fill=fill)

    def arc(self, cx, cy, r, a0, a1, w, fill=255, caps=True):
        n = max(2, int(abs(a1 - a0) / 2))
        pts = [(cx + r * math.cos(math.radians(a0 + (a1 - a0) * i / n)),
                cy + r * math.sin(math.radians(a0 + (a1 - a0) * i / n))) for i in range(n + 1)]
        self.line(pts, w, fill, caps)

    def rrect(self, x0, y0, x1, y1, r, fill=255, width=0):
        a, b = self.P(x0, y0); c, d = self.P(x1, y1)
        rr = r * self.sc * SS
        if width:
            self.d.rounded_rectangle((a, b, c, d), radius=rr, outline=fill, width=self.W(width))
        else:
            self.d.rounded_rectangle((a, b, c, d), radius=rr, fill=fill)

    def text(self, x, y, txt, path, size, fill=255, anchor="mm", spacing=0):
        f = font(path, size * self.sc * SS)
        self.d.multiline_text(self.P(x, y), txt, font=f, fill=fill, anchor=anchor,
                              spacing=spacing * self.sc * SS, align="center")

    def done(self):
        return self.m.resize((S, S), Image.BOX)

def text_w(txt, path, size):
    return font(path, size).getlength(txt)

def src_mask(src, w, cx, cy, sx=1.0, sy=1.0, rot=0.0):
    """Place an asset alpha (AI mark / wordmark) of width w centred at (cx, cy)."""
    h = src.height * w / src.width
    ww, hh = max(2, int(w * abs(sx))), max(2, int(h * sy))
    m = src.resize((ww, hh), Image.LANCZOS)
    if rot:
        m = m.rotate(rot, resample=Image.BICUBIC, expand=True)
    out = L()
    out.paste(m, (int(round(cx - m.width / 2)), int(round(cy - m.height / 2))))
    return out

# ---------------------------------------------------------------- paint
def _box(bb, pad):
    return (max(0, bb[0] - pad), max(0, bb[1] - pad), min(S, bb[2] + pad), min(S, bb[3] + pad))

def fill(m, c1, c2=None, angle=90, shine=0.0, alpha=1.0):
    """Colour a mask: solid c1, or linear gradient c1->c2 across the mask bbox (angle 90 = top->bottom).
    `shine` adds a soft white specular on the upper part of the shape. Works only inside the bbox (fast)."""
    bb = m.getbbox()
    out = blank()
    if not bb:
        return out
    x0, y0, x1, y1 = bb
    a = arr(m.crop(bb)) * alpha
    X, Y = XX[y0:y1, x0:x1], YY[y0:y1, x0:x1]
    if c2 is None:
        rgb = np.empty(a.shape + (3,), np.float32); rgb[:] = c1
    else:
        r = math.radians(angle); ca, sa = math.cos(r), math.sin(r)
        p = X * ca + Y * sa
        cs = [x * ca + y * sa for x in (x0, x1) for y in (y0, y1)]
        t = np.clip((p - min(cs)) / (max(cs) - min(cs) + 1e-6), 0, 1)[..., None]
        rgb = np.array(c1, np.float32) * (1 - t) + np.array(c2, np.float32) * t
    if shine:
        h = y1 - y0
        k = np.clip(1 - (Y - y0) / (0.5 * h + 1e-6), 0, 1)[..., None] ** 1.6 * shine
        rgb = rgb * (1 - k) + 255 * k
    out.paste(Image.fromarray(np.dstack([rgb, a * 255]).clip(0, 255).astype(np.uint8), "RGBA"), (x0, y0))
    return out

def fill_radial(m, c_in, c_out, cx, cy, r, alpha=1.0):
    a = arr(m) * alpha
    t = np.clip(np.sqrt((XX - cx) ** 2 + (YY - cy) ** 2) / r, 0, 1)[..., None]
    rgb = np.array(c_in, np.float32) * (1 - t) + np.array(c_out, np.float32) * t
    return Image.fromarray(np.dstack([rgb, a * 255]).clip(0, 255).astype(np.uint8), "RGBA")

def glow(m, r, color, strength=1.0):
    """Two-stage neon glow (tight core + wide halo) from a mask, never clipped. Computed in a padded bbox (fast)."""
    out = blank()
    bb = m.getbbox()
    if not bb:
        return out
    box = _box(bb, int(r * 3) + 4)
    mc = m.crop(box)
    a1 = arr(mc.filter(ImageFilter.GaussianBlur(max(1, r * 0.3))))
    a2 = arr(mc.filter(ImageFilter.GaussianBlur(max(1, r))))
    a = 1 - (1 - np.clip(a1 * 0.85 * strength, 0, 1)) * (1 - np.clip(a2 * 1.25 * strength, 0, 1))
    rgb = np.empty(a.shape + (3,), np.float32); rgb[:] = color
    out.paste(Image.fromarray(np.dstack([rgb, a * 255]).clip(0, 255).astype(np.uint8), "RGBA"), box[:2])
    return out

def m_sub(a, b):  return ImageChops.subtract(a, b)
def m_add(a, b):  return ImageChops.lighter(a, b)
def m_mul(a, b):  return ImageChops.multiply(a, b)

class Frame:
    """Two layers: `core` (clipped into the die-cut) and `free` (solid pieces allowed outside it)."""
    def __init__(self):
        self.core = blank()
        self.free = None

    def add(self, layer):
        self.core.alpha_composite(layer)
        return self

    def neon(self, m, c1, c2=None, angle=90, gcol=None, r=30, s=1.0, shine=0.0, alpha=1.0):
        if gcol is not None and s > 0:
            self.add(glow(m, r, gcol, s * alpha))
        self.add(fill(m, c1, c2, angle, shine, alpha))
        return self

    def add_free(self, layer):
        if self.free is None:
            self.free = blank()
        self.free.alpha_composite(layer)
        return self

    def out(self):
        return (self.core, self.free)

# ---------------------------------------------------------------- registry
STICKERS = {}
def sticker(name, group, dur=2.0, fps=20, emoji=True, cut="union"):
    """cut: 'union' = one stable silhouette for the whole loop, 'frame' = silhouette per frame."""
    def deco(fn):
        STICKERS[name] = dict(fn=fn, group=group, dur=dur, fps=fps, emoji=emoji, cut=cut)
        return fn
    return deco

C = S / 2  # centre

# =====================================================================
#  BRAND
# =====================================================================
@sticker("ai-pulse", "brand", dur=2.0)
def ai_pulse(t):
    F = Frame()
    p = 0.5 + 0.5 * wave(t, 1, -0.25)
    for k in range(2):
        u = (t + k * 0.5) % 1
        pen = Pen(); pen.ring(C, C, 330 + 100 * ease_out(u), 6 + 10 * (1 - u)); m = pen.done()
        F.neon(m, CYAN, gcol=CYAN, r=14, s=0.6, alpha=(1 - u) * 0.85)
    m = src_mask(AI_A, 560, C, C)
    col = lerp(BLUE, CYAN, p)
    F.neon(m, WHITE, ICE, 90, gcol=col, r=38 + 36 * p, s=1.0 + 0.5 * p, shine=0.15)
    return F.out()

@sticker("ai-flip", "brand", dur=2.0)
def ai_flip(t):
    F = Frame()
    sx = math.cos(2 * math.pi * ease(t * 2 % 1) / 2 + math.pi * (t >= 0.5))
    front = sx >= 0
    shade = 0.55 + 0.45 * abs(sx)
    m = src_mask(AI_A, 600, C, C + 10 * wave(t, 1), sx=max(0.02, abs(sx)))
    if front:
        F.neon(m, lerp(BLACKISH, WHITE, shade), lerp(BLACKISH, ICE, shade), 90, gcol=BLUE, r=40, s=0.9 * shade)
    else:
        F.neon(m, lerp(BLACKISH, CYAN, shade), lerp(BLACKISH, BLUE, shade), 90, gcol=CYAN, r=40, s=1.1 * shade)
    return F.out()
BLACKISH = (40, 60, 90)

_FLICK = [1, 1, 1, 1, 1, .2, 1, 1, .05, 1, 1, 1, 1, 1, 1, 1, .5, .8, 1, 1,
          1, 1, 1, 1, 1, 1, 1, .15, .9, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1]
@sticker("ionity-neon", "brand", dur=2.0)
def ionity_neon(t):
    F = Frame()
    k = _FLICK[int(t * len(_FLICK)) % len(_FLICK)]
    m = src_mask(WM_A, 820, C, C)
    F.add(fill(m, DIM))
    if k > 0.1:
        F.neon(m, lerp(DIM, ICE, k), lerp(DIM, CYAN, k), 90, gcol=CYAN, r=46, s=1.5 * k)
    return F.out()

@sticker("ionity-scan", "brand", dur=2.0)
def ionity_scan(t):
    F = Frame()
    m = src_mask(WM_A, 820, C, C)
    F.neon(m, BLUE, LOGO_BLUE, 90, gcol=BLUE, r=30, s=0.7, shine=0.12)
    x = -260 + (S + 520) * ease(t)
    pen = Pen(); pen.poly([(x - 60, 300), (x + 40, 300), (x - 80, 724), (x - 180, 724)]); band = pen.done()
    band = band.filter(ImageFilter.GaussianBlur(10))
    hb = m_mul(band, m)
    F.neon(hb, WHITE, CYAN, 0, gcol=CYAN, r=24, s=1.2)
    return F.out()

@sticker("ionity-typing", "brand", dur=3.0, emoji=False)
def ionity_typing(t):
    F = Frame()
    full = "> IONITY"
    n = int(len(full) * seg(t, 0.08, 0.5) + 0.999) if t > 0.08 else 0
    size = 150
    x0 = C - text_w(full + "_", MONO, size) / 2
    blink = (t * 6) % 1 < 0.55
    pen = Pen(); pen.text(x0, C - 40, full[:n] + ("_" if blink or n < len(full) else " "), MONO, size, anchor="lm")
    F.neon(pen.done(), WHITE, CYAN, 90, gcol=CYAN, r=26, s=1.1)
    sub = "Building Tomorrow, Today."
    k = int(len(sub) * seg(t, 0.55, 0.85))
    if k:
        x1 = C - text_w(sub, MONO_R, 46) / 2
        pen = Pen(); pen.text(x1, C + 100, sub[:k], MONO_R, 46, anchor="lm")
        F.neon(pen.done(), WHITE, gcol=BLUE, r=12, s=0.6)
    return F.out()

@sticker("ai-loader", "brand", dur=2.0)
def ai_loader(t):
    F = Frame()
    a0 = 360 * t
    pen = Pen()
    for k in range(24):           # comet tail, fading
        f = k / 24
        pen.arc(C, C, 392, a0 + f * 150, a0 + f * 150 + 8, 26 * (0.4 + 0.6 * f), fill=int(255 * f ** 1.3), caps=False)
    pen.arc(C, C, 392, a0 + 148, a0 + 160, 26)
    m1 = pen.done()
    pen = Pen(); pen.arc(C, C, 392, a0 + 200, a0 + 250, 18); m2 = pen.done()
    pen = Pen(); pen.arc(C, C, 318, -a0 * 2, -a0 * 2 + 70, 10); m3 = pen.done()
    F.neon(m1, CYAN, gcol=CYAN, r=22, s=0.9)
    F.neon(m2, BLUE, gcol=BLUE, r=18, s=0.8)
    F.neon(m3, WHITE, alpha=0.7)
    mk = src_mask(AI_A, 400, C, C)
    F.neon(mk, WHITE, ICE, 90, gcol=BLUE, r=34, s=0.8, shine=0.15)
    return F.out()

@sticker("ionity-wordmark-anim", "brand", dur=2.5, emoji=False)
def ionity_wordmark_anim(t):
    """Hi-res remake of the site's animated wordmark: zoom-in, shimmer, zoom-out."""
    F = Frame()
    if t < 0.3:
        sc = back_out(seg(t, 0, 0.3), 1.4)
    elif t < 0.85:
        sc = 1 + 0.02 * wave(seg(t, 0.3, 0.85), 1)
    else:
        sc = 1 - ease(seg(t, 0.85, 1.0))
    sc = max(sc, 0.02)
    m = src_mask(WM_A, 820 * sc, C, C)
    F.neon(m, CYAN, LOGO_BLUE, 90, gcol=BLUE, r=34, s=0.9, shine=0.1)
    if 0.3 <= t < 0.85:
        x = -200 + (S + 400) * seg(t, 0.35, 0.8)
        pen = Pen(); pen.poly([(x, 330), (x + 70, 330), (x - 40, 694), (x - 110, 694)])
        F.neon(m_mul(pen.done().filter(ImageFilter.GaussianBlur(8)), m), WHITE, gcol=CYAN, r=18, s=1.0)
    return F.out()

_TAGS = ["Native-AI", "AIoT", "Cloud", "Edge", "Audit"]
@sticker("ionity-global-badge", "brand", dur=3.0, emoji=False)
def ionity_global_badge(t):
    F = Frame()
    mk = src_mask(AI_A, 330, C, 330 + 8 * wave(t, 1))
    F.neon(mk, WHITE, ICE, 90, gcol=BLUE, r=30, s=0.8, shine=0.15)
    pen = Pen(); pen.text(C, 590, "IONITY GLOBAL", SANS, 96)
    F.neon(pen.done(), WHITE, (190, 225, 255), 90, gcol=BLUE, r=14, s=0.5)
    pen = Pen(); pen.line([(260, 668), (764, 668)], 5); F.add(fill(pen.done(), BLUE, CYAN, 0))
    u = t * len(_TAGS)
    tag = _TAGS[int(u) % len(_TAGS)]
    k = int((len(tag) + 4) * min(1, (u % 1) / 0.35))
    s = ("[ " + tag + " ]")[:k]
    pen = Pen(); pen.text(C, 735, s, MONO, 50)
    F.neon(pen.done(), CYAN, gcol=CYAN, r=14, s=0.9)
    return F.out()

# =====================================================================
#  REACTIONS
# =====================================================================
@sticker("yes-check", "reaction", dur=1.8)
def yes_check(t):
    F = Frame()
    pop = 1 + 0.12 * math.sin(math.pi * seg(t, 0.55, 0.75)) if 0.55 < t < 0.75 else 1
    pen = Pen(scale=pop)
    a = seg(t, 0.0, 0.35)
    if a > 0:
        pen.arc(C, C, 340, -90, -90 + 360 * ease_out(a), 30)
    pts = [(330, 530), (460, 655), (710, 385)]
    c = seg(t, 0.3, 0.6) * 2
    if c > 0:
        p = [pts[0]]
        for k in (1, 2):
            if c >= k: p.append(pts[k])
            else:
                f = ease_out(c - (k - 1)); p.append((pts[k-1][0] + (pts[k][0] - pts[k-1][0]) * f,
                                                     pts[k-1][1] + (pts[k][1] - pts[k-1][1]) * f)); break
        pen.line(p, 62)
    m = pen.done()
    gl = 1.0 + 0.5 * math.sin(math.pi * seg(t, 0.6, 1.0))
    F.neon(m, (120, 255, 200), GREEN, 90, gcol=GREEN, r=30, s=gl, shine=0.1)
    return F.out()

@sticker("no-x", "reaction", dur=1.8)
def no_x(t):
    F = Frame()
    shake = 22 * math.sin(t * 90) * (1 - seg(t, 0.55, 0.8)) if 0.45 < t < 0.8 else 0
    pen = Pen(dx=shake)
    a = seg(t, 0, 0.3)
    if a > 0:
        pen.arc(C, C, 340, -90, -90 + 360 * ease_out(a), 30)
    L1 = 190 * ease_out(seg(t, 0.2, 0.38)); L2 = 190 * ease_out(seg(t, 0.32, 0.5))
    if L1 > 1: pen.line([(C - 190, C - 190), (C - 190 + 2 * L1, C - 190 + 2 * L1)], 62)
    if L2 > 1: pen.line([(C + 190, C - 190), (C + 190 - 2 * L2, C - 190 + 2 * L2)], 62)
    F.neon(pen.done(), (255, 120, 110), RED, 90, gcol=RED, r=30, s=1.1, shine=0.1)
    return F.out()

@sticker("thinking", "reaction", dur=2.4)
def thinking(t):
    F = Frame()
    mk = src_mask(AI_A, 400, 450, 520, rot=6 * wave(t, 1))
    F.neon(mk, WHITE, ICE, 90, gcol=BLUE, r=30, s=0.8, shine=0.15)
    pen = Pen(); pen.text(770, 250 + 18 * wave(t, 2), "?", SANS, 300)
    F.neon(pen.done(), WHITE, CYAN, 90, gcol=CYAN, r=26, s=1.2)
    for k in range(3):
        on = int(t * 6) % 4 > k
        pen = Pen(); pen.circle(380 + k * 85, 790, 26); m = pen.done()
        F.neon(m, CYAN if on else DIM, gcol=CYAN if on else None, r=14, s=0.9)
    return F.out()

def _flame(t, layer, scale, by, n=36):
    left, right = [], []
    r, h = 250 * scale, 650 * scale
    for k in range(n + 1):
        u = k / n
        hw = r * (1 - u) ** 0.85 * min(1.0, u / 0.25) ** 0.55
        sway = (wave(t, 2, layer * 0.2) * 60 * u * u + wave(t, 3, u * 1.4 + layer * 0.3) * 22 * u)
        left.append((C - hw + sway, by - h * u)); right.append((C + hw + sway, by - h * u))
    pen = Pen(); pen.poly(left + right[::-1])
    return pen.done().filter(ImageFilter.GaussianBlur(2))

@sticker("ion-fire", "reaction", dur=1.6)
def ion_fire(t):
    F = Frame()
    m1 = _flame(t, 0, 1.0 + 0.03 * wave(t, 4), 870)
    m2 = _flame(t, 1, 0.70 + 0.03 * wave(t, 4, 0.3), 850)
    m3 = _flame(t, 2, 0.40 + 0.02 * wave(t, 4, 0.6), 830)
    F.add(glow(m1, 50, BLUE, 1.2))
    F.add(fill(m1, CYAN, BLUE, 90))
    F.add(glow(m2, 20, CYAN, 0.8)); F.add(fill(m2, ICE, CYAN, 90))
    F.add(fill(m3, WHITE, ICE, 90))
    pen = Pen()
    rnd = random.Random(7)
    for i in range(9):
        ph = rnd.random(); x0 = C + rnd.uniform(-170, 170)
        u = (t * 2 + ph) % 1
        y = 760 - 560 * u; x = x0 + 30 * math.sin(u * 7 + i)
        pen.circle(x, y, 13 * (1 - u) + 2)
    F.neon(pen.done(), WHITE, gcol=CYAN, r=12, s=1.0)
    return F.out()

_CONF = None
@sticker("celebrate", "reaction", dur=2.4, cut="union")
def celebrate(t):
    global _CONF
    if _CONF is None:
        rnd = random.Random(986)
        cols = [CYAN, BLUE, GREEN, AMBER, RED, LOGO_BLUE]
        _CONF = [(rnd.uniform(0, 1), rnd.uniform(-math.pi * 0.95, -math.pi * 0.05), rnd.uniform(520, 760),
                  rnd.choice(cols), rnd.uniform(0, 6.28), rnd.uniform(3, 9), rnd.choice((0, 1))) for _ in range(46)]
    F = Frame()
    bounce = -abs(math.sin(t * math.pi * 2)) * 46
    mk = src_mask(AI_A, 460, C, C + bounce)
    F.neon(mk, WHITE, ICE, 90, gcol=CYAN, r=40, s=1.1, shine=0.15)
    # confetti burst - solid pieces drawn outside the die-cut (free layer)
    big = Image.new("RGBA", (S * SS, S * SS), (0, 0, 0, 0)); d = ImageDraw.Draw(big)
    for (ph, ang, v, col, rot0, spin, kind) in _CONF:
        u = (t + ph) % 1
        x = C + math.cos(ang) * v * u
        y = C - 40 + math.sin(ang) * v * u + 900 * u * u
        if not (90 < x < S - 90 and 90 < y < S - 90):
            continue
        sz = 18 * (1 - 0.5 * u)
        a = rot0 + spin * u
        if kind:
            d.polygon([(px * SS, py * SS) for px, py in
                       [(x + sz * 1.4 * math.cos(a), y + sz * 1.4 * math.sin(a)),
                        (x + sz * .6 * math.cos(a + 1.57), y + sz * .6 * math.sin(a + 1.57)),
                        (x - sz * 1.4 * math.cos(a), y - sz * 1.4 * math.sin(a)),
                        (x - sz * .6 * math.cos(a + 1.57), y - sz * .6 * math.sin(a + 1.57))]], fill=col + (255,))
        else:
            r = sz * 0.75
            d.ellipse(((x - r) * SS, (y - r) * SS, (x + r) * SS, (y + r) * SS), fill=col + (255,))
    conf = big.resize((S, S), Image.BOX)
    keep = ImageChops.invert(mk.filter(ImageFilter.GaussianBlur(26)).point(lambda v: 255 if v > 8 else 0))
    conf.putalpha(ImageChops.multiply(conf.getchannel("A"), keep))   # never draw confetti over the mark
    F.add_free(conf)
    return F.out()

@sticker("warning", "reaction", dur=1.6)
def warning(t):
    F = Frame()
    on = (t * 4) % 1 < 0.6
    sh = 8 * math.sin(t * 120) if on and (t * 4) % 1 < 0.15 else 0
    pen = Pen(dx=sh)
    tri = [(C, 175), (870, 805), (154, 805)]
    pen.poly(tri); pen.line(tri + [tri[0]], 70)
    pen.rrect(C - 34, 390, C + 34, 640, 34, fill=0)
    pen.circle(C, 715, 40, fill=0)
    m = pen.done()
    F.neon(m, AMBER, (255, 90, 40), 90, gcol=(255, 120, 40) if on else None, r=34, s=1.3 if on else 0, shine=0.18,
           alpha=1.0 if on else 0.78)
    return F.out()

def _heart_pts(cx, cy, s, n=120):
    pts = []
    for i in range(n):
        a = 2 * math.pi * i / n
        x = 16 * math.sin(a) ** 3
        y = 13 * math.cos(a) - 5 * math.cos(2 * a) - 2 * math.cos(3 * a) - math.cos(4 * a)
        pts.append((cx + x * s, cy - y * s))
    return pts

@sticker("heartbeat", "reaction", dur=1.5)
def heartbeat(t):
    F = Frame()
    b = 0.16 * math.sin(math.pi * seg(t, 0.0, 0.14)) + 0.22 * math.sin(math.pi * seg(t, 0.2, 0.38))
    sc = 1 + b
    pen = Pen(); pen.poly(_heart_pts(C, C - 10, 21 * sc)); m = pen.done()
    F.neon(m, CYAN, BLUE, 90, gcol=lerp(BLUE, CYAN, b / 0.22), r=36, s=0.8 + 2 * b, shine=0.28)
    # ECG trace across the heart
    ecg = [(250, 520), (390, 520), (430, 470), (470, 520), (500, 520), (535, 350), (575, 650), (610, 520), (650, 520),
           (690, 485), (725, 520), (780, 520)]
    total = sum(math.dist(ecg[i], ecg[i + 1]) for i in range(len(ecg) - 1))
    dist = total * seg(t, 0.0, 0.7)
    if dist > 0:
        pts, acc = [ecg[0]], 0
        for i in range(len(ecg) - 1):
            sl = math.dist(ecg[i], ecg[i + 1])
            if acc + sl >= dist:
                f = (dist - acc) / sl
                pts.append((ecg[i][0] + (ecg[i+1][0] - ecg[i][0]) * f, ecg[i][1] + (ecg[i+1][1] - ecg[i][1]) * f)); break
            pts.append(ecg[i + 1]); acc += sl
        pen = Pen(scale=sc, center=(C, C - 10)); pen.line(pts, 16);
        F.neon(pen.done(), WHITE, gcol=WHITE, r=10, s=0.5, alpha=1 - seg(t, 0.75, 1.0))
    return F.out()

@sticker("hundred", "reaction", dur=2.5)
def hundred(t):
    F = Frame()
    n = int(round(100 * ease(seg(t, 0.0, 0.6))))
    done = n == 100
    pen = Pen(); pen.text(C, 430, f"{n}%", MONO, 240)
    F.neon(pen.done(), WHITE if done else ICE, CYAN if done else BLUE, 90, gcol=CYAN, r=34,
           s=0.8 + (0.6 + 0.3 * wave(t, 3) if done else 0))
    pen = Pen(); pen.rrect(170, 615, 854, 665, 25, width=6); F.add(fill(pen.done(), CYAN, alpha=0.7))
    if n:
        pen = Pen(); pen.rrect(182, 627, 182 + 660 * n / 100, 653, 13); F.neon(pen.done(), BLUE, CYAN, 0, gcol=CYAN, r=14, s=0.8)
    pen = Pen(); pen.text(C, 745, "SYSTEM OPTIMAL" if done else "optimising...", MONO if done else MONO_R, 54)
    F.neon(pen.done(), GREEN if done else WHITE, gcol=GREEN if done else None, r=12, s=0.8)
    return F.out()

@sticker("bolt", "reaction", dur=1.5)
def bolt(t):
    F = Frame()
    ph = (t * 2) % 1
    flash = ph < 0.25
    pts = [(600, 130), (330, 560), (490, 560), (420, 900), (705, 440), (540, 440), (660, 130)]
    pen = Pen(); pen.poly(pts); pen.line(pts + [pts[0]], 26); m = pen.done()
    F.neon(m, WHITE if flash else ICE, CYAN if flash else BLUE, 90, gcol=CYAN, r=52 if flash else 28,
           s=1.7 if flash else 0.8, shine=0.2)
    if flash:
        pen = Pen()
        for a in (200, 240, 320, 20):
            r0, r1 = 300, 300 + 120 * (1 - ph / 0.25)
            pen.line([(C + r0 * math.cos(math.radians(a)), C + r0 * math.sin(math.radians(a))),
                      (C + r1 * math.cos(math.radians(a)), C + r1 * math.sin(math.radians(a)))], 14)
        F.neon(pen.done(), WHITE, gcol=CYAN, r=12, s=1.0)
    return F.out()

def _thumb_mask():
    pen = Pen()
    pen.rrect(190, 495, 320, 865, 34)                         # cuff
    pen.rrect(345, 470, 720, 865, 80)                         # fist
    rows = [(470, 560, 812), (562, 652, 800), (654, 744, 782), (746, 836, 752)]
    for (y0, y1, x1) in rows:                                 # fingers
        pen.rrect(560, y0, x1, y1, (y1 - y0) / 2)
    pen.line([(455, 520), (535, 215)], 128)                  # thumb
    for (y0, _, x1) in rows[1:]:                              # finger gaps
        pen.line([(640, y0 - 1), (x1 - 30, y0 - 1)], 10, fill=0, caps=False)
    pen.line([(332, 500), (332, 860)], 18, fill=0, caps=False)  # cuff gap
    return pen.done()
_THUMB = None

@sticker("thumbs-up", "reaction", dur=1.8)
def thumbs_up(t):
    global _THUMB
    if _THUMB is None:
        _THUMB = _thumb_mask()
    F = Frame()
    pop = back_out(seg(t, 0, 0.3), 2.2) if t < 0.3 else 1 + 0.04 * wave(seg(t, 0.3, 1), 2)
    rot = 12 * math.sin(math.pi * 2 * seg(t, 0.3, 1.0)) * (1 - seg(t, 0.7, 1.0))
    m = _THUMB.rotate(rot, resample=Image.BICUBIC, center=(C, 700))
    pop = max(pop, 0.05)
    m = m.resize((int(S * pop), int(S * pop)), Image.LANCZOS)
    mm = L(); off = int((S - m.width) / 2); mm.paste(m, (off, off)) if off >= 0 else mm.paste(m.crop((-off, -off, -off + S, -off + S)))
    F.neon(mm, CYAN, BLUE, 60, gcol=CYAN, r=34, s=1.0, shine=0.2)
    if t > 0.22:   # sparkles on the pop
        u = seg(t, 0.22, 0.6)
        if u < 1:
            pen = Pen()
            for (x, y) in ((250, 230), (760, 260), (820, 470)):
                r = 34 * math.sin(math.pi * u)
                pen.poly([(x, y - r), (x + r * .3, y - r * .3), (x + r, y), (x + r * .3, y + r * .3),
                          (x, y + r), (x - r * .3, y + r * .3), (x - r, y), (x - r * .3, y - r * .3)])
            F.neon(pen.done(), WHITE, gcol=CYAN, r=12, s=1.0)
    return F.out()

# =====================================================================
#  TAGLINES & ASCII
# =====================================================================
def _typewriter(t, lines, size, col1, col2, gcol, sub=None, t_end=0.55):
    F = Frame()
    total = sum(len(l) for l in lines)
    n = int(total * seg(t, 0.03, t_end))
    lh = size * 1.22
    y0 = C - (len(lines) - 1) * lh / 2 - (40 if sub else 0)
    blink = (t * 5) % 1 < 0.55
    pen = Pen(); left = n; cursor = None
    for i, ln in enumerate(lines):
        x = C - text_w(ln, MONO, size) / 2
        y = y0 + i * lh
        show = ln[:max(0, left)]
        if show:
            pen.text(x, y, show, MONO, size, anchor="lm")
        if cursor is None and left <= len(ln):
            cursor = (x + text_w(show, MONO, size), y)
        left -= len(ln)
    if cursor and n < total and blink:
        pen.text(cursor[0], cursor[1], "_", MONO, size, anchor="lm")
    hold = seg(t, t_end, t_end + 0.12)
    F.neon(pen.done(), col1, col2, 90, gcol=gcol, r=22 + 18 * hold, s=0.9 + 0.7 * hold)
    if sub and hold > 0:
        k = int(len(sub) * seg(t, t_end + 0.05, t_end + 0.3))
        pen = Pen(); pen.text(C, y0 + len(lines) * lh + 10, sub[:k], MONO_R, 46)
        F.neon(pen.done(), CYAN, gcol=CYAN, r=10, s=0.6)
    return F.out()

@sticker("tagline-building-tomorrow", "tagline", dur=3.0, emoji=False)
def tagline_btt(t):
    return _typewriter(t, ["BUILDING", "TOMORROW,", "TODAY."], 118, WHITE, ICE, CYAN, sub="ionity.today")

@sticker("tagline-anything-possible", "tagline", dur=3.0, emoji=False)
def tagline_god(t):
    return _typewriter(t, ["ANYTHING IS", "POSSIBLE", "WITH GOD."], 112, ICE, CYAN, CYAN, sub="Johan W. van Antwerp")

_POSES = [" o \n/|\\\n/ \\", " o \n/|\\\n| |", " o \n\\|/\n/ \\", " o \n/|\\\n| |"]
@sticker("ascii-ioman-run", "tagline", dur=1.6, fps=10, emoji=False)
def ioman_run(t):
    F = Frame()
    i = int(t * 16)
    pen = Pen(); pen.text(C, 170, "IO-MAN", MONO, 116)
    F.neon(pen.done(), WHITE, ICE, 90, gcol=BLUE, r=14, s=0.7)
    pen = Pen(); pen.text(C, 255, "GET OVER IT DOOR", MONO_R, 42)
    F.neon(pen.done(), CYAN, gcol=CYAN, r=8, s=0.5)
    pen = Pen(); pen.text(C, 530, _POSES[i % 4], MONO, 150, spacing=4)
    F.neon(pen.done(), CYAN, gcol=CYAN, r=22, s=1.1)
    ground = "-=-=-=-=-=-=-=-=-=-=-"
    off = (i * 2) % 4
    pen = Pen(); pen.text(C, 790, ground[off:off + 15], MONO, 72)
    F.neon(pen.done(), BLUE, gcol=BLUE, r=12, s=0.6)
    return F.out()

_FACES = ["(o_o)", "(o_o)", "(o_o)", "(-_-)", "(o_o)", "(>_<)", "(o_o)", "(^_^)", "(o o)", "(O_O)", "(o_o)", "(-_-)"]
@sticker("ascii-spore", "tagline", dur=2.4, fps=5)
def ascii_spore(t):
    F = Frame()
    i = int(t * 12) % 12
    pen = Pen(); pen.text(C, C - 60, _FACES[i], MONO, 200)
    F.neon(pen.done(), WHITE, CYAN, 90, gcol=CYAN, r=22, s=1.0)
    pen = Pen(); pen.text(C, C + 120, "/|\\" if i % 2 else "\\|/", MONO, 120)
    F.neon(pen.done(), BLUE, gcol=BLUE, r=14, s=0.7)
    pen = Pen(); pen.text(C, 800, "spore #" + str(13 - i % 13).zfill(2), MONO_R, 46)
    F.add(fill(pen.done(), WHITE, alpha=0.8))
    return F.out()

_TERM = [("$ ionity --deploy edge", CYAN), ("[AEDI] policy 986 AED .. ok", None), ("[AIoT] nodes online .... 12", None),
         ("[EDGE] inference ....... ok", None), ("[SEC ] audit trail ..... ok", None), ("", None),
         ("> STATUS: ALL SYSTEMS GO", GREEN)]
@sticker("terminal-ok", "tagline", dur=3.0, emoji=False)
def terminal_ok(t):
    F = Frame()
    pen = Pen(); pen.rrect(100, 180, 924, 844, 44); win = pen.done()
    F.add(glow(win, 26, BLUE, 0.6))
    F.add(fill(win, (16, 24, 40), (8, 12, 22), 90))
    pen = Pen(); pen.rrect(100, 180, 924, 844, 44, width=6); F.add(fill(pen.done(), CYAN, BLUE, 90, alpha=0.9))
    pen = Pen(); pen.rrect(106, 186, 918, 256, 38); pen.rrect(106, 220, 918, 256, 0); F.add(fill(pen.done(), (24, 40, 70)))
    for k, c in enumerate((RED, AMBER, GREEN)):
        pen = Pen(); pen.circle(160 + k * 52, 221, 15); F.add(fill(pen.done(), c))
    pen = Pen(); pen.text(C, 221, "ionity@edge:~", MONO_R, 30); F.add(fill(pen.done(), (150, 180, 220)))
    n = int(len(_TERM) * seg(t, 0.05, 0.7) + 0.999) if t > 0.05 else 0
    blink = (t * 5) % 1 < 0.55
    y = 310
    for k, (ln, col) in enumerate(_TERM[:n]):
        if ln:
            pen = Pen(); pen.text(140, y, ln, MONO if col else MONO_R, 40, anchor="lm")
            if col is None:
                head, tail = ln.rsplit(" ", 1)
                pen = Pen(); pen.text(140, y, head + " ", MONO_R, 40, anchor="lm"); F.add(fill(pen.done(), (170, 215, 255)))
                pen = Pen(); pen.text(140 + text_w(head + " ", MONO_R, 40), y, tail, MONO, 40, anchor="lm")
                F.neon(pen.done(), GREEN, gcol=GREEN, r=8, s=0.6)
            else:
                g = col == GREEN
                F.neon(pen.done(), col, gcol=col, r=14 if g else 6, s=(1.0 + 0.4 * wave(t, 3)) if g else 0.4)
        y += 72
    if blink and n < len(_TERM):
        pen = Pen(); pen.rrect(140, y - 22, 166, y + 22, 3); F.add(fill(pen.done(), WHITE))
    return F.out()

# =====================================================================
#  TECH
# =====================================================================
@sticker("chip", "tech", dur=2.0)
def chip(t):
    F = Frame()
    p = 0.5 + 0.5 * wave(t, 1)
    pen = Pen()
    for k in range(5):
        o = 316 + k * 98
        for (a, b) in [((o, 165), (o, 300)), ((o, 724), (o, 859)), ((165, o), (300, o)), ((724, o), (859, o))]:
            pen.line([a, b], 30)
    F.neon(pen.done(), (120, 160, 255), BLUE, 90, gcol=BLUE, r=18, s=0.5)
    # data pulses travelling outwards along pins
    pen = Pen()
    for k in range(5):
        o = 316 + k * 98
        u = (t * 2 + k * 0.37) % 1
        d = 300 - 135 * u
        for (x, y) in [(o, d), (o, S - d), (d, o), (S - d, o)]:
            pen.circle(x, y, 13)
    F.neon(pen.done(), WHITE, gcol=CYAN, r=12, s=1.2)
    pen = Pen(); pen.rrect(270, 270, 754, 754, 54); body = pen.done()
    F.add(glow(body, 30 + 26 * p, CYAN, 0.5 + 0.5 * p))
    F.add(fill(body, (22, 40, 78), (10, 18, 36), 90))
    pen = Pen(); pen.rrect(270, 270, 754, 754, 54, width=18); F.neon(pen.done(), CYAN, BLUE, 90, shine=0.25)
    pen = Pen(); pen.rrect(392, 392, 632, 632, 26); core = pen.done()
    mk = src_mask(AI_A, 190, C, C)
    F.neon(m_sub(core, mk), lerp(BLUE, WHITE, p), lerp(LOGO_BLUE, CYAN, p), 90, gcol=CYAN, r=20, s=0.6 + 0.6 * p, shine=0.2)
    return F.out()

def _cloud_mask():
    pen = Pen()
    for (cx, cy, r) in [(370, 560, 165), (545, 445, 225), (720, 560, 165)]:
        pen.circle(cx, cy, r)
    pen.rrect(205, 520, 885, 725, 102)
    return pen.done()
_CLOUD = None

@sticker("cloud-sync", "tech", dur=2.0)
def cloud_sync(t):
    global _CLOUD
    if _CLOUD is None:
        _CLOUD = _cloud_mask()
    F = Frame()
    a = 180 * ease(t)  # two arrows => 180 deg is a seamless loop
    pen = Pen()
    cx, cy, r = 545, 575, 110
    for k in (0, 180):
        a0 = a + k + 20
        a1 = a0 + 130
        pen.arc(cx, cy, r, a0, a1, 34)
        ex, ey = cx + r * math.cos(math.radians(a1)), cy + r * math.sin(math.radians(a1))
        tx, ty = -math.sin(math.radians(a1)), math.cos(math.radians(a1))   # tangent (clockwise)
        nx, ny = math.cos(math.radians(a1)), math.sin(math.radians(a1))
        pen.poly([(ex + tx * 58, ey + ty * 58), (ex + nx * 46, ey + ny * 46), (ex - nx * 46, ey - ny * 46)])
    arrows = pen.done()
    F.neon(m_sub(_CLOUD, arrows), (120, 230, 255), BLUE, 90, gcol=BLUE, r=34, s=0.9, shine=0.22)
    return F.out()

@sticker("ion-orbit", "tech", dur=2.0)
def ion_orbit(t):
    F = Frame()
    orb = Pen()
    back, front = Pen(), Pen()
    for k in range(3):
        ang = math.radians(k * 60)
        pts = []
        for i in range(121):
            ph = 2 * math.pi * i / 120
            ex, ey = 390 * math.cos(ph), 140 * math.sin(ph)
            pts.append((C + ex * math.cos(ang) - ey * math.sin(ang), C + ex * math.sin(ang) + ey * math.cos(ang)))
        orb.line(pts, 10, caps=False)
        ph = 2 * math.pi * (t * (1 + (k == 1)) + k / 3)
        ex, ey = 390 * math.cos(ph), 140 * math.sin(ph)
        x, y = C + ex * math.cos(ang) - ey * math.sin(ang), C + ex * math.sin(ang) + ey * math.cos(ang)
        (front if math.sin(ph) > 0 else back).circle(x, y, 32)
    F.neon(back.done(), CYAN, gcol=CYAN, r=20, s=0.8, alpha=0.75)
    F.neon(orb.done(), BLUE, gcol=BLUE, r=14, s=0.6, alpha=0.9)
    pen = Pen(); pen.circle(C, C, 100); nuc = pen.done()
    F.add(glow(nuc, 40, CYAN, 0.9 + 0.3 * wave(t, 2)))
    F.add(fill_radial(nuc, WHITE, (60, 170, 255), C - 30, C - 30, 150))
    F.neon(front.done(), ICE, CYAN, 90, gcol=CYAN, r=20, s=1.0)
    return F.out()

_TRACE = [(140, 600), (300, 600), (380, 520), (520, 520), (580, 460), (580, 360), (680, 360), (760, 440), (884, 440)]
@sticker("circuit-trace", "tech", dur=2.0)
def circuit_trace(t):
    F = Frame()
    segs = [math.dist(_TRACE[k], _TRACE[k + 1]) for k in range(len(_TRACE) - 1)]
    total = sum(segs)
    def point_at(d):
        acc = 0
        for k, sl in enumerate(segs):
            if acc + sl >= d:
                f = (d - acc) / sl
                return (_TRACE[k][0] + (_TRACE[k+1][0] - _TRACE[k][0]) * f, _TRACE[k][1] + (_TRACE[k+1][1] - _TRACE[k][1]) * f)
            acc += sl
        return _TRACE[-1]
    def sub_path(d0, d1):
        d0, d1 = max(0, d0), min(total, d1)
        pts = [point_at(d0)]; acc = 0
        for k, sl in enumerate(segs):
            acc += sl
            if d0 < acc < d1: pts.append(_TRACE[k + 1])
        pts.append(point_at(d1)); return pts
    pen = Pen(); pen.line(_TRACE, 30)
    for p in (_TRACE[2], _TRACE[5], _TRACE[7]): pen.circle(*p, 26)
    F.neon(pen.done(), (40, 90, 150), DIM, 90)
    pen = Pen()
    for p in (_TRACE[0], _TRACE[-1]): pen.ring(*p, 46, 16)
    for p in (_TRACE[2], _TRACE[5], _TRACE[7]): pen.ring(*p, 26, 8)
    F.neon(pen.done(), CYAN, gcol=CYAN, r=14, s=0.8)
    head = total * ease(t) * 1.25 - 60
    if head > 0:
        pen = Pen(); pen.line(sub_path(head - 260, head), 22); F.neon(pen.done(), BLUE, CYAN, 0, gcol=CYAN, r=22, s=1.1)
        if head < total:
            pen = Pen(); pen.circle(*point_at(head), 30); F.neon(pen.done(), WHITE, gcol=CYAN, r=26, s=1.5)
    return F.out()

@sticker("signal", "tech", dur=1.6)
def signal(t):
    F = Frame()
    lit = int(t * 6) % 6
    for k in range(4):
        on = k < lit
        pen = Pen(); pen.arc(C, 770, 150 + k * 150, 225, 315, 46)
        F.neon(pen.done(), WHITE if on else DIM, CYAN if on else DIM, 90, gcol=CYAN if on else None, r=22, s=1.0)
    pen = Pen(); pen.circle(C, 770, 58)
    F.neon(pen.done(), WHITE if lit else DIM, CYAN if lit else DIM, 90, gcol=CYAN if lit else None, r=22, s=1.0)
    return F.out()

@sticker("edge-node", "tech", dur=2.0)
def edge_node(t):
    F = Frame()
    sats = [(C + 330 * math.cos(math.radians(a)), C + 330 * math.sin(math.radians(a))) for a in range(-90, 270, 60)]
    pen = Pen()
    for s in sats: pen.line([(C, C), s], 14, caps=False)
    F.add(fill(pen.done(), DIM))
    pen = Pen()
    for k, s in enumerate(sats):
        f = (t * 2 + k / 6) % 1
        if k % 2: f = 1 - f
        pen.circle(C + (s[0] - C) * f, C + (s[1] - C) * f, 16)
    F.neon(pen.done(), WHITE, gcol=CYAN, r=14, s=1.2)
    for k, s in enumerate(sats):
        pen = Pen(); pen.circle(*s, 56); m = pen.done()
        on = 0.5 + 0.5 * wave(t, 2, k / 6)
        F.neon(m, lerp(BLUE, CYAN, on), LOGO_BLUE, 90, gcol=BLUE, r=18, s=0.4 + 0.6 * on, shine=0.25)
    pen = Pen(); pen.circle(C, C, 128); hub = pen.done()
    mk = src_mask(AI_A, 150, C, C)
    F.add(glow(hub, 34, CYAN, 0.9))
    F.add(fill(m_sub(hub, mk), WHITE, ICE, 90))
    return F.out()

# =====================================================================
#  DIE-CUT + EXPORT
# =====================================================================
CUT_R = 46     # silhouette offset around the artwork (at 1024)
RIM_W = 7      # cyan rim width (at 1024)

def silhouette(alpha_L):
    m = alpha_L.point(lambda v: 255 if v > 150 else 0)
    m = m.filter(ImageFilter.GaussianBlur(CUT_R / 1.7)).point(lambda v: 255 if v > 6 else 0)
    m = m.filter(ImageFilter.GaussianBlur(3)).point(lambda v: max(0, min(255, (v - 128) * 3 + 128)))
    return m

def rim_of(sil):
    inner = sil.filter(ImageFilter.GaussianBlur(RIM_W)).point(lambda v: max(0, min(255, (v - 236) * 13)))
    return ImageChops.subtract(sil, inner)

def diecut(core, free, sil, rim):
    base = fill(sil, (16, 20, 30), DARK2, 90)
    base.alpha_composite(fill(rim, CYAN, BLUE, 90, alpha=0.95))
    art = core.copy()
    art.putalpha(ImageChops.multiply(core.getchannel("A"), sil))
    base.alpha_composite(art)
    base.alpha_composite(fill(rim, CYAN, BLUE, 90, alpha=0.55))   # rim over glow so the edge stays crisp
    if free is not None:
        base.alpha_composite(free)
    return base

def clean(core, free):
    out = core.copy()
    if free is not None:
        out.alpha_composite(free)
    return out

def render(name):
    meta = STICKERS[name]
    n = int(round(meta["dur"] * meta["fps"]))
    raw = [meta["fn"](i / n) for i in range(n)]
    if meta["cut"] == "union":
        u = L()
        for core, _ in raw:
            u = ImageChops.lighter(u, core.getchannel("A"))
        sil = silhouette(u); rim = rim_of(sil)
        cut = [diecut(c, f, sil, rim) for c, f in raw]
    else:
        cut = []
        for c, f in raw:
            sil = silhouette(c.getchannel("A")); cut.append(diecut(c, f, sil, rim_of(sil)))
    cln = [clean(c, f) for c, f in raw]
    return cut, cln

def rs(frames, size):
    return [f.resize((size, size), Image.LANCZOS) for f in frames]

# ---------------- writers
def save_webp(frames, path, fps, limit=None, qualities=(92, 85, 75, 62, 50)):
    for step in (1, 2):
        sub = frames[::step]
        for q in qualities:
            sub[0].save(path, save_all=True, append_images=sub[1:], duration=int(round(1000 * step / fps)), loop=0,
                        quality=q, method=4, alpha_quality=100, allow_mixed=False)
            if limit is None or os.path.getsize(path) <= limit:
                return os.path.getsize(path)
    print("  ! over limit", path, os.path.getsize(path), flush=True)
    return os.path.getsize(path)

def _gif_frames(frames, colors=255, dither=True):
    """Global adaptive palette over all frames, index 0 = transparent, Floyd-Steinberg dithering."""
    sample = []
    for f in frames[:: max(1, len(frames) // 12)]:
        a = np.asarray(f.getchannel("A")) > 127
        px = np.asarray(f.convert("RGB"))[a]
        if len(px):
            sample.append(px)
    px = np.concatenate(sample) if sample else np.zeros((1, 3), np.uint8)
    side = int(math.ceil(math.sqrt(len(px))))
    pad = np.zeros((side * side, 3), np.uint8); pad[:len(px)] = px; pad[len(px):] = px[0]
    pal_img = Image.fromarray(pad.reshape(side, side, 3), "RGB").quantize(colors, method=Image.Quantize.MEDIANCUT)
    pal = pal_img.getpalette()[: colors * 3]
    pal += [0] * (colors * 3 - len(pal))
    out = []
    for f in frames:
        q = f.convert("RGB").quantize(palette=pal_img, dither=Image.Dither.FLOYDSTEINBERG if dither else Image.Dither.NONE)
        idx = np.asarray(q, np.uint8).astype(np.int16) + 1
        idx[np.asarray(f.getchannel("A")) < 128] = 0
        im = Image.fromarray(idx.clip(0, 255).astype(np.uint8), "P")
        im.putpalette([0, 0, 0] + pal[: 255 * 3])
        im.info["transparency"] = 0
        out.append(im)
    return out

def save_gif(frames, path, fps, limit=None):
    for colors, step, dither in [(255, 1, True), (255, 1, False), (128, 1, False), (255, 2, False), (96, 2, False), (64, 3, False)]:
        sub = frames[::step]
        fr = _gif_frames(sub, colors, dither)
        fr[0].save(path, save_all=True, append_images=fr[1:], duration=int(round(1000 * step / fps)), loop=0,
                   disposal=2, transparency=0, optimize=False)
        if limit is None or os.path.getsize(path) <= limit:
            return os.path.getsize(path)
    print("  ! over limit", path, os.path.getsize(path), flush=True)
    return os.path.getsize(path)

def save_apng(frames, path, fps, limit=None):
    for step in (1, 2, 3):
        sub = frames[::step]
        sub[0].save(path, save_all=True, append_images=sub[1:], duration=int(round(1000 * step / fps)), loop=0,
                    disposal=1, blend=0, optimize=True)
        if limit is None or os.path.getsize(path) <= limit:
            return os.path.getsize(path)
    # last resort: reduce colour depth (RGBA quantise keeps per-pixel alpha)
    sub = [f.quantize(256, method=Image.Quantize.FASTOCTREE).convert("RGBA") for f in frames[::2]]
    sub[0].save(path, save_all=True, append_images=sub[1:], duration=int(round(2000 / fps)), loop=0, optimize=True)
    if limit and os.path.getsize(path) > limit:
        print("  ! over limit", path, os.path.getsize(path), flush=True)
    return os.path.getsize(path)

def save_webm(frames, path, fps, limit, max_s=3.0):
    """Telegram video sticker / custom emoji: VP9 + alpha, no audio, <= 3 s, <= 30 fps."""
    tmp = tempfile.mkdtemp(prefix="wm_")
    try:
        step = 1
        while len(frames[::step]) / (fps / step) > max_s:
            step += 1
        sub = frames[::step]
        for i, f in enumerate(sub):
            f.save(os.path.join(tmp, f"{i:04d}.png"))
        rate = fps / step
        for crf in (24, 30, 36, 42, 48, 54, 60):
            cmd = ["ffmpeg", "-y", "-loglevel", "error", "-framerate", f"{rate}", "-i", os.path.join(tmp, "%04d.png"),
                   "-c:v", "libvpx-vp9", "-pix_fmt", "yuva420p", "-b:v", "0", "-crf", str(crf),
                   "-deadline", "good", "-cpu-used", "2", "-row-mt", "1", "-an", path]
            subprocess.run(cmd, check=True)
            if os.path.getsize(path) <= limit:
                return os.path.getsize(path)
        print("  ! over limit", path, os.path.getsize(path), flush=True)
        return os.path.getsize(path)
    finally:
        shutil.rmtree(tmp, ignore_errors=True)

DIRS = ["stickers-512-whatsapp", "stickers-512-telegram", "stickers-320-discord", "web-800", "static-png-512",
        "emoji-128", "emoji-128-png", "emoji-100-telegram", "preview/frames"]

def export(name):
    meta = STICKERS[name]
    fps = meta["fps"]
    cut, cln = render(name)
    still = cut[int(len(cut) * 0.75)] if name not in ("ionity-wordmark-anim",) else cut[int(len(cut) * 0.5)]
    sizes = {}
    f512 = rs(cut, 512)
    sizes["webp512"] = save_webp(f512, os.path.join(OUT, "stickers-512-whatsapp", f"ionity-{name}.webp"), fps, limit=495_000)
    sizes["webm512"] = save_webm(f512, os.path.join(OUT, "stickers-512-telegram", f"ionity-{name}.webm"), fps, limit=255_000)
    f320 = rs(cut, 320)
    sizes["apng320"] = save_apng(f320, os.path.join(OUT, "stickers-320-discord", f"ionity-{name}.png"), fps, limit=510_000)
    sizes["gif320"] = save_gif(f320, os.path.join(OUT, "stickers-320-discord", f"ionity-{name}.gif"), fps, limit=510_000)
    sizes["webp800"] = save_webp(rs(cln, 800), os.path.join(OUT, "web-800", f"ionity-{name}.webp"), fps)
    sizes["gif800"] = save_gif(rs(cut, 800), os.path.join(OUT, "web-800", f"ionity-{name}.gif"), fps)
    still.resize((512, 512), Image.LANCZOS).save(os.path.join(OUT, "static-png-512", f"ionity-{name}.png"), optimize=True)
    still.resize((256, 256), Image.LANCZOS).save(os.path.join(OUT, "preview", "frames", f"{name}.png"))
    if meta["emoji"]:
        en = f"ionity_{name.replace('-', '_')}"
        e = rs(cut, 128)
        sizes["gif128"] = save_gif(e, os.path.join(OUT, "emoji-128", f"{en}.gif"), fps, limit=125_000)
        still.resize((128, 128), Image.LANCZOS).save(os.path.join(OUT, "emoji-128-png", f"{en}.png"), optimize=True)
        sizes["webm100"] = save_webm(rs(cut, 100), os.path.join(OUT, "emoji-100-telegram", f"{en}.webm"), fps, limit=63_000)
    print(f"done {name}: " + " ".join(f"{k}={v//1024}K" for k, v in sizes.items()), flush=True)
    return name, meta["group"], len(cut), fps, meta["emoji"], sizes

def checker(size, a=(205, 205, 205), b=(245, 245, 245), cell=16):
    im = Image.new("RGB", (size, size), a); d = ImageDraw.Draw(im)
    for y in range(0, size, cell):
        for x in range((y // cell) % 2 * cell, size, cell * 2):
            d.rectangle((x, y, x + cell - 1, y + cell - 1), fill=b)
    return im

def sheets(names):
    cols = 6; cell = 256; lab = 26
    rows = math.ceil(len(names) / cols)
    for tag, bg in (("dark", (11, 12, 16)), ("light", (246, 247, 250)), ("checker", None)):
        W, H = cols * cell, rows * (cell + lab)
        sheet = checker(max(W, H)).crop((0, 0, W, H)) if bg is None else Image.new("RGB", (W, H), bg)
        d = ImageDraw.Draw(sheet)
        for i, nm in enumerate(names):
            x, y = (i % cols) * cell, (i // cols) * (cell + lab)
            im = Image.open(os.path.join(OUT, "preview", "frames", f"{nm}.png")).convert("RGBA")
            sheet.paste(im, (x, y), im)
            d.text((x + 8, y + cell + 4), nm, font=font(MONO_R, 15),
                   fill=(200, 210, 225) if tag == "dark" else (40, 50, 70))
        sheet.save(os.path.join(OUT, "preview", f"sticker-sheet-{tag}.png"), optimize=True)

def main():
    only = [a for a in sys.argv[3:]]
    names = [n for n in STICKERS if not only or n in only]
    for d in DIRS:
        os.makedirs(os.path.join(OUT, d), exist_ok=True)
    procs = int(os.environ.get("JOBS", max(1, (os.cpu_count() or 2))))
    with Pool(procs) as pool:
        rows = pool.map(export, names, chunksize=1)
    # WhatsApp tray icon (96 x 96 PNG, < 50 KB)
    Image.open(os.path.join(OUT, "static-png-512", "ionity-ai-pulse.png")).resize((96, 96), Image.LANCZOS) \
        .save(os.path.join(OUT, "stickers-512-whatsapp", "tray-96.png"), optimize=True) \
        if os.path.exists(os.path.join(OUT, "static-png-512", "ionity-ai-pulse.png")) else None
    if not only:
        sheets(names)
        with open(os.path.join(OUT, "index.txt"), "w") as fh:
            fh.write("name\tgroup\tframes\tfps\temoji\t" + "\t".join(["webp512", "webm512", "apng320", "gif320", "webp800",
                                                                         "gif800", "gif128", "webm100"]) + "  (bytes)\n")
            for (nm, g, nf, fps, em, sz) in rows:
                fh.write(f"{nm}\t{g}\t{nf}\t{fps}\t{'yes' if em else '-'}\t" +
                         "\t".join(str(sz.get(k, "-")) for k in ["webp512", "webm512", "apng320", "gif320", "webp800",
                                                                   "gif800", "gif128", "webm100"]) + "\n")

if __name__ == "__main__":
    main()
