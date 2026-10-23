const { test, expect } = require('@playwright/test');

const pages = [
  ['/', 'home'],
  ['/services.html', 'services'],
  ['/about.html', 'about'],
  ['/students.html', 'students'],
  ['/students-ar.html', 'students-ar'],
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

/* Visitors complained the site was far too long on phones (the home page was
 * 16 screens). These are the most each page may measure on a 390 x 844 phone. */
const phoneLength = {home:5400, services:5000, about:4200, students:3000, 'students-ar':3200, contact:2700, privacy:4800};

for (const [url,name] of pages) {
  for (const vp of viewports) {
    test(name + ' • ' + vp.name + ': readable layout, no sideways scrolling', async ({page, browserName}) => {
      await page.setViewportSize(vp);
      const errors = [];
      page.on('pageerror', e => errors.push(e.message));
      page.on('console', m => { if (m.type() === 'error') errors.push(m.text()); });
      await page.goto(url);
      await expect(page.locator('h1:visible')).toHaveCount(1);
      await expect(page.locator('.hd-mark')).toBeVisible();
      const metrics = await page.evaluate(() => ({
        scrollWidth: document.documentElement.scrollWidth,
        height: document.documentElement.scrollHeight,
        header: document.querySelector('.hd').getBoundingClientRect().height
      }));
      if (metrics.scrollWidth > vp.width + 1) {
        const offenders = await page.evaluate(() => Array.from(document.querySelectorAll('body *')).map(el => {
          const r = el.getBoundingClientRect();
          return {tag: el.tagName, cls: String(el.className || '').slice(0, 60), right: Math.round(r.right), width: Math.round(r.width)};
        }).filter(x => x.right > window.innerWidth + 1 && x.width > 0).slice(0, 20));
        console.log('CROWNSMERE_OVERFLOW ' + JSON.stringify({name, vp, metrics, offenders}));
      }
      expect(metrics.scrollWidth, JSON.stringify({name, vp, metrics})).toBeLessThanOrEqual(vp.width + 1);
      expect(metrics.header).toBeLessThanOrEqual(80);
      expect(errors, JSON.stringify({name, vp, errors})).toEqual([]);
      if (vp.width < 1000) {
        const menu = page.locator('.hd-menu');
        await expect(menu).toBeVisible();
        await menu.click();
        await expect(page.locator('.menu a[href="students.html"]')).toBeVisible();
        await menu.click();
        await expect(page.locator('.menu')).toBeHidden();
      } else {
        await expect(page.locator('.hd-nav a[href="students.html"]')).toBeVisible();
        await expect(page.locator('.hd-menu')).toBeHidden();
      }
      if (vp.name === 'iphone-390') {
        expect(metrics.height, name + ' is ' + metrics.height + 'px tall on a phone').toBeLessThanOrEqual(phoneLength[name]);
      }
      if (['iphone-390', 'desktop-1440'].includes(vp.name)) {
        await page.emulateMedia({reducedMotion: 'reduce'});
        await page.reload();
        await page.screenshot({path: 'test-screenshots/' + browserName + '-' + name + '-' + vp.name + '.png', fullPage: true, animations: 'disabled'});
      }
    });
  }
}

test('every page loads only from crownsmere.com: no third-party requests', async ({page}) => {
  const outside = [];
  page.on('request', r => {
    const u = new URL(r.url());
    if (!['127.0.0.1:8765'].includes(u.host) && u.protocol !== 'data:') outside.push(r.url());
  });
  for (const [url] of pages) {
    await page.goto(url);
    await page.evaluate(() => window.scrollTo(0, document.documentElement.scrollHeight));
    await page.waitForTimeout(150);
  }
  expect(outside).toEqual([]);
});

for (const url of ['/', '/services.html', '/students.html', '/contact.html']) {
  test('keyboard focus is never hidden behind the header or quick-contact bar (WCAG 2.2) ' + url, async ({page}) => {
    await page.setViewportSize({width:390,height:844});
    await page.emulateMedia({reducedMotion: 'reduce'});
    await page.goto(url);
    const hidden = [];
    for (let i = 0; i < 40; i++) {
      await page.keyboard.press('Tab');
      await page.waitForTimeout(250); // any correction runs once scrolling has stopped
      const state = await page.evaluate(() => {
        const el = document.activeElement;
        if (!el || el === document.body || el.closest('.hd, .menu, .actionbar, .skip')) return null;
        const r = el.getBoundingClientRect();
        const x = Math.min(innerWidth - 1, Math.max(0, r.left + r.width / 2)), y = r.top + r.height / 2;
        const top = y >= 0 && y < innerHeight ? document.elementFromPoint(x, y) : null;
        return (!top || top.closest('.hd, .actionbar')) ? (el.textContent || el.name || el.tagName).trim().slice(0, 40) : null;
      });
      if (state) hidden.push(state);
    }
    expect(hidden).toEqual([]);
  });
}

test('photos are served as AVIF where supported, with WebP and JPEG fallbacks', async ({page, browserName}) => {
  await page.goto('/');
  const hero = page.locator('.hero img');
  await expect.poll(() => hero.evaluate(e => e.naturalWidth)).toBeGreaterThan(0);
  await expect(page.locator('.hero source[type="image/avif"]')).toHaveCount(1);
  await expect(page.locator('.hero source[type="image/webp"]')).toHaveCount(1);
  if (browserName === 'chromium') expect(await hero.evaluate(e => e.currentSrc)).toMatch(/townhouse\.avif$/);
});

test('instant navigation: the prefetch rules are allowed by the content security policy', async ({page}) => {
  const violations = [];
  page.on('console', m => { if (/Content Security Policy/i.test(m.text())) violations.push(m.text()); });
  await page.goto('/');
  const csp = await page.locator('meta[http-equiv="Content-Security-Policy"]').getAttribute('content');
  const rules = await page.locator('script[type="speculationrules"]').textContent();
  const digest = require('crypto').createHash('sha256').update(rules).digest('base64');
  expect(csp).toContain("'sha256-" + digest + "'");
  expect(JSON.parse(rules).prefetch[0].eagerness).toBe('moderate');
  expect(violations).toEqual([]);
});

test('every link, section link and image on every page works', async ({page, request}) => {
  const all = [...pages.map(([u]) => u), '/404.html'];
  const status = new Map(), idsOn = new Map(), broken = [];
  const check = async path => {
    if (!status.has(path)) {
      const res = await request.get(path);
      status.set(path, res.status());
      if (res.headers()['content-type']?.includes('text/html')) idsOn.set(path, [...(await res.text()).matchAll(/\sid="([^"]+)"/g)].map(m => m[1]));
    }
    return status.get(path);
  };
  for (const url of all) {
    await page.goto(url);
    // Scroll through so lazy images load.
    await page.evaluate(async () => {
      for (let y = 0; y < document.documentElement.scrollHeight; y += 500) { window.scrollTo(0, y); await new Promise(r => setTimeout(r, 40)); }
    });
    await page.waitForFunction(() => [...document.images].every(i => i.complete), null, {timeout: 15000});
    const found = await page.evaluate(() => ({
      links: [...document.querySelectorAll('a[href]')].map(a => a.href),
      files: [...document.querySelectorAll('img[src], source[srcset], link[rel~="icon"], link[rel="apple-touch-icon"], link[rel="manifest"], link[rel="stylesheet"], script[src]')]
        .map(el => el.src || el.href || new URL(el.getAttribute('srcset'), location.href).href),
      unloaded: [...document.images].filter(i => !i.complete || i.naturalWidth === 0).map(i => i.getAttribute('src'))
    }));
    broken.push(...found.unloaded.map(src => url + ': image did not load ' + src));
    for (const href of [...found.links, ...found.files]) {
      const u = new URL(href);
      if (u.origin !== new URL(page.url()).origin) continue; // email and webmail links
      const path = u.pathname === '/' ? '/index.html' : u.pathname;
      if (await check(path) !== 200) { broken.push(url + ' -> ' + u.pathname + ' (' + status.get(path) + ')'); continue; }
      const id = decodeURIComponent(u.hash.slice(1));
      if (id && !(idsOn.get(path) || []).includes(id)) broken.push(url + ' -> ' + u.pathname + u.hash + ' (no such section)');
    }
  }
  expect([...new Set(broken)]).toEqual([]);
});

test('home: photo first impression and three clear routes', async ({page}) => {
  await page.setViewportSize({width:390,height:844});
  await page.goto('/');
  const hero = page.locator('.hero');
  await expect(hero.locator('h1')).toContainText('London property');
  await expect(hero.locator('a[href="contact.html"]')).toBeVisible();
  await expect(hero.locator('a[href="students.html"]')).toBeVisible();
  await expect.poll(() => hero.locator('img').evaluate(e => e.naturalWidth)).toBeGreaterThan(0);
  const paths = page.locator('.path');
  await expect(paths).toHaveCount(3);
  const images = await page.locator('.path img').evaluateAll(els => els.map(el => el.getAttribute('src')));
  expect(new Set(images).size).toBe(3);
  await expect(page.locator('.fine')).toContainText('not available listings');
  const tall = await paths.evaluateAll(els => els.map(el => el.getBoundingClientRect().height));
  for (const h of tall) expect(h).toBeLessThan(150);
  await page.locator('.path[href="students.html"]').click();
  await expect(page).toHaveURL(/students\.html/);
});

test('services: each service has its own section and the jump links reach them', async ({page}) => {
  await page.setViewportSize({width:390,height:844});
  await page.goto('/services.html');
  for (const id of ['buy','sell','let','invest','advisory']) {
    await expect(page.locator('article.svc#' + id)).toHaveCount(1);
    await expect(page.locator('.jump a[href="#' + id + '"]')).toHaveCount(1);
  }
  await page.locator('.jump a[href="#invest"]').click();
  await expect(page.locator('#invest h2')).toBeInViewport();
  await expect(page.locator('.callout a[href="students.html"]')).toBeVisible();
});

test('mobile header slides away on scroll down and returns on scroll up', async ({page}) => {
  await page.setViewportSize({width:390,height:844});
  await page.goto('/');
  await page.evaluate(() => window.scrollTo({top: 1450, behavior: 'instant'}));
  await expect(page.locator('.hd')).toHaveClass(/is-hidden-on-scroll/);
  await page.evaluate(() => window.scrollTo({top: 1250, behavior: 'instant'}));
  await expect(page.locator('.hd')).not.toHaveClass(/is-hidden-on-scroll/);
  await expect(page.locator('.hd-menu')).toBeInViewport();
});

test('quick-contact bar appears after the opening view, on phones only', async ({page}) => {
  await page.setViewportSize({width:390,height:844});
  await page.goto('/');
  const bar = page.locator('.actionbar');
  await expect(bar).not.toBeInViewport();
  await page.evaluate(() => window.scrollTo({top: 900, behavior: 'instant'}));
  await expect(bar).toBeInViewport();
  await expect(bar.locator('a[href="contact.html"]')).toBeVisible();
  await page.goto('/contact.html');
  await expect(page.locator('.actionbar')).toHaveCount(0);
  await page.setViewportSize({width:1280,height:800});
  await page.goto('/');
  await expect(page.locator('.actionbar')).toBeHidden();
});

test('mobile menu keeps keyboard focus inside and Escape returns it', async ({page}) => {
  await page.setViewportSize({width:390,height:844});
  await page.goto('/');
  const button = page.locator('.hd-menu');
  await button.focus();
  await page.keyboard.press('Enter');
  await expect(button).toHaveAttribute('aria-expanded', 'true');
  await expect(page.locator('.menu a').first()).toBeFocused();
  await page.keyboard.press('Shift+Tab');
  await expect(button).toBeFocused();
  await page.keyboard.press('Shift+Tab');
  await expect(page.locator('.menu a').last()).toBeFocused();
  await page.keyboard.press('Tab');
  await expect(button).toBeFocused();
  await page.keyboard.press('Escape');
  await expect(button).toBeFocused();
  await expect(button).toHaveAttribute('aria-expanded', 'false');
  await expect(page.locator('.menu')).toHaveAttribute('inert', '');
});

test('mobile menu closes when the window becomes desktop width', async ({page}) => {
  await page.setViewportSize({width:390,height:844});
  await page.goto('/');
  await page.locator('.hd-menu').click();
  await expect(page.locator('.hd-menu')).toHaveAttribute('aria-expanded', 'true');
  await page.setViewportSize({width:1440,height:900});
  await expect(page.locator('.hd-menu')).toHaveAttribute('aria-expanded', 'false');
});

test('accessibility basics: skip link, image text, labelled fields, touch targets', async ({page}) => {
  await page.setViewportSize({width:390,height:844});
  for (const [url] of pages) {
    await page.goto(url);
    await expect(page.locator('a.skip')).toHaveAttribute('href', '#main');
    await expect(page.locator('main#main')).toHaveCount(1);
    expect(await page.locator('img:not([alt])').count(), url + ' images need alt text').toBe(0);
    const unlabelled = await page.locator('main input:not([type="hidden"]):not([tabindex="-1"]), main select, main textarea').evaluateAll(els =>
      els.filter(el => !(el.labels && el.labels.length) && !el.closest('label')).map(el => el.name));
    expect(unlabelled, url).toEqual([]);
    const small = await page.locator('.btn:visible, .hd-menu:visible, .choice span:visible, .path:visible').evaluateAll(els =>
      els.filter(el => el.getBoundingClientRect().height < 44).map(el => el.textContent.trim().slice(0, 30)));
    expect(small, url + ' touch targets').toEqual([]);
  }
});

test('without JavaScript the navigation and forms still work', async ({browser}) => {
  const ctx = await browser.newContext({javaScriptEnabled: false, viewport: {width:390,height:844}});
  const page = await ctx.newPage();
  await page.goto('http://127.0.0.1:8765/');
  await expect(page.locator('.menu a[href="services.html"]')).toBeVisible();
  await expect(page.locator('.paths')).toBeVisible();
  await page.goto('http://127.0.0.1:8765/contact.html');
  const form = page.locator('form.letter-form');
  await expect(form).toHaveAttribute('action', 'mailto:alaa.qadir@crownsmere.com');
  await expect(form.locator('.step')).toHaveCount(3);
  await expect(form.locator('button[type="submit"]')).toBeVisible();
  await ctx.close();
});

test('wording stays accurate: drafts are not called sent, consent and privacy text intact', async ({page}) => {
  await page.goto('/students.html');
  expect(await page.locator('main').innerText()).not.toContain('Your enquiry has been sent.');
  await page.goto('/students-ar.html');
  expect(await page.locator('main').innerHTML()).not.toContain('تم إرسال طلبك.');
  await page.goto('/contact.html');
  const contact = await page.locator('main').textContent();
  expect(contact).not.toContain('never shared');
  expect(contact).toContain('further agreement');
  await page.goto('/privacy.html');
  const privacy = await page.locator('main').innerText();
  expect(privacy).toContain('if enabled');
  expect(privacy).not.toContain('OpenStreetMap');
});
