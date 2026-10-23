# Crownsmere.com

Website of **Crownsmere Estate**, a private, by-request property service in prime London (Alaa Qadir, Senior Property Consultant): clients share a brief and Crownsmere finds the right property, on and off the market. There are deliberately no conventional property listings. Plain HTML, CSS and JavaScript, hosted on GitHub Pages at crownsmere.com.

## Structure
- `tools/build.py`: **the source of every page**, including both student pages. Edit the content there and run `python3 tools/build.py` (excluded from the website). The `rebuild-ux` workflow also regenerates the pages on every push to `main`.
- **Business details to fill in** (top of `tools/build.py`): `BUSINESS` (company and regulatory details), `FEES` (published letting fees) and `TESTIMONIALS` (real client comments). Each shows on the site only once filled in. See `docs/research-2026-10.md` for why they matter.
- `index.html`: photo hero, three routes (find a home, sell or let, international students), how it works, why Crownsmere, neighbourhoods, questions and a closing call to action
- `services.html`: buy, sell, let, invest and advisory, a student lettings callout, and how it works
- `about.html`: Alaa's approach, the Crownsmere difference and what clients can expect
- `students.html` (English) and `students-ar.html` (Arabic), with `assets/student.css` and `assets/student.js`: international-student rental and guarantor-assistance enquiry, written up as an organised email to Alaa Qadir with hello@crownsmere.com copied. This is an initial enquiry, not a paid guarantor application. Each language has its own address, linked with `hreflang`; old `students.html?lang=ar` links redirect to the Arabic page.
- `contact.html`: the three-step brief form, with what happens next and the direct email address
- `privacy.html`: UK GDPR privacy notice (linked from the footer and the forms)
- `404.html`: "This page has gone off-market" (GitHub Pages serves it for any missing address)
- `sitemap.xml`, `robots.txt`, `site.webmanifest`: search engine and home-screen metadata (generated)
- `assets/style.css`: the whole design system; `assets/main.js`: header, mobile menu, gentle reveal and the brief form
- `assets/fonts/`: Inter (reading and controls), Cormorant Garamond (headings) and Cinzel (the wordmark), self-hosted so no visitor data goes to Google; licences in `assets/fonts/OFL.txt`
- `assets/img/`: monogram, photography and the skyline drawing (AVIF and WebP, with JPEG fallbacks). After replacing a photograph, regenerate its AVIF: `python3 -c "from PIL import Image; Image.open('assets/img/NAME.jpg').convert('RGB').save('assets/img/NAME.avif', 'AVIF', quality=60, speed=4)"`
- `docs/research-2026-10.md`: research notes (law, market, accessibility, speed) behind the October 2026 improvements, with sources; not published
- `mail-filter/`: AI filter for the hello@ inbox, run on cPanel (see `mail-filter/README.md`; excluded from the website by `_config.yml`)

## Design (October 2026 redesign)
Visitors found the old site far too long on phones: the home page was 16 screens on an iPhone. The redesign keeps the brand (warm cream, navy ink, gold accents, the monogram and serif headings) and makes every page short, calm and easy to act on:

| Page (390 × 844 phone) | Before | After |
| --- | --- | --- |
| Home | 13,523px (16 screens) | 4,946px (under 6) |
| Services | 7,337px | 4,573px |
| About | 6,273px | 3,799px |
| Students | 3,750px | 2,616px |
| Contact | 3,190px | 2,316px |

