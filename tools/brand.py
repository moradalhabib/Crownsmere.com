#!/usr/bin/env python3
"""Business card, digital card, contact file and email signature for Crownsmere Estate.

One command makes everything in brand/ (kept out of the website by _config.yml), from the site's own
logo, fonts and colours:

    PLAYWRIGHT_BROWSERS_PATH=/opt/pw-browsers python3 tools/brand.py    # any Playwright Chromium

It writes the pages into brand/.build/, tools/brand-render.cjs draws them, and tools/brand_print.py makes
the CMYK print files, checks them (brand/crownsmere-business-card-preflight.txt) and draws the proof.
Tools it needs are listed in README.md.

Alaa's own email and mobile number (PERSON) go on the card, the signature and the contact file; the
rest is only what the website already states. Change a detail in PERSON and run it again.
"""
import base64, html, io, math, os, subprocess, sys

import numpy as np
import segno
from PIL import Image, ImageFilter

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
OUT = os.path.join(ROOT, "brand")
BUILD = os.path.join(OUT, ".build")    # pages, fonts and drafts the files are made from; not committed

SITE = "https://crownsmere.com/"
SITE_SHORT = "crownsmere.com"
BRAND = "Crownsmere Estate"
# Alaa's direct details, from the owner (October 2026). The website itself keeps hello@crownsmere.com.
PERSON = {"first": "Alaa", "last": "Qadir", "title": "Senior Property Consultant",
          "email": "alaa.qadir@crownsmere.com", "phone": "+44 7384 190760"}
TAGLINE = ("London property,", "personally handled.")      # the home page's heading
LINE = "Private property search · Prime London"            # the sharing image's strap line
# The signature's logo is fetched from the live site when an email is opened, so this file must stay online.
# The live site check (.github/workflows/site-check.yml) fails if it ever goes missing.
SIGNATURE_LOGO = SITE + "assets/img/monogram-sm.png"

NAVY, INK2, INK3 = "#0e1b2e", "#4a5263", "#5c6270"
GOLD, GOLD_INK, CREAM = "#b08d57", "#80612f", "#faf7f1"

e = html.escape
name = f'{PERSON["first"]} {PERSON["last"]}'


def write(fname, text):
    with open(os.path.join(OUT, fname), "w", encoding="utf-8", newline="") as f:
        f.write(text)


def qr_svg():
    # Medium error correction keeps the code to 25 x 25 modules: 0.68 mm each at 17 mm, which phones
    # read easily. The card keeps at least four modules of plain background around it (the standard's quiet zone).
    return segno.make(SITE, error="m").svg_inline(dark=NAVY, light=None, border=0, omitsize=True)


# The site's fonts are variable (any weight). Printed from those, Chromium embeds them in the PDF as
# Type 3 fonts, which some printers' file checks reject. So the card pages use fixed-weight copies,
# made into brand/.build/ (not committed, and not published).
STATIC = [("Inter", "normal", 400, "inter-latin"), ("Inter", "normal", 500, "inter-latin"),
          ("Cormorant Garamond", "normal", 400, "cormorant-garamond"),
          ("Cormorant Garamond", "normal", 500, "cormorant-garamond"),
          ("Cormorant Garamond", "italic", 400, "cormorant-garamond-italic"),
          ("Cinzel", "normal", 500, "cinzel")]


def static_fonts():
    from fontTools.ttLib import TTFont
    from fontTools.varLib import instancer
    os.makedirs(os.path.join(BUILD, "fonts"), exist_ok=True)
    for _, _, weight, src in STATIC:
        font = instancer.instantiateVariableFont(TTFont(os.path.join(ROOT, "assets/fonts", src + ".woff2")), {"wght": weight})
        font.flavor = None
        font.save(os.path.join(BUILD, "fonts", f"{src}-{weight}.ttf"))


