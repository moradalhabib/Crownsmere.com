"""Original line illustrations for Crownsmere Estate, generated as inline SVG.

Three drawings in the house style (navy line, gold accents, ivory paper):
  - elevation(): a Belgravia stucco terrace, as an architectural elevation
  - door():      a Georgian front door study (fanlight, Ionic columns, railings, bay trees)
  - london_map(): prime London, drawn from real coordinates, with numbered neighbourhoods

Every stroked element carries pathLength="1" so the site can "draw" it on scroll.
Classes: .d (navy line), .dg (gold line), .df (navy fill), .gf (gold fill), .pf (paper fill),
.t (text). Each group sets --d, the animation delay.
"""
import math


def f(v):
    return f"{v:.1f}".rstrip("0").rstrip(".")


class Path:
    """Accumulates many sub-paths into a single <path> (one element per stroke group)."""

    def __init__(self):
        self.parts = []

    def line(self, x1, y1, x2, y2):
        self.parts.append(f"M{f(x1)} {f(y1)}L{f(x2)} {f(y2)}")

    def poly(self, pts, close=False):
        self.parts.append("M" + "L".join(f"{f(x)} {f(y)}" for x, y in pts) + ("Z" if close else ""))

    def rect(self, x, y, w, h):
        self.poly([(x, y), (x + w, y), (x + w, y + h), (x, y + h)], close=True)

    def arc(self, cx, cy, r, a0, a1, steps=24):
        pts = [(cx + r * math.cos(math.radians(a0 + (a1 - a0) * i / steps)),
                cy + r * math.sin(math.radians(a0 + (a1 - a0) * i / steps))) for i in range(steps + 1)]
        self.poly(pts)

    def circle(self, cx, cy, r, steps=36):
        self.arc(cx, cy, r, 0, 360, steps)

    def raw(self, d):
        self.parts.append(d)

    def svg(self, cls="d", delay=0.0, extra=""):
        if not self.parts:
            return ""
        return f'<path class="{cls}" style="--d:{delay:.2f}s" pathLength="1" d="{"".join(self.parts)}"{extra}/>'


def fill_rect(x, y, w, h, cls):
    return f'<rect class="{cls}" x="{f(x)}" y="{f(y)}" width="{f(w)}" height="{f(h)}"/>'


def segments_skipping(x0, x1, holes):
    """Horizontal [x0, x1] split around a list of (a, b) holes."""
    segs, cur = [], x0
    for a, b in sorted(holes):
        if b <= cur or a >= x1:
            continue
        if a > cur:
            segs.append((cur, a))
        cur = max(cur, b)
    if cur < x1:
        segs.append((cur, x1))
    return segs


