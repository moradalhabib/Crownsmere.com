"""Generates the Crownsmere Estate website (static HTML).

All page content lives in this file, including the bilingual student page.
Edit it, then run:  python3 tools/build.py
(Images, styles and scripts live in assets/.)
"""
import base64
import hashlib
import json
import os
import re

OUT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SITE = "https://crownsmere.com"
BRAND = "Crownsmere Estate"
# No telephone number is published: Alaa shares it personally once a brief is received.
EMAIL = "hello@crownsmere.com"
# Enquiry forms prepare an email to Alaa, copied to EMAIL. The visitor sends it from their own mail app.
ALAA = "alaa.qadir@crownsmere.com"
UPDATED = "23 October 2026"
UPDATED_ISO = "2026-10-23"

# ---------------------------------------------------------------- business details (nothing shows until filled in)
# UK rules ask estate and letting agents to show some of these on their own website (company details,
# redress scheme, client money protection, published letting fees). Fill in only facts confirmed in
# writing (Companies House, the redress scheme, HMRC); anything left as None or empty is not shown.
BUSINESS = {
    "trading_name": BRAND,
    "principal": "Alaa Qadir, Senior Property Consultant",
    "contact": EMAIL,
    "legal_name": None,                 # e.g. "Crownsmere Estate Ltd", or the sole trader's name
    "company_number": None,             # Companies House number, for a limited company
    "registered_in": None,              # e.g. "England and Wales"
    "registered_office": None,          # registered office address
    "vat_number": None,
    "redress_scheme": None,             # e.g. "The Property Ombudsman"
    "redress_number": None,             # membership number
    "client_money_protection": None,    # CMP scheme, if client money is held (lettings)
    "aml_supervisor": None,             # e.g. "HM Revenue & Customs"
    "professional_bodies": [],          # e.g. ["Propertymark"]
}
# Letting agents in England must publish their fees (including VAT) on their own website.
# Each entry: (service, fee as clients should read it). Shown on the services page when filled in.
FEES = []
# Real client comments only, with their permission: (quote, attribution such as "Buyer, Kensington").
TESTIMONIALS = []
# Alaa's profile (about.html). PORTRAIT is the file name of a professional photograph in assets/img
# (e.g. "alaa-qadir" for alaa-qadir.jpg, with .webp/.avif versions), shown instead of the townhouse door.
PORTRAIT = None
# Verified figures only, e.g. ("12 years", "in prime London property"). Shown as a track record when filled in.
TRACK_RECORD = []

# ---------------------------------------------------------------- icons (24px line icons)
P = {
    "house": '<path d="M3 11 12 3l9 8M5.5 9.5V21h13V9.5M10 21v-6h4v6"/>',
    "key": '<circle cx="8" cy="15" r="4"/><path d="M11 12 20 3M16.5 6.5 19 9M14.5 8.5 16.5 10.5"/>',
    "people": '<circle cx="9" cy="8" r="3"/><path d="M3 20a6 6 0 0 1 12 0"/><circle cx="17" cy="9" r="2.5"/><path d="M15.6 14.3A5.5 5.5 0 0 1 21 20"/>',
    "person": '<circle cx="12" cy="8" r="4"/><path d="M4 21a8 8 0 0 1 16 0"/>',
    "pin": '<path d="M12 21s-7-6.2-7-11a7 7 0 0 1 14 0c0 4.8-7 11-7 11z"/><circle cx="12" cy="10" r="2.5"/>',
    "lock": '<rect x="5" y="11" width="14" height="10" rx="1"/><path d="M8 11V7a4 4 0 0 1 8 0v4M12 15v2"/>',
    "scales": '<path d="M12 3v18M7 21h10M4 7h16M4 7l-2.5 6h5zM20 7l-2.5 6h5z"/>',
    "speech": '<path d="M4 5h16v11H9l-5 4z"/>',
    "shield": '<path d="M12 3l8 3v6c0 5-3.5 8-8 9-4.5-1-8-4-8-9V6z"/><path d="M8.5 12l2.5 2.5 4.5-5"/>',
    "heart": '<path d="M12 20s-8-5-8-11a4.5 4.5 0 0 1 8-2.8A4.5 4.5 0 0 1 20 9c0 6-8 11-8 11z"/>',
    "document": '<path d="M6 3h9l4 4v14H6zM15 3v4h4M9 12h7M9 16h5"/>',
    "search": '<circle cx="11" cy="11" r="6.5"/><path d="M20 20l-4.4-4.4"/>',
    "mail": '<rect x="3" y="5" width="18" height="14" rx="1"/><path d="M3 6l9 7 9-7"/>',
    "check": '<path d="M5 12.5l4.5 4.5L19 7.5"/>',
    "arrow": '<path d="M4 12h15M13 6l6 6-6 6"/>',
    "chevron": '<path d="M9 5l7 7-7 7"/>',
    "plus": '<path d="M12 5v14M5 12h14"/>',
}

def ic(name, cls="ic"):
    return f'<svg class="{cls}" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.5" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true" focusable="false">{P[name]}</svg>'

ARROW = ic("arrow", "ic ic-arrow")

def sources(name):
    """AVIF (smallest) and WebP sources for a photograph, best first."""
    avif = os.path.exists(os.path.join(OUT, "assets", "img", name + ".avif"))
    return ((f'<source type="image/avif" srcset="assets/img/{name}.avif">' if avif else "")
            + f'<source type="image/webp" srcset="assets/img/{name}.webp">')

def pic(name, alt, w, h, cls="", lazy=True, ext="jpg", priority=False):
    """A <picture> with AVIF and WebP sources and a JPEG/PNG fallback."""
    attrs = f' class="{cls}"' if cls else ""
    load = (' fetchpriority="high"' if priority else "") if not lazy else ' loading="lazy" decoding="async"'
    return (f'<picture>{sources(name)}'
            f'<img{attrs} src="assets/img/{name}.{ext}" alt="{alt}" width="{w}" height="{h}"{load}></picture>')

LOGO = lambda lazy=False: pic("monogram-sm", "", 165, 259, lazy=lazy, ext="png")

def btn(href, text, kind="primary", arrow=True, extra=""):
    return f'<a class="btn btn-{kind}" href="{href}"{extra}>{text}{ARROW if arrow else ""}</a>'

# ---------------------------------------------------------------- chrome
NAV = [("index.html", "Home"), ("services.html", "Services"), ("about.html", "About Alaa"), ("students.html", "Students"), ("contact.html", "Contact")]

ORG = {
    "@context": "https://schema.org", "@type": "RealEstateAgent", "@id": f"{SITE}/#business",
    "name": BRAND,
    "description": "A private, by-request property search and consultancy service in prime London: clients share a brief and Alaa Qadir finds the right property, on and off the market.",
    "url": f"{SITE}/", "email": EMAIL,
    "image": f"{SITE}/assets/img/townhouse.jpg", "logo": f"{SITE}/assets/img/monogram.png",
    "areaServed": [{"@type": "City", "name": "London"}] + [{"@type": "Place", "name": n} for n in
                   ["Mayfair", "Belgravia", "Knightsbridge", "Chelsea", "Kensington", "Holland Park",
                    "Notting Hill", "Marylebone", "St John’s Wood", "Hampstead"]],
    "address": {"@type": "PostalAddress", "addressLocality": "London", "addressCountry": "GB"},
    "employee": {"@type": "Person", "name": "Alaa Qadir", "jobTitle": "Senior Property Consultant", "worksFor": {"@id": f"{SITE}/#business"}},
    "contactPoint": {"@type": "ContactPoint", "contactType": "customer service", "email": EMAIL,
                     "availableLanguage": ["English", "Arabic"]},
    "slogan": "A more personal London.",
    "knowsAbout": ["Prime London property", "Property search", "Off-market property", "Private property sales", "Lettings", "Property investment", "International student lettings"],
}

CRUMBS = {"services.html": "Services", "about.html": "About Alaa Qadir", "students.html": "Students", "students-ar.html": "الطلاب",
          "contact.html": "Contact", "privacy.html": "Privacy notice"}

# Pages in more than one language: each lists every version (hreflang), itself included.
ALTERNATES = {p: [("en-GB", "students.html"), ("ar", "students-ar.html"), ("x-default", "students.html")]
              for p in ("students.html", "students-ar.html")}

# Chromium browsers fetch a page in the background when a visitor is about to open it (on hover or
# press), so moving between pages feels instant. Same-site pages only. The CSP allows exactly this
# block by its hash, so no other inline script can run.
SPECULATION = '{"prefetch":[{"where":{"href_matches":"/*"},"eagerness":"moderate"}]}'
SPECULATION_HASH = "sha256-" + base64.b64encode(hashlib.sha256(SPECULATION.encode()).digest()).decode()

