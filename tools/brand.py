#!/usr/bin/env python3
"""Business card, digital card, contact file and email signature for Crownsmere Estate.

Writes everything into brand/ (kept out of the website by _config.yml). The pages use the site's own
logo, fonts and colours. Then tools/brand-render.cjs turns the card pages into the print PDF and the
PNG images.

    pip install segno fonttools brotli    # once: QR codes, and fixed-weight fonts for the print file
    python3 tools/brand.py
    PLAYWRIGHT_BROWSERS_PATH=/opt/pw-browsers node tools/brand-render.cjs   # any Playwright Chromium

Alaa's own email and mobile number (PERSON) go on the card, the signature and the contact file; the
rest is only what the website already states. Change a detail in PERSON and run both steps again.
"""
import base64, html, io, os

import segno
from PIL import Image

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
OUT = os.path.join(ROOT, "brand")

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
    # Medium error correction keeps the code to 25 x 25 modules, which scans easily at 17 mm.
    return segno.make(SITE, error="m").svg_inline(dark=NAVY, light=None, border=0, omitsize=True)


# The site's fonts are variable (any weight). Printed from those, Chromium embeds them in the PDF as
# Type 3 fonts, which some printers' file checks reject. So the card pages use fixed-weight copies,
# made here into brand/.fonts/ (not committed, and not published).
STATIC = [("Inter", "normal", 400, "inter-latin"), ("Inter", "normal", 500, "inter-latin"),
          ("Cormorant Garamond", "normal", 400, "cormorant-garamond"),
          ("Cormorant Garamond", "normal", 500, "cormorant-garamond"),
          ("Cormorant Garamond", "italic", 400, "cormorant-garamond-italic"),
          ("Cinzel", "normal", 500, "cinzel")]


def static_fonts():
    from fontTools.ttLib import TTFont
    from fontTools.varLib import instancer
    os.makedirs(os.path.join(OUT, ".fonts"), exist_ok=True)
    for _, _, weight, src in STATIC:
        font = instancer.instantiateVariableFont(TTFont(os.path.join(ROOT, "assets/fonts", src + ".woff2")), {"wght": weight})
        font.flavor = None
        font.save(os.path.join(OUT, ".fonts", f"{src}-{weight}.ttf"))


FONTS = "".join(f'@font-face {{ font-family: "{family}"; font-style: {style}; font-weight: {weight}; '
                f'src: url(".fonts/{src}-{weight}.ttf") format("truetype"); }}\n'
                for family, style, weight, src in STATIC)