# ==================================================================== elevation
def elevation():
    W, H = 1000, 760
    houses, HW, X0 = 4, 240, 20
    numbers = ["26", "27", "28", "29"]
    out = []
    # Pavement
    ground = Path()
    ground.line(0, 700, W, 700)
    ground.line(0, 716, W, 716)
    for x in range(10, W, 46):
        ground.line(x, 700, x, 716)
    out.append(ground.svg("d", 0.0))

    for i in range(houses):
        X = X0 + i * HW
        c = [X + 40, X + 120, X + 200]          # bay centres; c[0] is the door bay
        dl = 0.18 * i
        frame, rust, win, glaz, bal, rail, orn, gold = (Path() for _ in range(8))

        # Party walls / pilasters and main horizontals
        for px in (X, X + HW):
            frame.line(px - 2, 196, px - 2, 664)
            frame.line(px + 2, 196, px + 2, 664)
        frame.line(X, 664, X + HW, 664)                      # plinth
        for y in (536, 544):                                  # first-floor band
            frame.line(X, y, X + HW, y)
        frame.line(X, 380, X + HW, 380)
        frame.line(X, 384, X + HW, 384)
        frame.line(X, 286, X + HW, 286)
        for y in (212, 206, 200, 196):                        # main cornice
            frame.line(X - 4, y, X + HW + 4, y)
        for x in range(X + 2, X + HW - 2, 8):                 # dentils
            orn.rect(x, 206, 4, 6)
        # Attic / mansard with dormers
        frame.line(X, 180, X + HW, 180)
        frame.poly([(X + 6, 180), (X + 16, 140), (X + HW - 16, 140), (X + HW - 6, 180)])
        for cx in c:
            win.rect(cx - 13, 150, 26, 26)
            win.poly([(cx - 17, 150), (cx, 141), (cx + 17, 150)])
            glaz.line(cx, 150, cx, 176)
            glaz.line(cx - 13, 163, cx + 13, 163)
        # Chimney stacks on the party walls
        for px in ([X] + ([X + HW] if i == houses - 1 else [])):
            frame.rect(px - 13, 96, 26, 44)
            frame.line(px - 16, 96, px + 16, 96)
            frame.line(px - 16, 102, px + 16, 102)
            for k in (-8, 0, 8):
                orn.rect(px + k - 3, 82, 6, 14)

        # Ground floor: rustication around the openings
        holes = [(c[0] - 34, c[0] + 34)] + [(cx - 26, cx + 26) for cx in c[1:]]
        for y in range(652, 548, -12):
            for a, b in segments_skipping(X + 3, X + HW - 3, holes):
                rust.line(a, y, b, y)
        # Arched ground-floor windows
        for cx in c[1:]:
            win.poly([(cx - 22, 652), (cx - 22, 600)])
            win.arc(cx, 600, 22, 180, 360)
            win.poly([(cx + 22, 600), (cx + 22, 652)])
            win.rect(cx - 26, 652, 52, 5)                    # sill
            glaz.line(cx, 579, cx, 652)
            for y in (614, 633):
                glaz.line(cx - 22, y, cx + 22, y)
            glaz.arc(cx, 600, 11, 180, 360, 12)
            orn.rect(cx - 4, 574, 8, 9)                      # keystone
        # Portico: Tuscan columns, entablature, door with fanlight
        for sx in (-1, 1):
            x0 = c[0] + sx * 21 - 5
            orn.rect(x0 - 2, 658, 14, 6)                     # base
            frame.rect(x0, 554, 10, 104)                     # shaft
            orn.rect(x0 - 2, 548, 14, 6)                     # capital
            glaz.line(x0 + 5, 556, x0 + 5, 656)
        frame.rect(c[0] - 32, 532, 64, 16)                   # entablature
        frame.line(c[0] - 32, 538, c[0] + 32, 538)
        win.rect(c[0] - 15, 594, 30, 70)                     # door
        win.arc(c[0], 594, 15, 180, 360, 16)                 # fanlight
        for a in range(200, 360, 32):
            glaz.line(c[0], 594, c[0] + 15 * math.cos(math.radians(a)), 594 + 15 * math.sin(math.radians(a)))
        for y0 in (600, 624, 646):                           # door panels
            glaz.rect(c[0] - 11, y0, 9, 16 if y0 != 624 else 18)
            glaz.rect(c[0] + 2, y0, 9, 16 if y0 != 624 else 18)
        gold.circle(c[0] + 8, 632, 1.6, 10)                  # door knob
        # Wall lantern beside the portico
        lx = c[0] + 42
        gold.line(lx - 6, 586, lx, 586)
        gold.poly([(lx - 4, 588), (lx + 4, 588), (lx + 3, 600), (lx - 3, 600)], close=True)
        gold.poly([(lx - 5, 588), (lx, 583), (lx + 5, 588)])
        # Steps
        for k, y in enumerate((664, 673, 682, 691)):
            wv = 22 + k * 5
            frame.rect(c[0] - wv, y, 2 * wv, 9)

        # First floor (piano nobile): balcony balustrade + tall windows with hoods
        bal.line(X + 3, 512, X + HW - 3, 512)
        bal.line(X + 3, 516, X + HW - 3, 516)
        bal.line(X + 3, 534, X + HW - 3, 534)
        for x in range(X + 8, X + HW - 4, 8):
            bal.poly([(x - 1.5, 517), (x - 2.5, 524), (x - 1, 533)])
            bal.poly([(x + 1.5, 517), (x + 2.5, 524), (x + 1, 533)])
        for j, cx in enumerate(c):
            win.rect(cx - 20, 418, 40, 94)
            win.rect(cx - 24, 414, 48, 98)                   # architrave
            for y in (441, 464, 488):
                glaz.line(cx - 20, y, cx + 20, y)
            glaz.line(cx, 418, cx, 512)
            if j == 1:
                orn.poly([(cx - 30, 408), (cx, 390), (cx + 30, 408)], close=True)
            else:
                orn.rect(cx - 30, 402, 60, 6)
            orn.line(cx - 26, 410, cx + 26, 410)
        # Second floor
        for cx in c:
            win.rect(cx - 19, 300, 38, 66)
            win.rect(cx - 23, 296, 46, 70)
            win.rect(cx - 25, 366, 50, 4)
            glaz.line(cx - 19, 333, cx + 19, 333)
            for gx in (-6.3, 6.3):
                glaz.line(cx + gx, 300, cx + gx, 366)
            glaz.line(cx - 19, 316, cx + 19, 316)
            glaz.line(cx - 19, 350, cx + 19, 350)
        # Third floor
        for cx in c:
            win.rect(cx - 17, 222, 34, 50)
            win.rect(cx - 21, 218, 42, 54)
            win.rect(cx - 23, 272, 46, 4)
            glaz.line(cx - 17, 247, cx + 17, 247)
            glaz.line(cx, 222, cx, 272)

        # Area railings at the front, with a gap for the steps
        for a, b in segments_skipping(X, X + HW, [(c[0] - 46, c[0] + 46)]):
            rail.line(a, 660, b, 660)
            rail.line(a, 686, b, 686)
            rail.rect(a, 686, b - a, 14)
            for x in range(int(a) + 4, int(b) - 1, 7):
                rail.line(x, 654, x, 686)
                rail.poly([(x - 1.6, 655), (x, 649), (x + 1.6, 655)])

        out.append(f'<g class="h">'
                   f'{frame.svg("d", 0.1 + dl)}{rust.svg("d thin", 0.5 + dl)}{win.svg("d", 0.7 + dl)}'
                   f'{glaz.svg("d thin", 1.0 + dl)}{bal.svg("d thin", 1.2 + dl)}{orn.svg("d", 1.1 + dl)}'
                   f'{rail.svg("d thin", 1.4 + dl)}{gold.svg("dg", 1.8 + dl)}'
                   f'<text class="t num" x="{c[0]}" y="543.5" text-anchor="middle">{numbers[i]}</text></g>')

    return (f'<svg class="art art-elevation" viewBox="0 66 {W} {H - 30}" role="img" '
            f'aria-labelledby="elev-t"><title id="elev-t">Line drawing: elevation of a terrace of four '
            f'white stucco Belgravia townhouses, with porticoes, balconies and area railings</title>'
            + "".join(out) + "</svg>")


