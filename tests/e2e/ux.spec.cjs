const { test, expect } = require('@playwright/test');

const pages = [
  ['/', 'home'],
  ['/services.html', 'services'],
  ['/about.html', 'about'],
  ['/students.html', 'students'],
  ['/contact.html', 'contact'],
  ['/privacy.html', 'privacy']
];
const viewports = [
  {name:'small-320',width:320,height:680},
  {name:'phone-375',width:375,height:812},
  {name:'iphone-390',width:390,height:844},
  {name:'large-phone-430',width:430,height:932},
  {name:'tablet-768',width:768,height:1024},
  {name:'desktop-1280',width:1280,height:800},
  {name:'desktop-1440',width:1440,height:900}
];

for (const [url,name] of pages) {
  for (const vp of viewports) {
    test(name + ' • ' + vp.name + ': readable layout, no sideways scrolling', async ({page}) => {
      await page.setViewportSize(vp);
      const errors = [];
      page.on('pageerror', e => errors.push(e.message));
      await page.goto(url);
      await expect(page.locator('h1:visible').first()).toBeVisible();
      await expect(page.locator('.hd-mark')).toBeVisible();
      const metrics=await page.evaluate(() => ({
        viewport:window.innerWidth,
        scrollWidth:document.documentElement.scrollWidth,
        height:document.documentElement.scrollHeight,
        header:document.querySelector('.hd')?.getBoundingClientRect().height||0
      }));
      if(metrics.scrollWidth>vp.width+3) {
        const offenders=await page.evaluate(() => Array.from(document.querySelectorAll('body *')).map(el=>{
          const r=el.getBoundingClientRect(); const cs=getComputedStyle(el);
          return {tag:el.tagName,cls:String(el.className||'').slice(0,70),text:(el.textContent||'').trim().slice(0,38),left:Math.round(r.left),right:Math.round(r.right),width:Math.round(r.width),display:cs.display,overflow:cs.overflowX};
        }).filter(x=>x.display!=='none' && x.right>window.innerWidth+6 && x.width>20).slice(0,30));
        console.log('CROWNSMERE_OVERFLOW '+JSON.stringify({name,vp,metrics,offenders}));
      }
      expect(metrics.scrollWidth, JSON.stringify({name,vp,metrics})).toBeLessThanOrEqual(vp.width + 3);
      expect(metrics.height).toBeGreaterThan(500);
      expect(metrics.header).toBeLessThan(130);
      expect(errors, JSON.stringify({name,vp,errors})).toEqual([]);
      if (vp.width <= 430) {
        const menu=page.locator('.hd-menu');
        await expect(menu).toBeVisible();
        await menu.click();
        await expect(page.locator('.menu')).toBeVisible();
        await expect(page.locator('.menu a[href="students.html"]')).toBeVisible();
        await menu.click();
      }
      if ((name==='home'||name==='students') && ['iphone-390','desktop-1440'].includes(vp.name)) {
        await page.screenshot({path:'test-screenshots/'+name+'-'+vp.name+'.png',fullPage:true,animations:'disabled'});
      }
    });
  }
}

test('home: premium photo first impression and clear three service routes', async ({page}) => {
  await page.setViewportSize({width:390,height:844});
  await page.goto('/');
  const hero=page.locator('.home-showcase');
  await expect(hero).toBeVisible();
  await expect(hero.locator('h1')).toContainText('London property');
  await expect(hero.locator('a[href="contact.html"]')).toBeVisible();
  await expect(hero.locator('a[href="students.html"]')).toBeVisible();
  await expect(page.locator('.quick-card')).toHaveCount(3);
  await expect(page.locator('.quick-grid a[href="students.html"]')).toBeVisible();
  const heroImage=hero.locator('img');
  await expect.poll(async ()=>heroImage.evaluate(e=>e.naturalWidth)).toBeGreaterThan(0);
  await page.locator('.quick-entrances').scrollIntoViewIfNeeded();
  await expect(page.locator('.quick-card').first()).toBeVisible();
  await page.locator('.quick-grid a[href="students.html"]').click();
  await expect(page).toHaveURL(/students\.html/);
});

test('services: service images and each service section exist',async ({page})=>{
  await page.goto('/services.html');
  await expect(page.locator('.service-photo-band img')).toHaveCount(1);
  for(const id of ['buy','sell','let','invest','advisory']){
    await expect(page.locator('article.service#'+id)).toHaveCount(1);
  }
  await expect(page.locator('a[href="students.html"]').first()).toBeVisible();
  await expect(page.locator('.service-photo-band img')).toHaveJSProperty('complete',true);
});

test('website enquiry pages never submit to FormSubmit from the browser',async ({page})=>{
  const calls=[];
  page.on('request', r=>{if(r.url().includes('formsubmit.co'))calls.push(r.url())});
  await page.goto('/students.html');
  await expect(page.locator('form.student-form').first()).toHaveAttribute('action',/^mailto:/);
  await page.goto('/contact.html');
  await expect(page.locator('form.letter-form')).toHaveAttribute('action',/^mailto:/);
  expect(calls).toEqual([]);
});

test('no external 3D hero engine runs on the redesigned home',async ({page})=>{
  const requests=[];
  page.on('request',r=>{if(r.url().includes('crest.min.js'))requests.push(r.url());});
  await page.goto('/');
  await expect(page.locator('.home-showcase')).toBeVisible();
  await expect(page.locator('.hero3d-stage')).toHaveCount(0);
  expect(requests).toEqual([]);
});

test('keyboard navigation and page accessibility basics',async ({page})=>{
  await page.setViewportSize({width:390,height:844});
  await page.goto('/');
  await expect(page.locator('a.skip')).toHaveAttribute('href','#main');
  await expect(page.locator('main#main')).toBeVisible();
  const links=await page.locator('.quick-card').evaluateAll(xs=>xs.map(x=>({href:x.getAttribute('href'),label:x.getAttribute('aria-label')})));
  expect(links.every(x=>x.href&&x.label)).toBeTruthy();
});