def head(title, desc, path, extra_ld=None, og_desc=None, og_locale="en_GB"):
    canonical = f"{SITE}/{'' if path == 'index.html' else path}"
    ld = [ORG] + (extra_ld or [])
    if path in CRUMBS:
        ld.append({"@context": "https://schema.org", "@type": "BreadcrumbList", "itemListElement": [
            {"@type": "ListItem", "position": 1, "name": "Home", "item": f"{SITE}/"},
            {"@type": "ListItem", "position": 2, "name": CRUMBS[path], "item": canonical}]})
    if path == "index.html":
        ld.append({"@context": "https://schema.org", "@type": "WebSite", "name": BRAND, "url": f"{SITE}/",
                   "inLanguage": "en-GB", "publisher": {"@id": f"{SITE}/#business"}})
    og_desc = og_desc or desc
    amp = lambda t: re.sub(r"&(?![a-zA-Z]+;|#[0-9]+;)", "&amp;", t)  # a bare "&" in text must be "&amp;"
    title, desc, og_desc = amp(title), amp(desc), amp(og_desc)
    slug = "home" if path == "index.html" else path.replace(".html", "")
    preload = ('<link rel="preload" href="assets/img/townhouse.avif" as="image" type="image/avif" fetchpriority="high">\n'
               if path == "index.html" else "")
    extra_css = '<link rel="stylesheet" href="assets/student.css">\n' if path.startswith("students") else ""
    alternates = "".join(f'<link rel="alternate" hreflang="{l}" href="{SITE}/{u}">\n' for l, u in ALTERNATES.get(path, []))
    return f'''<!DOCTYPE html>
<html lang="en-GB" class="no-js">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1, viewport-fit=cover">
<meta http-equiv="Content-Security-Policy" content="default-src 'self'; script-src 'self' '{SPECULATION_HASH}'; style-src 'self'; img-src 'self' data:; font-src 'self'; connect-src 'self'; form-action 'self' mailto:; manifest-src 'self'; base-uri 'self'; object-src 'none'; upgrade-insecure-requests">
<meta name="referrer" content="strict-origin-when-cross-origin">
<meta name="robots" content="index, follow, max-image-preview:large">
<meta name="format-detection" content="telephone=no">
<title>{title}</title>
<meta name="description" content="{desc}">
<meta name="theme-color" content="#faf7f1">
<meta name="color-scheme" content="light only">
<link rel="canonical" href="{canonical}">
{alternates}
<meta property="og:type" content="website">
<meta property="og:site_name" content="{BRAND}">
<meta property="og:locale" content="{og_locale}">
<meta property="og:url" content="{canonical}">
<meta property="og:title" content="{title}">
<meta property="og:description" content="{og_desc}">
<meta property="og:image" content="{SITE}/assets/img/og-image.jpg">
<meta property="og:image:width" content="1200">
<meta property="og:image:height" content="630">
<meta property="og:image:alt" content="Crownsmere Estate: private property search in prime London">
<meta name="twitter:title" content="{title}">
<meta name="twitter:description" content="{og_desc}">
<meta name="twitter:image" content="{SITE}/assets/img/og-image.jpg">
<meta name="twitter:card" content="summary_large_image">
<link rel="icon" href="assets/img/favicon.png" type="image/png">
<link rel="apple-touch-icon" href="assets/img/apple-touch-icon.png">
<link rel="manifest" href="site.webmanifest">
<link rel="preload" href="assets/fonts/inter-latin.woff2" as="font" type="font/woff2" crossorigin>
<link rel="preload" href="assets/fonts/cormorant-garamond.woff2" as="font" type="font/woff2" crossorigin>
{preload}<link rel="stylesheet" href="assets/style.css">
{extra_css}<script type="speculationrules">{SPECULATION}</script>
<script type="application/ld+json">{json.dumps(ld if len(ld) > 1 else ORG, ensure_ascii=False)}</script>
</head>
<body class="page-{slug}">
<a class="skip" href="#main">Skip to content</a>'''

def header(current):
    current = "students.html" if current == "students-ar.html" else current
    cur = lambda h: ' aria-current="page"' if h == current else ""
    links = "".join(f'<a href="{h}"{cur(h)}>{t}</a>' for h, t in NAV[1:])
    items = "\n".join(f'    <li><a href="{h}"{cur(h)}>{t}</a></li>' for h, t in NAV)
    return f'''
<header class="hd">
  <div class="wrap hd-in">
    <a class="hd-mark" href="index.html" aria-label="{BRAND}, home">
      {LOGO()}
      <span class="wm"><b>CROWNSMERE</b><small>Estate</small></span>
    </a>
    <nav class="hd-nav" aria-label="Main">{links}</nav>
    {btn("contact.html", "Start enquiry", "primary", arrow=False, extra=' data-cta')}
    <button class="hd-menu" type="button" aria-expanded="false" aria-controls="menu"><span>Menu</span><i aria-hidden="true"></i></button>
  </div>
</header>
<nav class="menu" id="menu" aria-label="Mobile">
  <ol>
{items}
  </ol>
  <div class="menu-foot">
    {btn("contact.html", "Share your brief", "primary")}
    <a class="menu-mail" href="mailto:{EMAIL}">{ic("mail")}{EMAIL}</a>
  </div>
</nav>'''

def registration():
    """The company and regulatory line in the footer, built only from details filled in above."""
    b = BUSINESS
    parts = []
    if b["trading_name"]:
        parts.append(f'Trading name: {b["trading_name"]}')
    if b["principal"]:
        parts.append(f'Principal: {b["principal"]}')
    if b["contact"]:
        parts.append(f'Contact: <a href="mailto:{b["contact"]}">{b["contact"]}</a>')
    if b["legal_name"]:
        parts.append(b["legal_name"])
    if b["company_number"]:
        parts.append(f'Registered in {b["registered_in"] or "England and Wales"}, company no. {b["company_number"]}')
    if b["registered_office"]:
        parts.append(f'Registered office: {b["registered_office"]}')
    if b["vat_number"]:
        parts.append(f'VAT no. {b["vat_number"]}')
    if b["redress_scheme"]:
        parts.append(f'Member of {b["redress_scheme"]}' + (f' (no. {b["redress_number"]})' if b["redress_number"] else ""))
    if b["client_money_protection"]:
        parts.append(f'Client money protection: {b["client_money_protection"]}')
    if b["aml_supervisor"]:
        parts.append(f'Anti-money laundering supervision: {b["aml_supervisor"]}')
    parts += b["professional_bodies"]
    return f'<p class="ft-reg">{" &middot; ".join(parts)}</p>' if parts else ""

def footer(current, quick_href="contact.html", quick_label="Share your brief", quick_lang=""):
    links = "".join(f'<li><a href="{h}">{t}</a></li>' for h, t in NAV[1:]) + '<li><a href="privacy.html">Privacy</a></li>'
    lang = f' lang="{quick_lang}"' + (' dir="rtl"' if quick_lang == "ar" else "") if quick_lang else ""
    bar = "" if current == "contact.html" else (
        f'\n<nav class="actionbar" aria-label="Quick contact">'
        f'<a class="actionbar-mail" href="mailto:{EMAIL}" aria-label="Email {EMAIL}">{ic("mail")}<span>Email</span></a>'
        f'<a class="btn btn-primary" href="{quick_href}"{lang}>{quick_label}{ARROW}</a></nav>')
    return f'''
<footer class="ft">
  <div class="ft-skyline" aria-hidden="true">{pic("skyline", "", 1055, 181)}</div>
  <div class="wrap ft-in">
    <div class="ft-brand">
      <a class="ft-mark" href="index.html" aria-label="{BRAND}, home">{LOGO(lazy=True)}<span class="wm"><b>CROWNSMERE</b><small>Estate</small></span></a>
      <p>A more personal London. Private property consultancy, by appointment.</p>
      <a class="ft-mail" href="mailto:{EMAIL}">{EMAIL}</a>
    </div>
    <nav class="ft-nav" aria-label="Footer"><ul>{links}</ul></nav>
    <p class="ft-legal">&copy; <span data-year>2026</span> {BRAND} &middot; London, United Kingdom</p>
    {registration()}
  </div>
</footer>{bar}
<script src="assets/main.js"></script>'''

def page(fname, title, desc, body, extra_ld=None, og_desc=None, scripts="", quick=("contact.html", "Share your brief"), og_locale="en_GB"):
    html = (head(title, desc, fname, extra_ld, og_desc, og_locale) + header(fname) + '\n<main id="main">\n' + body + '\n</main>'
            + footer(fname, *quick) + scripts + '\n</body>\n</html>\n')
    open(os.path.join(OUT, fname), "w").write(html)
    return html