# ==================================================================== door study
def door():
    W, H = 600, 800
    cx = 300
    wall, rust, cols, ent, dr, panels, fan, bal, rail, steps, tree, gold = (Path() for _ in range(12))
    goldfills = []

    # Wall rustication (staggered joints), around columns and door
    col_x = [(104, 172), (428, 496)]
    holes = [(a, b) for a, b in col_x] + [(207, 393)]
    for k, y in enumerate(range(700, 300, -22)):
        segs = segments_skipping(20, 580, holes if y > 300 else [])
        for a, b in segs:
            rust.line(a, y, b, y)
            off = 0 if k % 2 else 26
            for x in range(int(a) + 14 + off, int(b) - 6, 52):
                rust.line(x, y, x, y - 22)

    # Pedestals, Ionic columns
    for x0, x1 in col_x:
        m = (x0 + x1) / 2
        cols.rect(m - 30, 690, 60, 70)                        # pedestal
        cols.rect(m - 34, 684, 68, 6)
        cols.rect(m - 34, 752, 68, 8)
        cols.rect(m - 24, 676, 48, 8)                         # base
        cols.arc(m, 676, 22, 180, 360, 12) if False else None
        cols.line(m - 22, 670, m + 22, 670)
        cols.poly([(m - 18, 670), (m - 18, 332)])
        cols.poly([(m + 18, 670), (m + 18, 332)])
        for fx in (-10, -3.5, 3.5, 10):
            cols.line(m + fx, 338, m + fx, 664)
        cols.rect(m - 34, 306, 68, 10)                        # abacus
        cols.poly([(m - 22, 316), (m - 20, 326), (m + 20, 326), (m + 22, 316)])  # echinus
        cols.line(m - 18, 332, m + 18, 332)
        for vx in (m - 28, m + 28):                           # volutes
            cols.circle(vx, 324, 9, 24)
            cols.circle(vx, 324, 4.5, 16)
            goldfills.append(f'<circle class="gf" cx="{f(vx)}" cy="324" r="1.6"/>')

    # Entablature and cornice with dentils
    ent.rect(90, 282, 420, 24)
    ent.line(90, 290, 510, 290)
    ent.line(90, 298, 510, 298)
    ent.rect(90, 254, 420, 28)
    for y in (254, 248, 236, 228, 222):
        ent.line(80, y, 520, y)
    for x in range(84, 516, 10):
        ent.rect(x, 248, 5, 6)
    ent.line(80, 222, 80, 254)
    ent.line(520, 222, 520, 254)

    # Balustrade above the portico
    bal.rect(84, 170, 432, 8)
    bal.rect(84, 214, 432, 8)
    for x in range(104, 500, 24):
        bal.raw(f"M{x - 4} 178C{x - 9} 186 {x - 10} 194 {x - 5} 200C{x - 8} 205 {x - 7} 210 {x - 5} 214"
                f"M{x + 4} 178C{x + 9} 186 {x + 10} 194 {x + 5} 200C{x + 8} 205 {x + 7} 210 {x + 5} 214")
    for px in (84, 300, 516):
        bal.rect(px - 9, 170, 18, 52)

    # Door architrave, fanlight with sunburst glazing
    dr.rect(207, 370, 186, 330)
    dr.rect(215, 378, 170, 322)
    fan.arc(cx, 370, 93, 180, 360, 48)
    fan.arc(cx, 370, 85, 180, 360, 48)
    fan.arc(cx, 370, 24, 180, 360, 20)
    fan.arc(cx, 370, 58, 180, 360, 36)
    for a in range(180, 361, 20):
        r0, r1 = 24, 85
        fan.line(cx + r0 * math.cos(math.radians(a)), 370 + r0 * math.sin(math.radians(a)),
                 cx + r1 * math.cos(math.radians(a)), 370 + r1 * math.sin(math.radians(a)))
    fan.line(cx - 93, 370, cx + 93, 370)
    for a in range(190, 360, 20):                             # little loops between spokes
        mx, my = cx + 71 * math.cos(math.radians(a)), 370 + 71 * math.sin(math.radians(a))
        fan.circle(mx, my, 5, 12)
    fan.rect(cx - 12, 274, 24, 16)                            # keystone

    # Door leaf (navy) with six panels in gold line
    door_fill = '<rect class="df" x="222" y="384" width="156" height="316"/>'
    for (x, w) in ((236, 54), (310, 54)):
        for (y, h) in ((400, 66), (482, 116), (618, 66)):
            panels.rect(x, y, w, h)
            panels.rect(x + 6, y + 6, w - 12, h - 12)
    panels.line(cx, 384, cx, 700)
    gold.circle(cx, 450, 13, 28)                              # knocker
    gold.circle(cx, 435, 4, 12)
    goldfills.append(f'<rect class="gf" x="{cx - 20}" y="604" width="40" height="7"/>')   # letterbox
    goldfills.append(f'<circle class="gf" cx="356" cy="548" r="5"/>')                    # knob

    # Steps
    for (y, x0, x1) in ((700, 172, 428), (720, 158, 442), (740, 144, 456)):
        steps.rect(x0, y, x1 - x0, 20)
    steps.line(0, 760, W, 760)
    steps.line(0, 780, W, 780)
    for x in range(30, W, 60):
        steps.line(x, 760, x, 780)

    # Bay trees in pots on the landing
    for tx in (190, 410):
        tree.poly([(tx - 15, 672), (tx + 15, 672), (tx + 12, 700), (tx - 12, 700)], close=True)
        tree.line(tx - 16, 678, tx + 16, 678)
        tree.line(tx, 672, tx, 622)
        # clipped-ball topiary: a soft silhouette filled with small leaf strokes
        pts = []
        for k in range(49):
            a = 2 * math.pi * k / 48
            r = 22 + 1.1 * math.sin(k * 7.3) + 0.8 * math.cos(k * 4.7)
            pts.append((tx + r * math.cos(a), 600 + r * math.sin(a)))
        tree.poly(pts, close=True)
        for k in range(26):
            a = k * 2.399963                       # golden-angle spiral for even spacing
            r = 19 * math.sqrt((k + 0.5) / 26)
            x, y = tx + r * math.cos(a), 600 + r * math.sin(a)
            rot = a + 1.2
            dx, dy = 3.2 * math.cos(rot), 3.2 * math.sin(rot)
            tree.raw(f"M{f(x - dx)} {f(y - dy)}Q{f(x - dy * 0.6)} {f(y + dx * 0.6)} {f(x + dx)} {f(y + dy)}")
        gold.line(tx - 13, 686, tx + 13, 686)

    # Wall lanterns on brackets
    for lx, sgn in ((52, 1), (548, -1)):
        wx = 20 if sgn == 1 else 580
        gold.raw(f"M{wx} 404C{wx + sgn * 14} 404 {lx - sgn * 4} 396 {lx} 410")
        gold.poly([(lx - 9, 414), (lx + 9, 414), (lx + 6, 452), (lx - 6, 452)], close=True)
        gold.poly([(lx - 12, 414), (lx, 404), (lx + 12, 414)])
        gold.line(lx, 414, lx, 452)
        gold.poly([(lx - 7, 452), (lx + 7, 452), (lx, 462)], close=True)

    # Railings either side
    for a, b in ((20, 70), (530, 580)):
        rail.line(a, 708, b, 708)
        rail.rect(a, 744, b - a, 16)
        for x in range(a + 5, b, 10):
            rail.line(x, 694, x, 744)
            rail.poly([(x - 2.5, 696), (x, 688), (x + 2.5, 696)])

    body = (rust.svg("d thin", 0.2) + cols.svg("d", 0.0) + ent.svg("d", 0.3) + bal.svg("d thin", 0.7)
            + door_fill + dr.svg("d", 0.4) + fan.svg("d thin", 0.8) + panels.svg("dg", 1.4)
            + steps.svg("d", 0.5) + tree.svg("d", 1.1) + rail.svg("d thin", 1.2) + gold.svg("dg", 1.6)
            + "".join(goldfills)
            + f'<text class="t fanno" x="{cx}" y="362" text-anchor="middle">28</text>')
    return (f'<svg class="art art-door" viewBox="0 150 {W} {H - 150}" role="img" aria-labelledby="door-t">'
            f'<title id="door-t">Line drawing: a black Georgian front door with a sunburst fanlight, '
            f'Ionic columns, brass fittings, bay trees in pots and iron railings</title>{body}</svg>')


