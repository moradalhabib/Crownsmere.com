const {test,expect}=require('@playwright/test');

// Capture the prepared email instead of launching a mail app. The pages call
// window.crownsmereOpenDraft when it exists; without it, Firefox in CI blocks on its
// "choose an application" prompt for mailto: links.
test.beforeEach(async ({page}) => {
  await page.addInitScript(() => { window.crownsmereOpenDraft = url => { window.__openedDraft = url; }; });
});
/* Tap "Next" until the form shows the given step. On GitHub's runners a tap straight after the
 * form has scrolled is now and then lost. Tapping again only while the step is unchanged can never
 * skip one, and a Next button that never works still fails the test. */
async function nextStep(form, step) {
  const current = form.locator('.step.on');
  await expect(async () => {
    if (await current.getAttribute('data-step') === String(step - 1)) await current.locator('[data-next]').click({timeout: 5000});
    await expect(current).toHaveAttribute('data-step', String(step), {timeout: 1500});
  }).toPass({timeout: 20000});
}

/* Tick a radio button or checkbox, ticking again if the tap is lost (seen in WebKit on GitHub's
 * runners, straight after the page scrolls). check() only ever ticks, so a retry cannot untick it,
 * and a control that never ticks still fails the test. */
async function tick(input) {
  await expect(async () => { await input.check({timeout: 5000}); }).toPass({timeout: 20000});
}

/* The contact brief becomes a reviewed email, not an automatically sent website form. */
async function complete(page){
  await page.goto('/contact.html');
  const form=page.locator('form.letter-form');
  await expect(form).toBeVisible();
  await expect(form).toHaveAttribute('action','mailto:alaa.qadir@crownsmere.com');
  await tick(form.locator('input[name="request"][value="Rent a home"]'));
  await nextStep(form, 2);
  await form.locator('textarea[name="brief"]').fill('Furnished two-bedroom flat in Chelsea.');
  await form.locator('input[name="areas"]').fill('Chelsea');
  await nextStep(form, 3);
  await form.locator('input[name="name"]').fill('Crownsmere QA Contact');
  await form.locator('input[name="email"]').fill('qa-contact@example.org');
  await form.locator('input[name="phone"]').fill('+447700900123');
  await tick(form.locator('input[name="consent"]'));
  return form;
}

test('general website brief opens a well-organised email draft, not a third-party request',async({page})=>{
  const thirdParty=[];
  page.on('request',r=>{if(r.url().includes('formsubmit.co'))thirdParty.push(r.url());});
  const form=await complete(page);
  await form.locator('button[type="submit"]').click();
  const backup=form.locator('.contact-mail-backup');
  await expect(backup).toBeVisible();
  await expect(form).not.toHaveClass(/sent/);
  await expect(form.locator('.form-status')).toContainText('email');
  const href=await backup.locator('[data-contact-email]').getAttribute('href');
  expect(await page.evaluate(()=>window.__openedDraft)).toBe(href); // the mail app opens this same draft
  const url=new URL(href);
  expect(url.protocol).toBe('mailto:');
  expect(url.pathname).toBe('alaa.qadir@crownsmere.com');
  expect(url.searchParams.get('cc')).toBe('hello@crownsmere.com');
  expect(url.searchParams.get('subject')).toContain('Crownsmere QA Contact');
  const body=url.searchParams.get('body');
  expect(body).toContain('Dear Alaa');
  expect(body).toContain('Furnished two-bedroom flat in Chelsea.');
  expect(body).toContain('qa-contact@example.org');
  expect(body).toContain('+447700900123');
  expect(body).toContain('crownsmere.com/contact.html');
  const gmail=new URL(await backup.locator('[data-webmail="gmail"]').getAttribute('href'));
  expect(gmail.searchParams.get('to')).toBe('alaa.qadir@crownsmere.com');
  expect(gmail.searchParams.get('cc')).toBe('hello@crownsmere.com');
  expect(gmail.searchParams.get('body')).toContain('Furnished two-bedroom flat in Chelsea.');
  await backup.locator('[data-contact-copy]').click();
  await expect(backup.locator('[data-contact-feedback]')).not.toBeEmpty();
  await expect(form.locator('input[name="name"]')).toHaveValue('Crownsmere QA Contact');
  expect(thirdParty).toEqual([]);
});

test('general contact form blocks missing consent and invalid phone',async({page})=>{
  await page.goto('/contact.html');
  const form=page.locator('form.letter-form');
  await tick(form.locator('input[name="request"][value="Buy a home"]'));
  await nextStep(form, 2);
  await nextStep(form, 3);
  await form.locator('input[name="name"]').fill('Crownsmere QA');
  await form.locator('input[name="email"]').fill('qa-contact@example.org');
  await form.locator('input[name="phone"]').fill('invalid');
  await form.locator('button[type="submit"]').click();
  await expect(form.locator('.contact-mail-backup')).toBeHidden();
  expect(await page.evaluate(()=>window.__openedDraft)).toBeUndefined();
  await form.locator('input[name="phone"]').fill('+447700900123');
  await tick(form.locator('input[name="consent"]'));
  await form.locator('button[type="submit"]').click();
  await expect(form.locator('.contact-mail-backup')).toBeVisible();
});