# ---------------------------------------------------------------- shared content
SERVICES = [
    ("01", "Buy", "buy",
     "Tell me what you are looking for, and I will find it: on the market, off the market, or not yet on anyone&rsquo;s radar.",
     ["A private briefing on your requirements", "A personal search, on and off the market",
      "A curated shortlist, checked before you see it", "Accompanied viewings, negotiation and support to completion"]),
    ("02", "Sell", "sell",
     "A quiet, private sale. Your property is introduced only to qualified buyers, without the noise of a public listing.",
     ["A confidential conversation about your plans", "Valuation advice and pricing strategy",
      "Discreet introductions to qualified buyers, viewings by appointment", "No public listing unless you wish it"]),
    ("03", "Let", "let",
     "Whether you are looking for a home to rent or the right tenant for your property, the search is personal and discreet.",
     ["A search for the right rental home, to your brief", "Or the right tenant for your property",
      "Private, by-appointment viewings", "Negotiation of terms and clear communication throughout"]),
    ("04", "Invest", "invest",
     "Investment opportunities sourced to your criteria, including those that never reach the open market.",
     ["Opportunities sourced to your brief, including off-market", "Neighbourhood-level analysis of yield and growth",
      "Review of existing holdings", "A long-term strategy around your goals"]),
    ("05", "Advisory", "advisory",
     "Honest, experienced advice whenever you need a trusted perspective.",
     ["Candid second opinions", "Guidance on timing, pricing and positioning",
      "Advice on offers and options", "Support for complex or sensitive situations, in complete confidence"]),
]

STEPS = [
    ("Share your brief", "A private conversation about what you are looking for, why, and when. No detail is too small."),
    ("See a curated shortlist", "I search personally, on and off the market, and check every property before you see it."),
    ("View, negotiate, complete", "Accompanied viewings, calm negotiation and support through to completion, and long after."),
]

AREAS = ["Mayfair", "Belgravia", "Knightsbridge", "Chelsea", "Kensington", "Holland Park",
         "Notting Hill", "Marylebone", "St John&rsquo;s Wood", "Hampstead"]

FAQ = {
    "how": ("How does it work?",
            "You share your brief, by email or through the form on this site. We then have a private conversation about what you are looking for and why. From there, I search personally and bring you a shortlist of properties that genuinely fit."),
    "listings": ("Why are there no properties listed on this website?",
                 "Deliberately. Crownsmere works from your brief rather than from a list of properties to sell. Many of the homes I find are never publicly advertised, and those that are deserve to be judged against your brief, not a shop window."),
    "agent": ("Are you a buying agent?",
              "When you are buying, the service works in much the same way as a buying agent or property finder: I represent you, search on and off the market to your brief, and negotiate on your behalf. Crownsmere can also help you sell or let privately, invest, or simply give you a second opinion."),
    "areas": ("Which areas do you cover?",
              "Prime and Super Prime London, including Mayfair, Belgravia, Knightsbridge, Chelsea, Kensington and Notting Hill. If your brief takes us further afield, just ask."),
    "overseas": ("I live overseas. Can you still help?",
                 "Please get in touch. A search can begin by telephone or video call, with regular updates until you are able to visit in person."),
    "private": ("Is my enquiry confidential?",
                "Completely. Your brief and your details are used only to help you, and are shared with relevant partners only with your further agreement. See the <a href=\"privacy.html\">privacy notice</a> for details."),
    "fees": ("How are fees agreed?",
             "Every brief is different, so terms are discussed openly at the outset and agreed in writing before any work begins."),
}
if FEES:
    FAQ["fees"] = (FAQ["fees"][0], FAQ["fees"][1] + ' Our <a href="services.html#fees">published fees</a> are on the services page.')
HOME_FAQ = ["how", "listings", "agent", "areas", "overseas", "fees"]
CONTACT_FAQ = ["how", "private", "overseas", "fees"]

def strip_tags(s):
    return re.sub(r"<[^>]+>", "", s).replace("&ldquo;", "“").replace("&rdquo;", "”").replace("&rsquo;", "’")

def faq_ld(keys):
    return {"@context": "https://schema.org", "@type": "FAQPage",
            "mainEntity": [{"@type": "Question", "name": strip_tags(FAQ[k][0]),
                            "acceptedAnswer": {"@type": "Answer", "text": strip_tags(FAQ[k][1])}} for k in keys]}

# ---------------------------------------------------------------- building blocks
def sec_head(eyebrow, heading, lede="", hid=""):
    hid = f' id="{hid}"' if hid else ""
    lede = f'<p class="lede">{lede}</p>' if lede else ""
    return f'<div class="sec-head" data-reveal><p class="eyebrow">{eyebrow}</p><h2{hid}>{heading}</h2>{lede}</div>'

def page_hero(eyebrow, heading, lede=""):
    lede = f'<p class="lede">{lede}</p>' if lede else ""
    return f'''<section class="page-hero">
  <div class="wrap">
    <p class="eyebrow">{eyebrow}</p>
    <h1>{heading}</h1>
    {lede}
  </div>
</section>'''

def steps():
    items = "".join(f'<li><span class="step-n" aria-hidden="true">{i + 1}</span><div><h3>{t}</h3><p>{d}</p></div></li>'
                    for i, (t, d) in enumerate(STEPS))
    return f'<ol class="steps" data-reveal>{items}</ol>'

def faq(keys):
    rows = "".join(
        f'<details class="faq-item"><summary><span>{FAQ[k][0]}</span>{ic("plus", "ic faq-ic")}</summary><div class="faq-a"><p>{FAQ[k][1]}</p></div></details>'
        for k in keys)
    return f'<div class="faq" data-reveal>{rows}</div>'

def signature(role="Senior Property Consultant"):
    return f'<p class="sig"><b>Alaa Qadir</b><span>{role}</span></p>'

def testimonials():
    """Client comments, shown only once real ones have been added to TESTIMONIALS."""
    if not TESTIMONIALS:
        return ""
    items = "".join(f'<figure class="quote"><blockquote><p>{q}</p></blockquote><figcaption>{who}</figcaption></figure>' for q, who in TESTIMONIALS)
    return f'''
<section class="sec sec-alt" aria-labelledby="clients-title">
  <div class="wrap">
    {sec_head("In their words", "What clients <em>say.</em>", hid="clients-title")}
    <div class="quotes" data-reveal>{items}</div>
  </div>
</section>'''

def fees():
    """Published fees, shown only once they have been added to FEES."""
    if not FEES:
        return ""
    rows = "".join(f"<div><dt>{what}</dt><dd>{fee}</dd></div>" for what, fee in FEES)
    return f'''
<section class="sec sec-tight" id="fees" aria-labelledby="fees-title">
  <div class="wrap sec-split">
    {sec_head("Fees", "Clear fees, <em>agreed in writing.</em>", hid="fees-title")}
    <dl class="fee-list" data-reveal>{rows}</dl>
  </div>
</section>'''

def cta(heading="Tell me what <em>you are looking for.</em>"):
    return f'''
<section class="sec cta" aria-labelledby="cta-title">
  <div class="wrap" data-reveal>
    <p class="eyebrow">By request</p>
    <h2 id="cta-title">{heading}</h2>
    <p class="lede">Whether you are searching for a home, an investment, or a discreet buyer for your own property, every engagement begins with a private conversation.</p>
    <div class="btn-row">
      {btn("contact.html", "Share your brief")}
      {btn(f"mailto:{EMAIL}", f"Email {EMAIL}", "ghost", arrow=False)}
    </div>
  </div>
</section>'''

# ---------------------------------------------------------------- home
PATHS = [
    ("contact.html", "colonnade", "A white-stucco London street with columned porches", 563, 398,
     "Buy &middot; Rent &middot; Invest", "Find a London home", "A personal search, including homes that are never publicly listed."),
    ("services.html#sell", "interior", "An elegant London drawing room with tall windows", 826, 463,
     "Sell &middot; Let", "Sell or let, discreetly", "Quiet introductions to qualified buyers and tenants."),
    ("students.html", "westminster", "Big Ben and Westminster seen through tall French windows", 420, 480,
     "Students", "Studying in London?", "Rental help, even without a UK guarantor."),
]

paths = "".join(
    f'<a class="path" href="{h}">{pic(img, alt, w, hh)}<div class="path-body"><span class="path-tag">{tag}</span>'
    f'<h3>{t}</h3><p>{d}</p></div>{ic("chevron", "ic path-go")}</a>'
    for h, img, alt, w, hh, tag, t, d in PATHS)

facts = "".join(f'<li>{ic(i)}<div><h3>{t}</h3><p>{d}</p></div></li>' for i, t, d in [
    ("person", "One-to-one", "You deal directly with me. No call centre, no hand-offs."),
    ("lock", "Off-market access", "A discreet network opens doors to homes that never appear online."),
    ("shield", "Complete discretion", "Your search, your plans and your details stay private."),
])

