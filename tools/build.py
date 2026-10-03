"""Generates the Crownsmere Estate website (static HTML).

All page content lives in this file. Edit it, then run:  python3 tools/build.py
(Images, styles and scripts live in assets/.)
"""
import json
import os
import re

OUT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SITE = "https://crownsmere.com"
BRAND = "Crownsmere Estate"
# No telephone number is published: Alaa shares it personally once a brief is received.
EMAIL = "hello@crownsmere.com"
UPDATED = "3 October 2026"
UPDATED_ISO = "2026-10-03"

# ---------------------------------------------------------------- icons (24px line icons)
P = {
    "house": '<path d="M3 11 12 3l9 8M5.5 9.5V21h13V9.5M10 21v-6h4v6"/>',
    "key": '<circle cx="8" cy="15" r="4"/><path d="M11 12 20 3M16.5 6.5 19 9M14.5 8.5 16.5 10.5"/>',
    "chart": '<path d="M3 20h18M7 20v-6M12 20V9M17 20V5"/>',
    "people": '<circle cx="9" cy="8" r="3"/><path d="M3 20a6 6 0 0 1 12 0"/><circle cx="17" cy="9" r="2.5"/><path d="M15.6 14.3A5.5 5.5 0 0 1 21 20"/>',
    "person": '<circle cx="12" cy="8" r="4"/><path d="M4 21a8 8 0 0 1 16 0"/>',
    "pin": '<path d="M12 21s-7-6.2-7-11a7 7 0 0 1 14 0c0 4.8-7 11-7 11z"/><circle cx="12" cy="10" r="2.5"/>',
    "lock": '<rect x="5" y="11" width="14" height="10"/><path d="M8 11V7a4 4 0 0 1 8 0v4M12 15v2"/>',
    "scales": '<path d="M12 3v18M7 21h10M4 7h16M4 7l-2.5 6h5zM20 7l-2.5 6h5z"/>',
    "speech": '<path d="M4 5h16v11H9l-5 4z"/>',
    "shield": '<path d="M12 3l8 3v6c0 5-3.5 8-8 9-4.5-1-8-4-8-9V6z"/><path d="M8.5 12l2.5 2.5 4.5-5"/>',
    "heart": '<path d="M12 20s-8-5-8-11a4.5 4.5 0 0 1 8-2.8A4.5 4.5 0 0 1 20 9c0 6-8 11-8 11z"/>',
    "document": '<path d="M6 3h9l4 4v14H6zM15 3v4h4M9 12h7M9 16h5"/>',
    "search": '<circle cx="11" cy="11" r="6.5"/><path d="M20 20l-4.4-4.4"/>',
    "phone": '<path d="M5 3h4l2 5-2.5 1.5a11 11 0 0 0 6 6L16 13l5 2v4a2 2 0 0 1-2 2A16 16 0 0 1 3 5a2 2 0 0 1 2-2z"/>',
    "mail": '<rect x="3" y="5" width="18" height="14"/><path d="M3 6l9 7 9-7"/>',
}

def ic(name, cls="ic"):
    return f'<svg class="{cls}" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.1" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true">{P[name]}</svg>'

def pic(name, alt, w, h, cls="", lazy=True, ext="jpg", priority=False):
    """A <picture> with a WebP source and a JPEG/PNG fallback."""
    attrs = f' class="{cls}"' if cls else ""
    load = ' loading="lazy" decoding="async"' if lazy else (' fetchpriority="high"' if priority else "")
    return (f'<picture><source type="image/webp" srcset="assets/img/{name}.webp">'
            f'<img{attrs} src="assets/img/{name}.{ext}" alt="{alt}" width="{w}" height="{h}"{load}></picture>')

LOGO = lambda lazy=False: pic("monogram-sm", "", 165, 259, lazy=lazy, ext="png")

# ---------------------------------------------------------------- chrome
NAV = [("index.html", "Home"), ("services.html", "Services"), ("about.html", "About"), ("contact.html", "Contact")]

ORG = {
    "@context": "https://schema.org", "@type": "RealEstateAgent", "@id": f"{SITE}/#business",
    "name": BRAND,
    "description": "A private, by-request property search and consultancy service in prime London: clients share a brief and Alaa Qadir finds the right property, on and off the market.",
    "url": f"{SITE}/", "email": EMAIL,
    "image": f"{SITE}/assets/img/townhouse.jpg", "logo": f"{SITE}/assets/img/monogram.png",
    "areaServed": {"@type": "City", "name": "London"},
    "address": {"@type": "PostalAddress", "addressLocality": "London", "addressCountry": "GB"},
    "founder": {"@type": "Person", "name": "Alaa Qadir", "jobTitle": "Individual Property Consultant"},
    "knowsAbout": ["Prime London property", "Property search", "Off-market property", "Private property sales", "Lettings", "Property investment"],
}