def front_gradient():
    """The front's soft light, drawn here as a 300 dpi image (91 x 61 mm) rather than a CSS gradient:
    converting a vector gradient to CMYK, Ghostscript turns it into a coarse 90 ppi image, which can band
    on press. A light dither (under one level of 256) keeps the steps from showing."""
    w, h = math.ceil(91 / 25.4 * 300), math.ceil(61 / 25.4 * 300)   # rounded up, so never under 300 dpi
    yy, xx = np.mgrid[0:h, 0:w].astype(float)
    # An ellipse 125% x 95% of the card, centred halfway across and 40% down (as CSS radial-gradient sizes it)
    t = np.clip(np.hypot((xx + 0.5 - w * 0.5) / (w * 1.25), (yy + 0.5 - h * 0.4) / (h * 0.95)), 0, 1)
    stops = [(0.0, "#172b46"), (0.58, NAVY), (1.0, "#0b1727")]
    rgb = np.zeros((h, w, 3))
    for (t0, c0), (t1, c1) in zip(stops, stops[1:]):
        a = np.array([int(c0[i:i + 2], 16) for i in (1, 3, 5)], float)
        b = np.array([int(c1[i:i + 2], 16) for i in (1, 3, 5)], float)
        k = ((t - t0) / (t1 - t0))[..., None]
        rgb = np.where(((t >= t0) & (t <= t1))[..., None], a + (b - a) * np.clip(k, 0, 1), rgb)
    rng = np.random.default_rng(39)
    rgb += rng.random(rgb.shape) + rng.random(rgb.shape) - 1   # triangular dither
    Image.fromarray(np.clip(np.round(rgb), 0, 255).astype(np.uint8)).save(os.path.join(BUILD, "front-gradient.png"))


def monogram_assets():
    """The logo, cropped tight to its edges so it lines up exactly with the type (the site's file has a
    transparent margin on the right and at the top), and its outline as vector shapes for the gold-foil
    layer, traced with potrace from the logo's transparency at 8 times its size. The trace matches the
    original outline to 99.3 per cent; brand/monogram-vector.svg keeps it for other print work."""
    src = Image.open(os.path.join(ROOT, "assets/img/monogram.png")).convert("RGBA")
    tight = src.crop(src.getchannel("A").point(lambda v: 255 if v > 8 else 0).getbbox())
    tight.save(os.path.join(BUILD, "monogram-tight.png"))
    scale, pad = 8, 4
    alpha = Image.new("L", (tight.width + 2 * pad, tight.height + 2 * pad), 0)
    alpha.paste(tight.getchannel("A"), (pad, pad))
    big = alpha.resize((alpha.width * scale, alpha.height * scale), Image.LANCZOS)
    big = big.filter(ImageFilter.GaussianBlur(scale * 0.7))
    big.point(lambda v: 0 if v >= 128 else 255, "1").save(os.path.join(BUILD, "monogram.pbm"))
    subprocess.run(["potrace", os.path.join(BUILD, "monogram.pbm"), "-s", "--flat", "-t", "40", "-a", "1.2",
                    "-O", "1.0", "-o", os.path.join(BUILD, "monogram-trace.svg")], check=True)
    svg = open(os.path.join(BUILD, "monogram-trace.svg")).read()
    body = svg[svg.index("<g"):svg.rindex("</svg>")]
    w, h = tight.width * scale, tight.height * scale
    view = f"{pad * scale} {pad * scale} {w} {h}"   # the padding stays outside the drawing
    with open(os.path.join(OUT, "monogram-vector.svg"), "w") as f:
        f.write(f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="{view}" width="{w / 100:.2f}mm" height="{h / 100:.2f}mm">\n'
                f"<title>{BRAND} monogram (outline traced from the website logo)</title>\n{body}</svg>\n")
    return view, body


_logo = Image.open(os.path.join(ROOT, "assets/img/monogram.png")).convert("RGBA")
_box = _logo.getchannel("A").point(lambda v: 255 if v > 8 else 0).getbbox()
MONO_RATIO = (_box[2] - _box[0]) / (_box[3] - _box[1])   # width over height of the logo itself
MONO_VIEW, MONO_BODY = "", ""   # the traced outline, set by main() before any card is written

# Measured from the monogram's opaque middle tones, so the lettering is the logo's own gold.
GOLD_ON_NAVY = "#dfb86e"
PRINT_ZOOM = 8

FONTS = "".join(f'@font-face {{ font-family: "{family}"; font-style: {style}; font-weight: {weight}; '
                f'src: url("fonts/{src}-{weight}.ttf") format("truetype"); }}\n'
                for family, style, weight, src in STATIC)

