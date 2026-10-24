========================================================================================
AEDI - IONITY GLOBAL - STICKER & EMOJI PACK v1.0
Author: Johan Wilhelm van Antwerp | Ionity (Pty) Ltd | AEDI
Document ID: DOC-2026-10-002 | Version: 1.0 | Updated: 2026-10-19 SAST
Governance: Policy 986 AED | License: AED 900 | CC BY-NC-SA 4.0 where stated
(c) 2018-2026 Antwerp Designs | Ionity (Pty) Ltd - All Rights Reserved - TM2
Web: https://www.ionity.today | https://www.ionity.world | Ref: https://www.ionity.co.za
Classification: PUBLIC | Building Tomorrow, Today. | Anything is Possible with God.
========================================================================================

[SOURCE ASSETS]
  AI mark ............ ionity.co.za/assets/img/ai-mark-white.png
  IONITY wordmark .... ionity.co.za/assets/img/wordmark.png
  Animated wordmark .. ionity.co.za/assets/img/ionity-anim.webp (upscaled, 58 frames)
  IO-MAN ............. ionity.co.za/assets/img/freebies/ioman-banner.webp (ASCII motifs)
  Palette ............ cyan #00D2FF, blue #3366FF, logo blue #2160AE, red #FF2828,
                       dark #0B0C10, green #00FF96 (ok/success), amber #FFBE28 (confetti)
  Type ............... monospace (Courier-style) for terminal/tagline stickers

[FOLDERS]
  stickers-512-whatsapp-telegram/   512x512 - GIF + animated WebP, dark rounded card
  stickers-320-discord/             320x320 GIF, each under 512 KB (Discord sticker limit)
  web-800/                          800x800 GIF for README, posts, ionity.today / .co.za
  emoji-128/                        128x128 transparent animated GIF, each under 128 KB
                                    (Slack limit; Discord allows 256 KB)
  emoji-128-png/                    128x128 transparent static PNG (fallback / Slack static)
  preview/                          256px stills of every sticker
  sticker-sheet.jpg                 contact sheet of all 29 stickers
  emoji-sheet.png                   contact sheet of all 22 emojis on a light background

[STICKERS - 29]
  brand (8)     ai-pulse, ai-flip, ai-loader, ionity-neon, ionity-scan, ionity-typing,
                ionity-wordmark-anim, ionity-global-badge
  reaction (10) yes-check, no-x, thinking, ion-fire, celebrate, warning, heartbeat,
                hundred, bolt, thumbs-up
  tagline (5)   tagline-building-tomorrow, tagline-anything-possible, ascii-ioman-run,
                ascii-spore, terminal-ok
  tech (6)      chip, cloud-sync, ion-orbit, circuit-trace, signal, edge-node

[EMOJIS - 22]
  Every sticker except the text-heavy ones (taglines, typing, badge, terminal, IO-MAN run),
  rendered transparent with the white AI mark recoloured to logo blue so it stays visible
  on light chat backgrounds. Names use underscores (ionity_ai_pulse) so they paste
  straight into Slack / Discord as :ionity_ai_pulse:.

[PLATFORM NOTES]
  WhatsApp   Animated stickers: use the .webp files (512x512, < 500 KB, loops). Add via a
             sticker-maker app or the WhatsApp Business sticker API.
  Telegram   Static sticker packs accept 512x512 .webp/.png. Animated Telegram packs need
             .tgs or .webm - send the .gif to @Stickers and it is converted to a video
             sticker, or convert with ffmpeg: ffmpeg -i x.gif -c:v libvpx-vp9 -b:v 0 -crf 30
             -an -t 3 x.webm
  Discord    Server emojis: emoji-128 GIFs (< 256 KB). Server stickers: stickers-320 GIFs
             (< 512 KB, 320x320).
  Slack      Custom emoji: emoji-128 GIFs (< 128 KB) or the PNG set.
  GitHub     ![Ionity](web-800/ionity-ai-pulse.gif) in README.md.

[REGENERATE]
  python3 gen.py <assets-dir> <out-dir> [sticker-name ...]
  All animations are procedural (Pillow); edit colours / timings at the top of gen.py.
