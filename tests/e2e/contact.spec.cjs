const {test,expect}=require('@playwright/test');
/* The contact brief becomes a reviewed email, not an automatically sent website form. */
async function complete(page){
  await page.goto('/contact.html');
  const form=page.locator('form.letter-form');
  await expect(form).toBeVisible();
  await expect(form).toHaveAttribute('action','mailto:alaa.qadir@crownsmere.com');
  await form.locator('input[name="request"][value="Rent a home"]').check();
  await form.locator('.step.on [data-next]').click();
  await expect(form.locator('.step.on')).toHaveAttribute('data-step','2');
  await form.locator('textarea[name="brief"]').fill('Furnished two-bedroom flat in Chelsea.');
  await form.locator('input[name="areas"]').fill('Chelsea');
  await form.locator('.step.on [data-next]').click();
  await expect(form.locator('.step.on')).toHaveAttribute('data-step','3');
  await form.locator('input[name="name"]').fill('Crownsmere QA Contact');
  await form.locator('input[name="email"]').fill('qa-contact@example.org');
  await form.locator('input[name="phone"]').fill('+447700900123');
  await form.locator('input[name="consent"]').check();
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
  await form.locator('input[name="request"][value="Buy a home"]').check();
  await form.locator('.step.on [data-next]').click();
  await form.locator('.step.on [data-next]').click();
  await form.locator('input[name="name"]').fill('Crownsmere QA');
  await form.locator('input[name="email"]').fill('qa-contact@example.org');
  await form.locator('input[name="phone"]').fill('invalid');
  await form.locator('button[type="submit"]').click();
  await expect(form.locator('.contact-mail-backup')).toBeHidden();
  await form.locator('input[name="phone"]').fill('+447700900123');
  await form.locator('input[name="consent"]').check();
  await form.locator('button[type="submit"]').click();
  await expect(form.locator('.contact-mail-backup')).toBeVisible();
});