# UK business card: 85 x 55 mm trimmed, with 3 mm bleed on every side (91 x 61 mm). Nothing that matters
# comes closer than 4 mm to the trim: .safe starts 7 mm from the edge of the bleed. No text is smaller than
# 6 pt. Lengths in the back's layout come from measuring the rendered type, so the lines meet exactly:
# the top of the name's tallest letter and the top of the monogram on the safe line, and the tagline's
# baseline level with the foot of the QR code, 1.2 mm above the safe line so its descenders stay inside it.
CARD_CSS = FONTS + f"""
* {{ box-sizing: border-box; }}
html, body {{ margin: 0; padding: 0; }}
body {{ -webkit-print-color-adjust: exact; print-color-adjust: exact; font-kerning: normal; text-rendering: geometricPrecision; }}
p {{ margin: 0; }}
.card {{ position: relative; width: 91mm; height: 61mm; overflow: hidden; }}
.safe {{ position: absolute; top: 7mm; right: 7mm; bottom: 7mm; left: 7mm; }}

/* Front: the monogram and wordmark, raised 1.2 mm above the true centre, where the eye reads the middle. */
.front {{ background: {NAVY} url("front-gradient.png") 0 0 / 100% 100% no-repeat; }}
.front .safe {{ display: flex; flex-direction: column; align-items: center; justify-content: center; padding-bottom: 2.4mm; }}
.front .mono {{ display: block; height: 22mm; width: {22 * MONO_RATIO:.3f}mm; }}
.wm {{ margin-top: 3.9mm; padding-left: 0.2em; font: 500 13.5pt/1 "Cinzel", serif; letter-spacing: 0.2em; color: {GOLD_ON_NAVY}; }}
.est {{ display: flex; align-items: center; gap: 2.4mm; margin-top: 2.5mm; }}
/* Centred on the line, which is the middle of Inter's capitals (its cap middle sits within 0.001 em of the
   line's centre); the preflight measures it in the print file. */
.est i {{ display: block; width: 7mm; height: 0.2mm; background: {GOLD_ON_NAVY}; }}
.est span {{ padding-left: 0.55em; font: 500 6.5pt/1 "Inter", sans-serif; letter-spacing: 0.55em; color: {GOLD_ON_NAVY}; }}

/* Back */
.back {{ background: {CREAM}; color: {NAVY}; }}
.back .safe > * {{ position: absolute; }}
.name {{ left: var(--name-left, 0mm); top: var(--name-top, 0mm); font: 500 17.5pt/1 "Cormorant Garamond", serif; }}
.role {{ left: 0; top: var(--role-top, 8mm); font: 500 6pt/1 "Inter", sans-serif; letter-spacing: 0.18em; color: {GOLD_INK}; }}
.back .rule {{ left: 0; top: var(--rule-top, 13mm); display: block; width: 10mm; height: 0.25mm; background: {GOLD}; }}
.lines {{ left: 0; top: var(--lines-top, 17mm); font: 400 7.5pt/1.62 "Inter", sans-serif; color: {NAVY}; }}
.lines b {{ display: inline-block; width: 3.8mm; font: 500 6pt/1 "Inter", sans-serif; color: {GOLD_INK}; }}
.tag {{ left: 0; bottom: var(--tag-bottom, 0mm); font: 400 10pt/1 "Cormorant Garamond", serif; color: {INK2}; }}
.tag em {{ color: {GOLD_INK}; }}
.back .mono {{ right: 0; top: var(--mono-top, 0mm); display: block; height: 10.5mm; width: {10.5 * MONO_RATIO:.3f}mm; }}
.qr {{ right: 0; bottom: 1.2mm; display: block; width: 17mm; height: 17mm; }}

/* The gold-foil pair: "base" is the colour print with the foil areas left empty, "layer" the foil areas
   alone in solid black, for printers that foil. */
.layer .card {{ background: none; }}
.layer .card * {{ visibility: hidden; }}
.layer .foil, .layer .foil * {{ visibility: visible; color: #000; }}
.layer i.foil {{ background: #000; }}
.base .foil {{ visibility: hidden; }}
"""

# Positions on the back, in mm from the edges of the safe area, set from the ink measured in the print file
# (the preflight report shows it). The name moves 0.06 mm right because the serif foot of its A reaches past
# the type's left edge.
BACK_LAYOUT = {"--name-left": "0.06mm", "--name-top": "-0.49mm", "--role-top": "6.85mm", "--rule-top": "11.95mm",
               "--lines-top": "15.35mm", "--tag-bottom": "0.595mm", "--mono-top": "0mm"}


def monogram(mode):
    if mode == "layer":
        return (f'<svg class="mono foil" viewBox="{MONO_VIEW}" preserveAspectRatio="none" aria-hidden="true">'
                f'{MONO_BODY.replace("#000000", "#000")}</svg>')
    return '<img class="mono foil" src="monogram-tight.png" alt="">'


