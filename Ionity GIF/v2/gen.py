#!/usr/bin/env python3
"""Ionity sticker + emoji pack generator.
Renders every animation at 1024px (supersampled), then exports to all target sizes.
(c) 2018-2026 Antwerp Designs | Ionity (Pty) Ltd - Policy 986 AED
"""
import math, os, random, sys
from PIL import Image, ImageDraw, ImageFilter, ImageFont, ImageChops

ASSETS = sys.argv[1]
OUT = sys.argv[2]
S = 1024  # render size
random.seed(986)

# Brand palette (from ionity.today / ionity.co.za)
CYAN = (0, 210, 255)
BLUE = (51, 102, 255)
LOGO_BLUE = (33, 96, 174)
RED = (255, 40, 40)
WHITE = (255, 255, 255)
DARK = (11, 12, 16)
DARK2 = (7, 8, 13)
GREEN = (0, 255, 150)
AMBER = (255, 190, 40)

MONO = "/usr/share/fonts/truetype/dejavu/DejaVuSansMono-Bold.ttf"
MONO_R = "/usr/share/fonts/truetype/dejavu/DejaVuSansMono.ttf"
SANS = "/usr/share/fonts/truetype/google-fonts/Poppins-Bold.ttf"

def font(path, size):
    return ImageFont.truetype(path, size)

# ---------- assets ----------
AI_MARK = Image.open(os.path.join(ASSETS, "ai-mark-white.png")).convert("RGBA")
AI_MARK = AI_MARK.crop(AI_MARK.getbbox())
WORDMARK = Image.open(os.path.join(ASSETS, "wordmark.png")).convert("RGBA")
WORDMARK = WORDMARK.crop(WORDMARK.getbbox())
ANIM_WEBP = os.path.join(ASSETS, "ionity-anim.webp")

def tinted(img, color, w=None):
    """Recolour a transparent mark to `color`, optionally resized to width w."""
    if w:
        h = round(img.height * w / img.width)
        img = img.resize((w, h), Image.LANCZOS)
    a = img.getchannel("A")
    out = Image.new("RGBA", img.size, color + (0,))
    out.putalpha(a)
    return out

# ---------- helpers ----------
def blank():
    return Image.new("RGBA", (S, S), (0, 0, 0, 0))

def card(border=CYAN):
    im = blank()
    d = ImageDraw.Draw(im)
    r = S * 0.22
    d.rounded_rectangle((0, 0, S - 1, S - 1), radius=r, fill=DARK + (255,))
    d.rounded_rectangle((6, 6, S - 7, S - 7), radius=r - 6, outline=border + (70,), width=6)
    return im

def glow(layer, radius, color, strength=1.0):
    """Return a glow halo image for the alpha of `layer`."""
    a = layer.getchannel("A").filter(ImageFilter.GaussianBlur(radius))
    if strength != 1.0:
        a = a.point(lambda v: min(255, int(v * strength)))
    g = Image.new("RGBA", layer.size, color + (0,))
    g.putalpha(a)
    return g

def paste_center(base, img, cx=None, cy=None, dx=0, dy=0):
    cx = S // 2 if cx is None else cx
    cy = S // 2 if cy is None else cy
    base.alpha_composite(img, (int(cx - img.width / 2 + dx), int(cy - img.height / 2 + dy)))

def with_glow(base, layer, radius, color, strength=1.0, pos=None):
    g = glow(layer, radius, color, strength)
    if pos is None:
        paste_center(base, g)
        paste_center(base, layer)
    else:
        base.alpha_composite(g, pos)
        base.alpha_composite(layer, pos)

def text_layer(txt, fnt, color, pad=40):
    d0 = ImageDraw.Draw(Image.new("RGBA", (1, 1)))
    box = d0.textbbox((0, 0), txt, font=fnt)
    w, h = box[2] - box[0] + pad * 2, box[3] - box[1] + pad * 2
    im = Image.new("RGBA", (w, h), (0, 0, 0, 0))
    ImageDraw.Draw(im).text((pad - box[0], pad - box[1]), txt, font=fnt, fill=color + (255,))
    return im

def ease(t):
    return 0.5 - 0.5 * math.cos(math.pi * t)

def lerp(a, b, t):
    return tuple(int(a[i] + (b[i] - a[i]) * t) for i in range(3))

STICKERS = {}
def sticker(name, group, fps=12, bg=True, emoji=True):
    def deco(fn):
        STICKERS[name] = dict(fn=fn, group=group, fps=fps, bg=bg, emoji=emoji)
        return fn
    return deco

# =====================================================================
#  BRAND MARKS
# =====================================================================
@sticker("ai-pulse", "brand")
def ai_pulse():
    frames = []
    mark = tinted(AI_MARK, WHITE, 600)
    for i in range(30):
        t = i / 30
        p = 0.5 + 0.5 * math.sin(t * 2 * math.pi)
        im = blank()
        col = lerp(BLUE, CYAN, p)
        with_glow(im, tinted(mark, col), 40 + 50 * p, col, 1.4)
        paste_center(im, mark)
        frames.append(im)
    return frames

