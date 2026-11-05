"""Generate Crownsmere's private-by-default property catalogue.

Run through tools/build.py. No draft, unapproved or incomplete listing is
ever written to a public HTML page. Do not publish personal owner/partner data.
"""
from html import escape
from pathlib import Path
from urllib.parse import quote
import json
import re

ALLOWED_IMAGE = re.compile(r"^[a-zA-Z0-9][a-zA-Z0-9._-]*\.(?:avif|webp|jpe?g|png)$")
ALLOWED_SLUG = re.compile(r"^[a-z0-9]+(?:-[a-z0-9]+)*$")

def txt(value):
    return escape(str(value if value is not None else ""), quote=True)

def display_price(row):
    amount = "£" + format(int(row["price"]), ",")
    if row["listing_type"] == "rent":
        return amount + (" per week" if row.get("rent_period") == "pw" else " pcm")
    return amount

def allowed_image_path(root, slug, filename):
    if not isinstance(filename, str) or not ALLOWED_IMAGE.fullmatch(filename):
        raise ValueError("Property image names must be plain jpg, png, webp or avif filenames")
    rel = "assets/img/properties/" + slug + "/" + filename
    if not (root / rel).is_file():
        raise ValueError("Missing image for published property: " + rel)
    return rel

def validate_published(root, row):
    if row.get("status") != "published":
        return False
    # Hard publishing gate. Future compliance work can change the approval
    # process, but an explicit verified approval is always required.
    if row.get("owner_authority") is not True or row.get("compliance_cleared") is not True:
        raise ValueError("Refusing to publish property without both approvals: " + str(row.get("slug")))
    slug = row.get("slug", "")
    if not isinstance(slug, str) or len(slug) > 80 or not ALLOWED_SLUG.fullmatch(slug):
        raise ValueError("Invalid public property slug")
    if row.get("listing_type") not in ("sale", "rent"):
        raise ValueError("Property listing_type must be sale or rent")
    for field in ("title", "area", "reference", "description", "property_type"):
        if not isinstance(row.get(field), str) or not row[field].strip():
            raise ValueError("Published property missing: " + field)
    try:
        if int(row.get("price", 0)) <= 0:
            raise ValueError("Property price must be positive")
    except (ValueError, TypeError):
        raise ValueError("Property price must be a valid integer")
    if row["listing_type"] == "rent" and row.get("rent_period", "pcm") not in ("pcm", "pw"):
        raise ValueError("Rental period must be pcm or pw")
    if not isinstance(row.get("photos"), list) or not row["photos"]:
        raise ValueError("At least one authorised photo is required for publication")
    for fn in row["photos"]:
        allowed_image_path(root, slug, fn)
    if row.get("floorplan"):
        allowed_image_path(root, slug, row["floorplan"])
    if not isinstance(row.get("features", []), list):
        raise ValueError("Property features must be a list")
    return True