index_body = f'''
<section class="hero" aria-labelledby="hero-title">
  <picture class="hero-media">{sources("townhouse")}<img src="assets/img/townhouse.jpg" alt="A white-stucco London townhouse with a black front door" width="1055" height="687" fetchpriority="high"></picture>
  <div class="wrap hero-in">
    <p class="eyebrow">Prime London property consultancy</p>
    <h1 id="hero-title">London property, <em>personally handled.</em></h1>
    <p class="hero-sub">Buying, selling, renting or moving to London? Work directly with Alaa Qadir for a discreet, personal search, on and off the market.</p>
    <div class="hero-actions">
      {btn("contact.html", "Share your brief", "light")}
      <a class="hero-link" href="students.html">International student? Get rental help{ARROW}</a>
    </div>
  </div>
</section>

<section class="sec" aria-labelledby="help-title">
  <div class="wrap">
    {sec_head("How can we help?", "Find your way <em>forward.</em>", hid="help-title")}
    <div class="paths" data-reveal>{paths}</div>
    <p class="fine">Photographs illustrate London homes and neighbourhoods, not available listings.</p>
  </div>
</section>

<section class="sec sec-alt" id="how" aria-labelledby="how-title">
  <div class="wrap">
    {sec_head("How it works", "From your brief <em>to the keys.</em>", hid="how-title")}
    {steps()}
  </div>
</section>

<section class="sec" id="why" aria-labelledby="why-title">
  <div class="wrap split">
    <div class="split-copy" data-reveal>
      <p class="eyebrow">Why Crownsmere</p>
      <h2 id="why-title">Not a typical <em>estate agency.</em></h2>
      <p>Rather than selling whatever happens to be on the books, I work from your brief and search personally for what is genuinely right for you. Each client is taken on individually, and you deal with me directly, from the first conversation to the day you collect the keys.</p>
      {signature()}
      <a class="more" href="about.html">Meet Alaa{ARROW}</a>
    </div>
    <ul class="facts" data-reveal>{facts}</ul>
  </div>
</section>
{testimonials()}

<section class="sec sec-alt" id="areas" aria-labelledby="areas-title">
  <div class="wrap sec-split">
    {sec_head("Where I search", "Prime London, <em>street by street.</em>", "Not sure which neighbourhood suits you? Helping you choose is part of the search.", "areas-title")}
    <ul class="tags" data-reveal>{"".join(f"<li>{a}</li>" for a in AREAS)}<li class="tags-more">and further afield</li></ul>
  </div>
</section>

<section class="sec" id="questions" aria-labelledby="faq-title">
  <div class="wrap sec-split">
    {sec_head("Questions", "Good questions, <em>plainly answered.</em>", hid="faq-title")}
    {faq(HOME_FAQ)}
  </div>
</section>
{cta()}'''

page("index.html", f"{BRAND} | Buy, Sell & Rent London Property",
     "Crownsmere Estate offers personal London property search, private sales, lettings and international student rental assistance. Speak to property consultant Alaa Qadir.",
     index_body, extra_ld=[faq_ld(HOME_FAQ)])

# ---------------------------------------------------------------- services
def svc(num, title, anchor, lede, points):
    lis = "".join(f"<li>{ic('check')}<span>{p}</span></li>" for p in points)
    return f'''<article class="svc" id="{anchor}" data-reveal>
      <div class="svc-head"><span class="svc-n">{num}</span><h2>{title}</h2><p>{lede}</p></div>
      <ul class="checks">{lis}</ul>
    </article>'''

jump = "".join(f'<a href="#{a}">{t}</a>' for n, t, a, d, p in SERVICES)

services_body = f'''
{page_hero("Services", "By request. <em>Personally found.</em>", "A clearer way to buy, sell, rent or invest in London. Choose the service you need, and Alaa will guide you personally.")}
<nav class="jump wrap" aria-label="Services on this page">{jump}</nav>

<section class="sec sec-tight">
  <div class="wrap svc-list">
    {"".join(svc(*s) for s in SERVICES)}
  </div>
</section>

<section class="sec sec-tight">
  <div class="wrap">
    <div class="callout" data-reveal>
      <div>
        <p class="eyebrow">International student lettings</p>
        <h2>Studying in London? <em>No UK guarantor?</em></h2>
        <p>We can help you explore London rental homes and professional guarantor options.</p>
      </div>
      {btn("students.html", "Student assistance")}
    </div>
  </div>
</section>

{fees()}
<section class="sec sec-alt" id="process" aria-labelledby="process-title">
  <div class="wrap">
    {sec_head("How it works", "From your brief <em>to the keys.</em>", "A private, unhurried process, shaped entirely around you.", "process-title")}
    {steps()}
  </div>
</section>
{cta("Shall we <em>begin?</em>")}'''

page("services.html", f"Property Search, Private Sales & Lettings | {BRAND}",
     "Buying, private sales, lettings, investment and property advice in prime London, delivered personally and discreetly by Crownsmere Estate.",
     services_body)

# ---------------------------------------------------------------- about: Alaa Qadir's profile
QUALITIES = [
    ("person", "A full one-to-one service", "You deal with Alaa directly, from the first conversation to the keys. No call centre, no hand-offs."),
    ("people", "Well connected", "A discreet network of owners, agents and advisers opens doors to homes that never appear online."),
    ("scales", "Direct negotiation, on your side", "Alaa negotiates with sellers, landlords and their agents for you: price or rent, terms and timing."),
    ("heart", "Client care", "Honest updates at every stage, viewings arranged around you, and support after you move in."),
    ("pin", "Prime London insight", "Street-by-street knowledge of Prime and Super Prime London, built over long-standing relationships."),
    ("shield", "Complete discretion", "Your plans and your details stay private, shared only with your agreement."),
]
TENANT_HELP = [
    "A search to your brief, on and off the market, including homes not yet advertised to rent",
    "Accompanied viewings, with an honest view on every property",
    "Direct negotiation of the rent, tenancy length, move-in date, furnishings and other terms",
    "Clear guidance on deposits, rent in advance and what to expect before you commit",
]
AUDIENCES = [
    ("services.html#buy", "Buyers", "A home or a pied-&agrave;-terre"),
    ("services.html#let", "Tenants", "The right rental, negotiated for you"),
    ("services.html#sell", "Owners selling", "A quiet, private sale"),
    ("services.html#let", "Landlords", "The right tenant, found discreetly"),
    ("services.html#invest", "Investors", "Opportunities sourced to your brief"),
    ("students.html", "International students", "Rentals and guarantor options"),
]

qualities = "".join(f'<div class="card" data-reveal>{ic(i)}<h3>{t}</h3><p>{d}</p></div>' for i, t, d in QUALITIES)
tenant_help = "".join(f"<li>{ic('check')}<span>{t}</span></li>" for t in TENANT_HELP)
audiences = "".join(f'<a class="who" href="{h}"><b>{t}</b><span>{d}</span>{ic("chevron", "ic who-go")}</a>' for h, t, d in AUDIENCES)
portrait = (pic(PORTRAIT, "Alaa Qadir, Senior Property Consultant at Crownsmere Estate", 800, 1000, lazy=False) if PORTRAIT
            else pic("door", "A black-lacquered London front door with brass fittings beside white columns", 433, 610, lazy=False))

def track_record():
    """Verified figures, shown only once they have been added to TRACK_RECORD."""
    if not TRACK_RECORD:
        return ""
    items = "".join(f"<div><dt>{label}</dt><dd>{figure}</dd></div>" for figure, label in TRACK_RECORD)
    return f'''
<section class="sec sec-tight" aria-labelledby="record-title">
  <div class="wrap">
    {sec_head("Track record", "Results, <em>quietly achieved.</em>", hid="record-title")}
    <dl class="stats" data-reveal>{items}</dl>
  </div>
</section>'''

about_body = f'''
<section class="profile-hero">
  <div class="wrap profile">
    <div class="profile-copy">
      <p class="eyebrow">Senior Property Consultant &middot; {BRAND}</p>
      <h1>Alaa <em>Qadir.</em></h1>
      <p class="lede">A one-to-one property consultant in prime London. Alaa finds, negotiates and secures homes for buyers and tenants, and represents owners who want a quiet, well-handled sale or let.</p>
      <ul class="tags tags-sm"><li>One-to-one service</li><li>Prime London</li><li>Buyers, tenants and owners</li><li>Enquiries in English and Arabic</li></ul>
      <div class="btn-row">
        {btn("contact.html", "Share your brief")}
        {btn(f"mailto:{EMAIL}", "Email Alaa", "ghost", arrow=False)}
      </div>
    </div>
    <figure class="profile-media">{portrait}</figure>
  </div>
</section>

<section class="sec sec-tight" aria-labelledby="story-title">
  <div class="wrap story-text" data-reveal>
    <h2 id="story-title" class="visually-hidden">In Alaa&rsquo;s words</h2>
    <p class="lead">As your dedicated consultant, I work for you and you alone. My clients come to me with a request, and my role is simple: to find what they are looking for, and to look after their interests at every step.</p>
    <p>Property is about people, not just buildings. I take on a small number of clients so that each one receives my full attention, honest advice and a search shaped entirely around them.</p>
    <p>You will never be passed between departments or shown a property simply because it needs selling. From the first conversation to the final signature, you deal directly with me, in complete confidence.</p>
    {signature(f"Senior Property Consultant &middot; {BRAND}")}
  </div>
</section>

<section class="sec sec-alt" aria-labelledby="working-title">
  <div class="wrap">
    {sec_head("Working with Alaa", "Personal, connected, <em>on your side.</em>", hid="working-title")}
    <div class="cards cards-3">{qualities}</div>
  </div>
</section>

<section class="sec" id="tenants" aria-labelledby="tenants-title">
  <div class="wrap split">
    <div class="split-copy" data-reveal>
      <p class="eyebrow">For tenants</p>
      <h2 id="tenants-title">Renting, with someone <em>on your side.</em></h2>
      <p>When you ask Alaa to find you a home to rent, she represents you: searching, viewing and negotiating directly with landlords and their agents on your behalf, so you secure the right home on the right terms.</p>
      <div class="btn-row">{btn("contact.html", "Share your rental brief")}</div>
    </div>
    <div data-reveal>
      <ul class="checks checks-lg">{tenant_help}</ul>
      <p class="fine">Studying in London? <a href="students.html">Rental help, including professional guarantor options</a>.</p>
    </div>
  </div>
</section>

<section class="sec sec-alt" aria-labelledby="who-title">
  <div class="wrap">
    {sec_head("Who Alaa works with", "One consultant, <em>every side of the move.</em>", hid="who-title")}
    <div class="whos" data-reveal>{audiences}</div>
  </div>
</section>
{track_record()}
{testimonials()}
{cta("Work with <em>Alaa.</em>")}'''