def front(mode="print"):
    return f'''<div class="card front"><div class="safe">
  {monogram(mode)}
  <p class="wm foil">CROWNSMERE</p>
  <p class="est"><i class="foil"></i><span class="foil">ESTATE</span><i class="foil"></i></p>
</div></div>'''


def back(mode="print"):
    # M(obile), E(mail), W(ebsite): the usual small labels on a UK card.
    rows = ([("M", PERSON["phone"])] if PERSON["phone"] else []) + [("E", PERSON["email"]), ("W", SITE_SHORT)]
    lines = "<br>".join(f"<b>{k}</b>{e(v)}" for k, v in rows)
    style = "; ".join(f"{k}: {v}" for k, v in BACK_LAYOUT.items())
    return f'''<div class="card back"><div class="safe" style="{style}">
  <p class="name">{e(name)}</p>
  <p class="role">{e(PERSON["title"]).upper()}</p>
  <i class="rule foil"></i>
  <p class="lines">{lines}</p>
  <p class="tag">{e(TAGLINE[0])} <em>{e(TAGLINE[1])}</em></p>
  {monogram(mode)}
  <div class="qr">{qr_svg()}</div>
</div></div>'''


def card_page(mode="print"):
    # Two pages, front then back, each 91 x 61 mm: the file a printer asks for.
    return f'''<!doctype html>
<html lang="en-GB"><head><meta charset="utf-8">
<title>{BRAND} business card ({mode}; 85 x 55 mm with 3 mm bleed)</title>
<style>{CARD_CSS}
/* Drawn 8 times larger for the PDF: Chromium snaps boxes (rules, images) to whole CSS pixels, 0.26 mm at
   full size but 0.03 mm at 8 times. tools/brand_print.py scales the pages back to 91 x 61 mm exactly. */
@page {{ size: {91 * PRINT_ZOOM}mm {61 * PRINT_ZOOM}mm; margin: 0; }}
@media print {{ html {{ zoom: {PRINT_ZOOM}; }} }}
.card {{ break-after: page; }}
.card:last-child {{ break-after: auto; }}
@media screen {{ body {{ background: #888; padding: 10mm; }} .card {{ margin-bottom: 8mm; }} }}
</style></head>
<body class="{mode}">
{front(mode)}
{back(mode)}
</body></html>
'''


def share_page():
    # Both sides, trimmed, side by side: an image to send by email, WhatsApp or LinkedIn.
    return f'''<!doctype html>
<html lang="en-GB"><head><meta charset="utf-8">
<title>{BRAND} digital card</title>
<style>{CARD_CSS}
body {{ width: 1600px; height: 640px; display: flex; align-items: center; justify-content: center; gap: 40px;
       background: radial-gradient(120% 140% at 50% 0%, #f2ebdf 0%, #e4d9c5 100%); }}
.trim {{ position: relative; width: 85mm; height: 55mm; overflow: hidden; zoom: 2.179; border-radius: 1mm;
        box-shadow: 0 0.3mm 0.8mm rgba(14, 27, 46, 0.14), 0 4mm 9mm -3mm rgba(14, 27, 46, 0.32); }}
.trim .card {{ position: absolute; left: -3mm; top: -3mm; }}
</style></head>
<body>
<div class="trim">{front()}</div>
<div class="trim">{back()}</div>
</body></html>
'''


def signature_html():
    """Tables and inline styles, because that is all email programs reliably keep. Georgia and Arial
    stand in for the site's fonts, which email programs do not load."""
    sans = "Arial, Helvetica, sans-serif"
    serif = "Georgia, 'Times New Roman', serif"
    p = f"margin: 0; font-family: {sans}; font-size: 13px; line-height: 19px; color: {NAVY};"
    a = f"color: {NAVY}; text-decoration: none;"
    bar = f'&nbsp;&nbsp;<span style="color: {GOLD};">|</span>&nbsp;&nbsp;'
    phone = (f'{bar}<a href="tel:{e(PERSON["phone"].replace(" ", ""))}" style="{a}">{e(PERSON["phone"])}</a>'
             if PERSON["phone"] else "")
    return f'''<table role="presentation" cellpadding="0" cellspacing="0" border="0" style="border-collapse: collapse;">
<tr>
<td valign="middle" style="padding: 0 16px 0 0;"><a href="{SITE}" style="text-decoration: none;"><img src="{SIGNATURE_LOGO}" width="40" height="63" alt="{BRAND}" style="display: block; border: 0; width: 40px; height: 63px;"></a></td>
<td valign="middle" style="padding: 0 0 0 16px; border-left: 1px solid {GOLD};">
<p style="margin: 0; font-family: {serif}; font-size: 19px; line-height: 24px; color: {NAVY};">{e(name)}</p>
<p style="margin: 2px 0 0; font-family: {sans}; font-size: 10px; line-height: 14px; letter-spacing: 1.5px; color: {GOLD_INK};">{e(PERSON["title"]).upper()}</p>
<p style="margin: 9px 0 0; font-family: {serif}; font-size: 13px; line-height: 19px; letter-spacing: 1.5px; color: {NAVY};">CROWNSMERE <span style="font-family: {sans}; font-size: 9px; letter-spacing: 2.5px; color: {GOLD_INK};">ESTATE</span></p>
<p style="{p}"><a href="mailto:{PERSON["email"]}" style="{a}">{PERSON["email"]}</a>{phone}</p>
<p style="{p}"><a href="{SITE}" style="{a}">{SITE_SHORT}</a></p>
<p style="margin: 3px 0 0; font-family: {serif}; font-size: 14px; line-height: 19px; font-style: italic; color: {GOLD_INK};">{e(" ".join(TAGLINE))}</p>
</td>
</tr>
</table>'''


