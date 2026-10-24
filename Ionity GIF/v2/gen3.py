#!/usr/bin/env python3
"""Ionity v2 transparent add-on: no card, no outline - only the artwork.
Usage: python3 gen3.py <assets-dir> <out-dir> [--only a,b] [--shard i/n]
  transparent-512-webp/  animated WebP, full 8-bit alpha (soft glow fades into any background)
  transparent-512-gif/   animated GIF, edge traced from the artwork alpha, glow trimmed (crisp edge)
  transparent-512-png/   PNG still, full alpha
White parts are switched to Ionity logo blue so stickers stay visible on light chat backgrounds.
(c) 2018-2026 Antwerp Designs | Ionity (Pty) Ltd - Policy 986 AED
"""
import os, sys, shutil, tempfile
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import gen2 as G
import gen as g
from PIL import Image

EDGE = 128  # alpha cut for GIF edge

def _no_glow(layer, radius, color, strength=1.0):
    """Transparent set: no neon halo, so the edge is the artwork's own edge."""
    return Image.new("RGBA", layer.size, (0, 0, 0, 0))
G.glow = _no_glow
g.glow = _no_glow

def soft_floor(fr, floor=70):
    """Remove faint background haze (e.g. light rays) so the area around the artwork is fully clear."""
    out = fr.copy()
    out.putalpha(fr.getchannel("A").point(lambda v: 0 if v < floor else v))
    return out

def hard_edge(fr):
    a = fr.getchannel("A").point(lambda v: 255 if v >= EDGE else 0)
    out = fr.copy()
    out.putalpha(a)
    return out

DIRS = ["stickers-512-webp-whatsapp", "stickers-512-webm-telegram", "stickers-512-gif", "stickers-320-discord",
        "web-800", "stills-512-png"]

def main():
    OUT = sys.argv[2]
    args = sys.argv[3:]
    names = list(G.STICKERS)
    if "--only" in args:
        names = args[args.index("--only") + 1].split(",")
    if "--shard" in args:
        i, n = map(int, args[args.index("--shard") + 1].split("/"))
        names = names[i::n]
    for d in DIRS:
        os.makedirs(os.path.join(OUT, d), exist_ok=True)
    tmp = tempfile.mkdtemp(prefix="tr_", dir=os.path.dirname(os.path.abspath(__file__)))
    for name in names:
        meta = G.STICKERS[name]
        raw = meta["fn"]()
        fps = meta["fps"]
        big = [soft_floor(g.emoji_recolor(f)) for f in raw]
        sd = os.path.join(tmp, name)
        s512 = os.path.join(sd, "s512"); G.write_seq(big, s512, 512)
        G.ff_webp(s512, os.path.join(OUT, "stickers-512-webp-whatsapp", f"ionity-{name}.webp"), fps, limit=495_000)
        G.ff_webm(s512, os.path.join(OUT, "stickers-512-webm-telegram", f"ionity-{name}.webm"), min(fps, 30), len(big))
        for size, d, lim in ((512, "stickers-512-gif", None), (320, "stickers-320-discord", 500_000), (800, "web-800", None)):
            hd = os.path.join(sd, "h%d" % size)
            G.write_seq([hard_edge(f.resize((size, size), Image.LANCZOS)) for f in big], hd, size)
            G.ff_gif(hd, os.path.join(OUT, d, f"ionity-{name}.gif"), fps, transparent=True, limit=lim)
        big[-1].resize((512, 512), Image.LANCZOS).save(os.path.join(OUT, "stills-512-png", f"ionity-{name}.png"))
        shutil.rmtree(sd, ignore_errors=True)
        print("done", name, flush=True)
    shutil.rmtree(tmp, ignore_errors=True)

if __name__ == "__main__":
    main()