# UK business card: 85 x 55 mm trimmed, with 3 mm bleed on every side (91 x 61 mm), and nothing that
# matters closer than 4 mm to the trim (the .safe box starts 7 mm from the bleed edge).
CARD_CSS = FONTS + f"""
* {{ box-sizing: border-box; }}
html, body {{ margin: 0; padding: 0; }}
body {{ -webkit-print-color-adjust: exact; print-color-adjust: exact; }}
.card {{ position: relative; width: 91mm; height: 61mm; overflow: hidden; }}
.safe {{ position: absolute; top: 7mm; right: 7mm; bottom: 7mm; left: 7mm; }}

.front {{ background: radial-gradient(120% 95% at 50% 36%, #182c47 0%, {NAVY} 64%); }}
.front .safe {{ display: flex; flex-direction: column; align-items: center; justify-content: center; }}
.front img {{ display: block; height: 21mm; width: auto; }}
.wm {{ margin: 3.4mm 0 0; padding-left: 0.16em; font: 500 12.5pt/1 "Cinzel", serif; letter-spacing: 0.16em; color: #ecd6aa; }}
.wm-sub {{ margin: 1.8mm 0 0; padding-left: 0.52em; font: 500 5.2pt/1 "Inter", sans-serif; letter-spacing: 0.52em; color: #c4a46e; }}

.back {{ background: {CREAM}; color: {NAVY}; }}
.back .safe {{ display: flex; justify-content: space-between; }}
.who {{ display: flex; flex-direction: column; justify-content: space-between; }}
.name {{ margin: 0; font: 500 17pt/1 "Cormorant Garamond", serif; }}
.role {{ margin: 1.7mm 0 0; font: 500 5.4pt/1 "Inter", sans-serif; letter-spacing: 0.16em; color: {GOLD_INK}; }}
.rule {{ width: 9mm; height: 0.25mm; margin: 3.4mm 0 3mm; background: {GOLD}; }}
.lines {{ margin: 0; font: 400 7pt/1.6 "Inter", sans-serif; color: {NAVY}; }}
.lines b {{ display: inline-block; width: 3.4mm; font: 500 5.2pt/1 "Inter", sans-serif; color: {GOLD_INK}; }}
.tag {{ margin: 0; font: 400 9.5pt/1.15 "Cormorant Garamond", serif; color: {INK2}; }}
.tag em {{ color: {GOLD_INK}; }}
.side {{ display: flex; flex-direction: column; align-items: flex-end; justify-content: space-between; }}
/* Negative right margins cancel the letter spacing after the last letter, so both lines end flush with the QR code. */
.brand {{ margin: 0 -0.92pt 0 0; text-align: right; font: 500 6.6pt/1 "Cinzel", serif; letter-spacing: 0.14em; color: {NAVY}; }}
.brand small {{ display: block; margin: 1.1mm -0.92pt 0 0; font: 500 4.4pt/1 "Inter", sans-serif; letter-spacing: 0.42em; color: {GOLD_INK}; }}
.qr {{ display: flex; flex-direction: column; align-items: center; }}
.qr svg {{ display: block; width: 17mm; height: 17mm; }}
/* 17 mm across 25 modules: the 2.8 mm gap keeps the four-module quiet zone the QR standard asks for. */
.qr p {{ margin: 2.8mm 0 0; font: 500 4.8pt/1 "Inter", sans-serif; letter-spacing: 0.14em; color: {INK3}; }}
"""


def front():
    return f'''<div class="card front"><div class="safe">
  <img src="../assets/img/monogram.png" alt="">
  <p class="wm">CROWNSMERE</p>
  <p class="wm-sub">ESTATE</p>
</div></div>'''


def back():
    # M(obile), E(mail), W(ebsite): the usual small labels on a UK card.
    rows = ([("M", PERSON["phone"])] if PERSON["phone"] else []) + [("E", PERSON["email"]), ("W", SITE_SHORT)]
    lines = [f"<b>{k}</b>{e(v)}" for k, v in rows]
    return f'''<div class="card back"><div class="safe">
  <div class="who">
    <div>
      <p class="name">{e(name)}</p>
      <p class="role">{e(PERSON["title"]).upper()}</p>
      <div class="rule"></div>
      <p class="lines">{"<br>".join(lines)}</p>
    </div>
    <p class="tag">{e(TAGLINE[0])} <em>{e(TAGLINE[1])}</em></p>
  </div>
  <div class="side">
    <p class="brand">CROWNSMERE<small>ESTATE</small></p>
    <div class="qr">{qr_svg()}<p>SCAN TO VISIT</p></div>
  </div>
</div></div>'''


def card_page():
    # Two pages, front then back, each 91 x 61 mm: the file a printer asks for.
    return f'''<!doctype html>
<html lang="en-GB"><head><meta charset="utf-8">
<title>{BRAND} business card (print, 85 x 55 mm with 3 mm bleed)</title>
<style>{CARD_CSS}
@page {{ size: 91mm 61mm; margin: 0; }}
.card {{ break-after: page; }}
.card:last-child {{ break-after: auto; }}
@media screen {{ body {{ background: #888; padding: 10mm; }} .card {{ margin-bottom: 8mm; }} }}
</style></head>
<body>
{front()}
{back()}
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


def main():
    os.makedirs(OUT, exist_ok=True)
    static_fonts()
    write("card.html", card_page())
    write("share-card.html", share_page())
    sig, text = signature_html(), signature_text()
    write("email-signature.html", signature_page(sig, text))
    write("email-signature-snippet.html", sig + "\n")
    write("email-signature.txt", text)
    write(f'{PERSON["first"].lower()}-{PERSON["last"].lower()}.vcf', vcard())
    print("Wrote brand/: card.html, share-card.html, email-signature.html, email-signature-snippet.html, "
          "email-signature.txt, and the contact file")


if __name__ == "__main__":
    main()