# ==================================================================== map
LON0, LON1, LAT0, LAT1 = -0.225, -0.095, 51.475, 51.565
MW, MH = 900, 1000


def P_(lon, lat):
    return ((lon - LON0) / (LON1 - LON0) * MW, (LAT1 - lat) / (LAT1 - LAT0) * MH)


def smooth(pts):
    """Catmull-Rom through points -> cubic Bezier path data."""
    p = [P_(*q) for q in pts]
    d = f"M{f(p[0][0])} {f(p[0][1])}"
    for i in range(len(p) - 1):
        p0 = p[i - 1] if i > 0 else p[i]
        p1, p2 = p[i], p[i + 1]
        p3 = p[i + 2] if i + 2 < len(p) else p2
        c1 = (p1[0] + (p2[0] - p0[0]) / 6, p1[1] + (p2[1] - p0[1]) / 6)
        c2 = (p2[0] - (p3[0] - p1[0]) / 6, p2[1] - (p3[1] - p1[1]) / 6)
        d += f"C{f(c1[0])} {f(c1[1])} {f(c2[0])} {f(c2[1])} {f(p2[0])} {f(p2[1])}"
    return d


def closed(pts):
    p = [P_(*q) for q in pts]
    return "M" + "L".join(f"{f(x)} {f(y)}" for x, y in p) + "Z"