@sticker("ai-flip", "brand")
def ai_flip():
    frames = []
    front = tinted(AI_MARK, WHITE, 600)
    back = tinted(AI_MARK, CYAN, 600)
    for i in range(32):
        t = i / 32
        sx = math.cos(t * 2 * math.pi)
        src = front if sx >= 0 else back
        w = max(2, int(abs(sx) * src.width))
        img = src.resize((w, src.height), Image.LANCZOS)
        im = blank()
        with_glow(im, img, 40, CYAN if sx < 0 else BLUE, 1.2)
        frames.append(im)
    return frames

@sticker("ionity-neon", "brand")
def ionity_neon():
    frames = []
    wm = tinted(WORDMARK, CYAN, 820)
    wm_dim = tinted(WORDMARK, (0, 70, 110), 820)
    pattern = [1,1,1,1,0.3,1,1,0.1,1,1,1,1,1,1,0.5,0.8,1,1,1,1,0.2,1,1,1]
    for k in pattern:
        im = blank()
        if k < 0.6:
            paste_center(im, wm_dim)
            paste_center(im, tinted(WORDMARK, lerp((0,70,110), CYAN, k), 820))
        else:
            with_glow(im, wm, 55, CYAN, 1.6 * k)
            paste_center(im, tinted(WORDMARK, lerp(CYAN, WHITE, 0.35 * k), 820))
        frames.append(im)
    return frames

@sticker("ionity-scan", "brand")
def ionity_scan():
    frames = []
    wm = tinted(WORDMARK, LOGO_BLUE, 820)
    for i in range(28):
        t = i / 28
        im = blank()
        with_glow(im, wm, 30, BLUE, 0.8)
        # sweeping highlight band
        band = Image.new("RGBA", wm.size, (0, 0, 0, 0))
        bd = ImageDraw.Draw(band)
        x = int(-200 + (wm.width + 400) * t)
        for j in range(60):
            a = int(255 * (1 - abs(j - 30) / 30))
            bd.line([(x + j, 0), (x + j - 120, wm.height)], fill=CYAN + (a,), width=3)
        band.putalpha(ImageChops.multiply(band.getchannel("A"), wm.getchannel("A")))
        paste_center(im, band)
        frames.append(im)
    return frames

@sticker("ionity-typing", "brand", fps=10, emoji=False)
def ionity_typing():
    frames = []
    f1 = font(MONO, 150)
    f2 = font(MONO_R, 46)
    full = "IONITY"
    for i in range(len(full) + 1):
        for blink in (1, 0):
            im = blank()
            txt = "> " + full[:i] + ("_" if blink else " ")
            lay = text_layer(txt, f1, CYAN)
            with_glow(im, lay, 30, CYAN, 1.2, pos=None)
            if i == len(full):
                sub = text_layer("Building Tomorrow, Today.", f2, WHITE)
                paste_center(im, sub, dy=150)
            frames.append(im)
    frames += [frames[-1]] * 8
    return frames

@sticker("ai-loader", "brand")
def ai_loader():
    frames = []
    mark = tinted(AI_MARK, WHITE, 420)
    for i in range(36):
        t = i / 36
        im = blank()
        ring = blank()
        d = ImageDraw.Draw(ring)
        r = 380
        bb = (S/2 - r, S/2 - r, S/2 + r, S/2 + r)
        a0 = t * 360
        d.arc(bb, a0, a0 + 100, fill=CYAN + (255,), width=22)
        d.arc(bb, a0 + 180, a0 + 250, fill=BLUE + (255,), width=22)
        r2 = 300
        bb2 = (S/2 - r2, S/2 - r2, S/2 + r2, S/2 + r2)
        d.arc(bb2, -a0 * 1.5, -a0 * 1.5 + 60, fill=WHITE + (160,), width=10)
        with_glow(im, ring, 25, CYAN, 1.0)
        with_glow(im, mark, 35, BLUE, 0.9)
        frames.append(im)
    return frames

@sticker("ionity-wordmark-anim", "brand", fps=12, emoji=False)
def ionity_wordmark_anim():
    """Up-scaled version of the site's own animated wordmark (ionity-anim.webp)."""
    frames = []
    src = Image.open(ANIM_WEBP)
    for i in range(src.n_frames):
        src.seek(i)
        fr = src.convert("RGBA")
        fr = fr.resize((S, round(S * fr.height / fr.width)), Image.LANCZOS)
        im = blank()
        paste_center(im, fr)
        frames.append(im)
    return frames

