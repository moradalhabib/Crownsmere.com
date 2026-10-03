# Crownsmere.com

Website of **Crownsmere Estate**, the independent prime London property consultancy of Alaa Qadir. Plain HTML, CSS and JavaScript with no build step, hosted on GitHub Pages at crownsmere.com.

## Structure
- `index.html`: home page (monogram intro, hero, approach, services, the selling journey, why Crownsmere, enquiry)
- `services.html`: buy, sell, let, invest and advisory; how we market your property; the selling journey
- `about.html`: why Crownsmere, Alaa Qadir, what you can expect
- `contact.html`: request-a-call-back form
- `assets/style.css`, `assets/main.js`
- `assets/img/`: monogram (transparent gold), photography and skyline taken from the brand materials, favicons
- `mail-filter/`: AI filter for the hello@ inbox, run on cPanel (see `mail-filter/README.md`; excluded from the website by `_config.yml`)

## Preview locally
`python3 -m http.server 8000`, then open http://localhost:8000

The monogram intro plays once per browser session. Open a new tab or window to see it again.

## Contact requests
`contact.html` collects enquiry type (buy, sell, let, invest, advice), name, email, telephone, preferred contact method, best time, timeframe, area, budget or value, a message and consent.

- Submissions are posted with JavaScript to [FormSubmit](https://formsubmit.co) (`data-endpoint` on the `<form>`), which emails them to **hello@crownsmere.com**.
- Every email has the subject `[Crownsmere Enquiry] Website request to be contacted` and a `source: crownsmere.com/contact` field, so the inbox filter recognises website enquiries.
- Spam protection: a hidden honeypot field (`_honey`) and validation (the telephone number must contain 7 to 15 digits).
- **One-time activation:** the first real submission triggers an activation email from FormSubmit to hello@crownsmere.com. Click its link, or no enquiries will be delivered. The inbox filter always forwards FormSubmit notices to Alaa.

## Images
The photographs were cut from the flyers, so they are fairly low resolution (about 1000px wide). Replacing them with the original high-resolution files, keeping the same names in `assets/img/`, will sharpen the site on large screens.
