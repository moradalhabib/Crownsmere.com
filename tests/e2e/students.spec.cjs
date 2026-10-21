const {test,expect}=require('@playwright/test');

/* No emails are actually sent during testing.
 * The complete mailto draft is checked in both languages before publication. */
for(const lang of ['en','ar']){
  const other=lang==='en'?'ar':'en';
  test(lang+' student page: language, clear header and responsive controls',async({page})=>{
    await page.setViewportSize({width:390,height:844});
    await page.goto('/students.html?lang='+lang);
    const panel=page.locator('[data-language-panel="'+lang+'"]');
    await expect(panel).toBeVisible();
    await expect(page.locator('[data-language-panel="'+other+'"]')).toBeHidden();
    await expect(panel).toHaveAttribute('dir',lang==='ar'?'rtl':'ltr');
    await expect(page.locator('.hd-mark')).toBeVisible();
    const header=await page.locator('header.hd').boundingBox();
    const switcher=await page.locator('.student-language-bar button[data-lang-switch="'+lang+'"]').boundingBox();
    expect(switcher.y).toBeGreaterThanOrEqual(header.y+header.height-2);
    await expect(page.locator('form.student-form[data-form-lang="'+lang+'"]')).toHaveAttribute('action','mailto:alaa.qadir@crownsmere.com');
    await expect(panel.locator('button[type="submit"]')).toContainText(lang==='ar'?'البريد الإلكتروني':'email');
    await page.locator('[data-lang-switch="'+other+'"]').click();
    await expect(page.locator('[data-language-panel="'+other+'"]')).toBeVisible();
    await expect(page.locator('[data-language-panel="'+lang+'"]')).toBeHidden();
    await expect(page.locator('.actionbar a[href^="#"]')).toHaveAttribute('href','#'+other+'-form');
  });

  test(lang+' student form: all three steps prepare a polished personal email',async({page})=>{
    await page.setViewportSize({width:390,height:844});
    const requests=[];
    page.on('request',r=>{if(r.url().includes('formsubmit.co'))requests.push(r.url())});
    await page.goto('/students.html?lang='+lang);
    const form=page.locator('form.student-form[data-form-lang="'+lang+'"]');
    await expect(form.locator('.student-stage.is-active')).toHaveAttribute('data-student-step','0');
    await form.locator('input[name="service"][value="Apartment and guarantor help"]').check();
    await form.locator('input[name="university"]').fill('Imperial College London');
    await form.locator('select[name="monthly_budget"]').selectOption('GBP 2500-4000');
    await form.locator('select[name="move_timeframe"]').selectOption('Within 1-3 months');
    await form.locator('.student-stage.is-active [data-next]').click();
    await expect(form.locator('.student-stage.is-active')).toHaveAttribute('data-student-step','1');
    await form.locator('input[name="guarantor_status"][value="No UK guarantor"]').check();
    await form.locator('select[name="property_found"]').selectOption('Already found a property');
    await form.locator('input[name="preferred_areas"]').fill('Kensington, Chelsea');
    await form.locator('textarea[name="additional_notes"]').fill('Furnished flat near campus.');
    await form.locator('.student-stage.is-active [data-next]').click();
    await expect(form.locator('.student-stage.is-active')).toHaveAttribute('data-student-step','2');
    await form.locator('input[name="name"]').fill('Crownsmere QA Student');
    await form.locator('input[name="email"]').fill('qa-student@example.org');
    await form.locator('input[name="phone"]').fill('+447700900123');
    await form.locator('input[name="preferred_contact"][value="WhatsApp"]').check();
    await form.locator('input[name="consent"]').check();
    await form.locator('button[type="submit"]').click();
    await expect(form.locator('.std-fallback')).toBeVisible();
    await expect(form.locator('.std-status')).toContainText(lang==='ar'?'البريد':'email');
    await expect(form.locator('.std-sent')).toBeHidden();
    const href=await form.locator('[data-email-fallback]').getAttribute('href');
    const url=new URL(href);
    expect(url.protocol).toBe('mailto:');
    expect(url.pathname).toBe('alaa.qadir@crownsmere.com');
    expect(url.searchParams.get('cc')).toBe('hello@crownsmere.com');
    const subject=url.searchParams.get('subject');
    expect(subject).toContain('Crownsmere Estate');
    expect(subject).toContain('Crownsmere QA Student');
    const body=url.searchParams.get('body');
    for(const term of ['Imperial College London','Kensington, Chelsea','qa-student@example.org','+447700900123','Furnished flat near campus.'])expect(body).toContain(term);
    expect(body).toContain('\n');
    if(lang==='en'){
      expect(body).toContain('STUDENT DETAILS');
      expect(body).toContain('RENTAL REQUIREMENTS');
      expect(body).toContain('GUARANTOR SITUATION');
      expect(body).toContain('CONTACT DETAILS');
      expect(body).toContain('£2,500–£4,000 per month');
      expect(body).not.toContain('GBP 2500-4000');
    }else{
      expect(body).toContain('بيانات الطالب');
      expect(body).toContain('متطلبات السكن');
      expect(body).toContain('وضع الضامن');
      expect(body).toContain('معلومات التواصل');
      expect(body).toContain('من £2,500 إلى £4,000 شهرياً');
      expect(body).not.toContain('GBP 2500-4000');
    }
    await form.locator('[data-copy-fallback]').click();
    await expect(form.locator('[data-copy-feedback]')).not.toBeEmpty();
    await expect(form.locator('input[name="name"]')).toHaveValue('Crownsmere QA Student');
    expect(requests).toEqual([]);
  });

  test(lang+' student form validates consent and contact methods before preparing mail',async({page})=>{
    await page.goto('/students.html?lang='+lang);
    const form=page.locator('form.student-form[data-form-lang="'+lang+'"]');
    await form.locator('.student-stage.is-active [data-next]').click();
    await form.locator('.student-stage.is-active [data-next]').click();
    await form.locator('input[name="name"]').fill('Test Person');
    await form.locator('input[name="email"]').fill('qa-test@example.org');
    await form.locator('input[name="preferred_contact"][value="WhatsApp"]').check();
    await form.locator('button[type="submit"]').click();
    await expect(form.locator('.std-fallback')).toBeHidden();
    await expect(form.locator('.std-status')).not.toBeEmpty();
    await form.locator('input[name="phone"]').fill('not-a-phone');
    await form.locator('input[name="consent"]').check();
    await form.locator('button[type="submit"]').click();
    await expect(form.locator('.std-fallback')).toBeHidden();
    await form.locator('input[name="phone"]').fill('+447700900123');
    await form.locator('button[type="submit"]').click();
    await expect(form.locator('.std-fallback')).toBeVisible();
  });
}
test('no-JavaScript student form still has a mailto destination and a visible final action',async({browser})=>{
 const ctx=await browser.newContext({javaScriptEnabled:false,viewport:{width:375,height:812}});
 const page=await ctx.newPage();
 await page.goto('http://127.0.0.1:8765/students.html');
 const form=page.locator('form.student-form[data-form-lang="en"]');
 await expect(form).toBeVisible();
 await expect(form).toHaveAttribute('action','mailto:alaa.qadir@crownsmere.com');
 await expect(form.locator('button[type="submit"]')).toBeVisible();
 await ctx.close();
});
