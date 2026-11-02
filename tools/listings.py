"""Properties for sale on crownsmere.com: the Private Collection.

Each property in LISTINGS gets its own page (property-<slug>.html), a card on collection.html, a tile on
the home page and a link in the navigation. With LISTINGS empty, none of that exists on the site.

Two safeguards in tools/build.py:
  * Nothing is published until BUSINESS (in build.py) names the redress scheme and the anti-money-laundering
    supervisor. Estate agency work needs both before any property is marketed.
  * A listing missing any required detail stops the build, with a message naming what is missing.
    Answers such as "ask agent" or "TBC" are refused: buyers must be told, not asked to ask.

The required details follow the "material information" a buyer needs before deciding to view or buy
(National Trading Standards' Parts A, B and C, under the Digital Markets, Competition and Consumers Act
2024), plus the EPC rating every advert must show. Fill in only what the owner has confirmed in writing,
keep the owner's written instructions and ID checks on file, and never put the full address, the owner's
name or anything confidential here: this repository is public.

Photographs: save each as a JPEG in assets/img/collection/ (for example collection/belgrave-1.jpg) and
name it below without the extension. The build makes the WebP and AVIF versions if Pillow is installed.
Only use photographs you have the right to use, and never edit them in a misleading way.

To add a property, copy TEMPLATE into LISTINGS, fill in every field and run: python3 tools/build.py
To preview the design with a fictional sample (never published): see SAMPLE at the bottom.
"""

TEMPLATE = dict(
    slug="belgrave-place",               # the page address: property-belgrave-place.html (a-z, 0-9, hyphens)
    title="A stucco-fronted townhouse",  # shown as the heading; describe the home, not the address
    area="Belgravia, SW1",               # neighbourhood and postcode district only; the exact address is given on request
    status="Available",                  # "Available", "Under offer" or "Sold subject to contract"
    listed="2026-11-02",                 # date first marketed (YYYY-MM-DD)
    updated="2026-11-02",                # date these particulars were last checked with the owner

    # ---- Part A: price, tenure, council tax, energy performance
    price=4950000,                       # in pounds, whole number. A price must be shown ("price on application" is not allowed)
    price_qualifier="Guide price",       # "Guide price", "Asking price", "Offers in excess of" or "Offers in the region of"
    tenure="Freehold",                   # "Freehold", "Leasehold" or "Share of freehold"
    lease=None,                          # for leasehold or share of freehold:
                                         #   dict(years_remaining=118, ground_rent="£250 a year, reviewed every 25 years",
                                         #        service_charge="£6,200 a year (2026)", notes="")
    council_tax_band="H",                # A to H, from the council's website or the Valuation Office
    council_tax_authority="Westminster City Council",
    epc=dict(current="C", current_score=71, potential="B", potential_score=82),
    epc_exempt=None,                     # only if exempt, with the reason, e.g. "Listed building, exempt from EPC"

    # ---- Part B: the property
    property_type="Terraced house",      # e.g. "Terraced house", "Lateral apartment", "Penthouse", "Mews house"
    construction="Standard brick and stucco",
    bedrooms=5, bathrooms=4, receptions=2,
    size_sqft=4210,                      # internal area in square feet, from the floor plan (approximate)
    floor="",                            # for flats, e.g. "Third floor of five, with lift"
    electricity="Mains", water="Mains", sewerage="Mains", heating="Gas central heating, underfloor heating to the lower ground floor",
    broadband="Ultrafast fibre (FTTP) available",   # check ofcom.org.uk (broadband and mobile checker)
    mobile_signal="Good indoor coverage from all four major networks",
    parking="Residents' permit parking (Westminster)",

    # ---- Part C: things a buyer must know
    occupancy="Sold with vacant possession",        # or "Sold with a tenant in place: assured shorthold tenancy until ..., rent £... a month"
    building_safety="No known building safety issues",
    restrictions="Grade II listed; within the Belgravia Conservation Area",
    rights_easements="None known",
    flood_risk="Very low (Environment Agency long-term flood risk)",
    planning="No current planning applications on the property",
    accessibility="Passenger lift to all floors",

    # ---- Description and photographs
    description=[
        "A first paragraph that sets the scene: the house, its setting and what makes it special.",
        "A second paragraph with the accommodation, floor by floor.",
    ],
    features=["Five bedrooms, four bathrooms", "Private garden", "Passenger lift"],
    photos=[("collection/belgrave-place-1", "The stucco front of the house, with its black front door")],
    floorplan=None,                      # e.g. "collection/belgrave-place-plan" (a JPEG of the floor plan)

    # Estate Agents Act 1979, s.21: any personal interest Alaa (or anyone connected with her or with
    # Crownsmere) has in the property must be disclosed. None means there is none.
    personal_interest=None,
)

# The published properties, in the order they appear. Empty: the Private Collection is not on the site.
LISTINGS = []

# ---------------------------------------------------------------- preview only
# A fictional property for previewing the design. It is used only when the build is run with
# CROWNSMERE_PREVIEW=1 and CROWNSMERE_OUT set to a separate folder, and is never published.
SAMPLE = [
    dict(
        TEMPLATE,
        slug="sample-belgravia-townhouse",
        title="A stucco-fronted townhouse",
        description=[
            "Set on one of Belgravia's quietest garden squares, this white stucco townhouse has been restored with care over five floors, keeping its period proportions while adding the comfort of a modern family home.",
            "The raised ground floor opens onto a double drawing room with tall sash windows and two marble fireplaces. Below, a family kitchen leads to a private garden. The principal suite occupies the whole first floor, and four further bedrooms and a study sit above.",
        ],
        features=["Five bedrooms, four bathrooms", "Double drawing room with two fireplaces",
                  "Kitchen and family room opening onto a private garden", "Passenger lift to all floors",
                  "Access to the communal square gardens"],
        photos=[("townhouse", "The white stucco front of the house, with a black front door and columned porch"),
                ("interior", "The drawing room, with a marble fireplace and tall sash windows"),
                ("door", "The black-lacquered front door with brass fittings"),
                ("colonnade", "The garden square in front of the house")],
    ),
    dict(
        TEMPLATE,
        slug="sample-knightsbridge-apartment",
        title="A lateral apartment overlooking the park",
        area="Knightsbridge, SW7",
        status="Under offer",
        price=2750000, price_qualifier="Offers in excess of",
        tenure="Share of freehold",
        lease=dict(years_remaining=990, ground_rent="Peppercorn", service_charge="£9,800 a year (2026), including porterage", notes=""),
        council_tax_band="G", council_tax_authority="Royal Borough of Kensington and Chelsea",
        epc=dict(current="D", current_score=64, potential="C", potential_score=74),
        property_type="Lateral apartment", construction="Red brick mansion block",
        bedrooms=3, bathrooms=2, receptions=1, size_sqft=1840, floor="Third floor of six, with lift",
        heating="Communal heating and hot water",
        parking="Underground parking space (by separate negotiation)",
        occupancy="Sold with vacant possession",
        restrictions="Within the Knightsbridge Conservation Area; no short lets under the lease",
        accessibility="Lift from the street-level entrance hall",
        description=["A wide, light-filled apartment on the third floor of a handsome mansion block, with views across the park."],
        features=["Three bedrooms, two bathrooms", "Porter and lift", "Share of the freehold"],
        photos=[("westminster", "The view from the apartment's windows towards Westminster"),
                ("colonnade", "The street outside the mansion block")],
    ),
]