def head(title, desc, path, extra_ld=None):
    body_cls = ' class="home"' if path == "index.html" else ""
    canonical = f"{SITE}/{'' if path == 'index.html' else path}"
    ld = [ORG] + (extra_ld or [])
    hero_preload = ('<link rel="preload" as="image" href="assets/img/townhouse.webp" type="image/webp" fetchpriority="high">\n'
                    if path == "index.html" else "")
    return f'''<!doctype html>
<html lang="en-GB" class="no-js">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1, viewport-fit=cover">
<title>{title}</title>
<meta name="description" content="{desc}">
<meta name="theme-color" content="#0e1b2e">
<link rel="canonical" href="{canonical}">
<meta property="og:type" content="website">
<meta property="og:site_name" content="{BRAND}">
<meta property="og:locale" content="en_GB">
<meta property="og:url" content="{canonical}">
<meta property="og:title" content="{title}">
<meta property="og:description" content="{desc}">
<meta property="og:image" content="{SITE}/assets/img/townhouse.jpg">
<meta property="og:image:width" content="1055">
<meta property="og:image:height" content="687">
<meta name="twitter:card" content="summary_large_image">
<link rel="icon" href="assets/img/favicon.png" type="image/png">
<link rel="apple-touch-icon" href="assets/img/apple-touch-icon.png">
<link rel="manifest" href="site.webmanifest">
<link rel="preload" href="assets/fonts/cormorant-garamond.woff2" as="font" type="font/woff2" crossorigin>
<link rel="preload" href="assets/fonts/eb-garamond.woff2" as="font" type="font/woff2" crossorigin>
<link rel="preload" href="assets/fonts/cinzel.woff2" as="font" type="font/woff2" crossorigin>
{hero_preload}<link rel="stylesheet" href="assets/style.css">
<script type="application/ld+json">{json.dumps(ld if len(ld) > 1 else ORG, ensure_ascii=False)}</script>
</head>
<body{body_cls}>
<a class="skip" href="#main">Skip to content</a>
<div class="progress" aria-hidden="true"></div>'''

def header(current):
    nav = "".join(
        '<a class="nl caps" href="%s"%s>%s</a>' % (h, ' aria-current="page"' if h == current else "", t) for h, t in NAV
    )
    items = "\n".join(
        '<li><a href="%s"%s><small>%02d</small>%s</a></li>' % (h, ' aria-current="page"' if h == current else "", i + 1, t)
        for i, (h, t) in enumerate(NAV)
    )
    return f'''
<header class="hd">
  <a class="hd-mark" href="index.html" aria-label="{BRAND}, home">
    {LOGO()}
    <span class="wm"><b>CROWNSMERE</b><small>Estate<span class="tl"> &middot; Individual Property Consultant</span></small></span>
  </a>
  <nav class="hd-nav" aria-label="Main">{nav}<a class="btn btn-gold caps" href="contact.html">Enquire <span aria-hidden="true">&rarr;</span></a></nav>
  <button class="hd-menu caps" type="button" aria-expanded="false" aria-controls="menu"><span>Menu</span><i aria-hidden="true"></i></button>
</header>
<nav class="menu" id="menu" aria-label="Mobile">
  <ol>
{items}
  </ol>
  <aside>
    <div><div class="caps">Your brief</div><a href="contact.html">Share it in confidence</a></div>
    <div><div class="caps">Email</div><a href="mailto:{EMAIL}">{EMAIL}</a></div>
  </aside>
</nav>'''

def footer(current):
    explore = "".join(f'<li><a href="{h}">{t}</a></li>' for h, t in NAV)
    services = "".join(f'<li><a href="services.html#{s.lower()}">{s}</a></li>' for s in ["Buy", "Sell", "Let", "Invest", "Advisory"])
    brief_href = "#brief" if current == "contact.html" else "contact.html"
    second = f'<a href="{brief_href}">{ic("document")}<span>Share your brief</span></a>'
    return f'''
<div class="skyline-wrap">{pic("skyline", "", 1055, 181, cls="skyline")}</div>
<footer class="ft">
  <div class="wrap">
    <div class="ft-top">
      <div class="ft-brand">
        <div class="mk">{LOGO(lazy=True)}<div><b>CROWNSMERE</b><small>Estate &middot; Individual Property Consultant</small></div></div>
        <p>A more personal London.</p>
      </div>
      <div><h4 class="caps">Explore</h4><ul>{explore}</ul></div>
      <div><h4 class="caps">Services</h4><ul>{services}</ul></div>
      <div><h4 class="caps">Contact</h4><ul><li><a href="contact.html">Share your brief</a></li><li><a href="mailto:{EMAIL}">{EMAIL}</a></li><li>London, United Kingdom</li></ul></div>
    </div>
    <div class="ft-motto" aria-hidden="true">DISCRETION &middot; EXPERTISE &middot; RESULTS</div>
    <div class="ft-bottom caps"><span>&copy; <span data-year>2026</span> {BRAND}</span><a href="privacy.html">Privacy notice</a><span>People &middot; Property &middot; Perspective</span><a href="#main">Back to top &uarr;</a></div>
  </div>
</footer>
<nav class="actionbar caps" aria-label="Quick contact"><a href="mailto:{EMAIL}">{ic("mail")}<span>Email</span></a>{second}</nav>
<script src="assets/main.js"></script>
</body>
</html>
'''

def page(fname, title, desc, body, intro="", extra_ld=None):
    html = head(title, desc, fname, extra_ld) + intro + header(fname) + '\n<main id="main">\n' + body + '\n</main>' + footer(fname)
    open(os.path.join(OUT, fname), "w").write(html)
    return html