def signature_text():
    rows = [name, PERSON["title"], BRAND, PERSON["email"]]
    if PERSON["phone"]:
        rows.append(PERSON["phone"])
    rows += [SITE_SHORT, " ".join(TAGLINE)]
    return "\n".join(rows) + "\n"


def signature_page(sig, text):
    return f'''<!doctype html>
<html lang="en-GB"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width, initial-scale=1">
<title>Email signature: {e(name)}, {BRAND}</title>
<style>
body {{ margin: 0; padding: 32px 20px 48px; background: {CREAM}; color: {NAVY}; font: 16px/1.55 Arial, Helvetica, sans-serif; }}
main {{ max-width: 720px; margin: 0 auto; }}
h1 {{ font: 500 30px/1.2 Georgia, serif; margin: 0 0 6px; }}
h2 {{ font: 600 13px/1.4 Arial, sans-serif; letter-spacing: 0.12em; text-transform: uppercase; color: {GOLD_INK}; margin: 36px 0 10px; }}
.lede {{ color: {INK2}; margin: 0 0 24px; }}
.box {{ background: #fff; border: 1px solid rgba(14, 27, 46, 0.12); border-radius: 10px; padding: 24px; overflow-x: auto; }}
button {{ margin-top: 14px; min-height: 44px; padding: 10px 20px; border: 0; border-radius: 6px; background: {NAVY}; color: #fff; font: 600 15px Arial, sans-serif; cursor: pointer; }}
.done {{ margin-left: 12px; color: #2d6a3e; font-weight: 600; }}
pre {{ margin: 0; font: 14px/1.6 Menlo, Consolas, monospace; white-space: pre-wrap; }}
ol {{ padding-left: 22px; }} li {{ margin: 4px 0; }}
.note {{ color: {INK2}; font-size: 14px; }}
</style></head>
<body><main>
<h1>Email signature</h1>
<p class="lede">For {e(name)}, {BRAND}. Copy it, then paste it into your email program's signature settings.</p>

<div class="box"><div id="sig">
{sig}
</div></div>
<button type="button" data-copy="sig">Copy signature</button><span class="done" id="sig-done" hidden>Copied</span>

<h2>Gmail (on a computer)</h2>
<ol>
<li>Open Gmail, click the gear icon, then <b>See all settings</b>.</li>
<li>On the <b>General</b> tab, scroll to <b>Signature</b> and click <b>Create new</b>. Name it "Crownsmere".</li>
<li>Click in the signature box and paste (Ctrl+V, or Cmd+V on a Mac).</li>
<li>Under <b>Signature defaults</b>, pick it for new emails and for replies.</li>
<li>Click <b>Save Changes</b> at the very bottom of the page.</li>
</ol>

<h2>Outlook (web and the new Outlook)</h2>
<ol>
<li>Open <b>Settings</b>, then <b>Account</b> (or <b>Accounts</b>), then <b>Signatures</b>.</li>
<li>Click <b>New signature</b>, name it "Crownsmere" and paste into the box.</li>
<li>Choose it as the default for new messages and replies, then <b>Save</b>.</li>
</ol>

<h2>Apple Mail (Mac)</h2>
<ol>
<li>Open this page in Safari and click <b>Copy signature</b>.</li>
<li>In Mail, open <b>Settings</b>, then <b>Signatures</b>, choose the account and click <b>+</b>.</li>
<li>Untick <b>Always match my default message font</b>, then paste into the right-hand box.</li>
</ol>

<h2>iPhone and iPad</h2>
<p class="note">The iPhone's Mail signature setting keeps only plain text, so use this version there:
Settings, Apps, Mail, Signature.</p>
<div class="box"><pre id="txt">{e(text)}</pre></div>
<button type="button" data-copy="txt">Copy plain text</button><span class="done" id="txt-done" hidden>Copied</span>

<p class="note">The logo in the signature is loaded from {SITE_SHORT} each time an email is opened. Some
email programs hide pictures until the reader allows them; the text still shows.</p>
</main>
<script>
document.querySelectorAll("[data-copy]").forEach(function (b) {{
  b.addEventListener("click", async function () {{
    var el = document.getElementById(b.dataset.copy), done = document.getElementById(b.dataset.copy + "-done");
    var rich = b.dataset.copy === "sig";
    try {{
      var items = {{ "text/plain": new Blob([el.innerText], {{ type: "text/plain" }}) }};
      if (rich) items["text/html"] = new Blob([el.innerHTML], {{ type: "text/html" }});
      await navigator.clipboard.write([new ClipboardItem(items)]);
    }} catch (err) {{
      // Older browsers, or a page opened from a file: copy the selection instead.
      var r = document.createRange(); r.selectNodeContents(el);
      var s = getSelection(); s.removeAllRanges(); s.addRange(r);
      document.execCommand("copy"); s.removeAllRanges();
    }}
    done.hidden = false; setTimeout(function () {{ done.hidden = true; }}, 2500);
  }});
}});
</script>
</body></html>
'''


