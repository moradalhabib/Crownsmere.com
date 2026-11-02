const { test, expect } = require('@playwright/test');

/* The Private Collection (properties for sale, from tools/listings.py). It is built only once Crownsmere's
 * redress scheme and anti-money-laundering supervisor are filled in, so these tests cover both states. */

const corePages = ['/', '/services.html', '/about.html', '/contact.html'];

test('Private Collection: unpublished means unlinked; published means every property page tells buyers what they must know', async ({page, request}) => {
  const res = await request.get('/collection.html');
  if (res.status() !== 200) {
    for (const url of corePages) {
      await page.goto(url);
      await expect(page.locator('a[href="collection.html"], a[href^="property-"]'), url).toHaveCount(0);
    }
    return;
  }

  await page.goto('/collection.html');
  const cards = page.locator('a.lst-card');
  expect(await cards.count()).toBeGreaterThan(0);
  const hrefs = await cards.evaluateAll(as => as.map(a => a.getAttribute('href')));
  for (const href of hrefs) {
    await page.goto('/' + href);
    await expect(page.locator('h1')).toHaveCount(1);
    await expect(page.locator('.lst-price')).toContainText('£');
    const mi = page.locator('#material-information');
    for (const label of ['Price', 'Tenure', 'Council tax', 'Energy performance (EPC)', 'Property type', 'Electricity',
                         'Water', 'Sewerage', 'Heating', 'Broadband', 'Mobile signal', 'Parking', 'Occupancy',
                         'Building safety', 'Restrictions', 'Rights and easements', 'Flood risk', 'Planning', 'Accessibility']) {
      await expect(mi.locator('dt', {hasText: new RegExp('^' + label.replace(/[()]/g, '\\$&') + '$')}), href + ': ' + label).toHaveCount(1);
    }
    await expect(mi).not.toContainText(/ask agent|\bTBC\b/i);
    // The enquiry opens the contact form with this property named on it.
    const ask = page.locator('.lst-ask a.btn-primary');
    const target = await ask.getAttribute('href');
    expect(target).toMatch(/^contact\.html\?property=[a-z0-9-]+#brief$/);
    await page.goto('/' + target);
    await expect(page.locator('[data-form-ref]')).toBeVisible();
    await expect(page.locator('input[value="Buy a home"]')).toBeChecked();
  }
});

test('contact form ignores a property reference it does not list', async ({page}) => {
  await page.goto('/contact.html?property=%3Cimg%20src%3Dx%3E');
  // The note exists only while the Collection is published; either way it must stay hidden here.
  for (const note of await page.locator('[data-form-ref]').all()) await expect(note).toBeHidden();
  await expect(page.locator('input[value="Buy a home"]')).not.toBeChecked();
});