PROFILE_LD = {"@context": "https://schema.org", "@type": "ProfilePage", "url": f"{SITE}/about.html",
              "mainEntity": {"@type": "Person", "name": "Alaa Qadir", "jobTitle": "Senior Property Consultant",
                             "worksFor": {"@id": f"{SITE}/#business"}, "workLocation": {"@type": "City", "name": "London"},
                             "knowsAbout": ["Prime London property", "Property search", "Off-market property",
                                            "Negotiation for buyers and tenants", "Private sales", "Lettings"],
                             **({"image": f"{SITE}/assets/img/{PORTRAIT}.jpg"} if PORTRAIT else {})}}

page("about.html", f"Alaa Qadir, Senior Property Consultant | {BRAND}",
     "Meet Alaa Qadir: a one-to-one property consultant in prime London, well connected and negotiating directly for buyers and tenants, with discreet sales and lettings for owners.",
     about_body, extra_ld=[PROFILE_LD])

# ---------------------------------------------------------------- contact
def webmail(label, gmail, outlook):
    """Compose links for webmail users, filled in by the form scripts. Shown on computers only,
    where mailto: often opens nothing; phones open their own mail app reliably."""
    attrs = 'target="_blank" rel="noopener noreferrer"'
    return (f'<div class="webmail"><span>{label}</span>'
            f'<a class="btn btn-ghost" data-webmail="gmail" href="https://mail.google.com/mail/?view=cm&amp;fs=1" {attrs}>{gmail}</a>'
            f'<a class="btn btn-ghost" data-webmail="outlook" href="https://outlook.live.com/mail/0/deeplink/compose" {attrs}>{outlook}</a></div>')

def choice(name, val, checked=False, required=False):
    return f'<label class="choice"><input type="radio" name="{name}" value="{val}"{" checked" if checked else ""}{" required" if required else ""}><span>{val}</span></label>'

def options(vals):
    return "".join(f"<option>{v}</option>" for v in vals)

def step_actions(n, last=False):
    back = '<button type="button" class="btn btn-ghost" data-back>Back</button>' if n > 1 else '<span></span>'
    nxt = (f'<button class="btn btn-primary" type="submit">Continue to email{ARROW}</button>' if last
           else f'<button type="button" class="btn btn-primary" data-next>Continue{ARROW}</button>')
    return f'<div class="step-actions">{back}{nxt}</div>'

NEXT = [
    ("Answer three short steps", "What you need, a few details about your brief, and how to reach you."),
    ("Review and send the email", "Your email app opens with your brief written out for Alaa. Nothing is sent until you press Send."),
    ("Alaa replies personally", "A private conversation follows, by telephone, email or video call."),
]
next_steps = "".join(f'<li><span class="step-n" aria-hidden="true">{i + 1}</span><div><h3>{t}</h3><p>{d}</p></div></li>' for i, (t, d) in enumerate(NEXT))

contact_body = f'''
<section class="sec sec-first">
  <div class="wrap enquiry">
    <div class="enquiry-intro">
      <p class="eyebrow">Contact</p>
      <h1>Share <em>your brief.</em></h1>
      <p class="lede">Tell Alaa what you need. Three short steps prepare a personal email for you to review and send.</p>
    </div>

    <div class="form-card" id="brief">
      <form class="letter-form" action="mailto:{ALAA}" method="POST" enctype="text/plain" novalidate>
        <input type="hidden" name="source" value="crownsmere.com/contact">
        <div class="hp" aria-hidden="true"><label for="f-hp">Leave this empty</label><input id="f-hp" type="text" name="_honey" tabindex="-1" autocomplete="off"></div>

        <ol class="steps-nav" aria-hidden="true"><li class="on">Request</li><li>Brief</li><li>Details</li></ol>
        <p class="step-count" aria-live="polite"></p>

        <div class="step" data-step="1">
          <h2 class="step-title" tabindex="-1">What can I help you with?</h2>
          <fieldset class="field choices">
            <legend>I am looking to</legend>
            {choice("request", "Buy a home", required=True)}{choice("request", "Rent a home")}{choice("request", "Sell privately")}{choice("request", "Let my property")}{choice("request", "Invest")}{choice("request", "Seek advice")}
          </fieldset>
          <div class="field"><label for="f-when">Timeframe <span class="opt">(optional)</span></label><select id="f-when" name="timeframe">{options(["Not specified", "As soon as possible", "Within 3 months", "3 to 6 months", "6 to 12 months", "When the right property appears"])}</select></div>
          {step_actions(1)}
        </div>

        <div class="step" data-step="2">
          <h2 class="step-title" tabindex="-1">Tell me about it.</h2>
          <div class="field"><label for="f-brief">Your brief <span class="opt">(optional)</span></label><textarea id="f-brief" name="brief" rows="4" maxlength="3000" placeholder="The kind of property, size, must-haves, anything that matters to you"></textarea></div>
          <div class="field-row">
            <div class="field"><label for="f-area">Preferred areas <span class="opt">(optional)</span></label><input id="f-area" type="text" name="areas" placeholder="e.g. Belgravia, Chelsea"></div>
            <div class="field"><label for="f-budget">Budget or value <span class="opt">(optional)</span></label><select id="f-budget" name="budget_or_value">{options(["Prefer not to say", "Under &pound;1m", "&pound;1m to &pound;2.5m", "&pound;2.5m to &pound;5m", "&pound;5m to &pound;10m", "Over &pound;10m", "Monthly rent (lettings)"])}</select></div>
          </div>
          {step_actions(2)}
        </div>

        <div class="step" data-step="3">
          <h2 class="step-title" tabindex="-1">How may I reach you?</h2>
          <div class="field"><label for="f-name">Full name</label><input id="f-name" type="text" name="name" autocomplete="name" required></div>
          <div class="field-row">
            <div class="field"><label for="f-email">Email address</label><input id="f-email" type="email" name="email" autocomplete="email" inputmode="email" required></div>
            <div class="field"><label for="f-tel">Telephone</label><input id="f-tel" type="tel" name="phone" autocomplete="tel" inputmode="tel" placeholder="+44" required></div>
          </div>
          <div class="field-row">
            <fieldset class="field choices">
              <legend>Please contact me by</legend>
              {choice("preferred_contact", "Telephone")}{choice("preferred_contact", "Email")}{choice("preferred_contact", "Either", checked=True)}
            </fieldset>
            <div class="field"><label for="f-time">Best time to call</label><select id="f-time" name="best_time">{options(["Any time", "Morning", "Afternoon", "Evening"])}</select></div>
          </div>
          <label class="consent"><input type="checkbox" name="consent" value="Yes" required><span>I am happy for {BRAND} to contact me by telephone and email about this request. My details will be handled confidentially and will not be shared with an estate agent or guarantor provider without my further agreement. See the <a href="privacy.html">privacy notice</a>.</span></label>
          {step_actions(3, last=True)}
        </div>

        <p class="form-status" role="status" aria-live="polite"></p>
        <div class="contact-mail-backup" hidden>
          <h3>Your email is ready.</h3>
          <p>Your email app should open with a private letter to Alaa. Please review it and press <strong>Send</strong>. If nothing opens, use the buttons below to keep your enquiry.</p>
          <div class="btn-row">
            <a class="btn btn-primary" data-contact-email href="mailto:{EMAIL}">Open prepared email{ARROW}</a>
            <button class="btn btn-ghost" type="button" data-contact-copy>Copy my enquiry</button>
          </div>
          {webmail("Use webmail instead:", "Open in Gmail", "Open in Outlook")}
          <p data-contact-feedback aria-live="polite"></p>
          <label class="contact-copy-label" hidden>Prepared enquiry<textarea rows="8" readonly data-contact-text></textarea></label>
        </div>
      </form>
    </div>

    <aside class="enquiry-aside" aria-label="What happens next">
      <h2 class="aside-title">What happens next</h2>
      <ol class="steps steps-sm">{next_steps}</ol>
      <dl class="contact-list">
        <div><dt>Email</dt><dd><a href="mailto:{EMAIL}">{EMAIL}</a></dd></div>
        <div><dt>Telephone</dt><dd>Shared personally, once your brief is received</dd></div>
        <div><dt>Consultations</dt><dd>By appointment, London</dd></div>
      </dl>
    </aside>
  </div>
</section>

<section class="sec sec-alt" id="questions" aria-labelledby="faq-title">
  <div class="wrap sec-split">
    {sec_head("Questions", "Before you <em>get in touch.</em>", hid="faq-title")}
    {faq(CONTACT_FAQ)}
  </div>
</section>'''