@sticker("ionity-global-badge", "brand", fps=12, emoji=False)
def ionity_global_badge():
    frames = []
    mark = tinted(AI_MARK, WHITE, 360)
    f1 = font(SANS, 96)
    f2 = font(MONO, 40)
    title = text_layer("IONITY GLOBAL", f1, WHITE)
    tags = ["Native-AI", "AIoT", "Cloud", "Edge", "Audit"]
    for i in range(40):
        t = i / 40
        im = blank()
        with_glow(im, mark, 30, BLUE, 0.8, pos=(int(S/2 - mark.width/2), 150))
        im.alpha_composite(title, (int(S/2 - title.width/2), 540))
        k = int(t * len(tags)) % len(tags)
        tag = text_layer("[ " + tags[k] + " ]", f2, CYAN)
        with_glow(im, tag, 18, CYAN, 1.0, pos=(int(S/2 - tag.width/2), 680))
        frames.append(im)
    return frames

# =====================================================================
#  REACTIONS
# =====================================================================
def pop(t):  # overshoot scale
    return 1 + 0.25 * math.sin(min(t, 1) * math.pi) if t < 1 else 1

@sticker("yes-check", "reaction")
def yes_check():
    frames = []
    pts = [(300, 540), (450, 690), (740, 360)]
    for i in range(24):
        t = min(1, i / 12)
        lay = blank()
        d = ImageDraw.Draw(lay)
        r = 330
        d.ellipse((S/2 - r, S/2 - r, S/2 + r, S/2 + r), outline=GREEN + (255,), width=26)
        # draw partial polyline
        total = 2
        seg = t * total
        p = [pts[0]]
        for k in range(1, 3):
            if seg >= k:
                p.append(pts[k])
            elif seg > k - 1:
                f = seg - (k - 1)
                p.append((pts[k-1][0] + (pts[k][0] - pts[k-1][0]) * f, pts[k-1][1] + (pts[k][1] - pts[k-1][1]) * f))
                break
        if len(p) > 1:
            d.line(p, fill=GREEN + (255,), width=52, joint="curve")
            for q in p: d.ellipse((q[0]-26, q[1]-26, q[0]+26, q[1]+26), fill=GREEN + (255,))
        im = blank()
        sc = pop(i / 14) if i >= 12 else 1
        if sc != 1:
            lay = lay.resize((int(S*sc), int(S*sc)), Image.LANCZOS)
        with_glow(im, lay, 30, GREEN, 1.0)
        frames.append(im)
    return frames + [frames[-1]] * 6

@sticker("no-x", "reaction")
def no_x():
    frames = []
    for i in range(24):
        lay = blank()
        d = ImageDraw.Draw(lay)
        r = 330
        d.ellipse((S/2 - r, S/2 - r, S/2 + r, S/2 + r), outline=RED + (255,), width=26)
        t = min(1, i / 8)
        L = 200 * t
        d.line([(S/2 - L, S/2 - L), (S/2 + L, S/2 + L)], fill=RED + (255,), width=52)
        if i >= 6:
            L2 = 200 * min(1, (i - 6) / 6)
            d.line([(S/2 + L2, S/2 - L2), (S/2 - L2, S/2 + L2)], fill=RED + (255,), width=52)
        shake = int(18 * math.sin(i * 2.5)) if 12 <= i < 20 else 0
        im = blank()
        with_glow(im, lay, 30, RED, 1.0, pos=(shake, 0))
        frames.append(im)
    return frames + [frames[-1]] * 6

