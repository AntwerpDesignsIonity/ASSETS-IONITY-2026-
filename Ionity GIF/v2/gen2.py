#!/usr/bin/env python3
"""Ionity Sticker & Emoji Pack v2 - high quality.
Usage: python3 gen2.py <assets-dir> <out-dir> [--list] [--only a,b,c] [--shard i/n]
Reuses every v1 animation from gen.py, adds new ones, a premium card and an ffmpeg
export pipeline (global palettes + dithering, Telegram VP9 WEBM, cut-out WebP).
(c) 2018-2026 Antwerp Designs | Ionity (Pty) Ltd - Policy 986 AED
"""
import math, os, random, shutil, subprocess, sys, tempfile
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import gen as g
from gen import (S, CYAN, BLUE, LOGO_BLUE, RED, WHITE, DARK, GREEN, AMBER, MONO, MONO_R, SANS,
                 font, tinted, blank, paste_center, text_layer, ease, lerp, sticker, STICKERS, AI_MARK, WORDMARK)
from PIL import Image, ImageDraw, ImageFilter, ImageChops

random.seed(2026)
HEB = "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf"
SANS_M = "/usr/share/fonts/truetype/google-fonts/Poppins-Medium.ttf"
GOLD = (255, 214, 102)
PURPLE = (140, 90, 255)

