"""Finishes the business card print files that tools/brand-render.cjs drafted, checks them, and draws a proof.

tools/brand.py runs this at the end. Each print file is:
- Print colour (CMYK), converted from screen colour (sRGB) with ISO Coated v2 300% (ECI), the FOGRA39
  standard most UK and European printers work to. It also caps the ink at 300%, so the navy dries and
  does not rub off. The profile is embedded as the file's output intent.
- Text as outlines, so no font can go missing or change at the printer.
- Exactly 91 x 61 mm, with the TrimBox (85 x 55 mm) and BleedBox set, so the printer's software knows
  where to cut.
For gold foil there are two more: the base (the colour print with the foil areas left empty) and the
layer (the foil areas alone, solid black, one ink).

Needs Ghostscript, qpdf and poppler-utils (pdffonts, pdfimages, pdftoppm), plus pypdf, numpy, zxing-cpp and
opencv-python-headless for the checks. The colour profile is in Debian's and Ubuntu's icc-profiles package;
elsewhere, download ISO Coated v2 300% from eci.org and set CMYK_PROFILE to its path.
"""
import io, json, os, re, subprocess, tempfile

import numpy as np
from PIL import Image, ImageDraw, ImageFont
from pypdf import PdfReader, PdfWriter
from pypdf.generic import (ArrayObject, DictionaryObject, NameObject, NumberObject, RectangleObject,
                           StreamObject, TextStringObject)

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
BRAND = os.path.join(ROOT, "brand")
BUILD = os.path.join(BRAND, ".build")
ICC = os.environ.get("CMYK_PROFILE", "/usr/share/color/icc/ISOcoated_v2_300_eci.icc")
SITE = "https://crownsmere.com/"

PT = 72 / 25.4                       # PDF points in a millimetre
W, H, BLEED = 91 * PT, 61 * PT, 3 * PT
TRIM_W, TRIM_H, SAFE = 85, 55, 4     # mm
EXTRA = {"front": "crownsmere-business-card-front.pdf", "back": "crownsmere-business-card-back.pdf",
         "crop": "crownsmere-business-card-print-crop-marks.pdf"}
FILES = {"print": "crownsmere-business-card-print.pdf",
         "base": "crownsmere-business-card-foil-base.pdf",
         "layer": "crownsmere-business-card-foil-layer.pdf"}


def run(*cmd, **kw):
    return subprocess.run(cmd, check=True, capture_output=True, text=True, **kw).stdout


def gs(*args):
    run("gs", "-q", "-dSAFER", "-dBATCH", "-dNOPAUSE", *args)


def convert(mode):
    src, tmp = os.path.join(BUILD, f"card-{mode}-rgb.pdf"), os.path.join(BUILD, f"card-{mode}-gs.pdf")
    keep = ["-dDownsampleColorImages=false", "-dDownsampleGrayImages=false", "-dDownsampleMonoImages=false",
            "-dAutoFilterColorImages=false", "-dColorImageFilter=/FlateEncode",   # images kept whole and lossless
            "-dAutoFilterGrayImages=false", "-dGrayImageFilter=/FlateEncode"]
    if mode == "layer":   # one ink: black only
        colour = ["-sColorConversionStrategy=Gray", "-sProcessColorModel=DeviceGray"]
    else:                 # relative colorimetric with black point compensation, the usual prepress choice
        colour = ["-sColorConversionStrategy=CMYK", "-sProcessColorModel=DeviceCMYK",
                  f"-sOutputICCProfile={ICC}", "-dRenderIntent=1", "-dBlackPtComp=1"]
    # The drafts are drawn 8 times larger (see PRINT_ZOOM in tools/brand.py); fitting them to the card
    # scales every outline, rule and image down exactly.
    fit = [f"-dDEVICEWIDTHPOINTS={W:.4f}", f"-dDEVICEHEIGHTPOINTS={H:.4f}", "-dFIXEDMEDIA", "-dPDFFitPage"]
    gs("-sDEVICE=pdfwrite", "-dCompatibilityLevel=1.6", "-dNoOutputFonts", "-dAutoRotatePages=/None",
       *fit, *keep, *colour, f"-sOutputFile={tmp}", src)

    reader = PdfReader(tmp)
    writer = PdfWriter(clone_from=reader)
    for page in writer.pages:
        # Ghostscript has already made the page 91 x 61 mm; the boxes are set from the top-left corner.
        top = float(page.mediabox.top)
        media = RectangleObject([0, round(top - H, 4), round(W, 4), top])
        page.mediabox = page.cropbox = page.bleedbox = media
        page.trimbox = RectangleObject([round(BLEED, 4), round(top - H + BLEED, 4), round(W - BLEED, 4), round(top - BLEED, 4)])
    titles = {"print": "business card, print file (CMYK)", "base": "business card, gold foil: base (CMYK)",
              "layer": "business card, gold foil: foil layer (solid black)"}
    writer.add_metadata({"/Title": f"Crownsmere Estate {titles[mode]}", "/Author": "Crownsmere Estate",
                         "/Subject": "85 x 55 mm with 3 mm bleed; page 1 front, page 2 back",
                         "/Trapped": NameObject("/False")})
    if mode != "layer":
        add_output_intent(writer)
    with open(os.path.join(BRAND, FILES[mode]), "wb") as f:
        writer.write(f)


