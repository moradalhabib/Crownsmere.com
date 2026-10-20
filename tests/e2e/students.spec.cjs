const { test, expect } = require('@playwright/test');

/*
 * Crownsmere international student experience tests.
 * All submissions in this suite are intercepted; no real applicant data is sent.
 * The live FormSubmit delivery/inbox must be verified in a controlled manual smoke test.
 */
const viewports = [
  { name: 'small-phone-320', width: 320, height: 640 },
  { name: 'iphone-375', width: 375, height: 812 },
  { name: 'iphone-390', width: 390, height: 844 },
  { name: 'tablet-768', width: 768, height: 1024 },
  { name: 'tablet-1024', width: 1024, height: 768 },
  { name: 'desktop-1440', width: 1440, height: 900 }
];
const langs = ['en', 'ar'];
function intersects(a, b, tolerance = 0) {
 return a.x < b.x + b.width - tolerance &&
        a.x + a.width > b.x + tolerance &&
        a.y < b.y + b.height - tolerance &&
        a.y + a.height > b.y + tolerance;
}
for (const vp of viewports) {
 for (const lang of langs) {
  test(`layout: ${vp.name} ${lang}: logo, language switch and application do not overlap`, async ({page}) => {
    await page.setViewportSize(vp);
    const errors=[];
    page.on('pageerror', error => errors.push(String(error)));
    await page.goto('/students.html?lang='+lang);
    await expect(page.locator(`[data-language-panel="${lang}"]`)).toBeVisible();
    await expect(page.locator(`[data-language-panel="${lang === 'ar' ? 'en' : 'ar'}"]`)).toBeHidden();
    await expect(page.locator('.hd-mark')).toBeVisible();
    const header=await page.locator('header.hd').boundingBox();
    const logo=await page.locator('header .hd-mark').boundingBox();
    const bar=await page.locator('.student-language-bar').boundingBox();
    const activeSwitch=await page.locator(`[data-lang-switch="${lang}"]`).boundingBox();
    expect(header && logo && bar && activeSwitch).toBeTruthy();
    expect(intersects(logo,bar,2)).toBeFalsy();
    expect(intersects(header,activeSwitch,2)).toBeFalsy();
    const metrics=await page.evaluate(() => ({
      pageScrollWidth:document.documentElement.scrollWidth,
      viewportWidth:window.innerWidth,
      activeCount:document.querySelectorAll('.student-language:not([hidden])').length,
      docDir: document.documentElement.dir,
      panelDir: document.querySelector('.student-language:not([hidden])')?.dir,
      activeInputs:document.querySelectorAll('.student-language:not([hidden]) .student-form').length
    }));
    expect(metrics.pageScrollWidth,JSON.stringify(metrics)).toBeLessThanOrEqual(metrics.viewportWidth+2);
    expect(metrics.activeCount).toBe(1);
    expect(metrics.activeInputs).toBe(1);
    expect(metrics.docDir).toBe('ltr');
    expect(metrics.panelDir).toBe(lang === 'ar' ? 'rtl' : 'ltr');
    await expect(page.locator(`[data-language-panel="${lang}"] .student-form`)).toBeVisible();
    await expect(page.locator(`[data-language-panel="${lang}"] .student-form .student-stage.is-active`)).toHaveCount(1);
    expect(errors, 'Uncaught page errors: '+JSON.stringify(errors)).toEqual([]);
    if (['iphone-390','desktop-1440'].includes(vp.name)) {
      await page.screenshot({path:`test-screenshots/${vp.name}-${lang}.png`,fullPage:true});
    }
  });
 }
}
for(const lang of langs) {
 test(`language switching, header remains stable and quick action targets correct form (${lang})`,async({page})=>{
   await page.setViewportSize({width:390,height:844});
   await page.goto('/students.html?lang='+lang);
   const other=lang==='en'?'ar':'en';
   await page.locator(`[data-lang-switch="${other}"]`).click();
   await expect(page.locator(`[data-language-panel="${other}"]`)).toBeVisible();
   await expect(page.locator(`[data-language-panel="${lang}"]`)).toBeHidden();
   await expect(page.locator(`[data-lang-switch="${other}"]`)).toHaveAttribute('aria-pressed','true');
   await expect(page.locator('.actionbar a[href^="#"]')).toHaveAttribute('href','#'+other+'-form');
   const logo=await page.locator('header .hd-mark').boundingBox();
   const bar=await page.locator('.student-language-bar').boundingBox();
   expect(intersects(logo,bar,2)).toBeFalsy();
   await page.locator('.hd-menu').click();
   await expect(page.locator('.menu')).toBeVisible();
   await expect(page.locator('.menu a[href="students.html"]')).toHaveAttribute('aria-current','page');
   await page.locator('.hd-menu').click();
   await page.locator('.actionbar a[href="#'+other+'-form"]').click();
   await expect(page.locator(`[data-language-panel="${other}"] .student-form`)).toBeInViewport();
 });
 test(`complete three-step ${lang} form and mocked successful delivery`,async({page})=>{
   await page.setViewportSize({width:390,height:844});
   let payload=null, calls=0;
   await page.route('https://formsubmit.co/ajax/**', async route=>{
     calls++;
     payload=JSON.parse(route.request().postData());
     await route.fulfill({status:200,contentType:'application/json',body:JSON.stringify({success:true,message:'Email sent'})});
   });
   await page.goto('/students.html?lang='+lang);
   const form=page.locator(`[data-language-panel="${lang}"] form.student-form`);
   await expect(form.locator('.student-stage.is-active')).toHaveAttribute('data-student-step','0');
   await form.locator('input[name="service"][value="Guarantor guidance for found property"]').check();
   await form.locator('input[name="university"]').fill("Imperial College London");
   await form.locator('select[name="monthly_budget"]').selectOption('GBP 2500-4000');
   await form.locator('select[name="move_timeframe"]').selectOption('Within 1 month');
   await form.locator('.student-stage.is-active [data-next]').click();
   await expect(form.locator('.student-stage.is-active')).toHaveAttribute('data-student-step','1');
   await form.locator('input[name="guarantor_status"][value="No UK guarantor"]').check();
   await form.locator('select[name="property_found"]').selectOption('Already found a property');
   await form.locator('input[name="preferred_areas"]').fill("Chelsea");
   await form.locator('textarea[name="additional_notes"]').fill("Crownsmere automated QA enquiry (not a client).");
   await form.locator('.student-stage.is-active [data-next]').click();
   await expect(form.locator('.student-stage.is-active')).toHaveAttribute('data-student-step','2');
   await form.locator('input[name="name"]').fill("Crownsmere QA Test");
   await form.locator('input[name="email"]').fill("qa-test@example.org");
   await form.locator('input[name="phone"]').fill("+447700900123");
   await form.locator('input[name="preferred_contact"][value="WhatsApp"]').check();
   await form.locator('input[name="consent"]').check();
   await form.locator('button[type="submit"]').click();
   await expect(form.locator('.std-sent')).toBeVisible();
   await expect(form.locator('.student-progress')).toBeHidden();
   expect(calls).toBe(1);
   expect(payload).toMatchObject({
     _subject:'[Crownsmere Enquiry] International student rental and guarantor request',
     source:'crownsmere.com/students',
     language:lang==='ar'?'Arabic':'English',
     service:'Guarantor guidance for found property',
     university:'Imperial College London',
     monthly_budget:'GBP 2500-4000',
     move_timeframe:'Within 1 month',
     guarantor_status:'No UK guarantor',
     property_found:'Already found a property',
     name:'Crownsmere QA Test',
     email:'qa-test@example.org',
     phone:'+447700900123',
     preferred_contact:'WhatsApp',
     consent:'Yes'
   });
   expect(payload).not.toHaveProperty('_honey');
 });
 test(`${lang} form blocks missing consent and invalid contact number`,async({page})=>{
  let calls=0;
  await page.route('https://formsubmit.co/ajax/**',route=>{calls++;return route.fulfill({status:200,contentType:'application/json',body:'{"success":true}'})});
  await page.goto('/students.html?lang='+lang);
  const form=page.locator(`[data-language-panel="${lang}"] form.student-form`);
  await form.locator('.student-stage.is-active [data-next]').click();
  await form.locator('.student-stage.is-active [data-next]').click();
  await form.locator('input[name="name"]').fill('Crownsmere QA Test');
  await form.locator('input[name="email"]').fill('qa-test@example.org');
  await form.locator('input[name="preferred_contact"][value="WhatsApp"]').check();
  await form.locator('button[type="submit"]').click();
  await expect(form.locator('.std-sent')).toBeHidden();
  await expect(form.locator('.std-status')).not.toBeEmpty();
  expect(calls).toBe(0);
  await form.locator('input[name="phone"]').fill('invalid');
  await form.locator('input[name="consent"]').check();
  await form.locator('button[type="submit"]').click();
  expect(calls).toBe(0);
  await form.locator('input[name="phone"]').fill('+447700900123');
  await form.locator('button[type="submit"]').click();
  await expect(form.locator('.std-sent')).toBeVisible();
  expect(calls).toBe(1);
 });
 test(`${lang} form handles network error without losing applicant data`,async({page})=>{
  await page.route('https://formsubmit.co/ajax/**',route=>route.fulfill({status:500,contentType:'application/json',body:'{"success":false}'}));
  await page.goto('/students.html?lang='+lang);
  const form=page.locator(`[data-language-panel="${lang}"] form.student-form`);
  await form.locator('.student-stage.is-active [data-next]').click();
  await form.locator('.student-stage.is-active [data-next]').click();
  await form.locator('input[name="name"]').fill('Crownsmere QA Test');
  await form.locator('input[name="email"]').fill('qa-test@example.org');
  await form.locator('input[name="consent"]').check();
  await form.locator('button[type="submit"]').click();
  await expect(form.locator('.std-status')).toHaveClass(/is-error/);
  await expect(form.locator('.std-sent')).toBeHidden();
  await expect(form.locator('input[name="name"]')).toHaveValue('Crownsmere QA Test');
  await expect(form.locator('button[type="submit"]')).toBeEnabled();
 });
}
test('works with JavaScript disabled: first form and submit are available', async({browser})=>{
 const context=await browser.newContext({javaScriptEnabled:false,viewport:{width:375,height:812}});
 const page=await context.newPage();
 await page.goto('http://127.0.0.1:8765/students.html');
 const form=page.locator('[data-language-panel="en"] form.student-form');
 await expect(form).toBeVisible();
 await expect(form.locator('[type="submit"]')).toBeVisible();
 expect(await form.getAttribute('action')).toMatch(/^https:\/\/formsubmit.co\//);
 await context.close();
});
