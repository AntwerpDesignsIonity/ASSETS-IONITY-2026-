<!--
========================================================================================
AEDI - IONITY GLOBAL - ASSETS WIKI - ASSET CATALOG
Author: Johan Wilhelm van Antwerp | Ionity (Pty) Ltd | AEDI
Document ID: DOC-2026-10-002 | Version: 1.0 | Updated: 2026-10-25 SAST
Governance: Policy 986 AED | License: AED 900 | CC BY-NC-SA 4.0 where stated
(c) 2018-2026 Antwerp Designs | Ionity (Pty) Ltd - All Rights Reserved - TM2
Classification: PUBLIC | Building Tomorrow, Today.
========================================================================================
-->

# Asset Catalog

The repository holds roughly **5,300 files (≈4.7 GB)** across brand, product, media, document and web assets. This page is the human map; the machine map is [`assets.json`](https://ionity-global.github.io/ASSETS-IONITY-2026-/assets.json) (contract: [`assets.schema.json`](https://ionity-global.github.io/ASSETS-IONITY-2026-/assets.schema.json)).

## Folder map

| Folder | Files | Size | Purpose |
|---|---:|---:|---|
| `Ionity GIF/` | ~1,080 | ~1.37 GB | Ionity sticker & emoji pack v2.0 and all platform exports |
| `derivatives/` | ~2,980 | ~360 MB | Generated size ladders and platform scopes for every master mark |
| `assets/` | ~200 | ~395 MB | Legacy web asset tree (images, css, js, favicon, audio, videos, licences) |
| `4k Walls/` | 29 | ~385 MB | 4K wallpapers and hero backgrounds |
| `business-pack/` | ~340 | ~185 MB | Curated, ready-to-send brand pack |
| `brand/` | ~100 | ~150 MB | Master logos, marks, icons, tokens, guidelines, music, clips |
| `archives/` | 4 | ~82 MB | Packed archives (e.g. `assets.7z`) |
| `ansi/` | ~425 | ~30 MB | Terminal art and players |
| `process/` | 3 | ~13 MB | Process documentation and working files |
| `data/` | 21 | <1 MB | Links registry (`data/links/`) and misc structured data |
| `Mario Sounds/` | 7 | <1 MB | Retro sound effects used by Ionity terminal / game projects |
| `scripts/` | 1 | <1 MB | `generate-catalog.mjs` — rebuilds `assets.json` |

### `brand/`
`brand/logos` · `brand/marks` · `brand/product-marks` · `brand/icons` · `brand/swatches` · `brand/tokens` · `brand/guidelines` · `brand/clips` · `brand/music` (AEDI.mp4, IONITY.mp4, IoT.mp4, instrumental and vocal tracks in `.m4a`).

### `business-pack/`
Numbered for hand-off: `01-logos` · `02-marks` · `03-favicon-web` · `04-social` · `05-team` · `06-documents` · `07-motion` · `08-brand-system` · `09-terminal` · `10-vector` · `11-modern-formats` · `12-terminal`.

### `derivatives/`
`png` (20-step ladder) · `png-square` · `avif` (256/512/1024) · `ico` · `favicon` · `pwa` · `social` (20 platform-exact sizes) · `posters` · `people` · `animation`. Everything here is generated from a master in `brand/` and is marked `linguist-generated`.

### `Ionity GIF/` — sticker & emoji pack v2.0
| Sub-folder | Target |
|---|---|
| `stickers-512-whatsapp-telegram/` | WhatsApp / Telegram 512 px (WebP / WebM) |
| `stickers-320-discord/` | Discord 320 px |
| `emoji-128/`, `emoji-128-png/` | Emoji 128 px |
| `web-800/` | Web 800 px GIF / WebP (ion-orbit, edge-node, chip, ai-pulse, ai-loader …) |
| `v2/` | v2 masters, `with-card/` business-card variants, zipped platform packs, `ionity-stickers-v2.wastickers` |
| `ionity-sticker-emoji-pack-v2.0/` | Assembled v2.0 release folder |
| `preview/` | Preview sheets |
| `Ionity-Stickers-Emojis-ALL.zip` | Everything in one archive (706 MB — stored with **Git LFS**) |

### Root-level highlights
| File | Use |
|---|---|
| `Ionity_Global_Pty_LTD_Transparrent.png` / `_optimized_1000.png` | Primary transparent logo (full / web-optimised) |
| `AEDi.svg`, `AEDi.png`, `AEDi-AntwerpDesigns-Ionityglobal.png` | AEDI mark |
| `ionity_logo.ico` | Favicon |
| `Ionity_Banner.png`, `Banner_ionity_YT.png`, `ionity_banner_YT_2.png` | Banners (YouTube / social) |
| `ionity_animation.gif`, `ionity_animation_transp.gif`, `ionity-card-electric.gif` | Animated marks |
| `*-Business-Card-ANIMATED.gif`, `*Business card*.png` | Team business cards |
| `Ionity Global Portfolio V7. REV 1 Johan.pdf` | Company portfolio |
| `IONITY_INTRO_POWERSHELL.ps1` | Terminal intro script |
| `ionity-links.{json,yml,txt,b64.txt}` + `.checksums.txt` | Official links registry (see [Official Links](Official-Links)) |
| `License-Ionity Global.txt`, `Lisence governing AEDI.txt`, `LICENSE` | Licensing (see [Brand and Licensing](Brand-and-Licensing)) |

## Categories and formats

Catalogue categories: `image` · `video` · `audio` · `document` · `metadata` · `code` · `archive` · `other`.

Common formats: PNG, JPG/JPEG, SVG, WebP, AVIF, GIF, ICO, MP4, WebM, MP3, M4A, WAV, PDF, DOCX, JSON, YAML, TXT, ANS, ZIP, 7z.

## Linking to an asset

| Need | URL pattern |
|---|---|
| Raw bytes (hot-link, `<img src>`, fetch) | `https://raw.githubusercontent.com/Ionity-Global/ASSETS-IONITY-2026-/main/<path>` |
| Human view with history | `https://github.com/Ionity-Global/ASSETS-IONITY-2026-/blob/main/<path>` |
| Pages-hosted copy | `https://ionity-global.github.io/ASSETS-IONITY-2026-/<path>` |

URL-encode spaces as `%20` (e.g. `Ionity%20GIF/web-800/ionity-chip.gif`).

## `assets.json` contract

Each record in the `assets` array contains:

```json
{
  "name": "Ionity_Global_Pty_LTD_Transparrent.png",
  "path": "Ionity_Global_Pty_LTD_Transparrent.png",
  "category": "image",
  "format": "png",
  "bytes": 2082820,
  "raw_url": "https://raw.githubusercontent.com/.../main/Ionity_Global_Pty_LTD_Transparrent.png",
  "github_url": "https://github.com/.../blob/main/Ionity_Global_Pty_LTD_Transparrent.png"
}
```

Agents should fetch `assets.json`, filter on `name` / `path` / `category` / `format`, use `raw_url` for bytes and `github_url` for context.

## Regenerating the catalogue

```console
node scripts/generate-catalog.mjs
```

Run after staging new files (the generator inventories tracked files), then commit the updated `assets.json` together with the asset changes.

## Large files

GitHub's hard limit is 100 MB per file. Files above that are tracked with **Git LFS** (currently `Ionity GIF/Ionity-Stickers-Emojis-ALL.zip`). Clone with `git lfs install` first if you need those archives; everything else clones normally.

---
*Ionity (Pty) Ltd · AEDI · Policy 986 AED · (c) 2018-2026 Antwerp Designs | Ionity (Pty) Ltd — All Rights Reserved — TM2*