def add_output_intent(writer):
    icc = StreamObject()
    icc.set_data(open(ICC, "rb").read())
    icc[NameObject("/N")] = NumberObject(4)
    intent = DictionaryObject({
        NameObject("/Type"): NameObject("/OutputIntent"), NameObject("/S"): NameObject("/GTS_PDFX"),
        NameObject("/OutputConditionIdentifier"): TextStringObject("FOGRA39"),
        NameObject("/RegistryName"): TextStringObject("http://www.color.org"),
        NameObject("/Info"): TextStringObject("ISO Coated v2 300% (ECI)"),
        NameObject("/DestOutputProfile"): writer._add_object(icc.flate_encode())})
    writer._root_object[NameObject("/OutputIntents")] = ArrayObject([writer._add_object(intent)])


# Crop marks: a 105 x 75 mm page with the card's bleed area in the middle (trim 10 mm from each edge), and
# 0.25 pt marks in solid black on the trim lines, starting 4 mm out from the trim (clear of the bleed).
CROP_PAGE, CROP_AT, MARK_GAP, MARK_LEN = (105, 75), 7, 4, 5    # mm


def other_versions():
    """From the finished print file: each side on its own (for upload forms that ask for front and back
    separately) and a copy with crop marks (for print shops that cut by hand). The artwork is the same file."""
    src = os.path.join(BRAND, FILES["print"])
    for keep, name in ((0, "front"), (1, "back")):
        writer = PdfWriter(clone_from=src)
        writer.remove_page(1 - keep)
        writer.add_metadata({"/Title": f"Crownsmere Estate business card, {name} (CMYK)",
                             "/Subject": f"85 x 55 mm with 3 mm bleed; the {name} only"})
        with open(os.path.join(BRAND, EXTRA[name]), "wb") as f:
            writer.write(f)
        # Rewritten by qpdf, which keeps only what the page uses (the other side's images go).
        done = subprocess.run(["qpdf", "--replace-input", os.path.join(BRAND, EXTRA[name])], capture_output=True)
        assert done.returncode in (0, 3), done.stderr

    writer = PdfWriter(clone_from=src)
    pw, ph, at = CROP_PAGE[0] * PT, CROP_PAGE[1] * PT, CROP_AT * PT
    t0x, t0y = at + BLEED, at + BLEED                    # trim corners on the new page
    t1x, t1y = t0x + TRIM_W * PT, t0y + TRIM_H * PT
    g, l = MARK_GAP * PT, MARK_LEN * PT
    marks = []
    for y in (t0y, t1y):
        marks += [(t0x - g - l, y, t0x - g, y), (t1x + g, y, t1x + g + l, y)]
    for x in (t0x, t1x):
        marks += [(x, t0y - g - l, x, t0y - g), (x, t1y + g, x, t1y + g + l)]
    for page in writer.pages:
        mb = page.mediabox
        # The card goes in as a form, which clips it to its own 91 x 61 mm, so nothing can reach the marks.
        form = StreamObject()
        form.set_data(page.get_contents().get_data())
        form.update({NameObject("/Type"): NameObject("/XObject"), NameObject("/Subtype"): NameObject("/Form"),
                     NameObject("/BBox"): RectangleObject([mb.left, mb.bottom, mb.right, mb.top]),
                     NameObject("/Resources"): page["/Resources"]})
        if "/Group" in page:
            form[NameObject("/Group")] = page["/Group"]
        ref = writer._add_object(form.flate_encode())
        content = StreamObject()
        lines = " ".join(f"{a:.3f} {b:.3f} m {c:.3f} {d:.3f} l S" for a, b, c, d in marks)
        content.set_data((f"q 1 0 0 1 {at - float(mb.left):.4f} {at - float(mb.bottom):.4f} cm /Card Do Q\n"
                          f"q 0 0 0 1 K 0.25 w 0 J {lines} Q\n").encode())
        page[NameObject("/Contents")] = writer._add_object(content.flate_encode())
        page[NameObject("/Resources")] = DictionaryObject({NameObject("/XObject"): DictionaryObject({NameObject("/Card"): ref})})
        page.mediabox = page.cropbox = RectangleObject([0, 0, pw, ph])
        page.bleedbox = RectangleObject([at, at, at + W, at + H])
        page.trimbox = RectangleObject([t0x, t0y, t1x, t1y])
    writer.add_metadata({"/Title": "Crownsmere Estate business card with crop marks (CMYK)",
                         "/Subject": "85 x 55 mm with 3 mm bleed and crop marks on a 105 x 75 mm page; page 1 front, page 2 back"})
    with open(os.path.join(BRAND, EXTRA["crop"]), "wb") as f:
        writer.write(f)


