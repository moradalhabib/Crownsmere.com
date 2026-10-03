# Crownsmere.com

The website of Crownsmere, a private house. Plain HTML, CSS and JavaScript with no build step, hosted on GitHub Pages at crownsmere.com.

## Structure
- `index.html`: home page (wax-seal intro, crest, the House, the Disciplines, horizontal Archive, motto, invitation)
- `about.html`: The House (story, Rules of the House, Chronicle)
- `services.html`: The Disciplines (ledger and manner of engagement)
- `portfolio.html`: The Archive (gallery of plates)
- `contact.html`: Correspondence (letter form with wax-seal submit)
- `assets/style.css`, `assets/main.js`, `assets/favicon.svg`

## Preview locally
`python3 -m http.server 8000`, then open http://localhost:8000

The wax-seal intro plays once per browser session. Open a new tab or window to see it again.

## Making it yours
- **Images:** the "plates" in the Archive are styled placeholders. Replace a plate's `<div class="plate …">` with an `<img>`, or set a `background-image` on it.
- **Copy:** all text is placeholder brand voice. Edit it directly in the HTML.
- **Contact form:** create a free form endpoint (for example at formspree.io), then put its URL in `data-endpoint=""` on the `<form>` in `contact.html`. Until then, the form politely tells visitors that the correspondence desk is not yet open.
