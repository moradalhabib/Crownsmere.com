// Draws the pages tools/brand.py wrote into brand/.build/: the three card PDFs (colour print, and the
// gold-foil base and layer) for tools/brand_print.py to finish, each side as a PNG, the digital card,
// and layout.json, which records where the ink of each element falls so the preflight can check it.
// tools/brand.py runs this; on its own:  PLAYWRIGHT_BROWSERS_PATH=/opt/pw-browsers node tools/brand-render.cjs
const fs = require('fs');
const path = require('path');
const { chromium } = require('@playwright/test');

const BRAND = path.join(__dirname, '..', 'brand');
const BUILD = path.join(BRAND, '.build');
const url = (f) => 'file://' + path.join(BUILD, f);
const MM = 96 / 25.4; // CSS pixels in a millimetre
const BLEED = 3 * MM;

// Runs in the page: the ink box of every element on each card, in mm from the trim's top-left corner.
// Text ink comes from the font's own glyph outlines (canvas measureText) on the element's baseline, so
// a descender or a tall letter is measured where it really is, not where its line box ends.
function measure() {
  const MM = 96 / 25.4;
  const ctx = document.createElement('canvas').getContext('2d');
  const out = { cards: [], minTextPt: Infinity, smallest: '' };
  for (const card of document.querySelectorAll('.card')) {
    const c = card.getBoundingClientRect();
    const ox = c.left + 3 * MM, oy = c.top + 3 * MM;
    const items = {};
    for (const el of card.querySelectorAll('.safe *')) {
      const cs = getComputedStyle(el);
      if (cs.visibility === 'hidden' || el.tagName === 'BR' || el.closest('svg') && el.tagName !== 'svg') continue;
      const key = (el.className.baseVal ?? el.className).split(' ').filter((c) => c && c !== 'foil')[0] || el.tagName.toLowerCase();
      const r = el.getBoundingClientRect();
      let box = { top: r.top, bottom: r.bottom, left: r.left, right: r.right };
      const ownText = [...el.childNodes].filter((n) => n.nodeType === 3).map((n) => n.textContent).join('').trim();
      if (ownText && el.tagName !== 'B') {
        // Smallest text size on the card
        const pt = parseFloat(cs.fontSize) * 0.75;
        if (pt < out.minTextPt) { out.minTextPt = pt; out.smallest = key + ' "' + ownText.slice(0, 24) + '"'; }
      }
      if (el.tagName === 'B' || el.tagName === 'EM') {
        const pt = parseFloat(cs.fontSize) * 0.75;
        if (pt < out.minTextPt) { out.minTextPt = pt; out.smallest = key + ' "' + el.textContent + '"'; }
      }
      if (ownText || el.matches('.lines, .tag, .est span')) {
        // Baseline of the first and last line, from zero-size markers placed in the text
        const first = document.createElement('span'), last = document.createElement('span');
        for (const m of [first, last]) m.style.cssText = 'display:inline-block;width:0;height:0;vertical-align:baseline';
        el.insertBefore(first, el.firstChild); el.appendChild(last);
        const b1 = first.getBoundingClientRect().bottom, b2 = last.getBoundingClientRect().bottom;
        first.remove(); last.remove();
        // Measured at 20 times the size: at the real size the browser rounds glyph bounds to whole pixels.
        ctx.font = `${cs.fontStyle} ${cs.fontWeight} ${parseFloat(cs.fontSize) * 20}px ${cs.fontFamily}`;
        const lines = el.innerText.split('\n');
        const m1 = ctx.measureText(lines[0]), m2 = ctx.measureText(lines[lines.length - 1]);
        box.top = b1 - m1.actualBoundingBoxAscent / 20;
        box.bottom = b2 + m2.actualBoundingBoxDescent / 20;
        box.baseline = b2;
      }
      const mm = {};
      for (const k in box) mm[k] = +(((k === 'left' || k === 'right') ? box[k] - ox : box[k] - oy) / MM).toFixed(3);
      items[key] = mm;
    }
    out.cards.push({ side: card.classList.contains('front') ? 'front' : 'back', items });
  }
  return out;
}

(async () => {
  const browser = await chromium.launch();

  // The print PDFs: two pages of 91 x 61 mm each. Fonts are embedded, the QR code and the foil
  // layer's monogram are vector, and the colour logo goes in at its full resolution.
  for (const mode of ['print', 'base', 'layer']) {
    const page = await browser.newPage();
    await page.goto(url(`card-${mode}.html`));
    await page.evaluate(() => document.fonts.ready);
    if (mode === 'print') fs.writeFileSync(path.join(BUILD, 'layout.json'), JSON.stringify(await page.evaluate(measure), null, 1));
    await page.pdf({ path: path.join(BUILD, `card-${mode}-rgb.pdf`), preferCSSPageSize: true, printBackground: true });
    await page.close();
  }

  // Each side, trimmed to 85 x 55 mm, at about 380 dpi.
  let page = await browser.newPage({ deviceScaleFactor: 4, viewport: { width: 600, height: 800 } });
  await page.goto(url('card-print.html'));
  await page.evaluate(() => document.fonts.ready);
  const cards = await page.locator('.card').all();
  const names = ['front', 'back'];
  for (let i = 0; i < cards.length; i++) {
    const b = await cards[i].boundingBox();
    await page.screenshot({
      path: path.join(BRAND, `crownsmere-card-${names[i]}.png`),
      clip: { x: b.x + BLEED, y: b.y + BLEED, width: b.width - 2 * BLEED, height: b.height - 2 * BLEED }
    });
  }
  await page.close();

  // Both sides together, to send by email, WhatsApp or LinkedIn.
  page = await browser.newPage({ deviceScaleFactor: 1.25, viewport: { width: 1600, height: 640 } });
  await page.goto(url('share-card.html'));
  await page.evaluate(() => document.fonts.ready);
  await page.screenshot({ path: path.join(BRAND, 'crownsmere-digital-card.png') });
  await page.close();

  await browser.close();
  console.log('Drew the card pages: three print drafts, both sides as PNGs, the digital card and layout.json');
})().catch((err) => { console.error(err); process.exit(1); });