# ---------------------------------------------------------------- fast glow
def glow(layer, radius, color, strength=1.0):
    """Blur at quarter resolution: 10x faster, visually identical for soft halos."""
    a = layer.getchannel("A")
    small = a.resize((max(1, a.width // 4), max(1, a.height // 4)), Image.BILINEAR)
    small = small.filter(ImageFilter.GaussianBlur(max(1, radius / 4)))
    a = small.resize(layer.size, Image.BICUBIC)
    if strength != 1.0:
        a = a.point(lambda v: min(255, int(v * strength)))
    out = Image.new("RGBA", layer.size, color + (0,))
    out.putalpha(a)
    return out
g.glow = glow  # patch v1 animations too

def with_glow(base, layer, radius, color, strength=1.0, pos=None):
    gl = glow(layer, radius, color, strength)
    if pos is None:
        paste_center(base, gl); paste_center(base, layer)
    else:
        base.alpha_composite(gl, pos); base.alpha_composite(layer, pos)
g.with_glow = with_glow

# ---------------------------------------------------------------- premium card
def _make_card():
    W = S
    # radial gradient navy -> near black
    grad = Image.radial_gradient("L").resize((W, W), Image.BICUBIC)  # 0 centre .. 255 edge
    c0, c1 = (16, 28, 52), (6, 7, 12)
    bg = Image.merge("RGB", [grad.point(lambda v, i=i: int(c0[i] + (c1[i] - c0[i]) * min(1, v / 200))) for i in range(3)])
    bg = bg.convert("RGBA")
    d = ImageDraw.Draw(bg)
    # faint dot grid
    for x in range(48, W, 48):
        for y in range(48, W, 48):
            d.ellipse((x - 2, y - 2, x + 2, y + 2), fill=(0, 210, 255, 22))
    # top gloss
    gloss = Image.new("L", (W, W), 0)
    gd = ImageDraw.Draw(gloss)
    gd.ellipse((-W * 0.3, -W * 0.85, W * 1.3, W * 0.38), fill=26)
    gloss = gloss.filter(ImageFilter.GaussianBlur(40))
    bg.alpha_composite(Image.merge("RGBA", [Image.new("L", (W, W), 255)] * 3 + [gloss]))
    # rounded mask
    r = int(W * 0.22)
    mask = Image.new("L", (W, W), 0)
    ImageDraw.Draw(mask).rounded_rectangle((0, 0, W - 1, W - 1), radius=r, fill=255)
    bg.putalpha(mask)
    # gradient border cyan (top-left) -> blue (bottom-right)
    ring = Image.new("L", (W, W), 0)
    ImageDraw.Draw(ring).rounded_rectangle((5, 5, W - 6, W - 6), radius=r - 5, outline=255, width=7)
    lin = Image.linear_gradient("L").resize((W, W)).rotate(45, expand=False, fillcolor=128)
    border = Image.merge("RGB", [lin.point(lambda v, i=i: int(CYAN[i] + (BLUE[i] - CYAN[i]) * v / 255)) for i in range(3)]).convert("RGBA")
    border.putalpha(ring.point(lambda v: int(v * 0.75)))
    bg.alpha_composite(border)
    return bg
CARD = _make_card()

def compose(frame, bg=True):
    if not bg:
        return frame
    base = CARD.copy()
    base.alpha_composite(frame)
    base.putalpha(CARD.getchannel("A"))  # clip everything to the rounded card
    return base

# ---------------------------------------------------------------- text helpers
def grad_text(txt, fnt, c_top=WHITE, c_bot=CYAN, stroke=0, stroke_col=DARK, pad=50):
    d0 = ImageDraw.Draw(Image.new("RGBA", (1, 1)))
    box = d0.textbbox((0, 0), txt, font=fnt, stroke_width=stroke)
    w, h = box[2] - box[0] + pad * 2, box[3] - box[1] + pad * 2
    mask = Image.new("L", (w, h), 0)
    ImageDraw.Draw(mask).text((pad - box[0], pad - box[1]), txt, font=fnt, fill=255)
    grad = Image.linear_gradient("L").resize((w, h))
    fill = Image.merge("RGB", [grad.point(lambda v, i=i: int(c_top[i] + (c_bot[i] - c_top[i]) * v / 255)) for i in range(3)]).convert("RGBA")
    fill.putalpha(mask)
    if stroke:
        sm = Image.new("L", (w, h), 0)
        ImageDraw.Draw(sm).text((pad - box[0], pad - box[1]), txt, font=fnt, fill=255, stroke_width=stroke, stroke_fill=255)
        out = Image.new("RGBA", (w, h), stroke_col + (0,))
        out.putalpha(sm)
        out.alpha_composite(fill)
        return out
    return fill

def fit_font(path, txt, max_w, start):
    size = start
    while size > 20:
        f = font(path, size)
        b = ImageDraw.Draw(Image.new("RGBA", (1, 1))).textbbox((0, 0), txt, font=f)
        if b[2] - b[0] <= max_w:
            return f
        size -= 6
    return font(path, size)

def scaled(img, sc):
    if abs(sc - 1) < 1e-3:
        return img
    return img.resize((max(1, int(img.width * sc)), max(1, int(img.height * sc))), Image.LANCZOS)

def back_out(t):  # overshoot ease 0..1
    c1 = 1.70158; c3 = c1 + 1
    t = max(0, min(1, t))
    return 1 + c3 * (t - 1) ** 3 + c1 * (t - 1) ** 2

def word_sticker(word, sub=None, c_top=WHITE, c_bot=CYAN, glow_col=CYAN, path=SANS, n=40, icon=None, max_w=820):
    """Pop-in word with gradient fill, dark stroke, breathing glow and sparkle."""
    frames = []
    f = fit_font(path, word, max_w, 230)
    lay = grad_text(word, f, c_top, c_bot, stroke=10, stroke_col=(4, 10, 24))
    subl = grad_text(sub, font(MONO, 50), WHITE, CYAN) if sub else None
    for i in range(n):
        t = i / n
        im = blank()
        sc = back_out(i / 10) if i < 10 else 1 + 0.03 * math.sin((i - 10) / (n - 10) * 2 * math.pi)
        sc = max(0.05, sc)
        L = scaled(lay, sc)
        cy = S / 2 - (40 if sub or icon else 0)
        if icon is not None:
            ic = icon(i, n)
            paste_center(im, ic, cy=S / 2 - 210)
            cy = S / 2 + 90
        gs = 1.0 + 0.5 * (0.5 + 0.5 * math.sin(t * 4 * math.pi))
        with_glow(im, L, 36, glow_col, gs, pos=(int(S / 2 - L.width / 2), int(cy - L.height / 2)))
        if subl is not None and i >= 6:
            a = min(1, (i - 6) / 6)
            s2 = subl.copy(); s2.putalpha(s2.getchannel("A").point(lambda v: int(v * a)))
            im.alpha_composite(s2, (int(S / 2 - s2.width / 2), int(cy + L.height / 2 - 30)))
        # sparkle that travels across
        sx = 160 + 700 * ((t * 2) % 1)
        sparkle(im, sx, cy - 150 + 40 * math.sin(t * 6), 40 * abs(math.sin(t * 2 * math.pi * 2)))
        frames.append(im)
    return frames

def sparkle(im, x, y, r, col=WHITE):
    if r < 3:
        return
    lay = Image.new("RGBA", im.size, (0, 0, 0, 0))
    d = ImageDraw.Draw(lay)
    d.polygon([(x, y - r), (x + r * 0.22, y - r * 0.22), (x + r, y), (x + r * 0.22, y + r * 0.22),
               (x, y + r), (x - r * 0.22, y + r * 0.22), (x - r, y), (x - r * 0.22, y - r * 0.22)], fill=col + (255,))
    im.alpha_composite(glow(lay, 18, CYAN, 1.2)); im.alpha_composite(lay)

def ai_icon(w=300, col=WHITE):
    m = tinted(AI_MARK, col, w)
    return m

# =====================================================================
#  GREETINGS  (Afrikaans / English / Hebrew)
# =====================================================================
def wave_hand(i, n):
    lay = Image.new("RGBA", (420, 420), (0, 0, 0, 0))
    d = ImageDraw.Draw(lay)
    col = AMBER
    d.rounded_rectangle((120, 170, 300, 380), radius=70, fill=col + (255,))
    for k, (x, h) in enumerate([(122, 150), (165, 190), (210, 200), (255, 170)]):
        d.rounded_rectangle((x, 170 - h + 60, x + 42, 260), radius=21, fill=col + (255,))
    th = Image.new("RGBA", lay.size, (0, 0, 0, 0))
    ImageDraw.Draw(th).rounded_rectangle((270, 210, 320, 330), radius=25, fill=col + (255,))
    lay.alpha_composite(th.rotate(35, center=(290, 320), resample=Image.BICUBIC))
    ang = 22 * math.sin(i / n * 4 * math.pi)
    lay = lay.rotate(ang, center=(210, 380), resample=Image.BICUBIC)
    out = Image.new("RGBA", lay.size, (0, 0, 0, 0))
    out.alpha_composite(glow(lay, 20, AMBER, 0.8)); out.alpha_composite(lay)
    # motion lines
    dd = ImageDraw.Draw(out)
    if math.sin(i / n * 4 * math.pi) > 0.3:
        dd.arc((20, 40, 400, 420), 200, 240, fill=CYAN + (255,), width=10)
        dd.arc((20, 40, 400, 420), 300, 340, fill=CYAN + (255,), width=10)
    return out

@sticker("hallo", "greeting", fps=20)
def hallo():
    return word_sticker("Hallo!", "hi from Ionity", icon=wave_hand)

@sticker("dankie", "greeting", fps=20)
def dankie():
    def heart(i, n):
        sc = 1 + 0.12 * max(0, math.sin(i / n * 6 * math.pi))
        lay = Image.new("RGBA", (360, 360), (0, 0, 0, 0)); d = ImageDraw.Draw(lay)
        r = 70 * sc; cx, cy = 180, 150
        d.ellipse((cx - 2 * r, cy - r, cx, cy + r), fill=CYAN + (255,))
        d.ellipse((cx, cy - r, cx + 2 * r, cy + r), fill=CYAN + (255,))
        d.polygon([(cx - 2 * r + 4, cy + r * 0.4), (cx + 2 * r - 4, cy + r * 0.4), (cx, cy + 2.55 * r)], fill=CYAN + (255,))
        out = Image.new("RGBA", lay.size, (0, 0, 0, 0)); out.alpha_composite(glow(lay, 24, CYAN, 1.2)); out.alpha_composite(lay)
        return out
    return word_sticker("Dankie!", "thank you", icon=heart)

@sticker("baie-dankie", "greeting", fps=20)
def baie_dankie():
    return word_sticker("Baie Dankie", "much appreciated", c_top=WHITE, c_bot=GOLD, glow_col=AMBER)

@sticker("goeie-more", "greeting", fps=20)
def goeie_more():
    def sun(i, n):
        lay = Image.new("RGBA", (420, 300), (0, 0, 0, 0)); d = ImageDraw.Draw(lay)
        rise = 40 * (1 - ease(min(1, i / 16)))
        cx, cy = 210, 230 + rise
        for k in range(12):
            a = math.radians(k * 30 + i * 3)
            r1, r2 = 115, 150 + 12 * math.sin(i * 0.5 + k)
            d.line([(cx + r1 * math.cos(a), cy + r1 * math.sin(a)), (cx + r2 * math.cos(a), cy + r2 * math.sin(a))], fill=GOLD + (255,), width=14)
        d.ellipse((cx - 95, cy - 95, cx + 95, cy + 95), fill=AMBER + (255,))
        lay = lay.crop((0, 0, 420, 250))
        out = Image.new("RGBA", lay.size, (0, 0, 0, 0)); out.alpha_composite(glow(lay, 30, AMBER, 1.0)); out.alpha_composite(lay)
        return out
    return word_sticker("Goeie môre!", "good morning", c_top=WHITE, c_bot=GOLD, glow_col=AMBER, icon=sun)

@sticker("goeie-nag", "greeting", fps=20)
def goeie_nag():
    def moon(i, n):
        lay = Image.new("RGBA", (360, 300), (0, 0, 0, 0)); d = ImageDraw.Draw(lay)
        d.ellipse((90, 40, 290, 240), fill=(210, 225, 255, 255))
        d.ellipse((150, 10, 330, 200), fill=(0, 0, 0, 0))
        for k, (x, y) in enumerate([(60, 60), (300, 230), (40, 200), (320, 40)]):
            r = 10 + 8 * abs(math.sin(i / n * 2 * math.pi + k))
            d.polygon([(x, y - r), (x + r / 4, y - r / 4), (x + r, y), (x + r / 4, y + r / 4), (x, y + r), (x - r / 4, y + r / 4), (x - r, y), (x - r / 4, y - r / 4)], fill=WHITE + (255,))
        out = Image.new("RGBA", lay.size, (0, 0, 0, 0)); out.alpha_composite(glow(lay, 24, BLUE, 1.0)); out.alpha_composite(lay)
        return out
    return word_sticker("Goeie nag", "good night", c_top=WHITE, c_bot=(150, 170, 255), glow_col=PURPLE, icon=moon)

@sticker("lekker", "greeting", fps=20)
def lekker():
    return word_sticker("LEKKER!", None, c_top=GOLD, c_bot=AMBER, glow_col=AMBER)

@sticker("shalom", "greeting", fps=20)
def shalom():
    frames = []
    f_he = font(HEB, 230)
    he = grad_text("שלום", f_he, WHITE, CYAN, stroke=10, stroke_col=(4, 10, 24))
    en = grad_text("SHALOM", font(MONO, 70), CYAN, BLUE)
    n = 40
    for i in range(n):
        t = i / n
        im = blank()
        sc = back_out(i / 10) if i < 10 else 1 + 0.03 * math.sin(t * 2 * math.pi)
        L = scaled(he, max(0.05, sc))
        with_glow(im, L, 36, CYAN, 1 + 0.4 * math.sin(t * 4 * math.pi), pos=(int(S / 2 - L.width / 2), int(S / 2 - 60 - L.height / 2)))
        if i >= 8:
            e = en.copy(); e.putalpha(e.getchannel("A").point(lambda v: int(v * min(1, (i - 8) / 8))))
            im.alpha_composite(e, (int(S / 2 - e.width / 2), 640))
        sparkle(im, 180 + 660 * ((t * 2) % 1), 260, 40 * abs(math.sin(t * 4 * math.pi)))
        frames.append(im)
    return frames

# =====================================================================
#  FAITH
# =====================================================================
@sticker("amen", "faith", fps=20)
def amen():
    frames = []
    n = 48
    word = grad_text("AMEN", font(SANS, 220), WHITE, GOLD, stroke=10, stroke_col=(20, 14, 4))
    for i in range(n):
        t = i / n
        im = blank()
        rays = Image.new("RGBA", (S, S), (0, 0, 0, 0)); d = ImageDraw.Draw(rays)
        for k in range(16):
            a = math.radians(k * 22.5 + t * 22.5)
            w = math.radians(5)
            p = [(S / 2, S / 2 - 40), (S / 2 + 700 * math.cos(a - w), S / 2 - 40 + 700 * math.sin(a - w)), (S / 2 + 700 * math.cos(a + w), S / 2 - 40 + 700 * math.sin(a + w))]
            d.polygon(p, fill=GOLD + (40,))
        rays = rays.filter(ImageFilter.GaussianBlur(6))
        im.alpha_composite(rays)
        with_glow(im, word, 45, AMBER, 1.2 + 0.4 * math.sin(t * 2 * math.pi), pos=(int(S / 2 - word.width / 2), int(S / 2 - 40 - word.height / 2)))
        sub = grad_text("Anything is Possible with God.", font(MONO, 40), WHITE, GOLD)
        im.alpha_composite(sub, (int(S / 2 - sub.width / 2), 680))
        frames.append(im)
    return frames

def praying():  # retired in v2.0 (read as a peace sign)
    frames = []
    n = 40
    for i in range(n):
        t = i / n
        lay = blank(); d = ImageDraw.Draw(lay)
        # two praying palms as mirrored rounded shapes
        for side in (-1, 1):
            hand = Image.new("RGBA", (S, S), (0, 0, 0, 0)); hd = ImageDraw.Draw(hand)
            hd.rounded_rectangle((S / 2 - 4 - 150 if side < 0 else S / 2 + 4, 260, S / 2 - 4 if side < 0 else S / 2 + 4 + 150, 760), radius=75, fill=CYAN + (255,))
            hand = hand.rotate(-side * 12, center=(S / 2, 760), resample=Image.BICUBIC)
            lay.alpha_composite(hand)
        d.rounded_rectangle((S / 2 - 210, 700, S / 2 + 210, 830), radius=40, fill=BLUE + (255,))
        im = blank()
        # halo
        halo = Image.new("RGBA", (S, S), (0, 0, 0, 0))
        ImageDraw.Draw(halo).ellipse((S / 2 - 260, 120, S / 2 + 260, 240), outline=GOLD + (255,), width=18)
        with_glow(im, halo, 30, AMBER, 1 + 0.6 * math.sin(t * 2 * math.pi))
        with_glow(im, lay, 30, CYAN, 0.9)
        frames.append(im)
    return frames

@sticker("cross-light", "faith", fps=20)
def cross_light():
    frames = []
    n = 40
    for i in range(n):
        t = i / n
        p = 0.5 + 0.5 * math.sin(t * 2 * math.pi)
        lay = blank(); d = ImageDraw.Draw(lay)
        d.rounded_rectangle((S / 2 - 50, 170, S / 2 + 50, 860), radius=20, fill=WHITE + (255,))
        d.rounded_rectangle((S / 2 - 230, 330, S / 2 + 230, 430), radius=20, fill=WHITE + (255,))
        im = blank()
        with_glow(im, lay, 50 + 40 * p, GOLD, 1.2 + p)
        for k in range(6):
            a = t * 2 * math.pi + k * math.pi / 3
            sparkle(im, S / 2 + 330 * math.cos(a), 400 + 330 * math.sin(a) * 0.6, 22 * (0.5 + 0.5 * math.sin(a * 2)))
        frames.append(im)
    return frames

# =====================================================================
#  DEV LIFE REACTIONS
# =====================================================================
@sticker("ship-it", "devlife", fps=24)
def ship_it():
    frames = []
    n = 48
    word = grad_text("SHIP IT!", font(SANS, 150), WHITE, CYAN, stroke=8, stroke_col=(4, 10, 24))
    stars = [(random.uniform(0, S), random.uniform(0, S), random.uniform(2, 6)) for _ in range(60)]
    for i in range(n):
        t = i / n
        im = blank(); d = ImageDraw.Draw(im)
        for (x, y, r) in stars:
            yy = (y + t * S * 1.5 * r / 4) % S
            d.line([(x, yy), (x, yy - r * 8)], fill=(150, 220, 255, 180), width=int(r / 1.5) + 1)
        roc = rocket_layer(i)
        shake = 6 * math.sin(i * 2.3)
        with_glow(im, roc, 30, CYAN, 1.0, pos=(int(S / 2 - roc.width / 2 + shake), int(150 + 20 * math.sin(t * 4 * math.pi))))
        with_glow(im, word, 30, CYAN, 1.0, pos=(int(S / 2 - word.width / 2), 760))
        frames.append(im)
    return frames

def rocket_layer(i):
    lay = Image.new("RGBA", (360, 600), (0, 0, 0, 0)); d = ImageDraw.Draw(lay)
    # flame
    fl = 120 + 40 * math.sin(i * 1.7) + 20 * math.sin(i * 3.1)
    d.polygon([(130, 400), (230, 400), (180, 400 + fl)], fill=AMBER + (255,))
    d.polygon([(150, 400), (210, 400), (180, 400 + fl * 0.6)], fill=WHITE + (255,))
    # body
    d.polygon([(180, 20), (250, 140), (250, 400), (110, 400), (110, 140)], fill=(230, 240, 255, 255))
    d.pieslice((110, 20, 250, 260), 180, 360, fill=(230, 240, 255, 255))
    d.ellipse((140, 170, 220, 250), fill=BLUE + (255,)); d.ellipse((155, 185, 205, 235), fill=CYAN + (255,))
    # fins
    d.polygon([(110, 300), (40, 420), (110, 400)], fill=BLUE + (255,))
    d.polygon([(250, 300), (320, 420), (250, 400)], fill=BLUE + (255,))
    d.rectangle((110, 380, 250, 400), fill=CYAN + (255,))
    return lay

@sticker("on-it", "devlife", fps=20)
def on_it():
    def gear(i, n):
        return gear_layer(260, i / n * 90, CYAN)
    return word_sticker("ON IT", "working...", icon=gear)

def gear_layer(size, ang, col, teeth=10):
    W = size * 2
    lay = Image.new("RGBA", (W, W), (0, 0, 0, 0)); d = ImageDraw.Draw(lay)
    c = W / 2; r = size * 0.7; R = size * 0.92
    pts = []
    for k in range(teeth * 2):
        a0 = math.radians(ang + k * 180 / teeth)
        rr = R if k % 2 == 0 else r
        for da in (-0.5, 0.5):
            a = a0 + math.radians(da * 180 / teeth * 0.8)
            pts.append((c + rr * math.cos(a), c + rr * math.sin(a)))
    d.polygon(pts, fill=col + (255,))
    d.ellipse((c - r * 0.45, c - r * 0.45, c + r * 0.45, c + r * 0.45), fill=(0, 0, 0, 0))
    lay = lay.resize((size, size), Image.LANCZOS)
    out = Image.new("RGBA", lay.size, (0, 0, 0, 0)); out.alpha_composite(glow(lay, 16, col, 1.0)); out.alpha_composite(lay)
    return out

@sticker("deploying", "devlife", fps=20)
def deploying():
    frames = []
    n = 60
    f = font(MONO, 64)
    for i in range(n):
        t = min(1, i / 44)
        p = ease(t)
        im = blank(); d = ImageDraw.Draw(im)
        txt = "DEPLOYED" if t >= 1 else "DEPLOYING" + "." * (1 + (i // 4) % 3)
        col = GREEN if t >= 1 else CYAN
        tl = grad_text(txt, f, WHITE, col)
        im.alpha_composite(tl, (int(S / 2 - tl.width / 2), 300))
        # segmented bar
        segs = 20
        for k in range(segs):
            x0 = 150 + k * 37
            on = k < int(p * segs)
            d.rounded_rectangle((x0, 470, x0 + 28, 560), radius=6, fill=(col if on else (20, 40, 70)) + (255,))
        pct = grad_text(f"{int(p*100):3d}%", font(MONO, 90), WHITE, col)
        im.alpha_composite(pct, (int(S / 2 - pct.width / 2), 590))
        bar = Image.new("RGBA", (S, S), (0, 0, 0, 0))
        ImageDraw.Draw(bar).rounded_rectangle((150, 470, 150 + int(p * segs) * 37, 560), radius=8, fill=col + (255,))
        im.alpha_composite(glow(bar, 24, col, 0.8))
        frames.append(im)
    return frames + [frames[-1]] * 12

@sticker("bug-fixed", "devlife", fps=20)
def bug_fixed():
    frames = []
    n = 44
    for i in range(n):
        t = i / n
        im = blank()
        bug = Image.new("RGBA", (S, S), (0, 0, 0, 0)); d = ImageDraw.Draw(bug)
        cx, cy = S / 2, S / 2 - 30
        leg = 14 * math.sin(i * 1.3)
        for k in (-1, 0, 1):
            y = cy + k * 80
            d.line([(cx - 120, y), (cx - 240, y - 40 + leg * k)], fill=RED + (255,), width=18)
            d.line([(cx + 120, y), (cx + 240, y - 40 - leg * k)], fill=RED + (255,), width=18)
        d.ellipse((cx - 140, cy - 170, cx + 140, cy + 200), fill=RED + (255,))
        d.ellipse((cx - 85, cy - 270, cx + 85, cy - 120), fill=(200, 30, 30, 255))
        d.line([(cx, cy - 160), (cx, cy + 190)], fill=(60, 0, 0, 255), width=10)
        for (dx, dy) in [(-60, -40), (60, -40), (-50, 80), (50, 80)]:
            d.ellipse((cx + dx - 25, cy + dy - 25, cx + dx + 25, cy + dy + 25), fill=(60, 0, 0, 255))
        if t < 0.45:
            with_glow(im, bug, 26, RED, 0.8)
        else:
            k = min(1, (t - 0.45) / 0.2)
            b2 = bug.copy(); b2.putalpha(b2.getchannel("A").point(lambda v: int(v * (1 - k) * 0.9)))
            im.alpha_composite(b2)
            chk = Image.new("RGBA", (S, S), (0, 0, 0, 0)); cd = ImageDraw.Draw(chk)
            r = 340
            cd.ellipse((S / 2 - r, S / 2 - r, S / 2 + r, S / 2 + r), outline=GREEN + (255,), width=26)
            pts = [(300, 540), (450, 690), (740, 360)]
            cd.line(pts[:2] + ([pts[2]] if k > 0.5 else []), fill=GREEN + (255,), width=52, joint="curve")
            with_glow(im, scaled(chk, 0.6 + 0.4 * back_out(k)), 30, GREEN, 1.0)
        lbl = grad_text("BUG FIXED" if t > 0.55 else "debugging...", font(MONO, 64), WHITE, GREEN if t > 0.55 else RED)
        im.alpha_composite(lbl, (int(S / 2 - lbl.width / 2), 820))
        frames.append(im)
    return frames + [frames[-1]] * 10

@sticker("coffee", "devlife", fps=20)
def coffee():
    frames = []
    n = 40
    for i in range(n):
        t = i / n
        lay = blank(); d = ImageDraw.Draw(lay)
        d.rounded_rectangle((300, 430, 660, 820), radius=50, fill=(230, 240, 255, 255))
        d.arc((600, 500, 800, 720), -90, 90, fill=(230, 240, 255, 255), width=40)
        d.rounded_rectangle((330, 450, 630, 520), radius=30, fill=(120, 70, 40, 255))
        m = tinted(AI_MARK, BLUE, 200)
        lay.alpha_composite(m, (int(480 - m.width / 2), 600))
        im = blank()
        with_glow(im, lay, 26, CYAN, 0.7)
        steam = Image.new("RGBA", (S, S), (0, 0, 0, 0)); sd = ImageDraw.Draw(steam)
        for k in range(3):
            x0 = 390 + k * 90
            pts = []
            for j in range(20):
                y = 400 - j * 14
                pts.append((x0 + 22 * math.sin(j * 0.45 - t * 2 * math.pi * 2 + k), y))
            a = 200
            sd.line(pts, fill=CYAN + (a,), width=16, joint="curve")
        steam = steam.filter(ImageFilter.GaussianBlur(3))
        im.alpha_composite(glow(steam, 20, CYAN, 0.8)); im.alpha_composite(steam)
        frames.append(im)
    return frames

@sticker("brb", "devlife", fps=20)
def brb():
    def clock(i, n):
        lay = Image.new("RGBA", (300, 300), (0, 0, 0, 0)); d = ImageDraw.Draw(lay)
        d.ellipse((20, 20, 280, 280), outline=CYAN + (255,), width=18)
        a = math.radians(i / n * 360 - 90); b = math.radians(i / n * 30 - 90)
        d.line([(150, 150), (150 + 100 * math.cos(a), 150 + 100 * math.sin(a))], fill=WHITE + (255,), width=14)
        d.line([(150, 150), (150 + 65 * math.cos(b), 150 + 65 * math.sin(b))], fill=CYAN + (255,), width=18)
        d.ellipse((135, 135, 165, 165), fill=WHITE + (255,))
        out = Image.new("RGBA", lay.size, (0, 0, 0, 0)); out.alpha_composite(glow(lay, 16, CYAN, 1.0)); out.alpha_composite(lay)
        return out
    return word_sticker("BRB", "be right back", icon=clock)

@sticker("well-done", "devlife", fps=20)
def well_done():
    def trophy(i, n):
        lay = Image.new("RGBA", (340, 320), (0, 0, 0, 0)); d = ImageDraw.Draw(lay)
        d.pieslice((70, -80, 270, 200), 0, 180, fill=GOLD + (255,))
        d.arc((20, 20, 120, 130), 90, 270, fill=GOLD + (255,), width=18)
        d.arc((220, 20, 320, 130), -90, 90, fill=GOLD + (255,), width=18)
        d.rectangle((150, 190, 190, 250), fill=GOLD + (255,))
        d.rounded_rectangle((100, 250, 240, 300), radius=10, fill=AMBER + (255,))
        out = Image.new("RGBA", lay.size, (0, 0, 0, 0)); out.alpha_composite(glow(lay, 24, AMBER, 1.0)); out.alpha_composite(lay)
        sparkle(out, 60 + 220 * ((i / n * 2) % 1), 60, 30 * abs(math.sin(i / n * 4 * math.pi)))
        return out
    return word_sticker("WELL DONE", None, c_top=WHITE, c_bot=GOLD, glow_col=AMBER, icon=trophy)

@sticker("wow", "devlife", fps=20)
def wow():
    frames = []
    n = 36
    word = grad_text("WOW", font(SANS, 300), WHITE, CYAN, stroke=12, stroke_col=(4, 10, 24))
    for i in range(n):
        t = i / n
        im = blank()
        # burst lines
        burst = Image.new("RGBA", (S, S), (0, 0, 0, 0)); d = ImageDraw.Draw(burst)
        for k in range(18):
            a = math.radians(k * 20 + t * 40)
            r0, r1 = 300 + 30 * math.sin(t * 6 + k), 480
            d.line([(S / 2 + r0 * math.cos(a), S / 2 + r0 * math.sin(a)), (S / 2 + r1 * math.cos(a), S / 2 + r1 * math.sin(a))], fill=(CYAN if k % 2 else BLUE) + (255,), width=16)
        im.alpha_composite(glow(burst, 20, CYAN, 0.8)); im.alpha_composite(burst)
        sc = back_out(i / 8) if i < 8 else 1 + 0.06 * abs(math.sin((i - 8) / (n - 8) * 3 * math.pi))
        with_glow(im, scaled(word, max(0.05, sc)), 40, CYAN, 1.3)
        frames.append(im)
    return frames

@sticker("error-404", "devlife", fps=16)
def error_404():
    frames = []
    n = 32
    base = grad_text("404", font(MONO, 280), WHITE, RED, stroke=8, stroke_col=(30, 4, 4))
    sub = grad_text("not found", font(MONO, 60), WHITE, RED)
    for i in range(n):
        im = blank()
        glitch = (i % 8) in (2, 3) or i in (17, 25)
        if glitch:
            r = base.copy()
            rch = Image.new("RGBA", r.size, (255, 0, 80, 0)); rch.putalpha(r.getchannel("A"))
            cch = Image.new("RGBA", r.size, CYAN + (0,)); cch.putalpha(r.getchannel("A"))
            paste_center(im, cch, dx=-16, dy=-60); paste_center(im, rch, dx=16, dy=-60)
            # slice offset
            sl = r.crop((0, r.height // 2 - 30, r.width, r.height // 2 + 30))
            im.alpha_composite(sl, (int(S / 2 - r.width / 2 + 40), int(S / 2 - 60 - 30)))
        else:
            with_glow(im, base, 30, RED, 0.9, pos=(int(S / 2 - base.width / 2), int(S / 2 - 60 - base.height / 2)))
        im.alpha_composite(sub, (int(S / 2 - sub.width / 2), 650))
        frames.append(im)
    return frames

@sticker("status-online", "devlife", fps=20)
def status_online():
    frames = []
    n = 40
    lbl = grad_text("ONLINE", font(SANS, 140), WHITE, GREEN, stroke=8, stroke_col=(4, 20, 10))
    for i in range(n):
        t = i / n
        im = blank(); d = ImageDraw.Draw(im)
        cx, cy = S / 2, 380
        for k in range(3):
            f = (t + k / 3) % 1
            r = 80 + 260 * f
            d.ellipse((cx - r, cy - r, cx + r, cy + r), outline=GREEN + (int(255 * (1 - f)),), width=12)
        dot = Image.new("RGBA", (S, S), (0, 0, 0, 0))
        ImageDraw.Draw(dot).ellipse((cx - 90, cy - 90, cx + 90, cy + 90), fill=GREEN + (255,))
        with_glow(im, dot, 40, GREEN, 1.3)
        im.alpha_composite(lbl, (int(S / 2 - lbl.width / 2), 680))
        frames.append(im)
    return frames

@sticker("countdown", "devlife", fps=10)
def countdown():
    frames = []
    for num, col in [("3", CYAN), ("2", BLUE), ("1", AMBER)]:
        for j in range(10):
            im = blank()
            sc = 1.4 - 0.4 * back_out(j / 5)
            a = 1 if j < 8 else 1 - (j - 7) / 3
            L = grad_text(num, font(SANS, 420), WHITE, col, stroke=10, stroke_col=(4, 10, 24))
            L = scaled(L, sc)
            L.putalpha(L.getchannel("A").point(lambda v: int(v * a)))
            ring = Image.new("RGBA", (S, S), (0, 0, 0, 0))
            ImageDraw.Draw(ring).arc((150, 150, S - 150, S - 150), -90, -90 + 360 * (j + 1) / 10, fill=col + (255,), width=26)
            im.alpha_composite(glow(ring, 20, col, 1.0)); im.alpha_composite(ring)
            with_glow(im, L, 30, col, 1.0)
            frames.append(im)
    go = grad_text("GO!", font(SANS, 300), WHITE, GREEN, stroke=12, stroke_col=(4, 20, 10))
    for j in range(14):
        im = blank()
        with_glow(im, scaled(go, max(0.05, back_out(j / 5))), 45, GREEN, 1.4)
        frames.append(im)
    return frames

# =====================================================================
#  MORE TECH
# =====================================================================
@sticker("globe", "tech", fps=24)
def globe():
    frames = []
    n = 48
    R = 330
    for i in range(n):
        t = i / n
        lay = blank(); d = ImageDraw.Draw(lay)
        cx, cy = S / 2, S / 2
        d.ellipse((cx - R, cy - R, cx + R, cy + R), outline=CYAN + (255,), width=16)
        for k in range(6):  # meridians rotating
            ph = (t * math.pi / 3 + k * math.pi / 6) % math.pi
            w = abs(R * math.cos(ph))
            col = CYAN if math.sin(ph) > 0 else BLUE
            d.ellipse((cx - w, cy - R, cx + w, cy + R), outline=col + (200,), width=8)
        for lat in (-0.6, -0.3, 0, 0.3, 0.6):
            y = cy + R * lat; w = R * math.sqrt(1 - lat * lat)
            d.ellipse((cx - w, y - w * 0.12, cx + w, y + w * 0.12), outline=BLUE + (200,), width=7)
        # orbiting satellite node
        a = t * 2 * math.pi
        sx, sy = cx + 430 * math.cos(a), cy + 140 * math.sin(a)
        if math.sin(a) > -0.2 or True:
            d.ellipse((sx - 28, sy - 28, sx + 28, sy + 28), fill=WHITE + (255,))
        im = blank()
        with_glow(im, lay, 30, CYAN, 1.0)
        m = tinted(AI_MARK, WHITE, 200)
        bgc = Image.new("RGBA", (S, S), (0, 0, 0, 0))
        ImageDraw.Draw(bgc).ellipse((cx - 140, cy - 110, cx + 140, cy + 110), fill=(6, 12, 24, 230))
        im.alpha_composite(bgc); paste_center(im, m)
        frames.append(im)
    return frames

@sticker("neural-net", "tech", fps=20)
def neural_net():
    frames = []
    n = 40
    layers = [3, 5, 5, 2]
    xs = [200, 400, 620, 830]
    nodes = [[(xs[l], S / 2 + (k - (c - 1) / 2) * 150) for k in range(c)] for l, c in enumerate(layers)]
    for i in range(n):
        t = i / n
        lay = blank(); d = ImageDraw.Draw(lay)
        wave = t * 4  # signal travels layer 0 -> 3
        for l in range(3):
            for a in nodes[l]:
                for b in nodes[l + 1]:
                    act = max(0, 1 - abs(wave - (l + 0.5)) * 1.5)
                    col = lerp((20, 50, 90), CYAN, act)
                    d.line([a, b], fill=col + (255,), width=6)
        for l in range(4):
            act = max(0, 1 - abs(wave - l) * 1.5)
            for (x, y) in nodes[l]:
                col = lerp(BLUE, WHITE, act)
                r = 34 + 10 * act
                d.ellipse((x - r, y - r, x + r, y + r), fill=col + (255,))
        im = blank()
        with_glow(im, lay, 26, CYAN, 1.1)
        frames.append(im)
    return frames

@sticker("lock-secure", "tech", fps=20)
def lock_secure():
    frames = []
    n = 44
    for i in range(n):
        t = min(1, i / 16)
        lift = 90 * (1 - back_out(t))
        lay = blank(); d = ImageDraw.Draw(lay)
        d.arc((S / 2 - 160, 210 - lift, S / 2 + 160, 530 - lift), 180, 360, fill=CYAN + (255,), width=56)
        d.line([(S / 2 - 132, 370 - lift), (S / 2 - 132, 480)], fill=CYAN + (255,), width=56)
        d.line([(S / 2 + 132, 370 - lift), (S / 2 + 132, 480 - (0 if t >= 1 else 60))], fill=CYAN + (255,), width=56)
        d.rounded_rectangle((S / 2 - 250, 450, S / 2 + 250, 830), radius=50, fill=BLUE + (255,))
        d.ellipse((S / 2 - 45, 570, S / 2 + 45, 660), fill=DARK + (255,))
        d.rounded_rectangle((S / 2 - 18, 630, S / 2 + 18, 740), radius=10, fill=DARK + (255,))
        im = blank()
        locked = t >= 1
        with_glow(im, lay, 30, GREEN if locked and i < 26 else CYAN, 1.3 if locked and i < 26 else 0.9)
        if locked:
            lbl = grad_text("SECURED", font(MONO, 60), WHITE, GREEN)
            im.alpha_composite(lbl, (int(S / 2 - lbl.width / 2), 850))
        frames.append(im)
    return frames

@sticker("audit-scan", "tech", fps=20)
def audit_scan():
    frames = []
    n = 44
    doc_lines = [(250, 300 + k * 70, 250 + random.randint(300, 480)) for k in range(7)]
    for i in range(n):
        t = i / n
        im = blank(); d = ImageDraw.Draw(im)
        d.rounded_rectangle((200, 200, 760, 860), radius=30, fill=(14, 26, 48, 255), outline=BLUE + (255,), width=8)
        for (x0, y, x1) in doc_lines:
            d.rounded_rectangle((x0, y, x1, y + 26), radius=13, fill=(40, 80, 140, 255))
        # magnifier moving in a figure 8
        mx = 480 + 170 * math.sin(t * 2 * math.pi)
        my = 520 + 160 * math.sin(t * 4 * math.pi)
        mag = Image.new("RGBA", (S, S), (0, 0, 0, 0)); md = ImageDraw.Draw(mag)
        md.ellipse((mx - 130, my - 130, mx + 130, my + 130), outline=CYAN + (255,), width=30)
        md.line([(mx + 95, my + 95), (mx + 230, my + 230)], fill=CYAN + (255,), width=46)
        lens = Image.new("L", (S, S), 0)
        ImageDraw.Draw(lens).ellipse((mx - 112, my - 112, mx + 112, my + 112), fill=90)
        hl = Image.new("RGBA", (S, S), CYAN + (0,)); hl.putalpha(lens)
        im.alpha_composite(hl)
        im.alpha_composite(glow(mag, 24, CYAN, 1.0)); im.alpha_composite(mag)
        frames.append(im)
    return frames

@sticker("battery-charge", "tech", fps=20)
def battery_charge():
    frames = []
    n = 40
    for i in range(n):
        t = i / n
        lvl = ease(min(1, t / 0.8))
        lay = blank(); d = ImageDraw.Draw(lay)
        d.rounded_rectangle((180, 330, 790, 700), radius=50, outline=WHITE + (255,), width=26)
        d.rounded_rectangle((800, 440, 860, 590), radius=16, fill=WHITE + (255,))
        col = lerp(AMBER, GREEN, lvl)
        w = int(530 * lvl)
        if w > 10:
            d.rounded_rectangle((220, 370, 220 + w, 660), radius=26, fill=col + (255,))
        bolt = [(520, 340), (420, 530), (500, 530), (460, 690), (590, 480), (510, 480), (560, 340)]
        d.polygon(bolt, fill=WHITE + (255,), outline=DARK + (255,), width=8)
        im = blank()
        with_glow(im, lay, 30, col, 1.0)
        lbl = grad_text(f"{int(lvl*100)}%  ENERGY-EFFICIENT", font(MONO, 44), WHITE, col)
        im.alpha_composite(lbl, (int(S / 2 - lbl.width / 2), 760))
        frames.append(im)
    return frames + [frames[-1]] * 6

@sticker("server-rack", "tech", fps=12)
def server_rack():
    frames = []
    n = 24
    rnd = random.Random(7)
    pat = [[rnd.random() for _ in range(n)] for _ in range(15)]
    for i in range(n):
        lay = blank(); d = ImageDraw.Draw(lay)
        for u in range(5):
            y = 200 + u * 130
            d.rounded_rectangle((250, y, 774, y + 110), radius=18, fill=(18, 34, 62, 255), outline=BLUE + (255,), width=6)
            for k in range(3):
                on = pat[u * 3 + k][i] > 0.4
                col = (GREEN if k == 0 else CYAN if k == 1 else AMBER) if on else (30, 50, 80)
                d.ellipse((290 + k * 50, y + 38, 324 + k * 50, y + 72), fill=col + (255,))
            for k in range(6):
                d.rounded_rectangle((520 + k * 38, y + 30, 540 + k * 38, y + 80), radius=6, fill=(40, 70, 120, 255))
        im = blank()
        with_glow(im, lay, 22, CYAN, 0.7)
        frames.append(im)
    return frames

@sticker("iot-home", "tech", fps=20)
def iot_home():
    frames = []
    n = 40
    for i in range(n):
        t = i / n
        lay = blank(); d = ImageDraw.Draw(lay)
        d.polygon([(S / 2, 230), (820, 520), (740, 520), (740, 830), (284, 830), (284, 520), (204, 520)], outline=CYAN + (255,), width=24)
        d.line([(S / 2, 230), (820, 520)], fill=CYAN + (255,), width=30); d.line([(S / 2, 230), (204, 520)], fill=CYAN + (255,), width=30)
        d.rounded_rectangle((452, 640, 572, 830), radius=16, fill=BLUE + (255,))
        # wifi above roof
        lit = int(t * 8) % 4
        for k in range(3):
            r = 60 + k * 55
            col = CYAN if k < lit else (20, 60, 100)
            d.arc((S / 2 - r, 470 - r, S / 2 + r, 470 + r), 225, 315, fill=col + (255,), width=20)
        d.ellipse((S / 2 - 20, 450, S / 2 + 20, 490), fill=CYAN + (255,))
        im = blank()
        with_glow(im, lay, 26, CYAN, 1.0)
        frames.append(im)
    return frames

@sticker("data-stream", "tech", fps=20)
def data_stream():
    frames = []
    n = 40
    f = font(MONO, 44)
    cols = 10
    rnd = random.Random(11)
    streams = [(rnd.uniform(0, 1), rnd.uniform(0.6, 1.4), [rnd.choice("01AEDIONITY986") for _ in range(30)]) for _ in range(cols)]
    for i in range(n):
        t = i / n
        im = blank(); d = ImageDraw.Draw(im)
        for c, (off, sp, chars) in enumerate(streams):
            x = 90 + c * 90
            head = ((off + t * sp) % 1) * (S + 400) - 200
            for k in range(9):
                y = head - k * 60
                if 0 < y < S:
                    a = int(255 * (1 - k / 9))
                    col = WHITE if k == 0 else CYAN
                    d.text((x, y), chars[(k + i) % 30], font=f, fill=col + (a,))
        m = tinted(AI_MARK, WHITE, 340)
        box = Image.new("RGBA", (S, S), (0, 0, 0, 0))
        ImageDraw.Draw(box).rounded_rectangle((S / 2 - 220, S / 2 - 150, S / 2 + 220, S / 2 + 150), radius=40, fill=(6, 10, 20, 235))
        im.alpha_composite(box)
        with_glow(im, m, 30, CYAN, 1 + 0.4 * math.sin(t * 2 * math.pi))
        frames.append(im)
    return frames

@sticker("ai-assemble", "brand", fps=24)
def ai_assemble():
    """Logo built from particles that fly in, hold, then dissolve."""
    frames = []
    mark = tinted(AI_MARK, WHITE, 600)
    a = mark.getchannel("A")
    rnd = random.Random(3)
    pts = []
    W, H = a.size
    for _ in range(9000):
        x, y = rnd.randrange(W), rnd.randrange(H)
        if a.getpixel((x, y)) > 128:
            pts.append((x, y, rnd.uniform(0, 2 * math.pi), rnd.uniform(300, 700)))
        if len(pts) >= 520:
            break
    ox, oy = S / 2 - W / 2, S / 2 - H / 2
    n = 56
    for i in range(n):
        if i < 22:
            k = ease(i / 22)
        elif i < 40:
            k = 1
        else:
            k = 1 - ease((i - 40) / 16)
        im = blank()
        if 22 <= i < 40:
            gl = 0.5 + 0.5 * math.sin((i - 22) / 18 * math.pi)
            with_glow(im, mark, 40, CYAN, 1 + gl, pos=(int(ox), int(oy)))
        else:
            lay = blank(); d = ImageDraw.Draw(lay)
            for (x, y, ang, dist) in pts:
                px = ox + x + math.cos(ang) * dist * (1 - k)
                py = oy + y + math.sin(ang) * dist * (1 - k)
                col = lerp(CYAN, WHITE, k)
                d.ellipse((px - 7, py - 7, px + 7, py + 7), fill=col + (255,))
            with_glow(im, lay, 22, CYAN, 1.0)
        frames.append(im)
    return frames

@sticker("ionity-glitch", "brand", fps=16)
def ionity_glitch():
    frames = []
    wm = tinted(WORDMARK, WHITE, 820)
    for i in range(32):
        im = blank()
        gl = i % 8 in (5, 6) or i in (13, 27)
        if gl:
            r = tinted(WORDMARK, (255, 0, 90), 820); c = tinted(WORDMARK, CYAN, 820)
            paste_center(im, c, dx=-14); paste_center(im, r, dx=14)
            for k in range(3):
                y0 = random.randint(0, wm.height - 30)
                sl = wm.crop((0, y0, wm.width, y0 + 26))
                im.alpha_composite(sl, (int(S / 2 - wm.width / 2 + random.randint(-50, 50)), int(S / 2 - wm.height / 2 + y0)))
        else:
            with_glow(im, tinted(WORDMARK, CYAN, 820), 40, CYAN, 1.2)
            paste_center(im, tinted(WORDMARK, (220, 245, 255), 820))
        sub = grad_text("Building Tomorrow, Today.", font(MONO, 44), WHITE, CYAN)
        im.alpha_composite(sub, (int(S / 2 - sub.width / 2), 690))
        frames.append(im)
    return frames

# text-heavy ones are stickers only (not emojis)
for _n in ["baie-dankie", "goeie-more", "goeie-nag", "amen", "deploying", "bug-fixed", "well-done",
           "error-404", "status-online", "battery-charge", "ionity-glitch", "ship-it"]:
    STICKERS[_n]["emoji"] = False

# =====================================================================
#  EXPORT (ffmpeg, high quality)
# =====================================================================
def run(cmd):
    r = subprocess.run(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
    if r.returncode:
        raise RuntimeError(" ".join(cmd) + "\n" + r.stderr[-1500:])

def write_seq(frames, d, size, mode="RGBA"):
    os.makedirs(d, exist_ok=True)
    for k, f in enumerate(frames):
        f.resize((size, size), Image.LANCZOS).save(os.path.join(d, "f%04d.png" % k), compress_level=1)

def ff_gif(seq, out, fps, transparent=False, limit=None, colors=256):
    tries = [("sierra2_4a", colors, 1), ("bayer:bayer_scale=4", colors, 1), ("bayer:bayer_scale=3", 128, 1),
             ("bayer:bayer_scale=3", 128, 2), ("bayer:bayer_scale=2", 96, 2), ("bayer:bayer_scale=2", 64, 3)]
    for dither, cols, step in tries:
        sel = f"fps={fps/step}," if step > 1 else ""
        if transparent:
            fl = f"{sel}split[a][b];[a]palettegen=max_colors={cols}:reserve_transparent=1:stats_mode=full[p];[b][p]paletteuse=dither={dither}:alpha_threshold=110:diff_mode=rectangle"
        else:
            fl = f"{sel}split[a][b];[a]palettegen=max_colors={cols}:reserve_transparent=0:stats_mode=full[p];[b][p]paletteuse=dither={dither}:diff_mode=rectangle"
        run(["ffmpeg", "-y", "-v", "error", "-framerate", str(fps), "-i", os.path.join(seq, "f%04d.png"),
             "-filter_complex", fl, "-loop", "0", "-gifflags", "+transdiff" if not transparent else "-transdiff", out])
        if limit is None or os.path.getsize(out) <= limit:
            return
    print("  ! over limit", out, os.path.getsize(out), flush=True)

def ff_webp(seq, out, fps, limit=None):
    """Animated WebP via libwebp (Pillow), method 4 - fast, good quality."""
    import glob as _g
    frames = [Image.open(f).convert("RGBA") for f in sorted(_g.glob(os.path.join(seq, "f*.png")))]
    for q, step in [(85, 1), (72, 1), (60, 1), (70, 2), (50, 2), (45, 3), (35, 3), (30, 4)]:
        sub = frames[::step]
        sub[0].save(out, save_all=True, append_images=sub[1:], duration=int(1000 / fps * step), loop=0,
                    quality=q, method=4, allow_mixed=True)
        if limit is None or os.path.getsize(out) <= limit:
            return
    print("  ! over limit", out, os.path.getsize(out), flush=True)

def ff_webm(seq, out, fps, nframes, limit=256_000):
    """Telegram video sticker: VP9 + alpha, 512px, <=3 s, <=30 fps, <=256 KB, no audio."""
    dur = min(3.0, nframes / fps)
    for crf in (30, 36, 42, 48, 54):
        run(["ffmpeg", "-y", "-v", "error", "-framerate", str(fps), "-i", os.path.join(seq, "f%04d.png"),
             "-t", "%.2f" % dur, "-c:v", "libvpx-vp9", "-pix_fmt", "yuva420p", "-b:v", "0", "-crf", str(crf),
             "-deadline", "good", "-row-mt", "1", "-an", out])
        if os.path.getsize(out) <= limit:
            return
    print("  ! over limit", out, os.path.getsize(out), flush=True)

def cutout(fr, size=512, stroke=12):
    """Classic die-cut sticker: content on transparent with a white outline + soft shadow."""
    f = fr.resize((size, size), Image.LANCZOS)
    a = f.getchannel("A").point(lambda v: 255 if v > 60 else 0)
    outline = a.filter(ImageFilter.MaxFilter(stroke * 2 + 1)).filter(ImageFilter.GaussianBlur(1.2))
    shadow = outline.filter(ImageFilter.GaussianBlur(6)).point(lambda v: int(v * 0.35))
    base = Image.new("RGBA", (size, size), (0, 0, 0, 0))
    sh = Image.new("RGBA", (size, size), (0, 0, 0, 0)); sh.putalpha(shadow)
    base.alpha_composite(sh, (0, 4))
    wl = Image.new("RGBA", (size, size), WHITE + (0,)); wl.putalpha(outline)
    base.alpha_composite(wl)
    # dark pad behind light glyphs so white/cyan art reads inside the white border
    pad = Image.new("RGBA", (size, size), (10, 16, 30, 0)); pad.putalpha(a.filter(ImageFilter.MaxFilter(stroke - 3 if stroke > 4 else 3)))
    base.alpha_composite(pad)
    base.alpha_composite(f)
    return base

def export(name, meta, OUT, tmp):
    raw = meta["fn"]()
    fps = meta["fps"]
    cards = [compose(f, meta["bg"]) for f in raw]
    sd = os.path.join(tmp, name)
    # 512
    s512 = os.path.join(sd, "c512"); write_seq(cards, s512, 512)
    ff_gif(s512, os.path.join(OUT, "stickers-512-gif", f"ionity-{name}.gif"), fps)
    ff_webp(s512, os.path.join(OUT, "stickers-512-webp-whatsapp", f"ionity-{name}.webp"), fps, limit=495_000)
    ff_webm(s512, os.path.join(OUT, "stickers-512-webm-telegram", f"ionity-{name}.webm"), min(fps, 30), len(cards))
    # cut-out (die-cut) WebP
    cut = [cutout(f) for f in raw]
    sc = os.path.join(sd, "cut"); write_seq(cut, sc, 512)
    ff_webp(sc, os.path.join(OUT, "stickers-512-cutout-webp", f"ionity-{name}.webp"), fps, limit=495_000)
    # 320 discord
    s320 = os.path.join(sd, "c320"); write_seq(cards, s320, 320)
    ff_gif(s320, os.path.join(OUT, "stickers-320-discord", f"ionity-{name}.gif"), fps, limit=500_000)
    # 800 web
    s800 = os.path.join(sd, "c800"); write_seq(cards, s800, 800)
    ff_gif(s800, os.path.join(OUT, "web-800", f"ionity-{name}.gif"), fps)
    # emoji
    if meta["emoji"]:
        ef = [g.emoji_recolor(f) for f in raw]
        se = os.path.join(sd, "e128"); write_seq(ef, se, 128)
        un = name.replace("-", "_")
        ff_gif(se, os.path.join(OUT, "emoji-128-gif", f"ionity_{un}.gif"), fps, transparent=True, limit=125_000)
        ef[-1].resize((128, 128), Image.LANCZOS).save(os.path.join(OUT, "emoji-128-png", f"ionity_{un}.png"))
    cards[len(cards) // 2].resize((256, 256), Image.LANCZOS).save(os.path.join(OUT, "preview", f"{name}.png"))
    cards[-1].resize((512, 512), Image.LANCZOS).save(os.path.join(OUT, "stills-512-png", f"ionity-{name}.png"))
    shutil.rmtree(sd, ignore_errors=True)
    return len(raw)

DIRS = ["stickers-512-gif", "stickers-512-webp-whatsapp", "stickers-512-webm-telegram", "stickers-512-cutout-webp",
        "stickers-320-discord", "web-800", "emoji-128-gif", "emoji-128-png", "preview", "stills-512-png"]

def main():
    OUT = sys.argv[2]
    args = sys.argv[3:]
    names = list(STICKERS)
    if "--list" in args:
        for n in names: print(n, STICKERS[n]["group"])
        return
    if "--only" in args:
        names = args[args.index("--only") + 1].split(",")
    if "--shard" in args:
        i, n = map(int, args[args.index("--shard") + 1].split("/"))
        names = names[i::n]
    for d in DIRS:
        os.makedirs(os.path.join(OUT, d), exist_ok=True)
    tmp = tempfile.mkdtemp(prefix="ion_", dir=os.path.dirname(os.path.abspath(__file__)))
    for name in names:
        out_log = os.path.join(OUT, "preview", f"{name}.png")
        if "--skip-done" in args and os.path.exists(out_log):
            continue
        nf = export(name, STICKERS[name], OUT, tmp)
        print("done", name, nf, flush=True)
    shutil.rmtree(tmp, ignore_errors=True)

if __name__ == "__main__":
    main()
