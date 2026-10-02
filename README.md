# Crownsmere.com

Static website (plain HTML/CSS/JS, no build step).

## Structure
- `index.html`, `about.html`, `services.html`, `portfolio.html`, `contact.html`
- `assets/style.css`, `assets/main.js`

## Preview locally
`python3 -m http.server 8000`, then open http://localhost:8000

## Deploying (domain bought on Namecheap)
- Namecheap shared hosting: upload these files to `public_html` via cPanel File Manager or FTP.
- Or use free hosting (GitHub Pages, Netlify, Cloudflare Pages) and point the Namecheap DNS records at it.

## TODO
- Replace placeholder text and add a logo and images.
- Hook the contact form to a form service (Formspree, Netlify Forms) or a backend.
