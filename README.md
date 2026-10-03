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
- **Contact form:** see below.

## Contact requests
`contact.html` has a "request to be contacted" form: name, organisation, email, telephone, preferred contact method, best time, introducer, area of interest, message and consent.

- Submissions are posted with JavaScript to [FormSubmit](https://formsubmit.co) (`data-endpoint` on the `<form>`), which emails them to **hello@crownsmere.com**.
- Every email has the subject `[Crownsmere Enquiry] Request to be contacted`, a `source: crownsmere.com/contact` field and the same field layout, so an inbox filter can recognise genuine website enquiries.
- Spam protection: a hidden honeypot field (`_honey`) and client-side validation (the telephone number must contain 7 to 15 digits).
- **One-time activation:** the first real submission triggers an activation email from FormSubmit to hello@crownsmere.com. Click its link, or no enquiries will be delivered. Make sure the AI filter does not discard that email.
- The internal address that filtered mail is forwarded to is deliberately not published anywhere on the site.
- To use a different service (Formspree, a serverless function and so on), change `data-endpoint`. The script posts JSON and expects a 2xx response.