# ---------------------------------------------------------------- shared content
SERVICES = [
    ("01", "Buy", "buy", "Tell me what you are looking for. I search personally, on and off the market, and bring you only what fits."),
    ("02", "Sell", "sell", "A discreet, private sale to qualified buyers from my network, without the noise of a public listing."),
    ("03", "Let", "let", "The right home to rent, or the right tenant for your property, found quietly and personally."),
    ("04", "Invest", "invest", "Investment opportunities sourced to your brief, including those that never reach the open market."),
    ("05", "Advisory", "advisory", "Independent, impartial advice whenever you need a trusted second opinion."),
]

PROCESS = [
    ("speech", "Your Brief", "A private conversation about what you are looking for, why, and when. No detail is too small."),
    ("search", "The Search", "I search personally, on and off the market, drawing on a discreet network of owners, agents and advisers."),
    ("document", "A Curated Shortlist", "You see only what genuinely fits. Every property is checked first, so your time is never wasted."),
    ("people", "Private Viewings", "Viewings arranged around you and accompanied personally, with an honest opinion on every property."),
    ("scales", "Negotiation", "Calm, strategic negotiation on your behalf, to secure the right property on the right terms."),
    ("key", "The Keys, and Beyond", "I stay with you through to completion, and remain on hand long after the keys are yours."),
]

PILLARS = [
    ("person", "Personal Representation", "You deal directly with me, from the first conversation to the final signature. No call centre, no junior negotiators, no hand-offs."),
    ("lock", "Off-Market Access", "Many of London&rsquo;s finest homes change hands quietly. A discreet network of owners, agents and advisers opens doors that never appear online."),
    ("pin", "Prime London Insight", "In-depth, neighbourhood-level knowledge across Prime and Super Prime London, built through experience and long-standing relationships."),
    ("scales", "Skilled Negotiation", "Calm, strategic negotiation to achieve the best possible outcome, backed by objectivity and a deep understanding of the market."),
]

EXPECT = [
    ("speech", "Clear Communication", "Regular updates and honest feedback at every stage."),
    ("person", "Tailored Guidance", "Advice that is specific to your brief and your goals."),
    ("shield", "Complete Discretion", "Your search, your plans and your details stay private."),
    ("heart", "Attentive Support", "A responsive, hands-on approach from start to finish."),
]

AREAS = [
    ("Mayfair", "Georgian townhouses and lateral apartments between Park Lane and Bond Street."),
    ("Belgravia", "White stucco squares, embassies and cobbled mews behind Hyde Park Corner."),
    ("Knightsbridge", "Garden squares and mansion blocks moments from Hyde Park."),
    ("Chelsea", "Period houses, garden squares and the King&rsquo;s Road, down to the river."),
    ("Kensington", "Grand stucco villas and mansion flats around Kensington Gardens."),
    ("Holland Park", "Detached and semi-detached villas on wide, quiet, tree-lined avenues."),
    ("Notting Hill", "Pastel terraces and private communal gardens with a village feel."),
    ("Marylebone", "Georgian streets and a village high street beside Regent&rsquo;s Park."),
    ("St John&rsquo;s Wood", "Villas with gardens, close to Regent&rsquo;s Park and Primrose Hill."),
    ("Hampstead", "Village lanes, Georgian houses and the open Heath."),
]

FAQ = [
    ("How does it work?",
     "You share your brief, by email or through the form on this site. We then have a private conversation about what you are looking for and why. From there, I search personally and bring you a shortlist of properties that genuinely fit."),
    ("Why are there no properties listed on this website?",
     "Deliberately. Crownsmere works from your brief rather than from a list of properties to sell. Many of the homes I find are never publicly advertised, and those that are deserve to be judged against your brief, not a shop window."),
    ("What does &ldquo;off-market&rdquo; mean?",
     "A property whose owner prefers to sell or let quietly, without public advertising. These homes are reached through a discreet network of owners, agents and advisers rather than through property portals."),
    ("Can you help me sell or let my own property?",
     "Yes. I can introduce your property privately to qualified buyers or tenants, without a public listing unless you would like one."),
    ("Which areas do you cover?",
     "Prime and Super Prime London, including Mayfair, Belgravia, Knightsbridge, Chelsea, Kensington and Notting Hill. If your brief takes us further afield, just ask."),
    ("I live overseas. Can you still help?",
     "Please get in touch. A search can begin by telephone or video call, with regular updates until you are able to visit in person."),
    ("Is my enquiry confidential?",
     "Completely. Your brief and your details are used only to help you, and are never shared without your permission. See the <a href=\"privacy.html\">privacy notice</a> for details."),
    ("How are fees agreed?",
     "Every brief is different, so terms are discussed openly at the outset and agreed in writing before any work begins."),
]

def strip_tags(s):
    return re.sub(r"<[^>]+>", "", s).replace("&ldquo;", "“").replace("&rdquo;", "”").replace("&rsquo;", "’")

FAQ_LD = {
    "@context": "https://schema.org", "@type": "FAQPage",
    "mainEntity": [{"@type": "Question", "name": strip_tags(q), "acceptedAnswer": {"@type": "Answer", "text": strip_tags(a)}} for q, a in FAQ],
}

def ledger():
    rows = "".join(
        f'<li data-reveal><a href="services.html#{a}"><span class="num">{n}</span><h3>{t}</h3><p>{d}</p><span class="go" aria-hidden="true">&rarr;</span></a></li>'
        for n, t, a, d in SERVICES
    )
    return f'<ol class="ledger">{rows}</ol>'

