# Crownsmere.com

Website of **Crownsmere Estate**, a private, by-request property service in prime London (Alaa Qadir, Senior Property Consultant): clients share a brief and Crownsmere finds the right property, on and off the market. There are deliberately no conventional property listings. Plain HTML, CSS and JavaScript, hosted on GitHub Pages at crownsmere.com.

## Structure
- `tools/build.py`: **the source of every page**, including both student pages. Edit the content there and run `python3 tools/build.py` (excluded from the website). The `rebuild-ux` workflow also regenerates the pages on every push to `main`.
- **Business details to fill in** (top of `tools/build.py`): `BUSINESS` (company and regulatory details), `FEES` (published letting fees), `TESTIMONIALS` (real client comments), `PORTRAIT` (Alaa's photograph) and `TRACK_RECORD` (verified figures). Each shows on the site only once filled in. See `docs/research-2026-10.md` for why they matter.
- `index.html`: a short front door: photo hero, six tiles (Buy, Sell, Rent, Invest, Students, Meet Alaa) and a closing call to action
- `services.html`: a tile for each service, how it works, where Alaa searches and a student lettings callout. Old links to its sections (`services.html#let` and so on) land on the matching tile.
- `buy.html`, `sell.html`, `rent.html`, `invest.html`, `advisory.html`: one short page per service (from `SERVICES` in `tools/build.py`), each with a breadcrumb back to Services and a link to the next service
- `about.html`: Alaa Qadir's profile ("About Alaa"): why Crownsmere, her one-to-one service, network, direct negotiation for buyers and tenants, client care, who she works with, and her track record and client comments once supplied
- `students.html` (English) and `students-ar.html` (Arabic), with `assets/student.css` and `assets/student.js`: international-student rental and guarantor-assistance enquiry, written up as an organised email to Alaa Qadir with hello@crownsmere.com copied. This is an initial enquiry, not a paid guarantor application. Each language has its own address, linked with `hreflang`; old `students.html?lang=ar` links redirect to the Arabic page.
- `contact.html`: the three-step brief form, with what happens next, the direct email address and all the questions and answers
- `privacy.html`: UK GDPR privacy notice (linked from the footer and the forms)
- `404.html`: "This page has gone off-market" (GitHub Pages serves it for any missing address)
- `sitemap.xml`, `robots.txt`, `site.webmanifest`: search engine and home-screen metadata (generated)
- `assets/style.css`: the whole design system; `assets/main.js`: header, keyboard focus, gentle reveal and the brief form
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
| About (now Alaa's profile) | 6,273px | 4,838px |
| Students | 3,750px | 2,616px |
| Contact | 3,190px | 2,316px |

**Navigation update (October 2026).** A client asked for "a navigating site as opposed to a page". Phones and tablets now have a tab bar along the bottom (Home, Services, About, Students, Contact), always on screen, replacing the hidden menu and the quick-contact bar. The home page became a short front door (2,314px on the same phone) with a tile for each part of the site, and each service has its own page. How it works and the neighbourhoods moved to Services, Why Crownsmere to About, and the questions to Contact.

- **One clear action everywhere:** "Share your brief" in the hero, the header on computers, the closing section of every page, and the Contact tab on phones.
- **Navigation you can see:** on phones and tablets a tab bar along the bottom, with the current page marked (Services stays marked on each service page); it steps aside while a form field is being filled in. Computers keep the navigation in the header.
- **Mobile first:** tiles in two columns on phones and three on computers; forms beside their explanation on desktop and straight after the introduction on phones.
- **Type:** Cormorant Garamond for headings, Inter for reading and buttons (much easier to read at small sizes than letter-spaced capitals), Cinzel only for the CROWNSMERE wordmark.
- **Colour tokens** are at the top of `assets/style.css`, with the contrast ratio of each text colour on the page and section backgrounds. Text over the hero photograph is at least 4.5:1 at every screen width.
- **Removed:** the 3D crest, smooth-scroll library, custom cursor, pinned horizontal scroll, flip cards, interactive map and neighbourhood matcher. They added weight and scrolling without helping visitors decide. The map also sent visitors' IP addresses to OpenStreetMap; the site now makes no third-party requests at all.
- **Motion:** a short fade-in as sections appear, and pages cross-fade into each other in browsers that support it (Chrome, Edge, Safari 18.2+). Both are switched off for visitors who prefer reduced motion. Content is fully visible without JavaScript.
- **Speed:** AVIF photographs, and Chrome and Edge fetch a same-site page in the background as soon as a visitor hovers or starts to tap a link (Speculation Rules).
- **Enquiries on computers:** if no mail app opens, the "your email is ready" panel also offers Gmail and Outlook on the web, as well as copying the enquiry.
- **Keyboard focus** is never hidden behind the sticky header or the tab bar (WCAG 2.2, 2.4.11).

## Search engines (SEO)
What is in place, all generated by `tools/build.py`:
- **Every page:** its own title (60 characters or fewer, so it is not cut off in results) and description (100 to 160), a canonical address, `hreflang` between the English and Arabic student pages, and the right page language (`<html lang="ar">` on the Arabic page). The home page is linked as `./`, its canonical address, never as `index.html`.
- **Structured data (JSON-LD), connected on every page:** the business (`RealEstateAgent`, with its five services, languages and service areas), the website (`WebSite`, with "Crownsmere" as a shorter alternate name for Google's site name), the page itself (`WebPage`, `CollectionPage`, `ProfilePage` or `ContactPage`) and its breadcrumb trail. Service pages add a `Service` and their questions (`FAQPage`); Contact carries every question. Nothing is invented: no reviews, ratings, prices or address.
- **Internal links:** the footer links every service and the Arabic student page from every page; the home page names the neighbourhoods Alaa covers.
- **Files:** `sitemap.xml` (accurate `lastmod`, set by `SITE_UPDATED_ISO`; the privacy notice keeps its own date), `robots.txt`, a 96px and 192px favicon (Google wants a multiple of 48px) and `/favicon.ico`.
- **IndexNow:** after each deploy to main, the `site-check` workflow tells Bing and other IndexNow engines (Bing also feeds ChatGPT search and Copilot) which pages exist, using the public key in `INDEXNOW_KEY` and its file `<key>.txt`. Google reads the sitemap instead.
- **Speed:** `main.js` is deferred, so it never holds up the first paint. Lighthouse scores 100 for SEO, accessibility and best practices on every page.

What only the owner can do, in order of impact:
1. **Google Search Console** and **Bing Webmaster Tools:** verify the site (paste each one's meta tag value into `VERIFY` in `tools/build.py`, or use a DNS record), then submit `https://crownsmere.com/sitemap.xml`.
2. **Google Business Profile** as a service-area business (address hidden, service area London). For local and AI search it is the most-cited source about a business. Keep the name, email and website exactly as on the site.
3. The same consistent listing on **Bing Places** and **Apple Business Connect**, then in professional directories once memberships are confirmed (for example The Property Ombudsman's member search or Propertymark).
4. **Real client reviews** on the Business Profile, and permitted quotes in `TESTIMONIALS`.
5. **Alaa's photograph** (`PORTRAIT`) and verified figures (`TRACK_RECORD`) on her profile, which strengthen the experience and expertise search engines look for.

## Preview locally
`python3 -m http.server 8000`, then open http://localhost:8000

The site sets no cookies and loads nothing from third parties. Website enquiry forms open the visitor's email application; the visitor must press Send and no website form data is sent automatically.

## Tests
`npm install --no-save @playwright/test@1.56.1`, then `npx playwright test --config=playwright.config.cjs`. The suite (`tests/e2e/`) checks every page at seven screen sizes for sideways scrolling, console errors and the navigation (the tab bar on phones and tablets, the header on computers); **a maximum page length on a phone for each page**; the tab bar marking the current page and opening each page, in English and Arabic; the service pages, their breadcrumbs and the old section links; that no third-party requests are made; focus never hidden behind the fixed bars; labelled fields and 44px touch targets; the no-JavaScript fallbacks; AVIF photographs; the prefetch rules matching the security policy's hash; the Arabic page's own address, `hreflang` links and old-link redirect; and the full contact and student email drafts (mail app, Gmail and Outlook) in English and Arabic. Browser tests never send email. Screenshots are saved to `test-screenshots/`.

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
