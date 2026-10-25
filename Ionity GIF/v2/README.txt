========================================================================================
AEDI - IONITY GLOBAL - STICKER & EMOJI PACK v2.0 (HIGH QUALITY)
Author: Johan Wilhelm van Antwerp | Ionity (Pty) Ltd | AEDI
Document ID: DOC-2026-10-003 | Version: 2.0 | Updated: 2026-10-24 SAST
Governance: Policy 986 AED | License: AED 900 | CC BY-NC-SA 4.0 where stated
(c) 2018-2026 Antwerp Designs | Ionity (Pty) Ltd - All Rights Reserved - TM2
Web: https://www.ionity.today | Ref: https://www.ionity.co.za
Classification: PUBLIC | Building Tomorrow, Today. | Anything is Possible with God.
========================================================================================

[WHAT'S NEW IN v2]
  - 59 animated stickers (v1 had 29) and 40 emojis (v1 had 22)
  - Premium card: navy radial gradient, dot grid, top gloss, cyan->blue gradient border
  - Global-palette GIFs with error-diffusion dithering (ffmpeg) - no banding on glows
  - Telegram video stickers (.webm, VP9 with alpha) - ready for @Stickers
  - Die-cut "cut-out" stickers: transparent with white outline + soft shadow (WhatsApp style)
  - 512 px PNG stills of every sticker
  - Smoother motion: 20-24 fps loops, eased pop-ins, overshoot bounces
  - Every file checked against its platform's size limit

[NEW STICKERS IN v2 - 30]
  greeting (7)  hallo, dankie, baie-dankie, goeie-more, goeie-nag, lekker, shalom (Hebrew)
  faith (2)     amen, cross-light
  devlife (11)  ship-it, on-it, deploying, bug-fixed, coffee, brb, well-done, wow,
                error-404, status-online, countdown
  tech (8)      globe, neural-net, lock-secure, audit-scan, battery-charge, server-rack,
                iot-home, data-stream
  brand (2)     ai-assemble (particles build the AI mark), ionity-glitch
  + all 29 v1 stickers re-rendered with the new card and encoder

[TRANSPARENT = MAIN FILES (v2.1)]
  Every sticker in every format now has NO background: only the artwork, edge traced from its
  shape, everything else see-through. White parts use Ionity logo blue so they show on light
  AND dark chats.
    stickers-512-webp-whatsapp/  soft anti-aliased edge (8-bit alpha)      < 500 KB
    stickers-512-webm-telegram/  VP9 with alpha                            < 256 KB, <= 3 s
    stickers-512-gif/            crisp 1-bit edge (GIF can't do soft edges)
    stickers-320-discord/        crisp 1-bit edge                           < 512 KB
    web-800/                     crisp 1-bit edge
    stills-512-png/              PNG, full alpha
    emoji-128-gif / emoji-128-png  transparent (unchanged)
  The earlier versions on the dark rounded card, and the white-outline die-cut set,
  are kept as zips in with-card/.

[FOLDERS - v2.0 card versions, now in with-card/*.zip]
  stickers-512-webp-whatsapp/  512x512 animated WebP on card, < 500 KB  -> WhatsApp
  stickers-512-cutout-webp/    512x512 die-cut WebP, transparent, < 500 KB -> WhatsApp / Signal
  stickers-512-webm-telegram/  512x512 VP9+alpha WEBM, <= 3 s, < 256 KB -> Telegram video stickers
  stickers-512-gif/            512x512 GIF on card (universal)
  stickers-320-discord/        320x320 GIF, < 512 KB -> Discord server stickers
  web-800/                     800x800 GIF -> websites, README, social posts
  emoji-128-gif/               128x128 transparent GIF, < 128 KB -> Slack / Discord emoji
  emoji-128-png/               128x128 transparent PNG (static emoji)
  stills-512-png/              512x512 PNG still of every sticker
  preview/                     256 px previews
  sticker-sheet-v2.jpg | cutout-sheet-v2.jpg | emoji-sheet-v2.png   contact sheets

[HOW TO ADD]
  Telegram   Message @Stickers -> /newvideo -> send each .webm from stickers-512-webm-telegram
  WhatsApp   Use a sticker-maker app (e.g. "Sticker Maker") and import the .webp files;
             3-30 stickers per pack, plus a 96x96 tray icon (use emoji-128-png/ionity_ai_pulse.png)
  Discord    Server Settings -> Emoji: emoji-128-gif   |  Stickers: stickers-320-discord
  Slack      Customize workspace -> Emoji -> Add: emoji-128-gif (name auto: :ionity_hallo:)
  GitHub     ![Ionity](web-800/ionity-ai-assemble.gif)

[REGENERATE]
  python3 gen2.py <assets-dir> <out-dir> [--only a,b] [--shard 0/2]   (needs gen.py + ffmpeg)
  Source assets: ionity.co.za/assets/img/ai-mark-white.png, wordmark.png, ionity-anim.webp