- **One clear action everywhere:** "Share your brief" in the hero, the header, the closing section and a slim quick-contact bar that slides up on phones once the visitor has scrolled past the opening view (not on the contact page).
- **Mobile first:** compact route cards with thumbnails on phones, image cards on desktop; forms beside their explanation on desktop and straight after the introduction on phones.
- **Type:** Cormorant Garamond for headings, Inter for reading and buttons (much easier to read at small sizes than letter-spaced capitals), Cinzel only for the CROWNSMERE wordmark.
- **Colour tokens** are at the top of `assets/style.css`, with the contrast ratio of each text colour on the page and section backgrounds. Text over the hero photograph is at least 4.5:1 at every screen width.
- **Removed:** the 3D crest, smooth-scroll library, custom cursor, pinned horizontal scroll, flip cards, interactive map and neighbourhood matcher. They added weight and scrolling without helping visitors decide. The map also sent visitors' IP addresses to OpenStreetMap; the site now makes no third-party requests at all.
- **Motion:** a short fade-in as sections appear, and pages cross-fade into each other in browsers that support it (Chrome, Edge, Safari 18.2+). Both are switched off for visitors who prefer reduced motion. Content is fully visible without JavaScript.
- **Speed:** AVIF photographs, and Chrome and Edge fetch a same-site page in the background as soon as a visitor hovers or starts to tap a link (Speculation Rules).
- **Enquiries on computers:** if no mail app opens, the "your email is ready" panel also offers Gmail and Outlook on the web, as well as copying the enquiry.
- **Keyboard focus** is never hidden behind the sticky header or the quick-contact bar (WCAG 2.2, 2.4.11).

## Preview locally
`python3 -m http.server 8000`, then open http://localhost:8000

The site sets no cookies and loads nothing from third parties. Website enquiry forms open the visitor's email application; the visitor must press Send and no website form data is sent automatically.

## Tests
`npm install --no-save @playwright/test@1.56.1`, then `npx playwright test --config=playwright.config.cjs`. The suite (`tests/e2e/`) checks every page at seven screen sizes for sideways scrolling, console errors and the mobile menu; **a maximum page length on a phone for each page**; that no third-party requests are made; keyboard focus in the menu and focus never hidden behind the fixed bars; labelled fields and 44px touch targets; the no-JavaScript fallbacks; AVIF photographs; the prefetch rules matching the security policy's hash; the Arabic page's own address, `hreflang` links and old-link redirect; and the full contact and student email drafts (mail app, Gmail and Outlook) in English and Arabic. Browser tests never send email. Screenshots are saved to `test-screenshots/`.

## Security
- Served over HTTPS only. In the repository's **Settings, Pages**, keep **Enforce HTTPS** ticked; GitHub then redirects all http:// traffic and adds an HSTS header.
- Every page carries a strict Content Security Policy: scripts, styles, fonts and images may only come from this site; no third-party form-posting endpoint. The only inline script is the Speculation Rules block (plain JSON), which the policy allows by its exact hash; `tools/build.py` computes the hash, so edit the rules there.
- `/.well-known/security.txt` tells researchers how to report a problem.
- `mail-filter/`, `tools/`, `tests/` and this README are excluded from the published site.
- `.github/workflows/site-check.yml` checks the live site after every deploy and weekly: certificate validity and expiry, HTTP to HTTPS redirects, security headers, every page, and that private folders are not published.

## Contact requests
No telephone number is published on the site. Alaa shares it personally once she has received a client's email. Visitors may use the guided forms to open prefilled emails, or email hello@crownsmere.com directly. The forms address alaa.qadir@crownsmere.com (copying hello@crownsmere.com); this address is public in the site's source. If it should be private, route mail exclusively to hello@ and configure internal forwarding.

`contact.html` guides visitors through three steps (request, brief, details). Without JavaScript it shows as one form. It collects the request (buy a home, rent a home, sell privately, let a property, invest, seek advice), the brief, preferred areas, budget or value, timeframe, name, email, telephone, preferred contact method, best time and consent.

- The form prepares an addressed email to **alaa.qadir@crownsmere.com**, copying **hello@crownsmere.com**. Nothing leaves the browser unless the visitor presses Send in their email app.
- If no mail app opens, the visitor can open the prepared email again or copy it.
- The forms use a hidden honeypot, required-field validation and telephone number checks.
- Confirm both mailboxes exist and can receive emails, and complete a manual send-and-receive test.

## Images
The photographs were cut from the flyers, so they are fairly low resolution (about 1000px wide). Replacing them with the original high-resolution files, keeping the same names in `assets/img/`, will sharpen the site on large screens, especially the full-width home hero (`townhouse`). Each photograph appears once. Images are illustrative and must not be presented as currently listed or available property; the home page says so under the route cards.