THAMES = [(-0.190, 51.468), (-0.183, 51.4745), (-0.176, 51.479), (-0.170, 51.4815), (-0.1615, 51.4840),
          (-0.150, 51.4858), (-0.138, 51.4865), (-0.127, 51.4880), (-0.1225, 51.4930), (-0.1215, 51.5005),
          (-0.1195, 51.5065), (-0.113, 51.5095), (-0.104, 51.5098), (-0.093, 51.5085)]

PARKS = {
    "Hyde Park": [(-0.1755, 51.5115), (-0.1585, 51.5135), (-0.1530, 51.5035), (-0.1585, 51.5025),
                  (-0.1755, 51.5050)],
    "Kensington Gardens": [(-0.1880, 51.5115), (-0.1755, 51.5115), (-0.1755, 51.5050), (-0.1765, 51.5018),
                           (-0.1880, 51.5022)],
    "Regent’s Park": "circle",
    "Green Park": [(-0.1500, 51.5045), (-0.1415, 51.5075), (-0.1395, 51.5035), (-0.1480, 51.5020)],
    "St James’s Park": [(-0.1395, 51.5035), (-0.1290, 51.5040), (-0.1285, 51.5010), (-0.1385, 51.5005)],
    "Holland Park": [(-0.2075, 51.5050), (-0.2010, 51.5055), (-0.2005, 51.5005), (-0.2070, 51.5000)],
    "Battersea Park": [(-0.1655, 51.4810), (-0.1505, 51.4830), (-0.1490, 51.4770), (-0.1640, 51.4755)],
    "Hampstead Heath": [(-0.1800, 51.5700), (-0.1480, 51.5700), (-0.1480, 51.5600), (-0.1560, 51.5555),
                        (-0.1680, 51.5545), (-0.1790, 51.5580)],
}