page("contact.html", f"Share Your Property Brief | {BRAND}",
     "Share your property brief with Crownsmere Estate. A private, by-request search for buying, renting, selling privately and investing in prime London.",
     contact_body)

# ---------------------------------------------------------------- students (English and Arabic)
# Each language has its own page (students.html, students-ar.html), linked by hreflang so search
# engines show Arabic speakers the Arabic page. assets/student.js runs the form and prepares the email.
# Field names and option values stay in English so Alaa receives consistent emails.
STUDENT = {
    "en": dict(
        dir="ltr", eyebrow="International student services",
        h1="Your London home. <em>A simpler start.</em>",
        lede="Studying in London but don't have a UK guarantor? Tell Alaa what you need. Crownsmere can help you explore rental options and professional guarantor services accepted by participating landlords.",
        note="Initial enquiries are free. Guarantor approval and landlord acceptance are never guaranteed.",
        form_h="Start your enquiry",
        form_p="A free initial enquiry. Your mail app will open with a prepared message to Alaa.",
        language="English",
        progress=["Your plans", "Your situation", "Your details"],
        s0="What are you looking for?", service_legend="What help do you need? *",
        service=[("Apartment and guarantor help", "Find an apartment and explore guarantor options"),
                 ("Guarantor guidance for found property", "Help with guarantor options for a property I found"),
                 ("Apartment search only", "Help finding a London rental only")],
        university="University or college", university_ph="Optional — e.g. UCL, Imperial, King's",
        budget="Monthly rental budget *",
        budget_opts=[("Not decided", "Not decided"), ("Under GBP 1500", "Under £1,500"), ("GBP 1500-2500", "£1,500–£2,500"),
                     ("GBP 2500-4000", "£2,500–£4,000"), ("Over GBP 4000", "Over £4,000")],
        when="When are you looking to move? *",
        when_opts=[("As soon as possible", "As soon as possible"), ("Within 1 month", "Within 1 month"),
                   ("Within 1-3 months", "Within 1–3 months"), ("Later/unsure", "Later / not sure")],
        next="Continue", back="Back", arrow="→",
        s1="Tell us about your situation", guarantor_legend="Your guarantor situation *",
        guarantor=[("No UK guarantor", "I do not have a UK guarantor"),
                   ("Potential overseas family guarantor", "I have a family member overseas who might help"),
                   ("Exploring professional guarantor", "I would like to understand professional guarantor services"),
                   ("Unsure", "I am not sure")],
        property="Have you already found a property?",
        property_opts=[("Need to find a property", "No — I need to find one"), ("Already found a property", "Yes — an agent / landlord has a property"),
                       ("Comparing options", "I am still comparing options")],
        areas="Preferred London areas", areas_ph="Optional — e.g. Kensington, Chelsea",
        notes="Anything else Alaa should know?", notes_ph="Optional — property type, university location, timing… Please don't enter passport or bank details.",
        s2="How can Alaa contact you?", name="Full name *", email="Email address *", phone="Phone / WhatsApp number",
        contact_legend="Preferred contact method", contact=[("Email", "Email"), ("Phone", "Phone call"), ("WhatsApp", "WhatsApp")],
        consent='I agree that Crownsmere Estate may contact me about this enquiry. I have read the <a href="privacy.html">privacy notice</a>. My information will not be shared with an estate agent or guarantor provider without further agreement.',
        submit="Continue to email",
        sent_h="Your email is ready.", sent_p="Review the prepared message and press Send in your email application. Crownsmere has not confirmed receipt.", home="Return home",
        status=dict(invalid="Please complete the required fields.", phone="Please check the phone number (7–15 digits).",
                    sending="Preparing your email…", error="Your email is ready. Open your email app and press Send."),
        fb_label="Alternative enquiry delivery", fb_h="Your email draft is ready",
        fb_p="Your completed application is ready in a professionally formatted email addressed to Alaa, with a copy to Crownsmere. Review it and press <strong>Send</strong> in your mail app. If no email app opens, use the buttons below; your answers remain on this page.",
        fb_open="Open prepared email", fb_copy="Copy completed enquiry", fb_text="Your completed enquiry",
        webmail=("Use webmail instead:", "Open in Gmail", "Open in Outlook"),
        advice_h="Good to know",
        advice=["<strong>New since 1 May 2026:</strong> under the Renters&rsquo; Rights Act 2025, most private landlords in England can ask for no more than one month&rsquo;s rent before a new tenancy starts, so paying several months upfront is rarely an option now. A UK or professional guarantor is often the alternative. University halls and some purpose-built student accommodation follow different rules.",
                "This is a free initial enquiry, not a guarantor application or guarantee of acceptance.",
                "Professional guarantor providers decide eligibility and fees. The landlord or agent must agree to accept the proposed guarantor; approval is not guaranteed.",
                "You can choose whether to use a professional guarantor provider. Crownsmere may receive a disclosed referral fee from partners.",
                "Please do not upload or enter passports, bank statements or other sensitive identification details here."],
        questions="Questions? Email",
    ),
    "ar": dict(
        dir="rtl", eyebrow="خدمات الطلاب الدوليين",
        h1="منزلك في لندن. <em>بداية أسهل.</em>",
        lede="تدرس في لندن وليس لديك ضامن مقيم في المملكة المتحدة؟ أخبر مستشارتنا العقارية علا بما تحتاج إليه. تساعدك Crownsmere على استكشاف خيارات الإيجار وخدمات الضمان التي قد يقبلها الملاك.",
        note="الاستفسار الأولي مجاني. تخضع الموافقة على الضمان وقبول المالك لشروط الجهات المعنية.",
        form_h="ابدأ طلب المساعدة",
        form_p="استفسار أولي مجاني. سيفتح البريد الإلكتروني برسالة موجهة إلى علا لمراجعتها وإرسالها.",
        language="Arabic",
        progress=["احتياجاتك", "وضعك الحالي", "بيانات التواصل"],
        s0="ما نوع المساعدة التي تحتاجها؟", service_legend="ما المساعدة المطلوبة؟ *",
        service=[("Apartment and guarantor help", "البحث عن شقة واستكشاف خيارات الضمان"),
                 ("Guarantor guidance for found property", "المساعدة في خيارات الضمان لعقار وجدته"),
                 ("Apartment search only", "البحث عن عقار للإيجار فقط")],
        university="الجامعة أو الكلية", university_ph="اختياري — مثال: UCL",
        budget="الميزانية الشهرية للإيجار *",
        budget_opts=[("Not decided", "لم أحدد بعد"), ("Under GBP 1500", "أقل من £1,500"), ("GBP 1500-2500", "من £1,500 إلى £2,500"),
                     ("GBP 2500-4000", "من £2,500 إلى £4,000"), ("Over GBP 4000", "أكثر من £4,000")],
        when="متى ترغب بالانتقال؟ *",
        when_opts=[("As soon as possible", "في أقرب وقت"), ("Within 1 month", "خلال شهر"),
                   ("Within 1-3 months", "خلال شهر إلى 3 أشهر"), ("Later/unsure", "لاحقاً / غير متأكد")],
        next="متابعة", back="السابق", arrow="←",
        s1="أخبرنا عن وضعك", guarantor_legend="وضع الضامن *",
        guarantor=[("No UK guarantor", "ليس لدي ضامن مقيم في المملكة المتحدة"),
                   ("Potential overseas family guarantor", "قد يستطيع أحد أفراد عائلتي خارج بريطانيا المساعدة"),
                   ("Exploring professional guarantor", "أود معرفة خدمات الضمان المهني"),
                   ("Unsure", "لست متأكداً")],
        property="هل وجدت عقاراً بالفعل؟",
        property_opts=[("Need to find a property", "لا، أبحث عن عقار"), ("Already found a property", "نعم، لدي عقار لدى وكيل أو مالك"),
                       ("Comparing options", "ما زلت أقارن الخيارات")],
        areas="المناطق المفضلة في لندن", areas_ph="اختياري — مثال: كنسينغتون، تشيلسي",
        notes="هل هناك تفاصيل أخرى تريد إخبار علا بها؟", notes_ph="اختياري — نوع العقار والموقع والتوقيت. لا تُدخل تفاصيل جواز السفر أو الحساب البنكي.",
        s2="كيف تتواصل معك علا؟", name="الاسم الكامل *", email="البريد الإلكتروني *", phone="رقم الهاتف أو واتساب",
        contact_legend="طريقة التواصل المفضلة", contact=[("Email", "البريد الإلكتروني"), ("Phone", "مكالمة هاتفية"), ("WhatsApp", "واتساب")],
        consent='أوافق على تواصل Crownsmere Estate معي بشأن هذا الطلب. وقد قرأت <a href="privacy.html">سياسة الخصوصية</a>. لن تتم مشاركة بياناتي مع وكيل عقاري أو مقدم خدمة ضمان دون موافقتي الإضافية.',
        submit="المتابعة إلى البريد الإلكتروني",
        sent_h="رسالتك جاهزة.", sent_p="راجع الرسالة المُعدّة واضغط إرسال في تطبيق البريد الإلكتروني. لم يتم تأكيد استلام Crownsmere للطلب بعد.", home="العودة للرئيسية",
        status=dict(invalid="يرجى تعبئة الحقول المطلوبة.", phone="يرجى التأكد من رقم الهاتف (7 إلى 15 رقماً).",
                    sending="جارٍ تجهيز البريد الإلكتروني…", error="رسالتك جاهزة. افتح تطبيق البريد واضغط إرسال."),
        fb_label="طريقة بديلة لإرسال الاستفسار", fb_h="رسالة طلبك جاهزة",
        fb_p="تم تجهيز طلبك في رسالة بريد إلكتروني منظمة موجهة إلى علا، مع إرسال نسخة إلى Crownsmere. راجع الرسالة واضغط <strong>إرسال</strong> من تطبيق البريد. إذا لم يفتح التطبيق، استخدم الأزرار أدناه وستبقى إجاباتك محفوظة هنا.",
        fb_open="فتح البريد المُجهّز", fb_copy="نسخ الطلب المكتمل", fb_text="تفاصيل طلبك",
        webmail=("أو استخدم البريد عبر المتصفح:", "فتح في Gmail", "فتح في Outlook"),
        advice_h="معلومات مهمة",
        advice=["<strong>جديد منذ 1 مايو 2026:</strong> بموجب قانون حقوق المستأجرين لعام 2025، لا يجوز لمعظم الملاك في إنجلترا طلب أكثر من إيجار شهر واحد مقدماً قبل بدء عقد الإيجار الجديد، لذا لم يعد دفع إيجار عدة أشهر مقدماً خياراً متاحاً في الغالب، وأصبح الضامن المقيم في المملكة المتحدة أو الضامن المهني هو البديل المعتاد. تخضع السكنات الجامعية وبعض مساكن الطلاب المخصصة لقواعد مختلفة.",
                "هذا طلب مساعدة أولي مجاني، وليس طلب ضمان رسمي ولا وعداً بالموافقة.",
                "يحدد مقدم خدمة الضمان الأهلية والرسوم، ويجب أن يوافق المالك أو الوكيل على الضامن المقترح.",
                "اختيار خدمة الضمان المهني يعود إليك. وقد تتلقى Crownsmere عمولة إحالة معلنة من بعض الشركاء.",
                "يرجى عدم إدخال أرقام جواز السفر أو كشوف الحسابات البنكية أو بيانات الهوية الحساسة هنا."],
        questions="للاستفسارات، راسلنا",
    ),
}

