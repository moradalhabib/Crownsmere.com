const {test,expect}=require('@playwright/test');
const viewports=[{name:'phone-320',width:320,height:680},{name:'iphone-390',width:390,height:844},{name:'large-phone-430',width:430,height:932},{name:'tablet-768',width:768,height:1024},{name:'desktop-1440',width:1440,height:900}];
for(const vp of viewports){
 test('visual refinement '+vp.name+': unique photos, no repeated gallery, readable cards',async({page})=>{
  await page.setViewportSize(vp);
  await page.goto('/');
  await expect(page.locator('.quick-card')).toHaveCount(3);
  await expect(page.locator('.gallery-strip')).toHaveCount(0);
  await expect(page.locator('#approach img')).toHaveCount(0);
  const imgs=await page.locator('.quick-card img').evaluateAll(els=>els.map(el=>el.getAttribute('src')));
  expect(new Set(imgs).size).toBe(3);
  expect(imgs).not.toContain('assets/img/townhouse.jpg');
  const result=await page.evaluate(()=>{
   const box=(selector)=>{const el=document.querySelector(selector);if(!el)return null;const r=el.getBoundingClientRect();return {top:r.top+scrollY,height:r.height,bottom:r.bottom+scrollY};};
   const cards=[...document.querySelectorAll('.quick-card')].map(el=>({height:el.getBoundingClientRect().height,title:el.querySelector('h3')?.textContent,link:el.getAttribute('href')}));
   return {scrollWidth:document.documentElement.scrollWidth,width:innerWidth,quick:box('.quick-entrances'),approach:box('#approach'),cards,heading:box('#approach .section-head h2'),hero:box('.home-showcase')};
  });
  expect(result.scrollWidth,JSON.stringify(result)).toBeLessThanOrEqual(vp.width+3);
  if(vp.width<=430){
   for(const card of result.cards){expect(card.height).toBeGreaterThanOrEqual(235);expect(card.height).toBeLessThan(355);}
   expect(result.approach.top-result.quick.bottom).toBeLessThan(55);
   expect(result.approach.height).toBeLessThan(1250);
  }
  if(vp.width>=1200)expect(result.cards.every(c=>c.height>=300)).toBeTruthy();
  for(const [name,selector] of [['hero','.home-showcase'],['cards','.quick-entrances'],['approach','#approach']]){
   const el=page.locator(selector);
   await el.scrollIntoViewIfNeeded();
   await el.screenshot({path:'test-screenshots/refined-'+vp.name+'-'+name+'.png',animations:'disabled'});
  }
 });
}

for(const [path,name] of [['/services.html','services'],['/about.html','about'],['/students.html','students'],['/contact.html','contact'],['/privacy.html','privacy']]){
  test('visual site review '+name+': mobile and desktop layout and visible content',async({page})=>{
    for(const vp of [{name:'mobile',width:390,height:844},{name:'desktop',width:1440,height:900}]){
      await page.setViewportSize(vp);
      await page.goto(path);
      const data=await page.evaluate(()=>{
        const header=document.querySelector('.hd')?.getBoundingClientRect();
        const main=document.querySelector('main')?.getBoundingClientRect();
        return {scrollWidth:document.documentElement.scrollWidth,viewport:innerWidth,headerHeight:header?.height,mainHeight:main?.height};
      });
      expect(data.scrollWidth).toBeLessThanOrEqual(vp.width+3);
      expect(data.mainHeight).toBeGreaterThan(500);
      await page.screenshot({path:'test-screenshots/refined-'+name+'-'+vp.name+'.png',fullPage:true,animations:'disabled'});
    }
  });
}

test('mobile header clears section headings on scroll down and returns on scroll up',async({page})=>{
 await page.setViewportSize({width:390,height:844});
 await page.goto('/');
 await expect(page.locator('.hd')).toBeVisible();
 await page.evaluate(()=>window.scrollTo(0,1450));
 await page.waitForTimeout(450);
 await expect(page.locator('.hd')).toHaveClass(/is-hidden-on-scroll/);
 const hidden=await page.locator('.hd').evaluate(e=>getComputedStyle(e).transform);
 expect(hidden).not.toBe('none');
 await page.evaluate(()=>window.scrollTo(0,1250));
 await page.waitForTimeout(450);
 await expect(page.locator('.hd')).not.toHaveClass(/is-hidden-on-scroll/);
 await expect(page.locator('.hd-menu')).toBeVisible();
});

test('student application starts promptly after concise introduction',async({page})=>{
 await page.setViewportSize({width:390,height:844});
 await page.goto('/students.html');
 await expect(page.locator('.student-info')).toHaveCount(0);
 const formTop=await page.locator('#en-form').evaluate(el=>el.getBoundingClientRect().top+window.scrollY);
 expect(formTop).toBeLessThan(1350);
 await expect(page.locator('form.student-form[data-form-lang="en"]')).toBeVisible();
});
