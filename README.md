# Crownsmere.com

Website of **Crownsmere Estate**, a private, by-request property service in prime London (Alaa Qadir, Senior Property Consultant): clients share a brief and Crownsmere finds the right property, on and off the market. There are deliberately no property listings. Plain HTML, CSS and JavaScript with no build step, hosted on GitHub Pages at crownsmere.com.

## Structure
- `index.html`: home page (monogram intro, hero, approach, services, how it works, where I search, why Crownsmere, questions, share your brief)
- `services.html`: buy, sell privately, let, invest and advisory (with a sticky section menu); how it works
- `about.html`: why Crownsmere, Alaa Qadir, what you can expect
- `contact.html`: three-step "Share your brief" form and common questions
- `privacy.html`: UK GDPR privacy notice (linked from the footer and the form)
- `404.html`: "This page has gone off-market" (GitHub Pages serves it for any missing address)
- `sitemap.xml`, `robots.txt`, `site.webmanifest`: search engine and home-screen metadata
- `assets/style.css`, `assets/main.js`
- `assets/fonts/`: Cinzel, Cormorant Garamond and EB Garamond, self-hosted so no visitor data goes to Google
- `assets/img/`: monogram (transparent gold), photography and skyline taken from the brand materials (WebP with JPEG fallbacks), icons
- `tools/build.py`: generates all the HTML pages. Edit the content there and run `python3 tools/build.py` (excluded from the website)
- `mail-filter/`: AI filter for the hello@ inbox, run on cPanel (see `mail-filter/README.md`; excluded from the website by `_config.yml`)

## Preview locally
`python3 -m http.server 8000`, then open http://localhost:8000

The monogram intro plays once per browser session. Open a new tab or window to see it again.

The site sets no cookies. The only outside requests are the OpenStreetMap map tiles on the home page (loaded only when the map scrolls into view) and FormSubmit when a brief is sent.

## Security
- Served over HTTPS only. In the repository's **Settings, Pages**, keep **Enforce HTTPS** ticked; GitHub then redirects all http:// traffic and adds an HSTS header.
- Every page carries a strict Content Security Policy: scripts, styles and fonts may only come from this site; images also from OpenStreetMap's tile server; form data only to FormSubmit. There is no inline script or style anywhere.
- Leaflet (the map library) is hosted on the site itself (`assets/vendor/leaflet`, BSD licence) rather than loaded from a CDN.
- `/.well-known/security.txt` tells researchers how to report a problem.
- `mail-filter/`, `tools/` and this README are excluded from the published site.
- `.github/workflows/site-check.yml` checks the live site after every deploy and weekly: certificate validity and expiry, HTTP to HTTPS redirects, security headers, every page, and that private folders are not published.

## Map
The Where I Search map uses [Leaflet](https://leafletjs.com) with [OpenStreetMap](https://www.openstreetmap.org) tiles (attribution shown on the map, as the licence requires). Neighbourhood coordinates live in `tools/build.py` (`AREA_COORDS`).

## Contact requests
No telephone number is published on the site: Alaa shares it personally once a brief is received. Visitors reach Crownsmere through the brief form or hello@crownsmere.com.

`contact.html` guides visitors through three steps (request, brief, details). Without JavaScript it shows as one form. It collects the request (buy a home, rent a home, sell privately, let a property, invest, seek advice), the brief, preferred areas, budget or value, timeframe, name, email, telephone, preferred contact method, best time and consent.

- Submissions are posted with JavaScript to [FormSubmit](https://formsubmit.co) (`data-endpoint` on the `<form>`), which emails them to **hello@crownsmere.com**.
- Every email has the subject `[Crownsmere Enquiry] New client brief from the website` and a `source: crownsmere.com/contact` field, so the inbox filter recognises website enquiries.
- Spam protection: a hidden honeypot field (`_honey`) and validation (the telephone number must contain 7 to 15 digits).
- **One-time activation:** the first real submission triggers an activation email from FormSubmit to hello@crownsmere.com. Click its link, or no enquiries will be delivered. The inbox filter always forwards FormSubmit notices to Alaa.

## Images
Each photograph appears only once on the site. The photographs were cut from the flyers, so they are fairly low resolution (about 1000px wide). Replacing them with the original high-resolution files, keeping the same names in `assets/img/`, will sharpen the site on large screens.
