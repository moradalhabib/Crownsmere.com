# Crownsmere Brand Charter — London Property

**Identity:** Crownsmere Estate. A private, commission-based London property introduction consultancy, with Alaa Qadir as the first point of contact and qualified appointed agents managing the relevant transactions.

## What the name should feel like

Crownsmere is dignified, rooted, composed and trustworthy. The visual identity suggests the character of Georgian London and a longstanding estate house: architectural symmetry, elegant serif typography, subtle stationery-like rules, considered photography and generous space. It should feel more like a prestigious private property house than a property search portal, a chain estate agency or a glossy hotel advertisement.

**Important:** The name is a brand, not evidence of a royal connection, royal warrant or historical estate heritage. The design must never claim or imply royal endorsement or a fictitious operating history.

## Brand foundations

- **Approved original brand mark:** use the existing Crownsmere monogram and wordmark. Do not redraw it as a crown, coat of arms, royal crest or new symbol.
- **Palette:** deep Oxford-style navy `#142438`, warm ivory `#f8f6f1`, parchment `#ebe6db`, restrained antique brass `#a98b5e`. Gold is an accent and never a glowing gradient.
- **Type:** the existing Cinzel wordmark for CROWNSMERE, Cormorant Garamond for large editorial headings, and accessible Inter for functional text. All fonts self-hosted.
- **Photography:** real architectural London heritage imagery, accurate authorised property photography on live listings. No generic AI homes, invented available listings or fake portraits of Alaa.
- **Composition:** composed margins, pale fine borders, an architectural framed hero, short editorial sections, clear property intent, compact content density and a distinctive, legible footer masthead.
- **Voice:** precise, personal and understated: "London property, with distinction", "The Crownsmere approach", "Considered addresses, discreet introductions". Avoid repeated generic "beautifully premium" claims, simulated exclusivity or false agent/royal credentials.

## Functional integrity

- Every property lead is prepared for Alaa Qadir first. The client must separately agree before sharing details with a partner agent.
- Clear sales and lettings roles. No suggestion that Crownsmere personally conducts conveyancing or tenancy administration.
- The existing property-publication gate stays active. Never commit private owner information or invented available properties to the public GitHub repository.
- Responsive design must work at 320px through desktop. Respect reduced motion, text contrast, keyboard focus visibility, native forms, and no third-party tracking.

## Mobbin reference links consulted

These are pattern references, not assets or instructions to copy another brand.

- [Kinfolk editorial section](https://mobbin.com/sites/sections/033cc912-2914-4fb4-84bb-281616e64147) — timeless editorial restraint and typography.
- [KOBU architectural hero](https://mobbin.com/sites/sections/d07ad815-77af-4cab-a6ff-c35761c7b2a6) — generous architectural imagery and composed hierarchy.
- [KOBU collection](https://mobbin.com/sites/sections/f5959421-5ded-4adb-98db-49143db77839) — photographic sequencing.
- [Pentagram contact section](https://mobbin.com/sites/sections/1046fdf6-61e6-4987-be32-89316b8e2515) — confident branding and minimal contact hierarchy.

## Technical touchpoints

`tools/build.py`: wordmark, sitewide footer, Crownsmere-specific home narrative.

`tools/property_pages.py`: Crownsmere Collection positioning and accurate Alaa-first process.

`assets/editorial.css`: heritage visual rules; all other CSS remains for compatibility.

`tests/e2e/ux.spec.cjs`: brand visibility and all existing responsive/accessibility and enquiry contracts.

For the full site redesign and release gates see `docs/mobbin-editorial-redesign-20261104.md`.