ROADS = [
    [(-0.2050, 51.5093), (-0.1880, 51.5118), (-0.1585, 51.5135)],                 # Bayswater Rd
    [(-0.1585, 51.5135), (-0.1420, 51.5150), (-0.1310, 51.5163)],                 # Oxford St
    [(-0.1585, 51.5135), (-0.1530, 51.5035)],                                     # Park Lane
    [(-0.1530, 51.5035), (-0.1420, 51.5070), (-0.1340, 51.5100)],                 # Piccadilly
    [(-0.1530, 51.5030), (-0.1620, 51.5015), (-0.1800, 51.5015), (-0.1930, 51.5010), (-0.2060, 51.4995)],
    [(-0.1620, 51.5015), (-0.1690, 51.4960), (-0.1760, 51.4930)],                 # Brompton Rd
    [(-0.1600, 51.5015), (-0.1575, 51.4925)],                                     # Sloane St
    [(-0.1575, 51.4925), (-0.1690, 51.4875), (-0.1830, 51.4815)],                 # King's Rd
    [(-0.1720, 51.5210), (-0.1550, 51.5225), (-0.1350, 51.5250)],                 # Marylebone Rd
    [(-0.1585, 51.5135), (-0.1720, 51.5250), (-0.1790, 51.5350)],                 # Edgware Rd
    [(-0.1760, 51.5320), (-0.1800, 51.5480), (-0.1830, 51.5600)],                 # Finchley Rd
    [(-0.2050, 51.5093), (-0.2180, 51.5050)],                                     # Holland Park Ave
    [(-0.1415, 51.5180), (-0.1360, 51.5105)],                                     # Regent St
    [(-0.1530, 51.5030), (-0.1440, 51.4960), (-0.1360, 51.4930)],                 # Grosvenor Pl / Victoria
    [(-0.1690, 51.4960), (-0.1650, 51.4850)],                                     # Sloane Ave / Oakley
]