def pillars(quote="The finest homes rarely need to be advertised."):
    items = "".join(f'<div class="pillar" data-reveal>{ic(i)}<h3>{t}</h3><p>{d}</p></div>' for i, t, d in PILLARS)
    return f'''<div class="pillars-wrap">
      <div class="pillars">{items}</div>
      <figure class="pillars-media reveal-img" data-reveal>
        <div class="frame">{pic("colonnade", "White stucco townhouses on a leafy London street", 563, 398)}</div>
        <blockquote>{quote}</blockquote>
      </figure>
    </div>'''

def areas():
    items = "".join(
        f'<li class="area" data-reveal><span class="an-n">{i + 1:02d}</span><span class="an">{n}</span><span class="ad">{d}</span></li>'
        for i, (n, d) in enumerate(AREAS)
    )
    return f'<ul class="areas">{items}</ul>'

def faq(items=FAQ):
    rows = "".join(
        f'<details class="faq-item" data-reveal><summary><span>{q}</span><i aria-hidden="true"></i></summary><div class="faq-a"><p>{a}</p></div></details>'
        for q, a in items
    )
    return f'<div class="faq">{rows}</div>'

def invite(heading="Tell me what <em>you are looking for.</em>"):
    return f'''
<section class="section invite">
  <div class="wrap">
    <div class="eyebrow caps" data-reveal>By request</div>
    <h2 class="display" data-reveal>{heading}</h2>
    <p class="lede" data-reveal>Whether you are searching for a home, an investment, or a discreet buyer for your own property, every engagement begins with a private conversation.</p>
    <div class="btn-row" data-reveal>
      <a class="btn btn-gold caps" href="contact.html">Share your brief <span aria-hidden="true">&rarr;</span></a>
      <a class="btn caps" href="mailto:{EMAIL}">Email {EMAIL}</a>
    </div>
    <div class="contact-line" data-reveal><span>By appointment</span><span>London, United Kingdom</span></div>
  </div>
</section>'''

def band(text, cite="Discretion &middot; Expertise &middot; Results"):
    return f'''
<section class="band">
  <img class="ghost" src="assets/img/monogram.png" alt="" width="330" height="518" loading="lazy" decoding="async">
  <blockquote>
    <p class="display">{text}</p>
    <cite class="caps">{cite}</cite>
  </blockquote>
</section>'''

def statement_figure(caption):
    return (f'<figure class="reveal-img" data-reveal><div class="frame">'
            f'{pic("door", "A black-lacquered front door with brass fittings beside white columns", 433, 610)}'
            f'</div><figcaption class="caps">{caption}</figcaption></figure>')

# ---------------------------------------------------------------- home
INTRO = '''
<div class="intro" aria-hidden="true">
  <div class="mono"><img src="assets/img/monogram.png" alt="" width="330" height="518"><span class="shine"></span></div>
  <div class="wm">CROWNSMERE</div>
  <div class="sub caps">Estate</div>
</div>'''

marquee = "".join(f"<span>{w}</span>" for w in ["By request", "Off-market", "Discretion", "One-to-one", "Prime London", "Expertise", "Results"])

process_cards = "".join(
    f'<article class="step-card"><span class="n">{i + 1:02d}</span><div>{ic(icn)}</div><div><h3>{t}</h3><p>{d}</p></div></article>'
    for i, (icn, t, d) in enumerate(PROCESS)
)