def student_panel(lang):
    s = STUDENT[lang]
    opts = lambda pairs: "".join(f'<option value="{v}">{t}</option>' for v, t in pairs)
    def radios(name, pairs, first_checked=True, required=True, small=False):
        cls = "std-radio std-radio-small" if small else "std-radio"
        return "".join(
            f'<label class="{cls}"><input type="radio" name="{name}" value="{v}"{" checked" if (i == 0 and first_checked) else ""}{" required" if required else ""}><span>{t}</span></label>'
            for i, (v, t) in enumerate(pairs))
    current = ' aria-current="step"'
    progress = "".join(f'<li data-step-indicator="{i}"{current if i == 0 else ""}><span>{i + 1}</span>{t}</li>' for i, t in enumerate(s["progress"]))
    nxt = f'<button class="btn btn-primary" type="button" data-next>{s["next"]} <span aria-hidden="true">{s["arrow"]}</span></button>'
    back = f'<button class="btn btn-ghost" type="button" data-back>{s["back"]}</button>'
    st = s["status"]
    copy_dir = ' dir="auto"' if lang == "ar" else ""
    return f'''<div class="student-language" data-language-panel="{lang}" lang="{lang}" dir="{s["dir"]}">
  <div class="wrap stu">
    <div class="stu-intro">
      <p class="eyebrow">{s["eyebrow"]}</p>
      <h1>{s["h1"]}</h1>
      <p class="lede">{s["lede"]}</p>
      <p class="stu-note">{s["note"]}</p>
    </div>
    <div class="student-application form-card" id="{lang}-form">
      <div class="student-form-header"><h2>{s["form_h"]}</h2><p>{s["form_p"]}</p></div>
      <form class="student-form" action="mailto:{ALAA}" method="POST" enctype="text/plain" data-form-lang="{lang}">
        <input type="hidden" name="source" value="crownsmere.com/students">
        <input type="hidden" name="language" value="{s["language"]}">
        <div class="std-hp" aria-hidden="true"><label for="{lang}-hp">Leave empty</label><input id="{lang}-hp" name="_honey" type="text" tabindex="-1" autocomplete="off"></div>
        <ol class="student-progress">{progress}</ol>
        <div class="student-stage" data-student-step="0">
          <h3 tabindex="-1">{s["s0"]}</h3>
          <fieldset class="std-field"><legend>{s["service_legend"]}</legend>{radios("service", s["service"])}</fieldset>
          <div class="std-row">
            <label class="std-field">{s["university"]}<input id="{lang}-university" type="text" name="university" maxlength="120" placeholder="{s["university_ph"]}"></label>
            <label class="std-field">{s["budget"]}<select id="{lang}-budget" name="monthly_budget" required>{opts(s["budget_opts"])}</select></label>
          </div>
          <label class="std-field">{s["when"]}<select id="{lang}-when" name="move_timeframe" required>{opts(s["when_opts"])}</select></label>
          <div class="std-actions"><span></span>{nxt}</div>
        </div>
        <div class="student-stage" data-student-step="1">
          <h3 tabindex="-1">{s["s1"]}</h3>
          <fieldset class="std-field"><legend>{s["guarantor_legend"]}</legend>{radios("guarantor_status", s["guarantor"])}</fieldset>
          <label class="std-field">{s["property"]}<select id="{lang}-property" name="property_found">{opts(s["property_opts"])}</select></label>
          <label class="std-field">{s["areas"]}<input id="{lang}-areas" type="text" name="preferred_areas" maxlength="160" placeholder="{s["areas_ph"]}"></label>
          <label class="std-field">{s["notes"]}<textarea id="{lang}-notes" name="additional_notes" rows="3" maxlength="750" placeholder="{s["notes_ph"]}"></textarea></label>
          <div class="std-actions">{back}{nxt}</div>
        </div>
        <div class="student-stage" data-student-step="2">
          <h3 tabindex="-1">{s["s2"]}</h3>
          <label class="std-field">{s["name"]}<input id="{lang}-name" type="text" name="name" autocomplete="name" maxlength="120" required></label>
          <div class="std-row">
            <label class="std-field">{s["email"]}<input id="{lang}-email" name="email" type="email" autocomplete="email" inputmode="email" maxlength="150" required></label>
            <label class="std-field">{s["phone"]}<input id="{lang}-phone" name="phone" type="tel" autocomplete="tel" inputmode="tel" maxlength="35" placeholder="+44"></label>
          </div>
          <fieldset class="std-field"><legend>{s["contact_legend"]}</legend><div class="std-pills">{radios("preferred_contact", s["contact"], required=False, small=True)}</div></fieldset>
          <label class="std-consent"><input type="checkbox" name="consent" value="Yes" required><span>{s["consent"]}</span></label>
          <div class="std-actions">{back}<button class="btn btn-primary" type="submit">{s["submit"]} <span aria-hidden="true">{s["arrow"]}</span></button></div>
        </div>
        <div class="std-sent" tabindex="-1" hidden><h3>{s["sent_h"]}</h3><p>{s["sent_p"]}</p><a href="index.html">{s["home"]}</a></div>
        <p class="std-status" data-invalid="{st["invalid"]}" data-phone="{st["phone"]}" data-sending="{st["sending"]}" data-error="{st["error"]}" role="status" aria-live="polite"></p>
        <section class="std-fallback" tabindex="-1" hidden aria-label="{s["fb_label"]}">
          <h4>{s["fb_h"]}</h4>
          <p>{s["fb_p"]}</p>
          <div class="std-fallback-actions">
            <a class="btn btn-primary std-email-link" data-email-fallback href="mailto:{ALAA}?cc=hello%40crownsmere.com">{s["fb_open"]} <span aria-hidden="true">{s["arrow"]}</span></a>
            <button class="btn btn-ghost" type="button" data-copy-fallback>{s["fb_copy"]}</button>
          </div>
          {webmail(*s["webmail"])}
          <p class="std-copy-feedback" data-copy-feedback aria-live="polite"></p>
          <label class="std-copy-label" hidden>{s["fb_text"]}<textarea class="std-copy-text" data-copy-text rows="7" readonly{copy_dir}></textarea></label>
        </section>
      </form>
    </div>
    <aside class="student-advice">
      <h2>{s["advice_h"]}</h2>
      <ul class="checks">{"".join(f"<li>{ic('check')}<span>{a}</span></li>" for a in s["advice"])}</ul>
      <p class="student-advice-contact">{s["questions"]} <a href="mailto:{EMAIL}">{EMAIL}</a></p>
    </aside>
  </div>
</div>'''

