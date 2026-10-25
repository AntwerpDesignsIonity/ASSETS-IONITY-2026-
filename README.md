<!--
========================================================================================
AEDI - IONITY GLOBAL - OFFICIAL ASSET REPOSITORY 2026
Author: Johan Wilhelm van Antwerp | Ionity (Pty) Ltd | AEDI | Policy 986 AED
(c) 2018-2026 Antwerp Designs | Ionity (Pty) Ltd - All Rights Reserved - TM2
Web: https://www.ionity.today | https://www.ionity.world | Ref: https://www.ionity.co.za
========================================================================================
-->

# Ionity Global — Official Asset Repository (2026)

Official public digital asset directory for **Ionity (Pty) Ltd / Ionity Global / AEDI** — logos, marks, icons, favicons, PWA and social sets, sticker & emoji packs, music, video, business cards, ANSI art, design tokens and a machine-readable catalogue. Governed by **Policy 986 AED**.

## Browse

- **Asset directory (GitHub Pages):** https://ionity-global.github.io/ASSETS-IONITY-2026-/
- **Machine-readable catalog:** https://ionity-global.github.io/ASSETS-IONITY-2026-/assets.json
- **AI discovery guide:** https://ionity-global.github.io/ASSETS-IONITY-2026-/llms.txt
- **Documentation (indexable):** https://ionity-global.github.io/ASSETS-IONITY-2026-/wiki/Home.html
- **Documentation (GitHub Wiki):** https://github.com/Ionity-Global/ASSETS-IONITY-2026-/wiki
- **Public mirror:** https://github.com/AntwerpDesignsIonity/ASSETS-IONITY-2026-

| Doc | |
|---|---|
| [Asset Catalog](wiki/Asset-Catalog.md) | Folder map, categories, formats, URL patterns, `assets.json` contract |
| [Brand and Licensing](wiki/Brand-and-Licensing.md) | Colours, logo rules, Policy 986 AED, License AED 900 / AED 990, Apache / MIT / CC sections |
| [IoT](wiki/IoT.md) | The related Ionity edge AI / AIoT / industrial IoT ecosystem |
| [SEO and Indexing](wiki/SEO-and-Indexing.md) | Keywords, metadata, structured data, sitemap / robots / llms.txt |
| [Official Links](wiki/Official-Links.md) | Verified identity and link registry |

The Pages interface is a searchable index, not a corporate website. It provides previews, direct downloads, raw URLs, repository links, categories, formats and file sizes for the public assets in this repository.

## Using an asset

1. Search the [asset directory](https://ionity-global.github.io/ASSETS-IONITY-2026-/) by filename, path, format or category.
2. Select **Copy raw URL** for use in code and integrations, or **Download** for a local copy. Raw pattern: `https://raw.githubusercontent.com/Ionity-Global/ASSETS-IONITY-2026-/main/<path>`
3. Review [Brand and Licensing](wiki/Brand-and-Licensing.md), [LICENSE](LICENSE) and `License-Ionity Global.txt` before publishing or redistributing an asset.

Files above GitHub's 100 MB limit are stored with Git LFS (`git lfs install` before cloning if you need them).

## Updating the catalog

After adding, moving or removing files, regenerate the index and commit `assets.json` with the asset changes:

```console
node scripts/generate-catalog.mjs
```

## AI and agent access

Agents should retrieve `assets.json` and filter its `assets` array. Each record contains `name`, `path`, `category`, `format`, `bytes`, `raw_url` and `github_url`; the contract is described by [assets.schema.json](assets.schema.json). Start from [`llms.txt`](llms.txt).

## Identity

Johan Wilhelm van Antwerp · Founder, Technical Lead & Architect — Ionity (Pty) Ltd · ORCID [0009-0005-7181-0347](https://orcid.org/0009-0005-7181-0347) · Centurion, Gauteng, South Africa · info@ionity.today · +27 646 999 877

**Ionity** here refers exclusively to www.ionity.today and www.ionity.world. Ionity (Pty) Ltd is not affiliated with the European EV charging company operating at ionity.com.

---
*(c) 2018-2026 Antwerp Designs | Ionity (Pty) Ltd — All Rights Reserved — TM2 · Policy 986 AED · License AED 900 · CC BY-NC-SA 4.0 where stated · Building Tomorrow, Today.*