index_body = f'''
<section class="hero">
  <div class="hero-copy">
    <div class="eyebrow caps">Private Property Search &nbsp;&middot;&nbsp; Prime London</div>
    <h1><span class="line"><span>The right home,</span></span><span class="line"><span><em>found for you.</em></span></span></h1>
    <p class="sub">A private, by-request property service. You share your brief; I search discreetly, on and off the market, and bring you only what is genuinely right.</p>
    <div class="btn-row">
      <a class="btn btn-gold caps" href="contact.html">Share your brief <span aria-hidden="true">&rarr;</span></a>
      <a class="btn caps" href="#process">How it works</a>
    </div>
    <div class="hero-meta caps"><span>By request &amp; appointment</span><span>London, United Kingdom</span></div>
  </div>
  <div class="hero-media">
    <div class="px">{pic("townhouse", "A white stucco London townhouse with a black front door and columned porch", 1055, 687, lazy=False, priority=True)}</div>
    <div class="hero-tag"><span class="caps">People<br>Property<br>Perspective</span><p>A more personal London.</p></div>
  </div>
</section>

<div class="marquee" aria-hidden="true"><div class="marquee-track">{marquee}{marquee}</div></div>

<section class="section" id="approach">
  <div class="wrap">
    <div class="section-head">
      <div class="section-mark caps"><b>I.</b>The Approach</div>
      <h2 data-reveal>No shop window. <em>No listings.</em> Just your brief.</h2>
    </div>
    <div class="statement">
      {statement_figure("Prime London")}
      <div class="copy">
        <p class="lede dropcap" data-reveal>Crownsmere Estate is not a typical estate agency. Rather than selling whatever happens to be on the books, I work from your brief, searching personally to find what is genuinely right for you.</p>
        <div class="cols" data-reveal>
          <p>Each client is taken on individually, and each search is shaped around their life, their timing and their priorities. You deal with me directly, from the first conversation to the day you collect the keys.</p>
          <p>Many of London&rsquo;s finest homes change hands quietly, without ever being advertised. Through a discreet network of owners, agents and advisers, I can open doors that never appear online.</p>
        </div>
        <div class="signature" data-reveal><b>Alaa Qadir</b><span class="caps">Individual Property Consultant</span></div>
      </div>
    </div>
    <div class="facts" data-reveal>
      <div><strong>By request</strong><span class="caps">Every search starts with your brief</span></div>
      <div><strong>One-to-one</strong><span class="caps">You deal directly with me</span></div>
      <div><strong>Off-market</strong><span class="caps">Homes that are never advertised</span></div>
    </div>
  </div>
</section>

<section class="section tight" id="services">
  <div class="wrap">
    <div class="section-head">
      <div class="section-mark caps"><b>II.</b>How I Can Help</div>
      <h2 data-reveal>Whatever you are looking for, <em>found personally.</em></h2>
    </div>
    {ledger()}
  </div>
</section>

<section class="journey" id="process" aria-label="How it works">
  <div class="journey-pin">
    <div class="journey-track">
      <div class="journey-intro">
        <div class="section-mark caps"><b>III.</b>How It Works</div>
        <h2>From your brief <em>to the keys.</em></h2>
        <p>A private, unhurried process, shaped entirely around you.</p>
        <a class="link caps" href="contact.html">Share your brief <span class="arrow" aria-hidden="true">&rarr;</span></a>
      </div>
      {process_cards}
    </div>
    <div class="journey-progress" aria-hidden="true"><i></i></div>
  </div>
</section>

{band("You share the brief. <em>I find the property.</em>")}

<section class="section" id="areas">
  <div class="wrap">
    <div class="section-head">
      <div class="section-mark caps"><b>IV.</b>Where I Search</div>
      <div><h2 data-reveal>Prime London, <em>street by street.</em></h2><p class="lede" data-reveal>Not sure which neighbourhood suits you? Helping you choose is part of the search.</p></div>
    </div>
    {areas()}
  </div>
</section>

<section class="section tight" id="why">
  <div class="wrap">
    <div class="section-head">
      <div class="section-mark caps"><b>V.</b>Why Crownsmere</div>
      <h2 data-reveal>Discretion. Expertise. <em>Results.</em></h2>
    </div>
    {pillars()}
  </div>
</section>

<section class="section tight" id="questions">
  <div class="wrap">
    <div class="section-head">
      <div class="section-mark caps"><b>VI.</b>Questions</div>
      <h2 data-reveal>Good questions, <em>plainly answered.</em></h2>
    </div>
    {faq()}
  </div>
</section>
{invite()}'''

page("index.html", f"{BRAND} — Private Property Search in Prime London",
     "Crownsmere Estate is a private, by-request property service in prime London. Share your brief and Alaa Qadir searches personally, on and off the market.",
     index_body, INTRO, extra_ld=[FAQ_LD])

# ---------------------------------------------------------------- services
def svc(num, title, anchor, lede, points):
    lis = "".join(f"<li>{p}</li>" for p in points)
    return f'''<article class="service" id="{anchor}" data-reveal>
      <span class="num">{num}</span>
      <div><h2>{title}</h2><p class="lede">{lede}</p><ul>{lis}</ul></div>
    </article>'''

process_grid = "".join(f'<div data-reveal><span class="n">{i + 1:02d}</span><h3>{t}</h3>{ic(icn)}<p>{d}</p></div>' for i, (icn, t, d) in enumerate(PROCESS))
subnav = "".join(f'<a href="#{a}" class="caps">{t}</a>' for n, t, a, d in SERVICES) + '<a href="#process" class="caps">How it works</a>'

services_body = f'''
<section class="page-hero">
  <div class="wrap">
    <div class="eyebrow caps">Services</div>
    <div class="row">
      <h1><span class="line"><span>By request.</span></span><span class="line"><span><em>Personally found.</em></span></span></h1>
      {LOGO()}
    </div>
    <p class="lede" data-reveal>There is no shop window here. Every engagement begins with your brief, and every search is carried out personally, with complete discretion.</p>
  </div>
</section>

<nav class="subnav" aria-label="Services"><div class="wrap">{subnav}</div></nav>

<section class="section tight services-list">
  <div class="wrap">
    {svc("01", "Buy", "buy", "Tell me what you are looking for, and I will find it: on the market, off the market, or not yet on anyone&rsquo;s radar.", ["A private briefing on your requirements", "A personal search, on and off the market", "Access to homes that are never advertised", "A curated shortlist, checked before you see it", "Accompanied private viewings", "Negotiation and support through to completion"])}
    {svc("02", "Sell", "sell", "A quiet, private sale. Your property is introduced only to qualified buyers, without the noise of a public listing.", ["A confidential conversation about your plans", "Valuation advice and pricing strategy", "Discreet introductions to qualified buyers", "No public listing unless you wish it", "Viewings strictly by appointment", "Negotiation and sale progression"])}
    {svc("03", "Let", "let", "Whether you are looking for a home to rent or the right tenant for your property, the search is personal and discreet.", ["A search for the right rental home, to your brief", "Or the right tenant for your property", "Careful matching, not volume", "Private, by-appointment viewings", "Negotiation of terms", "Clear communication throughout"])}
    {svc("04", "Invest", "invest", "Investment opportunities sourced to your criteria, including those that never reach the open market.", ["Opportunities sourced to your brief", "Access to off-market investments", "Neighbourhood-level analysis", "Assessment of yield and growth potential", "Review of existing holdings", "A long-term strategy around your goals"])}
    {svc("05", "Advisory", "advisory", "Independent, impartial advice whenever you need a trusted perspective.", ["Impartial second opinions", "Guidance on timing, pricing and positioning", "Advice on offers and options", "Straightforward, objective insight", "Support for complex or sensitive situations", "Complete confidentiality"])}
  </div>
</section>

<section class="section tight" id="process">
  <div class="wrap">
    <div class="section-head">
      <div class="section-mark caps"><b>&mdash;</b>How It Works</div>
      <div><h2 data-reveal>From your brief <em>to the keys.</em></h2><p class="lede" data-reveal>A private, unhurried process, shaped entirely around you.</p></div>
    </div>
    <figure class="market-media reveal-img" data-reveal>
      <div class="frame">{pic("interior", "An elegant London drawing room with a marble fireplace and tall windows", 826, 463)}</div>
      <figcaption>Only what fits your brief.</figcaption>
    </figure>
    <div class="market-steps three">{process_grid}</div>
  </div>
</section>
{invite("Shall we <em>begin?</em>")}'''