def vcard():
    """vCard 3.0, which every phone and email program reads. The contact photo is the monogram on navy."""
    logo = Image.open(os.path.join(ROOT, "assets/img/monogram.png")).convert("RGBA")
    size = 480
    photo = Image.new("RGB", (size, size), NAVY)
    h = int(size * 0.66)
    logo = logo.resize((round(logo.width * h / logo.height), h), Image.LANCZOS)
    photo.paste(logo, ((size - logo.width) // 2, (size - h) // 2), logo)
    buf = io.BytesIO()
    photo.save(buf, "JPEG", quality=86, optimize=True)
    b64 = base64.b64encode(buf.getvalue()).decode()

    def esc(s):
        return s.replace("\\", "\\\\").replace(",", "\\,").replace(";", "\\;")

    rows = ["BEGIN:VCARD", "VERSION:3.0",
            f'N:{esc(PERSON["last"])};{esc(PERSON["first"])};;;', f"FN:{esc(name)}",
            f"ORG:{esc(BRAND)}", f'TITLE:{esc(PERSON["title"])}',
            f'EMAIL;TYPE=INTERNET,WORK:{PERSON["email"]}', f"URL:{SITE}"]
    if PERSON["phone"]:
        rows.append(f'TEL;TYPE=CELL,VOICE:{PERSON["phone"].replace(" ", "")}')
    rows += [f"NOTE:{esc(LINE)}", f"PHOTO;ENCODING=b;TYPE=JPEG:{b64}", "END:VCARD"]

    def fold(line):
        # Lines longer than 75 characters continue on the next line after a single space (RFC 2425).
        out = [line[:75]]
        line = line[75:]
        while line:
            out.append(" " + line[:74])
            line = line[74:]
        return "\r\n".join(out)

    return "\r\n".join(fold(r) for r in rows) + "\r\n"


def write_build(fname, text):
    with open(os.path.join(BUILD, fname), "w", encoding="utf-8") as f:
        f.write(text)


def main():
    global MONO_VIEW, MONO_BODY
    os.makedirs(BUILD, exist_ok=True)
    static_fonts()
    front_gradient()
    MONO_VIEW, MONO_BODY = monogram_assets()
    for mode in ("print", "base", "layer"):
        write_build(f"card-{mode}.html", card_page(mode))
    write_build("share-card.html", share_page())
    sig, text = signature_html(), signature_text()
    write("email-signature.html", signature_page(sig, text))
    write("email-signature-snippet.html", sig + "\n")
    write("email-signature.txt", text)
    write(f'{PERSON["first"].lower()}-{PERSON["last"].lower()}.vcf', vcard())
    # Draw the pages in Chromium, then make the print files from them and check them.
    subprocess.run(["node", os.path.join(ROOT, "tools/brand-render.cjs")], check=True)
    sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
    import brand_print
    brand_print.finish()


if __name__ == "__main__":
    main()