# --- Checks ---------------------------------------------------------------------------------------------

class Report:
    def __init__(self):
        self.lines, self.failed = [], 0

    def check(self, ok, text):
        self.lines.append(("PASS  " if ok else "FAIL  ") + text)
        self.failed += not ok

    def note(self, text):
        self.lines.append("      " + text)

    def head(self, text):
        self.lines.append("\n" + text)


def colour_usage(pdf):
    """Colour spaces and colour operators in every object, read from an uncompressed copy."""
    with tempfile.TemporaryDirectory() as d:
        flat = os.path.join(d, "flat.pdf")
        subprocess.run(["qpdf", "--qdf", "--object-streams=disable", pdf, flat], check=False, capture_output=True)
        data = open(flat, "rb").read().decode("latin-1")
    rgb_spaces = len(re.findall(r"/DeviceRGB|/CalRGB|/Lab\b", data))
    rgb_ops = len(re.findall(r"(?:^|\s)(?:-?[\d.]+\s+){3}(?:rg|RG)\b", data))
    cmyk_ops = len(re.findall(r"(?:^|\s)(?:-?[\d.]+\s+){4}(?:k|K)\b", data))
    gray_vals = re.findall(r"(?:^|\s)(-?[\d.]+)\s+(?:g|G)\b", data)
    spot = len(re.findall(r"/Separation|/DeviceN", data))
    return rgb_spaces, rgb_ops, cmyk_ops, gray_vals, spot


def render(pdf, dpi, page=None, device="png16m", soft_proof=False, trim=False):
    with tempfile.TemporaryDirectory() as d:
        out = os.path.join(d, "p%d.tif" if device.startswith("tiff") else "p%d.png")
        args = [f"-sDEVICE={device}", f"-r{dpi}", "-dTextAlphaBits=4", "-dGraphicsAlphaBits=4"]
        if soft_proof:   # show the CMYK as the press would print it on coated paper
            args += [f"-sDefaultCMYKProfile={ICC}"]
        if page:
            args += [f"-dFirstPage={page}", f"-dLastPage={page}"]
        if trim:
            args += ["-dUseTrimBox"]
        gs(*args, f"-sOutputFile={out}", pdf)
        return [Image.open(os.path.join(d, f)).copy() for f in sorted(os.listdir(d))]


def qr_reads(im):
    import cv2, zxingcpp
    z = [r.text for r in zxingcpp.read_barcodes(im)] == [SITE]
    o = cv2.QRCodeDetector().detectAndDecode(cv2.cvtColor(np.array(im.convert("RGB")), cv2.COLOR_RGB2BGR))[0] == SITE
    return z, o


