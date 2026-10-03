# Crownsmere.com

Website of **Crownsmere Estate**, a private, by-request property service in prime London (Alaa Qadir, Senior Property Consultant): clients share a brief and Crownsmere finds the right property, on and off the market. There are deliberately no property listings. Plain HTML, CSS and JavaScript with no build step, hosted on GitHub Pages at crownsmere.com.

## Structure
- `index.html`: home page: a real-time 3D gold crest inside an engraved, slowly turning seal, an arched-window photo reveal, the approach (words light up as you read), services, how it works, briefs I take on (cards that turn over), where I search (neighbourhood matcher and map), why Crownsmere, questions, share your brief
- `services.html`: buy, sell privately, let, invest and advisory (with a sticky section menu); how it works
- `about.html`: why Crownsmere, Alaa Qadir, what you can expect
- `contact.html`: the brief composer: a three-step form whose answers are composed, live, into a letter to Alaa on Crownsmere stationery, sealed when sent
- `privacy.html`: UK GDPR privacy notice (linked from the footer and the form)
- `404.html`: "This page has gone off-market" (GitHub Pages serves it for any missing address)
- `sitemap.xml`, `robots.txt`, `site.webmanifest`: search engine and home-screen metadata
- `assets/style.css`, `assets/main.js`
- `assets/fonts/`: Cinzel, Cormorant Garamond and EB Garamond, self-hosted so no visitor data goes to Google
- `assets/img/`: monogram (transparent gold), photography and skyline taken from the brand materials (WebP with JPEG fallbacks), icons
- `tools/crest/`: source of the 3D crest (`crest.js`, the traced logo outline in `crest-shape.json`). Rebuild with `cd tools/crest && npm install && npm run build`, which writes `assets/vendor/crest.min.js` and copies `lenis.min.js`
- `assets/vendor/`: self-hosted libraries (three.js inside the crest bundle, Lenis smooth scrolling, Leaflet), licences in `LICENSES.txt`
- `tools/build.py`: generates all the HTML pages. Edit the content there and run `python3 tools/build.py` (excluded from the website)
- `mail-filter/`: AI filter for the hello@ inbox, run on cPanel (see `mail-filter/README.md`; excluded from the website by `_config.yml`)

## Design
A light palette of cream, sand and champagne, with gold accents and navy lettering (no dark sections). The colour tokens are at the top of `assets/style.css`; the comments there note which text colours meet the contrast standard on which backgrounds.

Royal details (the "Royal edition" section at the end of `assets/style.css`):
- **Gold leaf:** the italic words in headings are lettered in gold leaf, with a light that passes across them once. The leaf tones are deep enough to stay readable on cream.
- **The seal:** an engraved ring (an SVG in the hero, `SEAL` in `tools/build.py`) around the 3D crest; the crest positions and tilts it.
- **Maison header:** on wider screens the crest and name sit in the centre with the links either side. On the home page the name appears once you scroll past the great crest.
- **Crown ornaments** (`orn()` in `tools/build.py`) between sections, **gallery mounts** with a gilt fillet around photographs, gilt edges and double rules, and gilded buttons.
- **Monogram canvas:** `assets/img/monogram-canvas.webp`, a tone-on-tone repeat of the crest, behind the quote band, the footer and the mobile menu.

## Preview locally
`python3 -m http.server 8000`, then open http://localhost:8000

The site sets no cookies. The only outside requests are the OpenStreetMap map tiles on the home page (loaded only when the map scrolls into view) and FormSubmit when a brief is sent.

## Security
- Served over HTTPS only. In the repository's **Settings, Pages**, keep **Enforce HTTPS** ticked; GitHub then redirects all http:// traffic and adds an HSTS header.
- Every page carries a strict Content Security Policy: scripts, styles and fonts may only come from this site; images also from OpenStreetMap's tile server; form data only to FormSubmit. There is no inline script or style anywhere.
- Leaflet (the map library) is hosted on the site itself (`assets/vendor/leaflet`, BSD licence) rather than loaded from a CDN.
- `/.well-known/security.txt` tells researchers how to report a problem.
- `mail-filter/`, `tools/` and this README are excluded from the published site.
- `.github/workflows/site-check.yml` checks the live site after every deploy and weekly: certificate validity and expiry, HTTP to HTTPS redirects, security headers, every page, and that private folders are not published.

## Interactive features
- **3D crest:** WebGL (three.js), loaded only on the home page and only if the device supports it and Data Saver is off. It tilts towards the pointer (or the phone's orientation), pauses when off screen, and falls back to the flat gold monogram. Reduced-motion visitors see a still render.
- **Smooth scrolling:** Lenis, desktop only, off for reduced motion.
- **Neighbourhood matcher:** the tags behind it are in `tools/build.py` (`TAGS`, `AREA_TAGS`).
- **Briefs I take on:** clearly labelled illustrative examples (`BRIEFS` in `tools/build.py`); replace them with real, anonymised briefs when available.
- **Brief composer:** the composed letter is also sent with the enquiry (field `letter`), so it reaches the inbox exactly as the client saw it.

## Map
The Where I Search map uses [Leaflet](https://leafletjs.com) with [OpenStreetMap](https://www.openstreetmap.org) tiles (attribution shown on the map, as the licence requires). Neighbourhood coordinates live in `tools/build.py` (`AREA_COORDS`).

## Contact requests
No telephone number is published on the site: Alaa shares it personally once a brief is received. Visitors reach Crownsmere through the brief form or hello@crownsmere.com. Alaa's own address is never shown on the site, and it must never be committed to this repository (it is public): it lives only in the mail filter's `config.php` on the server.

`contact.html` guides visitors through three steps (request, brief, details). Without JavaScript it shows as one form. It collects the request (buy a home, rent a home, sell privately, let a property, invest, seek advice), the brief, preferred areas, budget or value, timeframe, name, email, telephone, preferred contact method, best time and consent.

- Submissions are posted with JavaScript to [FormSubmit](https://formsubmit.co) (`data-endpoint` on the `<form>`), which emails them to **hello@crownsmere.com**.
- Every email has the subject `[Crownsmere Enquiry] New client brief from the website` and a `source: crownsmere.com/contact` field, so the inbox filter recognises website enquiries.
- Spam protection: a hidden honeypot field (`_honey`) and validation (the telephone number must contain 7 to 15 digits).
- **One-time activation:** the first real submission triggers an activation email from FormSubmit to hello@crownsmere.com. Click its link, or no enquiries will be delivered. The inbox filter always forwards FormSubmit notices to Alaa.

## Images
Each photograph appears only once on the site. The photographs were cut from the flyers, so they are fairly low resolution (about 1000px wide). Replacing them with the original high-resolution files, keeping the same names in `assets/img/`, will sharpen the site on large screens.