page("services.html", f"Services — {BRAND}",
     "A personal, by-request service for buying, selling privately, letting, investing and independent advice in prime London.",
     services_body)

# ---------------------------------------------------------------- about
expect = "".join(f'<div data-reveal>{ic(i)}<span class="caps">{t}</span><p>{d}</p></div>' for i, t, d in EXPECT)

about_body = f'''
<section class="page-hero">
  <div class="wrap">
    <div class="eyebrow caps">About</div>
    <div class="row">
      <h1><span class="line"><span>Why</span></span><span class="line"><span><em>Crownsmere.</em></span></span></h1>
      {LOGO()}
    </div>
    <p class="lede" data-reveal>A personal, discreet and one-to-one property service, built around the client rather than the listing.</p>
  </div>
</section>

<section class="section tight">
  <div class="wrap">
    <div class="statement">
      {statement_figure("Alaa Qadir &middot; Individual Property Consultant")}
      <div class="copy">
        <p class="lede dropcap" data-reveal>As an independent consultant, I work exclusively for you. My clients come to me with a request, and my role is simple: to find what they are looking for, and to look after their interests at every step.</p>
        <div class="cols" data-reveal>
          <p>Property is about people, not just buildings. I take on a small number of clients so that each one receives my full attention, honest advice and a search shaped entirely around them.</p>
          <p>You will never be passed between departments or shown a property simply because it needs selling. From the first conversation to the final signature, you deal directly with me, in complete confidence.</p>
        </div>
        <div class="signature" data-reveal><b>Alaa Qadir</b><span class="caps">Founder &middot; {BRAND}</span></div>
      </div>
    </div>
  </div>
</section>

<section class="section tight">
  <div class="wrap">
    <div class="section-head">
      <div class="section-mark caps"><b>&mdash;</b>The Crownsmere Difference</div>
      <h2 data-reveal>A more personal approach. <em>Better guided decisions.</em></h2>
    </div>
    {pillars()}
  </div>
</section>

<section class="section tight">
  <div class="wrap">
    <div class="section-head">
      <div class="section-mark caps"><b>&mdash;</b>What You Can Expect</div>
      <h2 data-reveal>Four promises, <em>kept every time.</em></h2>
    </div>
    <div class="rules">{expect}</div>
  </div>
</section>

{band("People. Property. <em>Perspective.</em>", "A more personal London")}
{invite()}'''

page("about.html", f"About — {BRAND}",
     "Why Crownsmere: a personal, by-request property service in prime London. Personal representation, off-market access and skilled negotiation from Alaa Qadir.",
     about_body)

# ---------------------------------------------------------------- contact
def choice(name, val, checked=False, required=False):
    return f'<label class="choice"><input type="radio" name="{name}" value="{val}"{" checked" if checked else ""}{" required" if required else ""}><span>{val}</span></label>'

def options(vals):
    return "".join(f"<option>{v}</option>" for v in vals)

def step_actions(n, last=False):
    back = '<button type="button" class="btn btn-quiet caps" data-back>&larr; Back</button>' if n > 1 else '<span></span>'
    nxt = ('<button class="btn btn-gold caps" type="submit">Send my brief <span aria-hidden="true">&rarr;</span></button>' if last
           else '<button type="button" class="btn btn-gold caps" data-next>Continue <span aria-hidden="true">&rarr;</span></button>')
    return f'<div class="step-actions">{back}{nxt}</div>'

