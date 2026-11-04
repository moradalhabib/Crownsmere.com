const { test, expect } = require('@playwright/test');

// Run only against the CI fixture generated outside the tracked repository.
test.skip(!process.env.CROWNSMERE_PROPERTY_FIXTURE, 'QA-only property fixture');
test.use({ baseURL: 'http://127.0.0.1:8766' });

test.beforeEach(async ({ page }) => {
  await page.addInitScript(() => {
    window.crownsmereOpenDraft = url => { window.__propertyDraft = url; };
  });
});

test('published property appears in the catalogue and all filters work', async ({ page }) => {
  await page.setViewportSize({ width: 390, height: 844 });
  await page.goto('/properties.html');
  await expect(page.locator('.property-card')).toHaveCount(1);
  await expect(page.locator('.property-card')).toContainText('QA Fictional Apartment');
  await expect(page.locator('.property-card')).toContainText('£4,321 pcm');
  await expect(page.locator('[data-property-count]')).toContainText('1 property available');
  await page.locator('[data-filter="type"]').selectOption('sale');
  await expect(page.locator('.property-card:visible')).toHaveCount(0);
  await expect(page.locator('[data-filter-empty]')).toBeVisible();
  await page.locator('[data-filter="type"]').selectOption('rent');
  await expect(page.locator('.property-card:visible')).toHaveCount(1);
  await page.locator('[data-filter="beds"]').selectOption('3');
  await expect(page.locator('.property-card:visible')).toHaveCount(0);
  await page.locator('[data-filter="beds"]').selectOption('2');
  await expect(page.locator('.property-card:visible')).toHaveCount(1);
  await page.locator('[data-filter="area"]').selectOption('Test District');
  await expect(page.locator('.property-card:visible')).toHaveCount(1);
  await expect(page.locator('a[href="property-qa-fictional-apartment.html"]')).toBeVisible();
  const overflow = await page.evaluate(() => document.documentElement.scrollWidth - window.innerWidth);
  expect(overflow).toBeLessThanOrEqual(1);
});

test('detail page shows real fixture facts, has no injected script and routes enquiry to Alaa', async ({ page }) => {
  await page.goto('/property-qa-fictional-apartment.html');
  await expect(page.locator('h1')).toContainText('QA Fictional Apartment');
  await expect(page.locator('.property-detail-price')).toContainText('£4,321 pcm');
  await expect(page.locator('.property-gallery-photo')).toHaveCount(1);
  await expect.poll(() => page.locator('.property-gallery-photo img').evaluate(img => img.complete && img.naturalWidth > 0))
    .toBe(true);
  await expect(page.locator('.property-facts')).toContainText('Bedrooms');
  await expect(page.locator('form[data-property-enquiry]')).toHaveAttribute('action','mailto:alaa.qadir@crownsmere.com');
  expect(await page.locator('main').innerText()).toContain("<script>alert('xss')</script>");
  await expect(page.locator('main script')).toHaveCount(0);
  const form = page.locator('form[data-property-enquiry]');
  await form.locator('input[name="name"]').fill('Fixture Visitor');
  await form.locator('input[name="email"]').fill('visitor@example.test');
  await form.locator('input[name="phone"]').fill('+447700900123');
  await form.locator('textarea[name="message"]').fill('I want a viewing through the appointed agent.');
  await form.locator('input[name="contact_ok"]').check();
  await form.locator('.property-submit').click();
  const raw = await page.evaluate(() => window.__propertyDraft);
  expect(raw).toBeTruthy();
  const draft = new URL(raw);
  expect(draft.protocol).toBe('mailto:');
  expect(draft.pathname).toBe('alaa.qadir@crownsmere.com');
  expect(draft.searchParams.get('cc')).toBe('hello@crownsmere.com');
  expect(draft.searchParams.get('subject')).toContain('CME-QA-ONLY');
  expect(draft.searchParams.get('body')).toContain('visitor@example.test');
  expect(draft.searchParams.get('body')).toContain('No introduction to another agent is authorised');
  await expect(page.locator('[data-property-ready]')).toBeVisible();
  const ownerSecret = await page.content();
  expect(ownerSecret).not.toContain('private-qa-owner@example.test');
});

test('property enquiry cannot proceed without consent', async ({ page }) => {
  await page.goto('/property-qa-fictional-apartment.html');
  const form = page.locator('form[data-property-enquiry]');
  await form.locator('input[name="name"]').fill('Fixture Visitor');
  await form.locator('input[name="email"]').fill('visitor@example.test');
  await form.locator('.property-submit').click();
  expect(await page.evaluate(() => window.__propertyDraft)).toBeUndefined();
  await expect(form.locator('[data-property-ready]')).toBeHidden();
});