@sticker("thinking", "reaction", fps=10)
def thinking():
    frames = []
    mark = tinted(AI_MARK, WHITE, 380)
    f = font(MONO, 120)
    for i in range(24):
        im = blank()
        with_glow(im, mark, 30, BLUE, 0.8, pos=(int(S/2 - mark.width/2), 280))
        q = text_layer("?", font(MONO, 200), CYAN)
        bounce = int(14 * math.sin(i * 0.6))
        with_glow(im, q, 25, CYAN, 1.2, pos=(700, 120 + bounce))
        dots = "." * (1 + (i // 4) % 3)
        dl = text_layer(dots, f, CYAN)
        im.alpha_composite(dl, (int(S/2 - 110), 640))
        frames.append(im)
    return frames

@sticker("ion-fire", "reaction")
def ion_fire():
    """Blue-cyan plasma flame - 'ionised' fire in brand colours."""
    frames = []
    for i in range(24):
        lay = blank()
        d = ImageDraw.Draw(lay)
        for layer, (col, scale) in enumerate([(BLUE, 1.0), (CYAN, 0.68), (WHITE, 0.36)]):
            # teardrop flame: bottom at by, tip at by - h, half width hw(u)
            r = 250 * scale
            h = 640 * scale
            by = S/2 + 340 - 40 * layer
            n = 24
            left, right = [], []
            for k in range(n + 1):
                u = k / n
                hw = r * (1 - u) ** 0.9 * min(1.0, u / 0.22) ** 0.5
                sway = math.sin(i * 0.8 + layer) * 70 * u * u + math.sin(i * 1.6 + u * 9 + layer) * 25 * u
                y = by - h * u
                left.append((S/2 - hw + sway, y))
                right.append((S/2 + hw + sway, y))
            pts = left + right[::-1]
            d.polygon(pts, fill=col + (255,))
        lay = lay.filter(ImageFilter.GaussianBlur(3))
        im = blank()
        with_glow(im, lay, 45, CYAN, 1.3)
        frames.append(im)
    return frames

@sticker("celebrate", "reaction")
def celebrate():
    frames = []
    mark = tinted(AI_MARK, WHITE, 460)
    parts = [(random.uniform(0, S), random.uniform(-S, 0), random.choice([CYAN, BLUE, WHITE, GREEN, AMBER]),
              random.uniform(0.6, 1.4), random.uniform(0, 6)) for _ in range(70)]
    for i in range(36):
        t = i / 36
        im = blank()
        d = ImageDraw.Draw(im)
        for (x, y0, col, sp, ph) in parts:
            y = (y0 + t * S * 1.6 * sp) % (S + 100) - 50
            x2 = x + 30 * math.sin(t * 10 + ph)
            w = 22
            d.rectangle((x2 - w/2, y - 8, x2 + w/2, y + 8), fill=col + (255,))
        bounce = -abs(math.sin(t * math.pi * 2)) * 50
        with_glow(im, mark, 40, CYAN, 1.2, pos=(int(S/2 - mark.width/2), int(S/2 - mark.height/2 + bounce)))
        frames.append(im)
    return frames

@sticker("warning", "reaction", fps=8)
def warning():
    frames = []
    f = font(MONO, 300)
    for i in range(12):
        on = i % 4 < 2
        lay = blank()
        d = ImageDraw.Draw(lay)
        col = RED if on else (120, 20, 20)
        d.polygon([(S/2, 130), (S - 110, 850), (110, 850)], outline=col + (255,), width=34)
        ex = text_layer("!", f, col)
        lay.alpha_composite(ex, (int(S/2 - ex.width/2), 330))
        im = blank()
        with_glow(im, lay, 35, RED, 1.2 if on else 0.3)
        frames.append(im)
    return frames

@sticker("heartbeat", "reaction")
def heartbeat():
    frames = []
    def heart(scale, col):
        lay = blank()
        d = ImageDraw.Draw(lay)
        r = 170 * scale
        cx, cy = S/2, S/2 - 40 * scale
        d.ellipse((cx - 2*r, cy - r, cx, cy + r), fill=col + (255,))
        d.ellipse((cx, cy - r, cx + 2*r, cy + r), fill=col + (255,))
        d.polygon([(cx - 2*r + 8, cy + r*0.45), (cx + 2*r - 8, cy + r*0.45), (cx, cy + 2.6*r)], fill=col + (255,))
        return lay
    beat = [1,1.18,1.05,1.25,1.1,1,1,1,1,1,1,1]
    for i, sc in enumerate(beat):
        im = blank()
        col = lerp(BLUE, CYAN, (sc - 1) / 0.25)
        lay = heart(sc, col)
        with_glow(im, lay, 40, CYAN, 0.8 + (sc - 1) * 2)
        frames.append(im)
    return frames

@sticker("hundred", "reaction")
def hundred():
    frames = []
    f = font(MONO, 260)
    f2 = font(MONO_R, 50)
    for i in range(30):
        t = min(1, i / 20)
        n = int(100 * ease(t))
        im = blank()
        lay = text_layer(f"{n}%", f, lerp(BLUE, CYAN, t))
        with_glow(im, lay, 35, CYAN, 0.6 + t)
        # progress bar
        d = ImageDraw.Draw(im)
        d.rounded_rectangle((160, 700, 864, 740), radius=20, outline=CYAN + (120,), width=4)
        d.rounded_rectangle((160, 700, 160 + 704 * n / 100, 740), radius=20, fill=CYAN + (255,))
        sub = text_layer("SYSTEM OPTIMAL" if n == 100 else "optimising...", f2, WHITE)
        im.alpha_composite(sub, (int(S/2 - sub.width/2), 790))
        frames.append(im)
    return frames

@sticker("bolt", "reaction", fps=10)
def bolt():
    frames = []
    for i in range(14):
        lay = blank()
        d = ImageDraw.Draw(lay)
        pts = [(590, 110), (340, 560), (500, 560), (430, 920), (700, 440), (540, 440), (650, 110)]
        on = i % 7 < 4
        col = CYAN if on else WHITE
        d.polygon(pts, fill=col + (255,))
        im = blank()
        with_glow(im, lay, 55 if on else 25, CYAN, 1.6 if on else 0.6)
        frames.append(im)
    return frames

@sticker("thumbs-up", "reaction")
def thumbs_up():
    frames = []
    def hand(col):
        lay = blank()
        d = ImageDraw.Draw(lay)
        # cuff
        d.rounded_rectangle((230, 470, 370, 830), radius=30, fill=col + (255,))
        # fist with four fingers
        for k in range(4):
            y = 470 + k * 92
            d.rounded_rectangle((400, y, 820, y + 86), radius=43, fill=col + (255,))
        d.rounded_rectangle((400, 470, 560, 830), radius=40, fill=col + (255,))
        # thumb: rotated rounded rect rising from the fist
        th = Image.new("RGBA", (S, S), (0, 0, 0, 0))
        ImageDraw.Draw(th).rounded_rectangle((430, 180, 570, 560), radius=70, fill=col + (255,))
        th = th.rotate(-18, resample=Image.BICUBIC, center=(500, 520))
        lay.alpha_composite(th)
        # finger separators
        for k in range(1, 4):
            y = 470 + k * 92
            d.line([(570, y), (805, y)], fill=DARK + (255,), width=10)
        return lay
    for i in range(24):
        t = i / 24
        rot = 10 * math.sin(t * 2 * math.pi)
        sc = 1 + 0.08 * math.sin(t * 2 * math.pi)
        lay = hand(lerp(BLUE, CYAN, 0.5 + 0.5 * math.sin(t * 2 * math.pi))).rotate(rot, resample=Image.BICUBIC, center=(S/2, 650))
        lay = lay.resize((int(S*sc), int(S*sc)), Image.LANCZOS)
        im = blank()
        with_glow(im, lay, 35, CYAN, 1.0)
        frames.append(im)
    return frames

# =====================================================================
#  TAGLINES & ASCII
# =====================================================================
def typewriter(lines, fnt, col, glow_col, hold=10, sub=None, step=1):
    frames = []
    text = "\n".join(lines)
    n = len(text)
    for i in range(0, n + 1, step):
        im = blank()
        shown = text[:i] + "_"
        lay = Image.new("RGBA", (S, S), (0, 0, 0, 0))
        d = ImageDraw.Draw(lay)
        d.multiline_text((S/2, S/2), shown, font=fnt, fill=col + (255,), anchor="mm", align="center", spacing=30)
        with_glow(im, lay, 22, glow_col, 1.0)
        frames.append(im)
    last = blank()
    lay = Image.new("RGBA", (S, S), (0, 0, 0, 0))
    d = ImageDraw.Draw(lay)
    d.multiline_text((S/2, S/2), text, font=fnt, fill=col + (255,), anchor="mm", align="center", spacing=30)
    with_glow(last, lay, 40, glow_col, 1.6)
    if sub:
        s = text_layer(sub, font(MONO_R, 44), CYAN)
        last.alpha_composite(s, (int(S/2 - s.width/2), 760))
    frames += [last] * hold
    return frames

@sticker("tagline-building-tomorrow", "tagline", fps=12, emoji=False)
def tagline_btt():
    return typewriter(["BUILDING", "TOMORROW,", "TODAY."], font(MONO, 120), WHITE, CYAN, sub="ionity.today", step=2)

@sticker("tagline-anything-possible", "tagline", fps=12, emoji=False)
def tagline_god():
    return typewriter(["ANYTHING IS", "POSSIBLE", "WITH GOD."], font(MONO, 120), CYAN, CYAN, sub="Johan W. van Antwerp", step=2)

@sticker("ascii-ioman-run", "tagline", fps=8, emoji=False)
def ioman_run():
    frames = []
    f = font(MONO, 150)
    ft = font(MONO, 70)
    poses = [" o \n/|\\\n/ \\", " o \n/|\\\n| |", " o \n\\|/\n/ \\", " o \n/|\\\n| |"]
    ground = "-=-=-=-=-=-=-=-=-=-=-"
    for i in range(16):
        im = blank()
        lay = Image.new("RGBA", (S, S), (0, 0, 0, 0))
        d = ImageDraw.Draw(lay)
        d.multiline_text((S/2, S/2 + 40), poses[i % 4], font=f, fill=CYAN + (255,), anchor="mm", align="center", spacing=10)
        off = (i * 2) % 4
        d.text((S/2, 780), ground[off:off + 17], font=ft, fill=BLUE + (255,), anchor="mm")
        d.text((S/2, 160), "IO-MAN", font=font(MONO, 110), fill=WHITE + (255,), anchor="mm")
        d.text((S/2, 250), "GET OVER IT DOOR", font=font(MONO_R, 40), fill=CYAN + (255,), anchor="mm")
        with_glow(im, lay, 22, CYAN, 1.0)
        frames.append(im)
    return frames

@sticker("ascii-spore", "tagline", fps=6)
def ascii_spore():
    frames = []
    f = font(MONO, 200)
    faces = ["(o_o)", "(o_o)", "(o_o)", "(-_-)", "(o_o)", "(>_<)", "(o_o)", "(^_^)", "(o o)", "(O_O)", "(o_o)", "(-_-)"]
    for i, face in enumerate(faces):
        im = blank()
        lay = Image.new("RGBA", (S, S), (0, 0, 0, 0))
        d = ImageDraw.Draw(lay)
        d.text((S/2, S/2 - 30), face, font=f, fill=CYAN + (255,), anchor="mm")
        d.text((S/2, S/2 + 160), "/|\\" if i % 2 else "\\|/", font=font(MONO, 120), fill=BLUE + (255,), anchor="mm")
        d.text((S/2, 860), "spore #" + str(13 - i % 13).zfill(2), font=font(MONO_R, 44), fill=WHITE + (180,), anchor="mm")
        with_glow(im, lay, 22, CYAN, 1.0)
        frames.append(im)
    return frames

@sticker("terminal-ok", "tagline", fps=10, emoji=False)
def terminal_ok():
    frames = []
    f = font(MONO_R, 54)
    lines = ["$ ionity --deploy edge", "[AEDI] policy 986 AED .. ok", "[AIoT] nodes online .... 12", "[EDGE] inference ....... ok", "[SEC ] audit trail ..... ok", "", "> STATUS: ALL SYSTEMS GO"]
    for i in range(len(lines) + 1):
        for blink in (1, 0):
            im = blank()
            lay = Image.new("RGBA", (S, S), (0, 0, 0, 0))
            d = ImageDraw.Draw(lay)
            y = 150
            for k, ln in enumerate(lines[:i]):
                col = GREEN if "ok" in ln or "GO" in ln else CYAN
                d.text((90, y), ln, font=f, fill=col + (255,))
                y += 90
            d.text((90, y), "_" if blink else " ", font=f, fill=WHITE + (255,))
            with_glow(im, lay, 14, CYAN, 0.8)
            frames.append(im)
    return frames + [frames[-1]] * 10

# =====================================================================
#  TECH ICONS
# =====================================================================
@sticker("chip", "tech")
def chip():
    frames = []
    for i in range(24):
        t = i / 24
        p = 0.5 + 0.5 * math.sin(t * 2 * math.pi)
        lay = blank()
        d = ImageDraw.Draw(lay)
        d.rounded_rectangle((262, 262, 762, 762), radius=40, outline=CYAN + (255,), width=22)
        for k in range(5):
            o = 300 + k * 106
            for (a, b) in [((o, 150), (o, 262)), ((o, 762), (o, 874)), ((150, o), (262, o)), ((762, o), (874, o))]:
                d.line([a, b], fill=BLUE + (255,), width=26)
        core = lerp(BLUE, WHITE, p)
        d.rounded_rectangle((390, 390, 634, 634), radius=20, fill=core + (255,))
        mark = tinted(AI_MARK, DARK, 200)
        lay.alpha_composite(mark, (int(S/2 - mark.width/2), int(S/2 - mark.height/2)))
        im = blank()
        with_glow(im, lay, 30 + 30 * p, CYAN, 0.8 + 0.8 * p)
        frames.append(im)
    return frames

@sticker("cloud-sync", "tech")
def cloud_sync():
    frames = []
    def cloud(col):
        lay = blank()
        d = ImageDraw.Draw(lay)
        for (cx, cy, r) in [(400, 520, 170), (560, 440, 210), (720, 540, 150), (560, 580, 160)]:
            d.ellipse((cx - r, cy - r, cx + r, cy + r), fill=col + (255,))
        d.rectangle((260, 560, 860, 700), fill=col + (255,))
        return lay
    for i in range(24):
        t = i / 24
        im = blank()
        c = cloud(BLUE)
        with_glow(im, c, 35, BLUE, 0.9)
        # arrow rising
        d = ImageDraw.Draw(im)
        y = 720 - 300 * t
        a = int(255 * (1 - t) if t > 0.7 else 255)
        d.line([(S/2, y + 110), (S/2, y)], fill=CYAN + (a,), width=40)
        d.polygon([(S/2 - 80, y + 70), (S/2 + 80, y + 70), (S/2, y - 20)], fill=CYAN + (a,))
        frames.append(im)
    return frames

@sticker("ion-orbit", "tech")
def ion_orbit():
    frames = []
    for i in range(36):
        t = i / 36
        lay = blank()
        d = ImageDraw.Draw(lay)
        for k in range(3):
            ang = k * 60
            ell = Image.new("RGBA", (S, S), (0, 0, 0, 0))
            ImageDraw.Draw(ell).ellipse((S/2 - 400, S/2 - 150, S/2 + 400, S/2 + 150), outline=BLUE + (200,), width=10)
            lay.alpha_composite(ell.rotate(ang, resample=Image.BICUBIC))
            ph = t * 2 * math.pi + k * 2.1
            ex, ey = 400 * math.cos(ph), 150 * math.sin(ph)
            a = math.radians(ang)
            x = S/2 + ex * math.cos(a) - ey * math.sin(a)
            y = S/2 - (ex * math.sin(a) + ey * math.cos(a))
            d.ellipse((x - 30, y - 30, x + 30, y + 30), fill=CYAN + (255,))
        d.ellipse((S/2 - 90, S/2 - 90, S/2 + 90, S/2 + 90), fill=WHITE + (255,))
        im = blank()
        with_glow(im, lay, 30, CYAN, 1.1)
        frames.append(im)
    return frames

@sticker("circuit-trace", "tech")
def circuit_trace():
    frames = []
    path = [(120, 512), (320, 512), (400, 420), (560, 420), (560, 620), (720, 620), (800, 512), (904, 512)]
    segs = [math.dist(path[k], path[k+1]) for k in range(len(path) - 1)]
    total = sum(segs)
    for i in range(30):
        t = (i / 30)
        lay = blank()
        d = ImageDraw.Draw(lay)
        d.line(path, fill=(0, 60, 100, 255), width=28, joint="curve")
        for p in path: d.ellipse((p[0]-24, p[1]-24, p[0]+24, p[1]+24), fill=(0, 60, 100, 255))
        dist = t * total
        acc = 0
        pts = [path[0]]
        head = path[-1]
        for k, sl in enumerate(segs):
            if acc + sl >= dist:
                f = (dist - acc) / sl
                head = (path[k][0] + (path[k+1][0] - path[k][0]) * f, path[k][1] + (path[k+1][1] - path[k][1]) * f)
                pts.append(head)
                break
            pts.append(path[k+1]); acc += sl
        d.line(pts, fill=CYAN + (255,), width=28, joint="curve")
        d.ellipse((head[0]-48, head[1]-48, head[0]+48, head[1]+48), fill=WHITE + (255,))
        for p in (path[0], path[-1]): d.ellipse((p[0]-40, p[1]-40, p[0]+40, p[1]+40), outline=CYAN + (255,), width=14)
        im = blank()
        with_glow(im, lay, 30, CYAN, 1.2)
        frames.append(im)
    return frames

@sticker("signal", "tech", fps=8)
def signal():
    frames = []
    for i in range(12):
        lay = blank()
        d = ImageDraw.Draw(lay)
        lit = i % 6
        for k in range(4):
            r = 140 + k * 150
            on = k < lit
            col = CYAN if on else (0, 60, 100)
            d.arc((S/2 - r, 760 - r, S/2 + r, 760 + r), 225, 315, fill=col + (255,), width=42)
        d.ellipse((S/2 - 55, 705, S/2 + 55, 815), fill=(CYAN if lit > 0 else (0, 60, 100)) + (255,))
        im = blank()
        with_glow(im, lay, 30, CYAN, 1.0)
        frames.append(im)
    return frames

@sticker("edge-node", "tech")
def edge_node():
    frames = []
    sats = [(S/2 + 340 * math.cos(math.radians(a)), S/2 + 340 * math.sin(math.radians(a))) for a in range(0, 360, 60)]
    mark = tinted(AI_MARK, DARK, 130)
    for i in range(30):
        t = i / 30
        lay = blank()
        d = ImageDraw.Draw(lay)
        for k, s in enumerate(sats):
            d.line([(S/2, S/2), s], fill=(0, 60, 100, 255), width=14)
            f = (t + k / 6) % 1
            px, py = S/2 + (s[0] - S/2) * f, S/2 + (s[1] - S/2) * f
            d.ellipse((px - 18, py - 18, px + 18, py + 18), fill=CYAN + (255,))
            d.ellipse((s[0] - 50, s[1] - 50, s[0] + 50, s[1] + 50), fill=BLUE + (255,))
        d.ellipse((S/2 - 120, S/2 - 120, S/2 + 120, S/2 + 120), fill=WHITE + (255,))
        lay.alpha_composite(mark, (int(S/2 - mark.width/2), int(S/2 - mark.height/2)))
        im = blank()
        with_glow(im, lay, 30, CYAN, 1.0)
        frames.append(im)
    return frames

# =====================================================================
#  EXPORT
# =====================================================================
def compose(frame, bg):
    if not bg:
        return frame
    base = card()
    base.alpha_composite(frame)
    return base

def to_gif_frames(frames, size, bg, colors=255):
    out = []
    for fr in frames:
        f = fr.resize((size, size), Image.LANCZOS)
        if bg:
            f = f.convert("RGB").convert("P", palette=Image.ADAPTIVE, colors=colors)
        else:
            # 1-bit alpha for GIF: threshold then quantize with reserved transparent index
            a = f.getchannel("A").point(lambda v: 255 if v > 110 else 0)
            rgb = f.convert("RGB")
            p = rgb.quantize(colors=255, method=Image.MEDIANCUT)
            p = p.point(lambda v: v + 1 if v < 255 else v)  # shift to free index 0
            # build final: index 0 transparent
            pal = p.getpalette()[:255*3]
            img = Image.new("P", f.size, 0)
            img.putpalette([0, 0, 0] + pal)
            mask = a.point(lambda v: 255 if v else 0)
            img.paste(p, (0, 0), mask)
            img.info["transparency"] = 0
            f = img
        out.append(f)
    return out

def save_gif(frames, path, fps, bg, limit=None):
    """Save GIF; if `limit` bytes given, progressively reduce colours / frames until under it."""
    attempts = [(255, 1), (128, 1), (255, 2), (96, 2), (64, 2), (64, 3)]
    for colors, step in attempts:
        sub = frames[::step]
        fr = to_gif_frames(sub, sub[0].width, bg, colors)
        kw = dict(save_all=True, append_images=fr[1:], duration=int(1000 / fps * step), loop=0, optimize=True, disposal=2)
        if not bg:
            kw["transparency"] = 0
        fr[0].save(path, **kw)
        if limit is None or os.path.getsize(path) <= limit:
            return
    print("  ! still over limit:", path, os.path.getsize(path))

def save_webp(frames, path, fps, quality=80, limit=None):
    for q, step in [(quality, 1), (60, 1), (45, 1), (60, 2), (40, 2)]:
        sub = frames[::step]
        sub[0].save(path, save_all=True, append_images=sub[1:], duration=int(1000 / fps * step), loop=0,
                    quality=q, method=4)
        if limit is None or os.path.getsize(path) <= limit:
            return
    print("  ! still over limit:", path, os.path.getsize(path))

def emoji_recolor(fr):
    """White -> Ionity logo blue so marks stay visible on light chat backgrounds."""
    r, g, b, a = fr.split()
    white = ImageChops.multiply(ImageChops.multiply(r.point(lambda v: 255 if v > 215 else 0),
                                                   g.point(lambda v: 255 if v > 215 else 0)),
                                b.point(lambda v: 255 if v > 215 else 0))
    blue = Image.new("RGBA", fr.size, LOGO_BLUE + (0,))
    blue.putalpha(a)
    out = fr.copy()
    out.paste(blue, (0, 0), white)
    return out

def resize_all(frames, size):
    return [f.resize((size, size), Image.LANCZOS) for f in frames]

def main():
    only = set(sys.argv[3:])
    for d in ["stickers-512-whatsapp-telegram", "stickers-320-discord", "web-800", "emoji-128", "emoji-128-png", "preview"]:
        os.makedirs(os.path.join(OUT, d), exist_ok=True)
    index = []
    for name, meta in STICKERS.items():
        if only and name not in only:
            continue
        print("rendering", name, flush=True)
        raw = meta["fn"]()
        fps = meta["fps"]
        card_frames = [compose(f, meta["bg"]) for f in raw]
        # 512 sticker: GIF (dark card) + WebP (dark card, full alpha corners)
        f512 = resize_all(card_frames, 512)
        save_gif(f512, os.path.join(OUT, "stickers-512-whatsapp-telegram", f"ionity-{name}.gif"), fps, True)
        save_webp(f512, os.path.join(OUT, "stickers-512-whatsapp-telegram", f"ionity-{name}.webp"), fps, limit=490_000)
        # 320 discord sticker (Discord limit 512 KB)
        save_gif(resize_all(card_frames, 320), os.path.join(OUT, "stickers-320-discord", f"ionity-{name}.gif"), fps, True, limit=500_000)
        # 800 web
        save_gif(resize_all(card_frames, 800), os.path.join(OUT, "web-800", f"ionity-{name}.gif"), fps, True)
        # emoji 128 transparent (Slack limit 128 KB, Discord 256 KB)
        if meta["emoji"]:
            ef = [emoji_recolor(f) for f in raw]
            e = resize_all(ef[::2] if len(ef) > 16 else ef, 128)
            save_gif(e, os.path.join(OUT, "emoji-128", f"ionity_{name.replace('-', '_')}.gif"), max(6, fps // 2 if len(ef) > 16 else fps), False, limit=125_000)
            # static PNG emoji = most "complete" frame (last of first cycle)
            ef[-1].resize((128, 128), Image.LANCZOS).save(os.path.join(OUT, "emoji-128-png", f"ionity_{name.replace('-', '_')}.png"))
        # preview still
        card_frames[len(card_frames) // 2].resize((256, 256), Image.LANCZOS).save(os.path.join(OUT, "preview", f"{name}.png"))
        index.append((name, meta["group"], len(raw), fps))
    with open(os.path.join(OUT, "index.txt"), "w") as fh:
        for row in index:
            fh.write("%s\t%s\t%d frames\t%d fps\n" % row)

if __name__ == "__main__":
    main()