def build_properties(ctx):
    root = Path(ctx["OUT"])
    records = json.loads((root / "data/properties.json").read_text(encoding="utf-8"))
    if not isinstance(records, list):
        raise ValueError("data/properties.json must be a JSON array")
    active = [row for row in records if validate_published(root, row)]
    slugs = [row["slug"] for row in active]
    refs = [row["reference"] for row in active]
    if len(set(slugs)) != len(slugs) or len(set(refs)) != len(refs):
        raise ValueError("Published property slugs and references must be unique")
    # Remove stale previously generated listing pages on every build, including
    # those for withdrawn properties. Other pages are never touched.
    for old in root.glob("property-*.html"):
        if old.name not in ["property-" + s + ".html" for s in slugs]:
            old.unlink()

    page = ctx["page"]
    btn = ctx["btn"]
    brand = ctx["BRAND"]
    site = ctx["SITE"]
    ctx["CRUMBS"]["properties.html"] = "Properties"
    areas = sorted({str(r["area"]) for r in active})
    areas_html = "".join('<option value="' + txt(a) + '">' + txt(a) + "</option>" for a in areas)

    def property_card(row):
        slug = row["slug"]
        photo = allowed_image_path(root, slug, row["photos"][0])
        label = "For sale" if row["listing_type"] == "sale" else "To rent"
        beds = row.get("bedrooms")
        baths = row.get("bathrooms")
        meta = []
        if beds is not None:
            meta.append(str(int(beds)) + " bedroom" + ("" if int(beds) == 1 else "s"))
        if baths is not None:
            meta.append(str(int(baths)) + " bathroom" + ("" if int(baths) == 1 else "s"))
        if row.get("floor_area_sqft") is not None:
            meta.append(format(int(row["floor_area_sqft"]), ",") + " sq ft")
        summary = " · ".join(meta)
        url = "property-" + slug + ".html"
        return f'''<article class="property-card" data-type="{txt(row["listing_type"])}" data-area="{txt(row["area"])}" data-beds="{txt(beds if beds is not None else 0)}">
  <a href="{url}" class="property-card-link" aria-label="View {txt(row["title"])}">
    <div class="property-photo"><img src="{photo}" alt="{txt(row["title"])}" width="800" height="600" loading="lazy" decoding="async"><span class="property-pill">{label}</span></div>
    <div class="property-body"><p class="property-location">{txt(row["area"])}</p><h3>{txt(row["title"])}</h3>
      <p class="property-price">{txt(display_price(row))}</p>
      <p class="property-metrics">{txt(summary or row["property_type"])}</p>
      <span class="property-card-action">Explore property <span aria-hidden="true">→</span></span>
    </div>
  </a>
</article>'''

    cards = "".join(property_card(row) for row in active)
    empty = '''<div class="property-empty">
      <figure class="property-empty-image"><img src="assets/img/interior.jpg" alt="Illustrative light-filled London living room; not a currently available property" width="826" height="463" loading="eager"></figure>
      <div class="property-empty-copy">
        <p class="eyebrow">A private collection</p>
        <h2>Every home begins <em>with a conversation.</em></h2>
        <p>Our public collection is being prepared. While we confirm each opportunity, tell Alaa the area, style and lifestyle you have in mind.</p>
        <a class="btn btn-primary" href="contact.html">Tell Alaa your brief</a>
        <p class="property-empty-note">No properties are publicly listed yet. Image is illustrative.</p>
      </div>
    </div>''' if not active else ""
    filters = f'''<div class="property-filters" role="group" aria-label="Filter properties">
        <label>Looking to<select data-filter="type"><option value="all">All properties</option><option value="sale">To buy</option><option value="rent">To rent</option></select></label>
        <label>Location<select data-filter="area"><option value="all">All areas</option>{areas_html}</select></label>
        <label>Bedrooms<select data-filter="beds"><option value="0">Any</option><option value="1">1+</option><option value="2">2+</option><option value="3">3+</option><option value="4">4+</option><option value="5">5+</option></select></label>
      </div>''' if active else ""
    count_text = f"{len(active)} {'property' if len(active) == 1 else 'properties'} available" if active else "Private introductions by request"
    list_body = f'''
<section class="property-index-hero">
  <div class="wrap property-index-intro">
    <p class="eyebrow">Crownsmere collection</p>
    <h1>London homes, <em>thoughtfully selected.</em></h1>
    <p class="lede">Explore a carefully curated selection of properties for sale and rent. Every enquiry starts with Alaa Qadir, your personal point of contact.</p>
    <div class="btn-row">{btn("contact.html", "Ask Alaa about private opportunities", "ghost")}</div>
  </div>
</section>
<section class="sec sec-tight property-catalogue" aria-labelledby="properties-title">
  <div class="wrap">
    <div class="property-toolbar">
      <div><p class="eyebrow">Discover</p><h2 id="properties-title">The <em>collection.</em></h2>
        <p class="property-count" aria-live="polite" data-property-count>{count_text}</p></div>
{filters}
    </div>
    <div class="property-grid" data-property-grid>{cards}</div>
{empty}
    <p class="property-none" data-filter-empty hidden>No properties match those filters. Try a wider search or <a href="contact.html">ask Alaa directly</a>.</p>
  </div>
</section>
<section class="sec sec-alt property-guidance"><div class="wrap">
  <p class="eyebrow">Personally handled</p><h2>One contact. <em>Every next step.</em></h2>
  <div class="property-guidance-grid">
    <div><span>01</span><h3>Choose a home</h3><p>Browse the public collection or describe the property you have in mind.</p></div>
    <div><span>02</span><h3>Speak to Alaa</h3><p>Alaa reviews every enquiry personally, confirms your requirements and discusses an introduction.</p></div>
    <div><span>03</span><h3>Meet the appointed agent</h3><p>With your agreement, Alaa coordinates a handover to the agent responsible for viewings and the transaction.</p></div>
  </div>
</div></section>
<section class="sec cta"><div class="wrap">
  <p class="eyebrow">Private opportunities</p><h2>Not seeing <em>the right home?</em></h2>
  <p class="lede">Some of the finest opportunities never appear online. Tell Alaa what matters most.</p>
  <div class="btn-row">{btn("contact.html", "Share your requirements")}</div>
</div></section>'''
    page("properties.html", "London Properties for Sale & Rent | " + brand,
         "Explore Crownsmere's curated London property collection. Enquire with Alaa Qadir about homes for sale, to rent and private opportunities.",
         list_body, page_type="CollectionPage", scripts='\n<script src="assets/property.js" defer></script>')

    details = []
    for row in active:
        slug = row["slug"]
        path = "property-" + slug + ".html"
        ctx["CRUMBS"][path] = row["title"]
        ctx["SECTION_OF"][path] = "properties.html"
        ref = txt(row["reference"])
        ptitle = txt(row["title"])
        price = txt(display_price(row))
        photo_tags = "".join(
            f'<figure class="property-gallery-photo"><img src="{allowed_image_path(root, slug, filename)}" alt="Photo {n} of {ptitle}" width="1100" height="750" loading="{"eager" if n == 1 else "lazy"}"></figure>'
            for n, filename in enumerate(row["photos"], 1)
        )
        facts = []
        for field, title in (("bedrooms","Bedrooms"), ("bathrooms","Bathrooms"),
                             ("floor_area_sqft","Area (sq ft)"), ("property_type","Property type"),
                             ("tenure","Tenure"), ("council_tax_band","Council tax band"),
                             ("furnished","Furnishing"), ("availability","Availability"),
                             ("epc_rating","EPC rating")):
            value = row.get(field)
            if value not in (None, ""):
                facts.append(f"<div><dt>{title}</dt><dd>{txt(format(value, ',') if isinstance(value,int) and field == 'floor_area_sqft' else value)}</dd></div>")
        facts_html = "".join(facts)
        features = "".join("<li>" + txt(v) + "</li>" for v in row.get("features", []))
        feature_block = f'<section class="property-features"><h2>Highlights</h2><ul>{features}</ul></section>' if features else ""
        floorplan_block = ""
        if row.get("floorplan"):
            fp = allowed_image_path(root, slug, row["floorplan"])
            floorplan_block = f'<section class="property-floorplan"><h2>Floor plan</h2><a href="{fp}" target="_blank" rel="noopener"><img src="{fp}" alt="Floor plan of {ptitle}" loading="lazy"></a></section>'
        label = "For sale" if row["listing_type"] == "sale" else "To rent"
        subject = quote("Crownsmere property enquiry | " + str(row["reference"]), safe="")
        detail_body = f'''
<section class="property-detail-top wrap">
  <nav class="crumbs" aria-label="Breadcrumb"><ol><li><a href="properties.html">Properties</a></li><li aria-current="page">{ptitle}</li></ol></nav>
  <p class="eyebrow">{label} · {txt(row["area"])}</p>
  <div class="property-detail-heading">
    <div><h1>{ptitle}</h1><p class="property-detail-reference">Reference {ref} · {txt(row.get("address_public", row["area"]))}</p></div>
    <p class="property-detail-price">{price}</p>
  </div>
</section>
<section class="wrap property-detail-gallery" aria-label="Property photographs">{photo_tags}</section>
<section class="sec sec-tight">
  <div class="wrap property-detail-layout">
    <div class="property-detail-main">
      <p class="eyebrow">The property</p>
      <h2>A closer <em>look.</em></h2>
      <p class="property-description">{txt(row["description"])}</p>
      <dl class="property-facts">{facts_html}</dl>
{feature_block}
{floorplan_block}
      <p class="fine">All particulars are subject to confirmation with the appointed agent. Images and descriptions relate to this property and are published with authority.</p>
    </div>
    <aside class="property-enquire" aria-labelledby="property-enquire-title">
      <p class="eyebrow">A personal introduction</p><h2 id="property-enquire-title">Enquire with <em>Alaa.</em></h2>
      <p>Your enquiry reaches Crownsmere first. Alaa will discuss your requirements and arrange a relevant agent introduction only with your agreement.</p>
      <form data-property-enquiry data-ref="{ref}" data-title="{ptitle}" action="mailto:{ctx["ALAA"]}" method="post" enctype="text/plain">
        <div class="field"><label for="p-name">Full name</label><input id="p-name" type="text" name="name" autocomplete="name" required maxlength="90"></div>
        <div class="field"><label for="p-email">Email</label><input id="p-email" type="email" name="email" autocomplete="email" required maxlength="180"></div>
        <div class="field"><label for="p-phone">Telephone <span class="opt">(optional)</span></label><input id="p-phone" type="tel" name="phone" autocomplete="tel" maxlength="35"></div>
        <div class="field"><label for="p-message">Message <span class="opt">(optional)</span></label><textarea id="p-message" name="message" rows="3" maxlength="1500" placeholder="Your requirements or preferred viewing dates"></textarea></div>
        <label class="consent"><input type="checkbox" name="contact_ok" required><span>I agree to be contacted by Crownsmere about this property. My details will not be sent to a partner agent without my separate agreement. <a href="privacy.html">Privacy notice</a>.</span></label>
        <button type="submit" class="btn btn-primary property-submit">Prepare enquiry <span aria-hidden="true">→</span></button>
        <p class="fine">Your email app opens a prepared message. Nothing is sent until you press Send.</p>
        <div class="property-email-ready" data-property-ready hidden>
          <p><strong>Email prepared.</strong> Please review and send it using your mail app.</p>
          <a href="mailto:{ctx["ALAA"]}?subject={subject}" data-property-mailto>Open prepared email</a>
          <button type="button" data-property-copy>Copy enquiry</button>
          <p data-property-feedback role="status"></p>
        </div>
      </form>
      <p class="property-direct-email">Prefer email? <a href="mailto:{ctx["ALAA"]}?subject={subject}">Contact Alaa directly</a>.</p>
    </aside>
  </div>
</section>
<nav class="wrap property-detail-return" aria-label="Back to properties"><a class="more" href="properties.html">← Back to properties</a></nav>'''
        structured = {"@context":"https://schema.org","@type":"RealEstateListing",
                      "name":row["title"],"description":row["description"],
                      "url":site+"/"+path,
                      "offers":{"@type":"Offer","price":int(row["price"]),"priceCurrency":"GBP",
                                "url":site+"/"+path}}
        page(path, row["title"] + " | " + brand,
             (row["title"] + " in " + row["area"] + ". Enquire through Alaa Qadir at Crownsmere Estate.")[:160],
             detail_body, extra_ld=[structured], scripts='\n<script src="assets/property.js" defer></script>')
        details.append(path)
    return details
