<!--
========================================================================================
AEDI - IONITY GLOBAL - ASSETS WIKI - SEO AND INDEXING
Author: Johan Wilhelm van Antwerp | Ionity (Pty) Ltd | AEDI
Document ID: DOC-2026-10-005 | Version: 1.0 | Updated: 2026-10-25 SAST
Governance: Policy 986 AED | License: AED 900 | CC BY-NC-SA 4.0 where stated
(c) 2018-2026 Antwerp Designs | Ionity (Pty) Ltd - All Rights Reserved - TM2
Classification: PUBLIC | Building Tomorrow, Today.
========================================================================================
-->

# SEO and Indexing

How search engines, social platforms and AI agents should discover, index and attribute this repository — and how to keep it that way.

## Canonical URLs

| Surface | URL | Notes |
|---|---|---|
| **Canonical site (GitHub Pages)** | https://ionity-global.github.io/ASSETS-IONITY-2026-/ | Built from `main` at `/`; `.nojekyll` present |
| Canonical repository | https://github.com/Ionity-Global/ASSETS-IONITY-2026- | Source of truth |
| Public mirror | https://github.com/AntwerpDesignsIonity/ASSETS-IONITY-2026- | Same history; pages there point `rel=canonical` back to the Ionity-Global site |
| Wiki (GitHub) | https://github.com/Ionity-Global/ASSETS-IONITY-2026-/wiki | GitHub serves wikis of repositories under 500 stars with `noindex`, so every wiki page is **also** committed under `wiki/` in the repo and published as HTML on Pages for indexing |
| Indexable docs | https://ionity-global.github.io/ASSETS-IONITY-2026-/wiki/ | `Home`, `Asset-Catalog`, `Brand-and-Licensing`, `IoT`, `SEO-and-Indexing`, `Official-Links` as `.html` (+ `.md` sources) |
| Machine catalogue | https://ionity-global.github.io/ASSETS-IONITY-2026-/assets.json | Schema: `assets.schema.json` |
| AI discovery | https://ionity-global.github.io/ASSETS-IONITY-2026-/llms.txt | llms.txt convention |
| Sitemap | https://ionity-global.github.io/ASSETS-IONITY-2026-/sitemap.xml | Referenced from `robots.txt` |

## Target keywords

| Cluster | Keywords |
|---|---|
| Brand | Ionity, Ionity Global, Ionity (Pty) Ltd, AEDI, AEDi, Antwerp Designs, Antwerp Ecosystems Designs Ionity, Johan Wilhelm van Antwerp |
| Assets | Ionity logo, Ionity brand assets, Ionity media kit, Ionity sticker pack, Ionity emoji, Ionity wallpaper 4K, AEDI logo, Ionity favicon, Ionity business card, official assets, AI asset catalog |
| IoT / AI | Ionity IoT, AIoT, Edge AI, Edge AI Node, Industrial IoT, Zero-Trust IoT Security, Digital Twin Architecture, Cloud-to-Edge Continuity, Predictive Maintenance Systems, SCADA, Ultra-Low Power Edge Hardware, Energy-Efficient Computing, Power Saving Units, IO // WAY Gateway, Native-AI |
| Governance | Policy 986 AED, License AED 900, AED 990, CC BY-NC-SA 4.0 |
| Location | Centurion, Gauteng, Pretoria, South Africa |

Avoid optimising for "Ionity charging", "Ionity EV" or "ionity.com" — those belong to an unrelated European company; every page carries the exclusion notice instead.

## Page metadata standard

Every HTML page in the repository (site and `wiki/*.html`) carries:

```html
<title>Ionity Global — <Page> | Official Assets | AEDI</title>
<meta name="description" content="…120–160 characters…">
<meta name="keywords" content="Ionity, Ionity Global, AEDI, …">
<meta name="robots" content="index, follow, max-image-preview:large">
<meta name="author" content="Johan Wilhelm van Antwerp">
<meta name="theme-color" content="#0d1b2a">
<link rel="canonical" href="https://ionity-global.github.io/ASSETS-IONITY-2026-/<page>">
<link rel="icon" href="../ionity_logo.ico">
<meta property="og:type" content="website">
<meta property="og:site_name" content="Ionity Global — Official Assets">
<meta property="og:title" content="…"> <meta property="og:description" content="…">
<meta property="og:image" content="https://ionity-global.github.io/ASSETS-IONITY-2026-/Ionity_Banner.png">
<meta name="twitter:card" content="summary_large_image"> <meta name="twitter:site" content="@JohanAntwerp">
```