contact_body = f'''
<section class="page-hero">
  <div class="wrap">
    <div class="eyebrow caps">Contact</div>
    <div class="row">
      <h1><span class="line"><span>Share</span></span><span class="line"><span><em>your brief.</em></span></span></h1>
      {LOGO()}
    </div>
  </div>
</section>

<section class="section tight">
  <div class="wrap letter-wrap">
    <div class="details">
      <p class="lede" style="font-size:clamp(22px,2vw,30px);color:var(--ink-soft)">Tell me what you are looking for, in as much or as little detail as you like. I will be in touch personally, in complete confidence, by telephone or email as you prefer.</p>
      <dl>
        <div><dt class="caps">Telephone</dt><dd>Shared personally<br><em>once your brief is received.</em></dd></div>
        <div><dt class="caps">Email</dt><dd><a href="mailto:{EMAIL}">{EMAIL}</a></dd></div>
        <div><dt class="caps">Location</dt><dd>London, United Kingdom</dd></div>
        <div><dt class="caps">Consultations</dt><dd>By appointment</dd></div>
      </dl>
    </div>

    <div class="letter" id="brief" data-reveal>
      <div class="letter-head">
        {LOGO()}
        <div class="caps">{BRAND} &nbsp;&middot;&nbsp; London</div>
        <p class="display" style="margin:0">A private brief</p>
      </div>
      <form class="letter-form" data-endpoint="https://formsubmit.co/ajax/{EMAIL}" novalidate>
        <input type="hidden" name="_subject" value="[Crownsmere Enquiry] New client brief from the website">
        <input type="hidden" name="_template" value="table">
        <input type="hidden" name="_captcha" value="false">
        <input type="hidden" name="source" value="crownsmere.com/contact">
        <div class="hp" aria-hidden="true"><label for="f-hp">Leave this empty</label><input id="f-hp" type="text" name="_honey" tabindex="-1" autocomplete="off"></div>

        <ol class="steps-nav caps" aria-hidden="true"><li class="on">Request</li><li>Brief</li><li>Details</li></ol>
        <p class="step-count caps" aria-live="polite"></p>

        <div class="step" data-step="1">
          <h3 class="step-title" tabindex="-1">What can I help you with?</h3>
          <fieldset class="field choices">
            <legend class="caps">I am looking to</legend>
            {choice("request", "Buy a home", required=True)}{choice("request", "Rent a home")}{choice("request", "Sell privately")}{choice("request", "Let my property")}{choice("request", "Invest")}{choice("request", "Seek advice")}
          </fieldset>
          <div class="field"><label class="caps" for="f-when">Timeframe <span class="opt">(optional)</span></label><select id="f-when" name="timeframe">{options(["Not specified", "As soon as possible", "Within 3 months", "3 to 6 months", "6 to 12 months", "When the right property appears"])}</select></div>
          {step_actions(1)}
        </div>

        <div class="step" data-step="2">
          <h3 class="step-title" tabindex="-1">Tell me about it.</h3>
          <div class="field"><label class="caps" for="f-brief">Your brief <span class="opt">(optional)</span></label><textarea id="f-brief" name="brief" rows="4" maxlength="3000" placeholder="The kind of property, size, must-haves, anything that matters to you"></textarea></div>
          <div class="field-row">
            <div class="field"><label class="caps" for="f-area">Preferred areas <span class="opt">(optional)</span></label><input id="f-area" name="areas" placeholder="e.g. Belgravia, Chelsea"></div>
            <div class="field"><label class="caps" for="f-budget">Budget or value <span class="opt">(optional)</span></label><select id="f-budget" name="budget_or_value">{options(["Prefer not to say", "Under &pound;1m", "&pound;1m to &pound;2.5m", "&pound;2.5m to &pound;5m", "&pound;5m to &pound;10m", "Over &pound;10m", "Monthly rent (lettings)"])}</select></div>
          </div>
          {step_actions(2)}
        </div>

        <div class="step" data-step="3">
          <h3 class="step-title" tabindex="-1">How may I reach you?</h3>
          <div class="field"><label class="caps" for="f-name">Full name</label><input id="f-name" name="name" autocomplete="name" required></div>
          <div class="field-row">
            <div class="field"><label class="caps" for="f-email">Email address</label><input id="f-email" type="email" name="email" autocomplete="email" inputmode="email" required></div>
            <div class="field"><label class="caps" for="f-tel">Telephone</label><input id="f-tel" type="tel" name="phone" autocomplete="tel" inputmode="tel" placeholder="+44" required></div>
          </div>
          <fieldset class="field choices">
            <legend class="caps">Please contact me by</legend>
            {choice("preferred_contact", "Telephone")}{choice("preferred_contact", "Email")}{choice("preferred_contact", "Either", checked=True)}
          </fieldset>
          <div class="field"><label class="caps" for="f-time">Best time to call</label><select id="f-time" name="best_time">{options(["Any time", "Morning", "Afternoon", "Evening"])}</select></div>
          <label class="consent"><input type="checkbox" name="consent" value="Yes" required><span>I am happy for {BRAND} to contact me by telephone and email about this request. My details will be held in confidence and never shared. See the <a href="privacy.html">privacy notice</a>.</span></label>
          {step_actions(3, last=True)}
        </div>

        <div class="sent-panel" tabindex="-1">
          <p class="display">Thank you.</p>
        </div>
        <p class="form-status" role="status" aria-live="polite"></p>
      </form>
    </div>
  </div>
</section>

<section class="section tight" id="questions">
  <div class="wrap">
    <div class="section-head">
      <div class="section-mark caps"><b>&mdash;</b>Questions</div>
      <h2 data-reveal>Before you <em>get in touch.</em></h2>
    </div>
    {faq([FAQ[0], FAQ[6], FAQ[5], FAQ[7]])}
  </div>
</section>'''

page("contact.html", f"Contact — {BRAND}",
     "Share your property brief with Crownsmere Estate. A private, by-request search for buying, renting, selling privately and investing in prime London.",
     contact_body)