def ink_box(mask, near, pad=0.6):
    """The ink inside an element's rough box (from the browser's layout, widened by pad mm), in mm from the
    trim. The baseline is the lowest row that many letters stand on; descenders below it are sparse."""
    mm = mask.shape[1] / TRIM_W
    y0, x0 = max(0, int((near["top"] - pad) * mm)), max(0, int((near["left"] - pad) * mm))
    sub = mask[y0:int((near["bottom"] + pad) * mm), x0:int((near["right"] + pad) * mm)]
    count = sub.sum(axis=1)
    rows, cols = np.where(count > 0)[0], np.where(sub.any(axis=0))[0]
    busy = np.where(count >= 0.25 * count.max())[0]
    return {"top": (y0 + rows.min()) / mm, "bottom": (y0 + rows.max() + 1) / mm, "baseline": (y0 + busy.max() + 1) / mm,
            "left": (x0 + cols.min()) / mm, "right": (x0 + cols.max() + 1) / mm}


def preflight():
    r = Report()
    layout = json.load(open(os.path.join(BUILD, "layout.json")))
    pdf = os.path.join(BRAND, FILES["print"])

    r.head("Print file: " + FILES["print"])
    reader = PdfReader(pdf)
    r.check(len(reader.pages) == 2, f"2 pages, front then back ({len(reader.pages)})")
    for i, page in enumerate(reader.pages, 1):
        mb, tb, bb = page.mediabox, page.trimbox, page.bleedbox
        size = (float(mb.width) / PT, float(mb.height) / PT)
        trim = (float(tb.width) / PT, float(tb.height) / PT)
        insets = [(float(tb.left) - float(mb.left)) / PT, (float(mb.right) - float(tb.right)) / PT,
                  (float(tb.bottom) - float(mb.bottom)) / PT, (float(mb.top) - float(tb.top)) / PT]
        r.check(abs(size[0] - 91) < 0.01 and abs(size[1] - 61) < 0.01, f"page {i}: {size[0]:.2f} x {size[1]:.2f} mm, card plus bleed")
        r.check(abs(trim[0] - 85) < 0.01 and abs(trim[1] - 55) < 0.01, f"page {i}: TrimBox {trim[0]:.2f} x {trim[1]:.2f} mm")
        r.check(all(abs(x - 3) < 0.01 for x in insets), f"page {i}: bleed {min(insets):.2f} to {max(insets):.2f} mm on every side")
        r.check(list(bb) == list(mb), f"page {i}: BleedBox matches the page")

    rgb_spaces, rgb_ops, cmyk_ops, _, spot = colour_usage(pdf)
    r.check(rgb_spaces == 0 and rgb_ops == 0, f"no screen (RGB) colour anywhere ({rgb_spaces} colour spaces, {rgb_ops} colour settings)")
    r.check(cmyk_ops > 0 and spot == 0, f"process colour only: {cmyk_ops} CMYK colour settings, no spot colours")
    r.check(len(reader.trailer["/Root"].get("/OutputIntents", [])) == 1, "output intent: ISO Coated v2 300% (FOGRA39) embedded")

    fonts = run("pdffonts", pdf).strip().splitlines()[2:]
    r.check(not fonts, f"all text converted to outlines ({len(fonts)} fonts left)")

    imgs = [l.split() for l in run("pdfimages", "-list", pdf).splitlines()[2:]]
    colour_imgs = [l for l in imgs if l[2] == "image"]
    r.check(all(l[5] == "cmyk" for l in colour_imgs), f"images in CMYK ({', '.join(l[5] for l in colour_imgs)})")
    ppi = min(min(int(l[12]), int(l[13])) for l in colour_imgs)
    r.check(ppi >= 300, f"image resolution at least 300 ppi (lowest {ppi} ppi)")

    pages = render(pdf, 300, device="tiff32nc")
    for i, im in enumerate(pages, 1):
        tac = np.asarray(im, dtype=np.uint16).sum(axis=2) / 255 * 100
        r.check(tac.max() <= 300.5, f"page {i}: total ink at most 300% (highest {tac.max():.0f}%)")
        if i == 1:
            c, m, y, k = (np.asarray(im)[30, 30] / 255 * 100).round()
            r.note(f"navy at the corner of the front: C{c:.0f} M{m:.0f} Y{y:.0f} K{k:.0f}")

    r.head("Layout, measured in the print files at 1200 dpi (mm from the trim)")
    r.check(layout["minTextPt"] >= 6, f'smallest text {layout["minTextPt"]:.1f} pt ({layout["smallest"]}); printers ask for 6 pt or more')
    # The browser's layout (layout.json) only says roughly where each element is; the positions checked
    # here are the ink in the print file itself. The front is read from the foil layer, which holds every
    # element of the front in solid black on white.
    front_items = next(c for c in layout["cards"] if c["side"] == "front")["items"]
    back_items = next(c for c in layout["cards"] if c["side"] == "back")["items"]
    fl = np.asarray(render(os.path.join(BRAND, FILES["layer"]), 1200, page=1, device="pnggray", trim=True)[0]) < 128
    bg = np.asarray(render(pdf, 1200, page=2, device="pnggray", soft_proof=True, trim=True)[0]).astype(int)
    bk = np.abs(bg - int(np.median(bg[20:200, 20:200]))) > 40
    F = {k: ink_box(fl, front_items[k]) for k in ("mono", "wm", "est")}
    B = {k: ink_box(bk, back_items[k]) for k in ("name", "role", "rule", "lines", "tag", "mono", "qr")}
    for side, boxes, mask in (("front", F, fl), ("back", B, bk)):
        mm = mask.shape[1] / TRIM_W
        rows, cols = np.where(mask.any(axis=1))[0], np.where(mask.any(axis=0))[0]
        near = min(rows.min() / mm, cols.min() / mm, TRIM_W - (cols.max() + 1) / mm, TRIM_H - (rows.max() + 1) / mm)
        r.check(near >= SAFE - 0.01, f"{side}: all ink at least {SAFE} mm inside the trim (closest {near:.2f} mm)")
    top, bottom = min(b["top"] for b in F.values()), max(b["bottom"] for b in F.values())
    left, right = min(b["left"] for b in F.values()), max(b["right"] for b in F.values())
    lift = TRIM_H / 2 - (top + bottom) / 2
    r.check(0.8 <= lift <= 1.6, f"front: logo group {lift:.2f} mm above the true centre (the optical centre)")
    r.check(abs((left + right) / 2 - TRIM_W / 2) <= 0.05, f"front: centred across ({(left + right) / 2 - TRIM_W / 2:+.3f} mm)")
    name, mono, tag, qr = B["name"], B["mono"], B["tag"], B["qr"]
    r.check(abs(name["top"] - mono["top"]) <= 0.05, f"back: tops of the name and the monogram level ({name['top']:.3f}, {mono['top']:.3f})")
    r.check(abs(tag["baseline"] - qr["bottom"]) <= 0.05, f"back: tagline baseline level with the foot of the QR code ({tag['baseline']:.3f}, {qr['bottom']:.3f})")
    r.check(abs(mono["right"] - qr["right"]) <= 0.05, f"back: monogram and QR code share a right edge ({mono['right']:.3f}, {qr['right']:.3f})")
    lefts = {k: B[k]["left"] for k in ("name", "role", "rule", "lines", "tag")}
    r.check(max(lefts.values()) - min(lefts.values()) <= 0.2,
            "back: left column on one edge (" + ", ".join(f"{k} {v:.2f}" for k, v in lefts.items()) + ")")
    module = (qr["right"] - qr["left"]) / 25
    others = [b for k, b in B.items() if k != "qr"]
    gap_left = min(qr["left"] - b["right"] for b in others if b["bottom"] > qr["top"] and b["top"] < qr["bottom"] and b["right"] <= qr["left"])
    gap_top = min(qr["top"] - b["bottom"] for b in others if b["right"] > qr["left"] and b["bottom"] <= qr["top"])
    quiet = min(gap_left, gap_top, TRIM_W - qr["right"], TRIM_H - qr["bottom"])
    r.check(abs(module - 0.68) < 0.01 and quiet >= 4 * module,
            f"QR code: {module:.3f} mm modules, clear space of at least 4 modules ({quiet / module:.1f})")

    r.head("QR code (opens " + SITE + ")")
    back = render(pdf, 300, page=2, soft_proof=True)[0].convert("RGB")
    r.check(all(qr_reads(back)), "reads from the print file at 300 dpi (two different readers)")
    small = back.resize((back.width * 600 // 1004 // 2, back.height * 600 // 1004 // 2), Image.LANCZOS)
    r.check(qr_reads(small)[0], "reads from a small, low-resolution photo of the card (about 6 pixels per mm)")

    r.head("Other versions of the print file (same artwork)")
    proofs = render(pdf, 150, soft_proof=True, trim=True)
    for key, pages in (("front", [1]), ("back", [2]), ("crop", [1, 2])):
        f = os.path.join(BRAND, EXTRA[key])
        pp = PdfReader(f).pages
        ok = len(pp) == len(pages)
        for x in pp:
            size = (float(x.mediabox.width) / PT, float(x.mediabox.height) / PT)
            trim = (float(x.trimbox.width) / PT, float(x.trimbox.height) / PT)
            want = CROP_PAGE if key == "crop" else (91, 61)
            ok &= abs(size[0] - want[0]) < 0.01 and abs(size[1] - want[1]) < 0.01 and abs(trim[0] - 85) < 0.01 and abs(trim[1] - 55) < 0.01
        rgb_spaces, rgb_ops, cmyk_ops, _, spot = colour_usage(f)
        ok &= rgb_spaces == rgb_ops == spot == 0 and not run("pdffonts", f).strip().splitlines()[2:]
        ok &= len(PdfReader(f).trailer["/Root"].get("/OutputIntents", [])) == 1
        same = max(float(np.abs(np.asarray(a.convert("RGB"), int) - np.asarray(proofs[n - 1].convert("RGB"), int)).mean())
                   for a, n in zip(render(f, 150, soft_proof=True, trim=True), pages))
        ok &= same < 0.5
        r.check(ok, f"{EXTRA[key]}: {len(pp)} page(s), {'105 x 75 mm with crop marks' if key == 'crop' else '91 x 61 mm'}, "
                f"trim 85 x 55 mm, CMYK, outlines, artwork identical to the print file (difference {same:.2f} of 255)")
    # Every mark where it belongs, and nothing else outside the bleed (positions in mm from the top-left).
    for n in (1, 2):
        ink = np.asarray(render(os.path.join(BRAND, EXTRA["crop"]), 600, page=n, device="pnggray")[0]) < 160
        mmc = ink.shape[1] / CROP_PAGE[0]
        box = lambda x0, x1, y0, y1: (slice(int(y0 * mmc), int(y1 * mmc) + 1), slice(int(x0 * mmc), int(x1 * mmc) + 1))
        t0, t1x, t1y, b0 = CROP_AT + 3, CROP_AT + 3 + TRIM_W, CROP_AT + 3 + TRIM_H, CROP_AT
        outside = ink.copy()
        outside[box(b0, b0 + 91, b0, b0 + 61)] = False
        want, tol = [], 0.3
        for y in (t0, t1y):
            for x0 in (t0 - MARK_GAP - MARK_LEN, t1x + MARK_GAP):
                want.append(box(x0 - tol, x0 + MARK_LEN + tol, y - tol, y + tol))
        for x in (t0, t1x):
            for y0 in (t0 - MARK_GAP - MARK_LEN, t1y + MARK_GAP):
                want.append(box(x - tol, x + tol, y0 - tol, y0 + MARK_LEN + tol))
        expected = np.zeros_like(ink)
        for w_ in want:
            expected[w_] = True
        present = sum(bool(ink[w_].any()) for w_ in want)
        stray = int((outside & ~expected).sum())
        r.check(present == 8 and stray == 0,
                f"crop marks, page {n}: {present} of 8 on the trim lines, {MARK_GAP} mm clear of the trim, nothing else outside the bleed")

    r.head("Gold foil pair")
    base, layer = os.path.join(BRAND, FILES["base"]), os.path.join(BRAND, FILES["layer"])
    for f in (base, layer):
        p = PdfReader(f).pages
        r.check(all(abs(float(x.mediabox.width) - W) < 0.03 and abs(float(x.trimbox.width) - TRIM_W * PT) < 0.03 for x in p),
                f"{os.path.basename(f)}: same page and trim as the print file")
    rgb_spaces, rgb_ops, cmyk_ops, gray_vals, spot = colour_usage(layer)
    r.check(rgb_spaces == rgb_ops == cmyk_ops == spot == 0 and gray_vals and all(float(v) == 0 for v in gray_vals),
            f"foil layer: one ink, solid black only ({len(gray_vals)} fills, all 100%)")
    r.check(not run("pdffonts", layer).strip().splitlines()[2:], "foil layer: text as outlines")
    # Measured in the print geometry itself (the foil layer at 1200 dpi): the rules beside ESTATE level
    # with the middle of its capitals.
    front = next(c for c in layout["cards"] if c["side"] == "front")["items"]
    ink = np.asarray(render(layer, 1200, page=1, device="pnggray", trim=True)[0]) < 128
    mm = ink.shape[1] / TRIM_W
    def rows(b):
        sub = ink[int((b["top"] - 0.5) * mm):int((b["bottom"] + 0.5) * mm), int(b["left"] * mm):int(b["right"] * mm)]
        r_ = np.where(sub.any(axis=1))[0]
        return (r_.min() + r_.max() + 1) / 2 / mm + b["top"] - 0.5
    gap = rows(front["i"]) - rows(front["span"])
    r.check(abs(gap) <= 0.03, f"front: ESTATE rules level with the middle of the capitals ({gap:+.3f} mm)")
    lp = render(layer, 600, device="pnggray")
    bp = render(base, 150, device="png16m")
    covered = [(np.asarray(im) < 128).mean() * 100 for im in lp]
    r.check(all(c > 0 for c in covered), f"foil layer: foil on both sides ({covered[0]:.1f}% of the front, {covered[1]:.1f}% of the back)")
    r.note("foil: the monogram, CROWNSMERE, ESTATE and its rules on the front; the monogram and the rule on the back")
    r.note("finest foil detail: 0.2 mm rules and 6.5 pt ESTATE; check the printer's foil minimums (usually 0.1 to 0.2 mm lines, 6 to 8 pt text)")

    text = ("Crownsmere Estate business card: preflight report\n"
            "Made by tools/brand.py. Card 85 x 55 mm, 3 mm bleed, 4 mm safe area, ISO Coated v2 300% (FOGRA39).\n"
            + "\n".join(r.lines) + f"\n\n{'All checks passed.' if not r.failed else str(r.failed) + ' check(s) FAILED.'}\n")
    with open(os.path.join(BRAND, "crownsmere-business-card-preflight.txt"), "w") as f:
        f.write(text)
    print(text)
    return r.failed


# --- Proof ----------------------------------------------------------------------------------------------

def proof():
    """Both sides as the press will print them (soft proof from the CMYK file), with the trim, bleed and
    safe lines drawn on, and the gold-foil version beside them."""
    dpi = 220
    px = dpi / 25.4
    font_dir = os.path.join(BUILD, "fonts")
    f_title = ImageFont.truetype(os.path.join(font_dir, "cormorant-garamond-500.ttf"), 46)
    f_label = ImageFont.truetype(os.path.join(font_dir, "inter-latin-500.ttf"), 19)
    f_small = ImageFont.truetype(os.path.join(font_dir, "inter-latin-400.ttf"), 17)

    printed = [p.convert("RGB") for p in render(os.path.join(BRAND, FILES["print"]), dpi, soft_proof=True)]
    base = [p.convert("RGB") for p in render(os.path.join(BRAND, FILES["base"]), dpi, soft_proof=True)]
    layer = [p.convert("L") for p in render(os.path.join(BRAND, FILES["layer"]), dpi, device="pnggray")]

    def foiled(b, l):
        # Foil drawn as a soft metallic gold over the base, with a light sheen from the top left
        w, h = b.size
        yy, xx = np.mgrid[0:h, 0:w]
        t = ((xx / w) * 0.6 + (yy / h) * 0.4)
        sheen = 0.5 + 0.5 * np.cos((t * 2.2 + 0.15) * np.pi)
        lo, hi = np.array([168, 128, 62]), np.array([246, 222, 160])
        gold = (lo + (hi - lo) * sheen[..., None]).astype(np.uint8)
        mask = (255 - np.asarray(l, dtype=np.uint8))[..., None] / 255.0
        out = np.asarray(b) * (1 - mask) + gold * mask
        return Image.fromarray(out.astype(np.uint8))

    pw, ph = printed[0].size
    gap, margin, head = 70, 80, 150
    sheet = Image.new("RGB", (margin * 2 + pw * 2 + gap, head + (ph + 90) * 2 + margin), "#f4f1ec")
    d = ImageDraw.Draw(sheet)
    d.text((margin, 50), "Crownsmere Estate · business card proof", font=f_title, fill="#0e1b2e")
    d.text((margin, 108), "Soft proof of the CMYK print files on coated paper (ISO Coated v2 300%). Not to scale on screen.",
           font=f_small, fill="#4a5263")

    def guides(x0, y0):
        b, s = 3 * px, 7 * px
        # bleed: everything outside the trim is cut off
        d.rectangle([x0, y0, x0 + pw - 1, y0 + ph - 1], outline="#9aa3b2", width=1)
        d.rectangle([x0 + b, y0 + b, x0 + pw - b, y0 + ph - b], outline="#d6342c", width=2)
        for x in np.arange(x0 + s, x0 + pw - s, 14):
            d.line([x, y0 + s, min(x + 7, x0 + pw - s), y0 + s], fill="#2f6fd6", width=1)
            d.line([x, y0 + ph - s, min(x + 7, x0 + pw - s), y0 + ph - s], fill="#2f6fd6", width=1)
        for y in np.arange(y0 + s, y0 + ph - s, 14):
            d.line([x0 + s, y, x0 + s, min(y + 7, y0 + ph - s)], fill="#2f6fd6", width=1)
            d.line([x0 + pw - s, y, x0 + pw - s, min(y + 7, y0 + ph - s)], fill="#2f6fd6", width=1)

    cols = [("Print file", printed), ("With gold foil", [foiled(b, l) for b, l in zip(base, layer)])]
    for ci, (title, imgs) in enumerate(cols):
        x0 = margin + ci * (pw + gap)
        for ri, (side, im) in enumerate(zip(("Front", "Back"), imgs)):
            y0 = head + ri * (ph + 90) + 40
            d.text((x0, y0 - 34), f"{title} · {side}", font=f_label, fill="#0e1b2e")
            sheet.paste(im, (x0, y0))
            if ci == 0:
                guides(x0, y0)
    y = sheet.height - margin + 18
    for i, (colour, label) in enumerate((("#d6342c", "Trim: 85 × 55 mm, where the card is cut"),
                                         ("#2f6fd6", "Safe area: 4 mm inside the trim"),
                                         ("#9aa3b2", "Bleed: 3 mm beyond the trim, cut away"))):
        x = margin + i * 560
        d.line([x, y + 11, x + 34, y + 11], fill=colour, width=3)
        d.text((x + 46, y), label, font=f_small, fill="#4a5263")
    sheet.save(os.path.join(BRAND, "crownsmere-business-card-proof.png"), optimize=True)


def printer_notes():
    """A note to send the print shop with the files."""
    text = f"""Crownsmere Estate: business card for Alaa Qadir
Print instructions

FILE TO PRINT: {FILES["print"]}
  - Finished size: 85 x 55 mm (UK standard), landscape, printed both sides.
  - Page 1 is the front, page 2 the back, both the same way up.
  - 3 mm bleed on every side (each page is 91 x 61 mm); the trim box is set in the PDF.
  - CMYK, ISO Coated v2 300% (FOGRA39). Text is outlined; images are 300 ppi or more.

SAME ARTWORK, IF YOU NEED IT ANOTHER WAY
  - {EXTRA["front"]} and {EXTRA["back"]}: one side each.
  - {EXTRA["crop"]}: with crop marks, on a 105 x 75 mm page.

GOLD FOIL (OPTIONAL)
  - {FILES["base"]}: print this in CMYK.
  - {FILES["layer"]}: the foil areas in solid black (gold foil on the monogram,
    CROWNSMERE and ESTATE with its rules on the front; the monogram and the rule on the back).

PLEASE
  - Use board of 400 gsm or more, with a matt or soft-touch finish.
  - Send a printed proof before the full run: the navy is close to the darkest colour the paper can hold.
"""
    with open(os.path.join(BRAND, "crownsmere-business-card-printer-notes.txt"), "w") as f:
        f.write(text)


def finish():
    for mode in FILES:
        convert(mode)
    other_versions()
    failed = preflight()
    proof()
    printer_notes()
    print("Wrote brand/: " + ", ".join([*FILES.values(), *EXTRA.values()]) +
          ", crownsmere-business-card-preflight.txt, -proof.png and -printer-notes.txt")
    if failed:
        raise SystemExit(f"{failed} preflight check(s) failed: see brand/crownsmere-business-card-preflight.txt")


if __name__ == "__main__":
    finish()