Plus Dublin Core (`DC.title`, `DC.creator`, `DC.publisher`, `DC.rights`) and a `rel="license"` link to the licence page, matching www.ionity.today.

## Structured data (JSON-LD)

The site root declares a `schema.org/DataCatalog` with a `Dataset` distribution (`assets.json`). Wiki pages add `WebPage` / `TechArticle` with `isPartOf` → the catalogue and `publisher` → the `Organization`:

```json
{
  "@context": "https://schema.org",
  "@type": "Organization",
  "name": "Ionity (Pty) Ltd",
  "alternateName": ["Ionity Global", "AEDI", "Antwerp Designs"],
  "url": "https://www.ionity.today",
  "logo": "https://ionity-global.github.io/ASSETS-IONITY-2026-/Ionity_Global_Pty_LTD_Transparrent_optimized_1000.png",
  "founder": {"@type": "Person", "name": "Johan Wilhelm van Antwerp",
              "sameAs": "https://orcid.org/0009-0005-7181-0347"},
  "address": {"@type": "PostalAddress", "addressLocality": "Centurion",
              "addressRegion": "Gauteng", "addressCountry": "ZA"},
  "email": "info@ionity.today", "telephone": "+27646999877",
  "sameAs": ["https://www.ionity.world", "https://www.ionity.co.za",
             "https://github.com/Ionity-Global", "https://github.com/AntwerpDesignsIonity",
             "https://www.youtube.com/@Ionityglobal", "https://www.linkedin.com/in/ionity",
             "https://x.com/JohanAntwerp"]
}
```

## robots.txt and sitemap.xml

`robots.txt` allows all agents and names the sitemap. `sitemap.xml` lists the directory, `assets.json`, `llms.txt` and every `wiki/*.html` page with `changefreq` and `priority`. AI crawlers (GPTBot, ClaudeBot, Google-Extended, PerplexityBot, CCBot) are **allowed** — public assets are meant to be discoverable — subject to the licence terms in [Brand and Licensing](Brand-and-Licensing).

## llms.txt

`llms.txt` follows the llms.txt convention: a one-paragraph description, the canonical catalogue / schema / docs links, discovery guidance (use `assets.json` as the authoritative index; `raw_url` for bytes, `github_url` for context; do not infer endorsement from public availability) and the exclusion notice. Agents should treat `assets.json` + `llms.txt` + the `wiki/` pages as the complete, authoritative description of this repository.

## GitHub-side signals

Repository **description**, **website** (homepage) and **topics** are set so GitHub's own search and Google's crawl of github.com surface the repo for the brand keywords: topics `ionity`, `ionity-global`, `aedi`, `antwerp-designs`, `brand-assets`, `media-kit`, `design-tokens`, `logos`, `stickers`, `iot`, `edge-ai`, `aiot`, `south-africa`, `policy-986-aed`. `CITATION.cff` gives scholarly tools a citable record; `README.md` links to the site, catalogue, wiki and `llms.txt`.

## Indexing checklist

1. Submit `https://ionity-global.github.io/ASSETS-IONITY-2026-/sitemap.xml` in Google Search Console and Bing Webmaster Tools (verify the `ionity-global.github.io` property via HTML-file or meta-tag method).
2. Link to the Pages site from www.ionity.today, www.ionity.world, www.ionity.co.za and the Linktree/Gravatar profiles — inbound links from the owned domains are the strongest ranking signal available.
3. After every asset change: `node scripts/generate-catalog.mjs`, commit `assets.json`, bump the `<lastmod>` dates in `sitemap.xml`.
4. Keep file names descriptive (`ionity-edge-node.gif`, not `adasd.png`) — image search indexes file names and alt text.
5. Keep every page's `rel=canonical` pointing at the Ionity-Global Pages site, including the mirror.
6. Re-check `robots.txt` is reachable and returns `200` after any Pages change.

---
*Ionity (Pty) Ltd · AEDI · Policy 986 AED · (c) 2018-2026 Antwerp Designs | Ionity (Pty) Ltd — All Rights Reserved — TM2*