# name, lon, lat, label dx, dy, anchor
AREAS = [
    ("Mayfair", -0.1470, 51.5100, 16, 4, "start"),
    ("Belgravia", -0.1530, 51.4975, 16, 4, "start"),
    ("Knightsbridge", -0.1650, 51.4995, -14, -14, "end"),
    ("Chelsea", -0.1680, 51.4880, -16, 4, "end"),
    ("Kensington", -0.1910, 51.4980, -16, 18, "end"),
    ("Holland Park", -0.2060, 51.5070, -14, -18, "start"),
    ("Notting Hill", -0.2000, 51.5150, 16, -6, "start"),
    ("Marylebone", -0.1530, 51.5190, 16, 4, "start"),
    ("St John’s Wood", -0.1740, 51.5340, 16, 4, "start"),
    ("Hampstead", -0.1780, 51.5530, -16, 4, "end"),
]


def area_slug(name):
    return "".join(ch for ch in name.lower().replace("’", "") if ch.isalnum() or ch == " ").replace(" ", "-")


def london_map():
    out = []
    # Faint graticule
    g = Path()
    for k in range(1, 9):
        g.line(k * MW / 9, 0, k * MW / 9, MH)
    for k in range(1, 10):
        g.line(0, k * MH / 10, MW, k * MH / 10)
    out.append(g.svg("grid", 0.0))
    # Parks
    parks = []
    for name, pts in PARKS.items():
        if pts == "circle":
            x, y = P_(-0.1530, 51.5290)
            parks.append(f'<ellipse class="park" cx="{f(x)}" cy="{f(y)}" rx="64" ry="62" pathLength="1" style="--d:0.4s"/>')
            parks.append(f'<ellipse class="d thin" cx="{f(x)}" cy="{f(y)}" rx="34" ry="32" pathLength="1" style="--d:0.8s"/>')
        else:
            parks.append(f'<path class="park" style="--d:0.4s" pathLength="1" d="{closed(pts)}"/>')
    # Serpentine and Round Pond
    serp = smooth([(-0.1720, 51.5085), (-0.1660, 51.5068), (-0.1600, 51.5052)])
    parks.append(f'<path class="water-line" style="--d:0.9s" pathLength="1" d="{serp}"/>')
    rx, ry = P_(-0.1815, 51.5060)
    parks.append(f'<ellipse class="water" cx="{f(rx)}" cy="{f(ry)}" rx="9" ry="7"/>')
    out.append("<g>" + "".join(parks) + "</g>")
    # Roads
    out.append("".join(f'<path class="road" style="--d:{0.6 + 0.05 * i:.2f}s" pathLength="1" d="{smooth(r)}"/>'
                       for i, r in enumerate(ROADS)))
    # The Thames: dark bank stroke beneath a paler water stroke
    th = smooth(THAMES)
    out.append(f'<path class="river-bank" style="--d:0.2s" pathLength="1" d="{th}"/>'
               f'<path class="river" style="--d:0.3s" pathLength="1" d="{th}"/>')
    # Park + river labels
    labels = [("Hyde Park", -0.1665, 51.5095), ("Kensington", -0.1825, 51.5085), ("Gardens", -0.1825, 51.5068),
              ("Regent’s Park", -0.1530, 51.5270), ("Green Park", -0.1440, 51.5047),
              ("Battersea Park", -0.1570, 51.4795), ("Hampstead Heath", -0.1640, 51.5620),
              ("River Thames", -0.1330, 51.4835)]
    out.append("".join(f'<text class="t park-t" x="{f(P_(lo, la)[0])}" y="{f(P_(lo, la)[1])}" text-anchor="middle">{n}</text>'
                       for n, lo, la in labels))
    # Neighbourhood markers
    marks = []
    for i, (name, lo, la, dx, dy, anchor) in enumerate(AREAS):
        x, y = P_(lo, la)
        slug = area_slug(name)
        marks.append(
            f'<g class="mk" id="mk-{slug}" data-area="{slug}" style="--d:{1.4 + 0.08 * i:.2f}s">'
            f'<circle class="mk-halo" cx="{f(x)}" cy="{f(y)}" r="20"/>'
            f'<circle class="mk-dot" cx="{f(x)}" cy="{f(y)}" r="11"/>'
            f'<text class="t mk-n" x="{f(x)}" y="{f(y + 3.6)}" text-anchor="middle">{i + 1:02d}</text>'
            f'<text class="t mk-l" x="{f(x + dx)}" y="{f(y + dy)}" text-anchor="{anchor}">{name.upper()}</text></g>')
    out.append("".join(marks))
    # Compass rose and scale bar
    cx, cy = 92, 900
    comp = Path()
    comp.circle(cx, cy, 34, 40)
    comp.circle(cx, cy, 28, 40)
    comp.poly([(cx, cy - 44), (cx + 7, cy), (cx, cy + 44), (cx - 7, cy)], close=True)
    comp.poly([(cx - 44, cy), (cx, cy - 6), (cx + 44, cy), (cx, cy + 6)], close=True)
    out.append(comp.svg("dg", 1.6) + f'<text class="t comp-n" x="{cx}" y="{cy - 50}" text-anchor="middle">N</text>')
    half_mile = 0.5 * 1609.34 / (111320 * math.cos(math.radians(51.5))) / (LON1 - LON0) * MW
    sb = Path()
    sx, sy = 640, 950
    sb.line(sx, sy, sx + half_mile * 2, sy)
    for k in range(3):
        sb.line(sx + k * half_mile, sy - 6, sx + k * half_mile, sy + 6)
    out.append(sb.svg("d", 1.6) +
               f'<text class="t scale-t" x="{f(sx)}" y="{sy + 22}">0</text>'
               f'<text class="t scale-t" x="{f(sx + half_mile)}" y="{sy + 22}" text-anchor="middle">½</text>'
               f'<text class="t scale-t" x="{f(sx + 2 * half_mile)}" y="{sy + 22}" text-anchor="middle">1 mile</text>')
    # Cartouche
    out.append('<g class="cart"><rect class="pf" x="610" y="40" width="250" height="96"/>'
               '<rect class="d thin" style="--d:1.5s" pathLength="1" x="610" y="40" width="250" height="96"/>'
               '<rect class="dg" style="--d:1.7s" pathLength="1" x="618" y="48" width="234" height="80"/>'
               '<text class="t cart-t" x="735" y="86" text-anchor="middle">PRIME LONDON</text>'
               '<text class="t cart-s" x="735" y="112" text-anchor="middle">Where I search</text></g>')
    return (f'<svg class="art art-map" viewBox="0 0 {MW} {MH}" role="img" aria-labelledby="map-t">'
            f'<title id="map-t">Illustrated map of prime London showing the River Thames, Hyde Park, '
            f'Regent’s Park and the ten neighbourhoods searched: '
            + ", ".join(a[0] for a in AREAS) + "</title>" + "".join(out) + "</svg>")


if __name__ == "__main__":
    import os
    here = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    os.makedirs(os.path.join(here, "assets", "art"), exist_ok=True)
    for name, fn in (("elevation", elevation), ("door", door), ("london-map", london_map)):
        svg = fn().replace("<svg ", '<svg xmlns="http://www.w3.org/2000/svg" ', 1)
        open(os.path.join(here, "assets", "art", name + ".svg"), "w").write(svg)
    print("ok")