# ---------------------------------------------------------------- privacy
privacy_body = f'''
<section class="page-hero compact">
  <div class="wrap">
    <div class="eyebrow caps">Privacy notice</div>
    <h1><span class="line"><span>Your privacy,</span></span><span class="line"><span><em>respected.</em></span></span></h1>
    <p class="lede" data-reveal>Discretion is at the heart of what I do. This notice explains, plainly, what happens to the information you share with {BRAND}.</p>
  </div>
</section>

<section class="section tight">
  <div class="wrap prose">
    <p class="caps updated">Last updated {UPDATED}</p>

    <h2>Who I am</h2>
    <p>{BRAND} is an independent property consultancy run by Alaa Qadir in London, United Kingdom. For the purposes of UK data protection law, {BRAND} is the controller of the personal information described here. You can contact me about privacy at any time at <a href="mailto:{EMAIL}">{EMAIL}</a>.</p>

    <h2>What I collect</h2>
    <p>Only what you choose to share: your name, email address and telephone number, how and when you prefer to be contacted, and the details of your request (for example the kind of property you are looking for, preferred areas, budget and timeframe). If you write to me or call, I also keep that correspondence.</p>

    <h2>How I use it</h2>
    <ul>
      <li>To reply to your enquiry and discuss your brief.</li>
      <li>To carry out the search or other services you ask me to provide.</li>
      <li>To keep a record of our correspondence.</li>
    </ul>
    <p>I rely on your request for me to act before any agreement is made, my legitimate interest in responding to enquiries, and, where you give it on the contact form, your consent to be contacted. I never use your details for unrelated marketing, and I never sell them.</p>

    <h2>Who helps me</h2>
    <p>A small number of trusted service providers process information on my behalf, only to provide their service:</p>
    <ul>
      <li><strong>FormSubmit</strong> delivers messages sent through the contact form to my inbox.</li>
      <li><strong>My email hosting provider</strong> stores the emails you send me.</li>
      <li><strong>Anthropic</strong> provides the AI service that screens emails sent to {EMAIL}, so that spam is filtered out and genuine enquiries reach me promptly. Emails are processed for this purpose only.</li>
    </ul>
    <p>Some of these providers are based outside the UK, including in the United States. Where that is the case, information is transferred with appropriate safeguards in place. With your agreement, I may also share relevant details with others involved in your matter, such as solicitors or agents, when that is needed to help you.</p>

    <h2>How long I keep it</h2>
    <p>I keep your information only for as long as it is needed for the purposes above, including any legal, accounting or regulatory requirements, and then delete it securely.</p>

    <h2>Your rights</h2>
    <p>You can ask to see the information I hold about you, to correct it, to delete it, to restrict or object to its use, or to receive a copy of it. Where I rely on your consent, you can withdraw it at any time. Just email <a href="mailto:{EMAIL}">{EMAIL}</a>. If you are unhappy with how your information has been handled, you can complain to the Information Commissioner&rsquo;s Office at <a href="https://ico.org.uk" rel="noopener">ico.org.uk</a>.</p>

    <h2>Cookies</h2>
    <p>This website does not use cookies, analytics or advertising trackers. It remembers, for the length of your visit only, that you have seen the opening animation, so that it does not play on every page. Fonts and images are served from this website itself.</p>

    <h2>Changes</h2>
    <p>If this notice changes, the updated version will be published on this page with a new date.</p>
  </div>
</section>'''

page("privacy.html", f"Privacy Notice — {BRAND}",
     "How Crownsmere Estate collects, uses and protects the information you share.",
     privacy_body)

# ---------------------------------------------------------------- 404
notfound_body = f'''
<section class="page-hero notfound">
  <div class="wrap">
    <div class="eyebrow caps">Page not found</div>
    <h1><span class="line"><span>This page has gone</span></span><span class="line"><span><em>off-market.</em></span></span></h1>
    <p class="lede" data-reveal>The page you were looking for is not here, but the right property may well be. Let me help you find it.</p>
    <div class="btn-row" data-reveal style="margin-top:44px">
      <a class="btn btn-gold caps" href="index.html">Return home <span aria-hidden="true">&rarr;</span></a>
      <a class="btn caps" href="contact.html">Share your brief</a>
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
pages = [("", "1.0"), ("services.html", "0.9"), ("about.html", "0.8"), ("contact.html", "0.9"), ("privacy.html", "0.3")]
sitemap = '<?xml version="1.0" encoding="UTF-8"?>\n<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">\n' + "".join(
    f"  <url><loc>{SITE}/{p}</loc><lastmod>{UPDATED_ISO}</lastmod><priority>{pr}</priority></url>\n" for p, pr in pages) + "</urlset>\n"
open(os.path.join(OUT, "sitemap.xml"), "w").write(sitemap)
open(os.path.join(OUT, "robots.txt"), "w").write(f"User-agent: *\nAllow: /\n\nSitemap: {SITE}/sitemap.xml\n")
manifest = {
    "name": BRAND, "short_name": "Crownsmere", "description": "Private property search in prime London.",
    "start_url": "/", "display": "browser", "background_color": "#f6f2ea", "theme_color": "#0e1b2e",
    "icons": [{"src": "/assets/img/apple-touch-icon.png", "sizes": "180x180", "type": "image/png"},
              {"src": "/assets/img/icon-512.png", "sizes": "512x512", "type": "image/png"}],
}
open(os.path.join(OUT, "site.webmanifest"), "w").write(json.dumps(manifest, indent=2) + "\n")

print("built")