def students_body(lang):
    cur = lambda l: ' aria-current="page"' if l == lang else ""
    return f'''
<nav class="student-language-bar wrap" aria-label="Language / اللغة">
  <div class="lang-switch"><a href="students.html" hreflang="en" lang="en"{cur("en")}>English</a><a href="students-ar.html" hreflang="ar" lang="ar"{cur("ar")}>العربية</a></div>
</nav>
{student_panel(lang)}'''

STUDENT_SCRIPT = '\n<script src="assets/student.js" defer></script>'
page("students.html", f"International Student Lettings & Guarantor Help | {BRAND}",
     "Find a London rental home and explore guarantor options with Crownsmere Estate. English and Arabic enquiries for international students.",
     students_body("en"),
     extra_ld=[{"@context": "https://schema.org", "@type": "WebPage", "name": "International Student Lettings & Guarantor Help",
                "url": f"{SITE}/students.html", "inLanguage": "en-GB"}],
     og_desc="Find London rentals and explore guarantor options. English and Arabic assistance for international students from Crownsmere Estate.",
     scripts=STUDENT_SCRIPT, quick=("#en-form", "Start enquiry"))
page("students-ar.html", f"مساعدة الطلاب الدوليين في الإيجار والضامن في لندن | {BRAND}",
     "ابحث عن سكن للإيجار في لندن واستكشف خيارات الضامن مع Crownsmere Estate. خدمة باللغة العربية للطلاب الدوليين.",
     students_body("ar"),
     extra_ld=[{"@context": "https://schema.org", "@type": "WebPage", "name": "مساعدة الطلاب الدوليين في الإيجار والضامن",
                "url": f"{SITE}/students-ar.html", "inLanguage": "ar"}],
     scripts=STUDENT_SCRIPT, quick=("#ar-form", "ابدأ الاستفسار", "ar"), og_locale="ar_AR")

# ---------------------------------------------------------------- privacy
privacy_body = f'''
{page_hero("Privacy notice", "Your privacy, <em>respected.</em>", f"Discretion is at the heart of what we do. This notice explains, plainly, what happens to the information you share with {BRAND}.")}

<section class="sec sec-tight">
  <div class="wrap prose">
    <p class="updated">Last updated {UPDATED}</p>

    <h2>Who we are</h2>
    <p>{BRAND} is a private property consultancy based in London, United Kingdom. Its principal is {BUSINESS["principal"]}. For the purposes of UK data protection law, {BRAND} is the controller of the personal information described here. You can contact us about privacy at any time at <a href="mailto:{EMAIL}">{EMAIL}</a>.</p>

    <h2>What we collect</h2>
    <p>Only what you choose to share: your name, email address and telephone number, how and when you prefer to be contacted, and the details of your request (for example the kind of property you are looking for, preferred areas, budget and timeframe). Student enquiries may also include your university, your housing and guarantor situation and whether you have found a property. If you write to us or call, we also keep that correspondence. Please do not submit passport details, bank statements or identity documents through these public enquiry forms.</p>

    <h2>How we use it</h2>
    <ul>
      <li>To reply to your enquiry and discuss your brief.</li>
      <li>To carry out the search or other services you ask us to provide.</li>
      <li>To keep a record of our correspondence.</li>
      <li>To discuss potential professional guarantor services and rental options when you ask for student assistance.</li>
    </ul>
    <p>We rely on your request for us to act before any agreement is made, our legitimate interest in responding to enquiries, and, where you give it on our forms, your agreement to be contacted. We never use your details for unrelated marketing, and we never sell your personal data.</p>
    <p>If you ask us to introduce you to an estate agent or a professional guarantor provider, we will explain the proposed introduction and request your agreement before sharing information with them. Those firms may then act as independent controllers of the information you supply to them. Crownsmere may receive a disclosed referral commission from a participating partner. An enquiry does not automatically apply for a guarantor, guarantee a rental property, or authorise us to share your details with such partners.</p>

    <h2>Who helps us</h2>
    <p>A small number of trusted service providers process information on our behalf, only to provide their service:</p>
    <ul>
      <li><strong>Your chosen email provider</strong> sends the email you choose to send from your mail application. We do not automatically receive or store incomplete website form entries.</li>
      <li><strong>Our email hosting provider</strong> stores the emails you send us.</li>
      <li><strong>AI-assisted email filtering</strong> may be used for spam screening if enabled for our {EMAIL} mailbox. Where active, messages may be processed by Anthropic for that limited purpose.</li>
    </ul>
    <p>Some of these providers are based outside the UK, including in the United States. Where that is the case, information is transferred with appropriate safeguards in place. With your separate agreement, we may also share relevant details with others involved in your matter, such as solicitors, agents or professional guarantor providers, when that is needed to help you.</p>

    <h2>How long we keep it</h2>
    <p>We keep your information only for as long as it is needed for the purposes above, including any legal, accounting or regulatory requirements, and then delete it securely.</p>

    <h2>Your rights</h2>
    <p>You can ask to see the information we hold about you, to correct it, to delete it, to restrict or object to its use, or to receive a copy of it. Where we rely on your consent, you can withdraw it at any time. Just email <a href="mailto:{EMAIL}">{EMAIL}</a>. If you are unhappy with how your information has been handled, you can complain to the Information Commissioner&rsquo;s Office at <a href="https://ico.org.uk" rel="noopener">ico.org.uk</a>.</p>

    <h2>Cookies</h2>
    <p>This website does not use cookies, analytics or advertising trackers. Its fonts, images and scripts are all loaded from this website; nothing is requested from third parties. Your draft enquiries remain in your browser until you send them from your own mail application.</p>

    <h2>Security</h2>
    <p>This website is served only over an encrypted (HTTPS) connection and uses a strict content security policy. To report a security concern, please email <a href="mailto:{EMAIL}">{EMAIL}</a>.</p>

    <h2>Changes</h2>
    <p>If this notice changes, the updated version will be published on this page with a new date.</p>
  </div>
</section>'''

page("privacy.html", f"Privacy Notice | {BRAND}",
     "How Crownsmere Estate collects, uses and protects the personal information you share with us, and the rights you have over it.",
     privacy_body)

# ---------------------------------------------------------------- 404
notfound_body = f'''
<section class="page-hero notfound">
  <div class="wrap">
    <p class="eyebrow">Page not found</p>
    <h1>This page has gone <em>off-market.</em></h1>
    <p class="lede">The page you were looking for is not here, but the right property may well be. Let me help you find it.</p>
    <div class="btn-row">
      {btn("index.html", "Return home")}
      {btn("contact.html", "Share your brief", "ghost", arrow=False)}
    </div>
  </div>
</section>'''

html = page("404.html", f"Page Not Found — {BRAND}", "This page could not be found.", notfound_body)
# GitHub Pages serves 404.html at any missing path, so make every link root-relative.
html = re.sub(r'(href|src|srcset)="(?!https?:|mailto:|tel:|#|/)([^"]+)"', r'\1="/\2"', html)
html = html.replace('href="/index.html"', 'href="/"')
html = html.replace('<link rel="canonical" href="https://crownsmere.com/404.html">', '<meta name="robots" content="noindex">')
open(os.path.join(OUT, "404.html"), "w").write(html)

# ---------------------------------------------------------------- SEO files
pages = [("", "1.0"), ("services.html", "0.9"), ("about.html", "0.8"), ("students.html", "0.9"), ("students-ar.html", "0.9"),
         ("contact.html", "0.9"), ("privacy.html", "0.3")]
def sitemap_alternates(p):
    return "".join(f'<xhtml:link rel="alternate" hreflang="{l}" href="{SITE}/{u}"/>' for l, u in ALTERNATES.get(p, []))
sitemap = ('<?xml version="1.0" encoding="UTF-8"?>\n<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9" xmlns:xhtml="http://www.w3.org/1999/xhtml">\n'
           + "".join(f"  <url><loc>{SITE}/{p}</loc>{sitemap_alternates(p)}<lastmod>{UPDATED_ISO}</lastmod><priority>{pr}</priority></url>\n" for p, pr in pages)
           + "</urlset>\n")
open(os.path.join(OUT, "sitemap.xml"), "w").write(sitemap)
open(os.path.join(OUT, "robots.txt"), "w").write(f"User-agent: *\nAllow: /\n\nSitemap: {SITE}/sitemap.xml\n")
manifest = {
    "name": BRAND, "short_name": "Crownsmere", "description": "Private property search in prime London.",
    "start_url": "/", "display": "browser", "background_color": "#faf7f1", "theme_color": "#faf7f1",
    "icons": [{"src": "/assets/img/apple-touch-icon.png", "sizes": "180x180", "type": "image/png"},
              {"src": "/assets/img/icon-512.png", "sizes": "512x512", "type": "image/png"}],
}
open(os.path.join(OUT, "site.webmanifest"), "w").write(json.dumps(manifest, indent=2) + "\n")

print("built")
