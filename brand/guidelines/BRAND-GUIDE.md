<!--
========================================================================================
AEDI - IONITY GLOBAL - BRAND GUIDE
Author: Johan Wilhelm van Antwerp | Ionity (Pty) Ltd | AEDI
Document ID: DOC-2026-08-002 | Version: 1.0 | Updated: 2026-08-30 SAST
Governance: Policy 986 AED | License: AED 900 | CC BY-NC-SA 4.0 where stated
(c) 2018-2026 Antwerp Designs | Ionity (Pty) Ltd - All Rights Reserved - TM2
Classification: PUBLIC | Building Tomorrow, Today.
========================================================================================
-->

# Ionity Global — Brand Guide

> **Building Tomorrow, Today.**
> Ionity (Pty) Ltd · AEDI — Antwerp Ecosystems Designs Ionity

---

## 1 · The marks

| Mark | File | When to use |
|---|---|---|
| **Primary logo** | `brand/logos/ionity-global-logo-primary.png` | Default. Any surface, any medium. |
| **White logo** | `brand/logos/ionity-logo-white.png` | Dark backgrounds, photography, video lower-thirds. |
| **Dark logo** | `brand/logos/ionity-logo-dark.png` | Light backgrounds, print, documents. |
| **Transparent lockup** | `brand/logos/ionity-global-pty-ltd-transparent.png` | Overlays, watermarks, slide corners. |
| **Badge** | `brand/logos/ionity-global-badge-932.png` | Avatars, app tiles, square crops. |
| **AEDI mark** | `brand/marks/aedi-mark.svg` | Engineering, governance and Policy 986 contexts. True vector. |
| **Ecosystems Eagle** | `brand/marks/ionity-ecosystems-eagle.svg` | Ecosystem, partner and community material. |
| **AI mark** | `brand/marks/ionity-ai-mark.png` | AI / Edge-AI product surfaces. |
| **Nobify** | `brand/product-marks/nobify-logo.png` | Nobify product only. |

Every mark above has a full generated set under `derivatives/` — sizes, WebP, `.ico`,
PWA icons and social scopes. **Never re-export a mark by hand; take the generated size.**

### Clear space & minimum size

```
        ┌ ── ── ── ── ── ── ── ── ── ┐
        │        25% of height       │
        │   ┌───────────────────┐    │      clear space = 0.25 × mark height
        │   │                   │    │      on all four sides
   25%  │   │      [ MARK ]     │    │ 25%
        │   │                   │    │      minimum size
        │   └───────────────────┘    │        mark ......... 24 px
        │        25% of height       │        full lockup ... 96 px wide
        └ ── ── ── ── ── ── ── ── ── ┘        print lockup ... 20 mm wide
```

### Do not

- recolour, gradient-fill or invert a mark outside the supplied variants
- stretch, squash, rotate, skew or add perspective
- add drop shadows, outlines, bevels, glows or strokes
- place a mark on a low-contrast background or a busy photograph without a scrim
- re-typeset the wordmark or set it in a substitute typeface
- combine a mark with another logo inside the clear-space zone
- use the marks on third-party deliverables (Ionity property, TM²)

---

## 2 · Colour

| Token | Hex | RGB | Role |
|---|---|---|---|
| `--ionity-brand-purple` | `#5746E3` | 87, 70, 227 | Primary |
| `--ionity-brand-teal` | `#00D4B8` | 0, 212, 184 | Secondary |
| `--ionity-brand-cyan` | `#00D2FF` | 0, 210, 255 | Web accent |
| `--ionity-brand-c6ff` | `#00C6FF` | 0, 198, 255 | PWA `theme-color` |
| `--ionity-surface-bg` | `#0B0D12` | 11, 13, 18 | Canvas |
| `--ionity-surface-surface-1` | `#151922` | 21, 25, 34 | Cards, panels |
| `--ionity-surface-border` | `#242B38` | 36, 43, 56 | Hairlines |
| `--ionity-surface-ink` | `#06061E` | 6, 6, 30 | AEDI mark field |
| `--ionity-text-default` | `#E7EBF2` | 231, 235, 242 | Body text |
| `--ionity-text-muted` | `#8B93A4` | 139, 147, 164 | Secondary text |

**Brand gradient** `linear-gradient(90deg, #5746E3 0%, #00D4B8 50%, #00D2FF 100%)` —
use for accent rules, key numbers and hero fills. Never for body text at small sizes.

**Document palette** (letterhead, reports, per the AEDI document standard):
header `#1A1A2E` · accent `#E94560` · body `#16213E` · secondary `#0F3460` ·
watermark `#B8C5D6` · rule `#D4E6F1` · band `#F0F7FA`.

Machine sources: `brand/tokens/ionity-tokens.{json,yaml,css,scss,ts,js}` ·
palette plate `brand/swatches/ionity-colour-system.png` · GIMP/Inkscape `ionity-global.gpl`.

### Contrast

Text on `#0B0D12`: default text passes AA at all sizes; muted text is for ≥ 14 px
secondary content only. Cyan and teal on the dark canvas pass AA for large text and
UI components — do not set small body copy in either.

---

## 3 · Typography

| Use | Stack | Size |
|---|---|---|
| Interface & headings | `Inter, 'Segoe UI', system-ui, -apple-system, sans-serif` | — |
| Code, data, identifiers | `'JetBrains Mono', 'Cascadia Mono', Consolas, monospace` | — |
| Document body | per AEDI document standard | 11 pt |
| Document subheader | " | 14 pt |
| Document header | " | 18 pt |

Bold for authority and key terms · italic for definitions and secondary emphasis ·
monospace for technical specification, hashes and identifiers.

---

## 4 · Naming & versioning

```
<subject>-<variant>-<size>.<ext>
ionity-global-logo-primary-512.png
ionity-global-logo-primary-og-facebook-linkedin-1200x630.png
ionity-ai-mark-maskable-512.png
```

Lower-case kebab-case only. No spaces, no capitals, no parentheses, no " - Copy".
Document IDs follow `DOC-YYYY-MM-###`, versions `V#.#`.

---

## 5 · Voice

**Tagline** — *Building Tomorrow, Today.*
**Motto** — *Anything is Possible with God.*
**Positioning** — "I do not innovate. I create."

Direct, engineering-first, confident. Lead with the outcome, then the mechanism.
Prefer active voice. Quantify where a number exists (e.g. "up to 68 % ongoing
maintenance saving vs. legacy OEM"). Never over-claim, never pad.

---

## 6 · Governance

All marks and material are governed by **Policy 986 AED**; licence **AED 900**
(hardware & software), **CC BY-NC-SA 4.0** where explicitly stated. Marks are
Ionity property, **TM²**. Use on Ionity / Johan Wilhelm van Antwerp deliverables only.

"Ionity" refers exclusively to **www.ionity.today**
(reference www.ionity.co.za). Not affiliated with ionity.com or any related domain.

---

© 2018–2026 Antwerp Designs | Ionity (Pty) Ltd — All Rights Reserved — TM²
Author: Johan Wilhelm van Antwerp · ORCID 0009-0005-7181-0347 · info@ionity.today
