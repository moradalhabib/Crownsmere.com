// Turns the pages tools/brand.py wrote into files: the print PDF, each side as a PNG, and the
// digital card image. Run after tools/brand.py:
//   PLAYWRIGHT_BROWSERS_PATH=/opt/pw-browsers node tools/brand-render.cjs
const path = require('path');
const { chromium } = require('@playwright/test');

const BRAND = path.join(__dirname, '..', 'brand');
const url = (f) => 'file://' + path.join(BRAND, f);
const MM = 96 / 25.4; // CSS pixels in a millimetre
const BLEED = 3 * MM;

(async () => {
  const browser = await chromium.launch();

  // Print file: two pages of 91 x 61 mm (85 x 55 mm card with 3 mm bleed). Fonts are embedded,
  // the QR code stays vector, and the logo goes in at its full resolution.
  let page = await browser.newPage();
  await page.goto(url('card.html'));
  await page.evaluate(() => document.fonts.ready);
  await page.pdf({ path: path.join(BRAND, 'crownsmere-business-card-print.pdf'), preferCSSPageSize: true, printBackground: true });
  await page.close();

  // Each side, trimmed to 85 x 55 mm, at about 380 dpi.
  page = await browser.newPage({ deviceScaleFactor: 4, viewport: { width: 600, height: 800 } });
  await page.goto(url('card.html'));
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
  console.log('Wrote brand/: crownsmere-business-card-print.pdf, crownsmere-card-front.png, crownsmere-card-back.png, crownsmere-digital-card.png');
})().catch((err) => { console.error(err); process.exit(1); });
