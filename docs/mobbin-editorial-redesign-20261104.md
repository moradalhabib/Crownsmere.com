# Crownsmere Editorial Edition — Mobbin-informed redesign
**Date:** 4 November 2026
**Scope:** entire responsive website; no publication of unapproved inventory

## Design direction
Crownsmere is a one-to-one London property introduction consultancy, not an inventory-heavy portal. The new site has a quieter, image-led editorial design informed by premium hospitality and property discovery UI patterns, using Crownsmere's own photography and established identity: the existing logo/monogram, warm stone, deep navy and muted gold; Cormorant Garamond, Inter and Cinzel (all already self-hosted).

**The new default:** every user must quickly see the relevant action: browse available property, understand Crownsmere's introduction model, or speak personally with Alaa. Avoid fake listing cards or inflated track records; retain transparency about indicative photography and the role of partner agents.

## Mobbin references used in research
Patterns were researched for the redesign. These are references for information hierarchy and interactions, NOT image, layout, branding or copy sources.

- [KOBU website hero](https://mobbin.com/sites/sections/d07ad815-77af-4cab-a6ff-c35761c7b2a6): imagery, spatial rhythm and hospitality-like restraint applied to the homepage cover.
- [KOBU editorial collection](https://mobbin.com/sites/sections/4226456d-e845-483a-ad1b-305a93fe7d36): curated photographic selection, applied to two clear discovery paths.
- [Zillow search results](https://mobbin.com/screens/c429086a-9480-4e1f-b845-e5427aed9ba3): scannable price, purpose and filtering; actual listing filters remain only when inventory exists.
- [Zillow detail](https://mobbin.com/screens/d5f8bb0a-fa13-4584-8ab1-b690aea56262): primary photo, property facts and visible enquiry form.
- [Instrument service section](https://mobbin.com/sites/sections/d0850530-6f9d-4590-83bc-baa018680be2): editorial service hierarchy and whitespace.
- [Framer contact](https://mobbin.com/sites/sections/914df681-c24d-4800-bd11-9c144d0175fb): a clear introductory heading alongside a structured enquiry.
- [Fiasco footer](https://mobbin.com/sites/sections/af0c1930-9ed3-4ed4-9af0-dfbc96b3a625): confident typography and link hierarchy.

## Implementation
- \`assets/editorial.css\` loaded AFTER base/student/property styles so design tokens and page-specific overrides work consistently.
- New homepage hierarchy: large architectural cover → buying/renting photographic discovery → personal role of Alaa → six services → private enquiry.
- Inner-page cover treatment: shared editorial split with distinctive original architectural images by service.
- About Alaa: human-focused narrative, no fabricated portrait; original doorway photograph remains illustrative.
- Contact and international student journeys: premium two-column layouts without changing existing three-step validation, bilingual layout, direct mail drafting, privacy text, or consent.
- Properties: photographic empty state (NOT a fake listing), with filters removed until approved public properties exist. Published listings keep real photos, location, price, property details and Alaa-first enquiry.
- Footer and CTA: strong navy closing section, high-contrast links and clear first contact.
- Motion remains subtle, keyboard focus remains visible, reduced-motion respected, no third-party requests/cookies/trackers.
- Private legal details and owner documents must never be committed to this public repository.

## QA and release gates
1. Regenerate all HTML from \`tools/build.py\`; never edit generated files as the source of truth.
2. Run \`tools/test_properties.py\` and \`html-validate *.html\`.
3. Execute full Playwright sitewide suite across Chromium, WebKit and Firefox at seven viewports.
4. Run the isolated synthetic property listing fixture across all three browsers, checking filters, real image loads, privacy, consent, and lead email draft to Alaa.
5. Visually review mobile/desktop screenshot output; check sideways overflow, readability, navigation, one h1, unique meta, CSP, alternative text and non-invented claims.
6. Merge only after QA passes; GitHub Pages deploys from main. Follow with live site-check including private data exclusion.
7. Property inventory stays empty until verified particulars, written marketing authority and clearance for each proposed public listing.
