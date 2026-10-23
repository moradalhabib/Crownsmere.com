const { test, expect } = require('@playwright/test');

const pages = [
  ['/', 'home'],
  ['/services.html', 'services'],
  ['/buy.html', 'buy'],
  ['/sell.html', 'sell'],
  ['/rent.html', 'rent'],
  ['/invest.html', 'invest'],
  ['/advisory.html', 'advisory'],
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

/* A tap straight after a scroll is now and then lost on GitHub's runners.
 * Centre the link, let the page settle, then tap. */
async function tapBelowTheFold(link) {
  await link.evaluate(el => el.scrollIntoView({block: 'center'}));
  await link.page().evaluate(() => new Promise(done => requestAnimationFrame(() => requestAnimationFrame(done))));
  await link.click();
}

/* Visitors complained the site was far too long on phones (the home page was
 * 16 screens). These are the most each page may measure on a 390 x 844 phone.
 * The home page is a short front door; each service has its own short page. */
const phoneLength = {home:2500, services:3700, buy:2700, sell:1900, rent:3300, invest:1900, advisory:1900,
                     about:5300, students:3000, 'students-ar':3200, contact:2900, privacy:4800};

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
        // Phones and tablets: the tab bar is the navigation, always on screen.
        await expect(page.locator('.tabbar a')).toHaveCount(5);
        await expect(page.locator('.tabbar')).toBeInViewport();
        await expect(page.locator('.hd-nav')).toBeHidden();
      } else {
        await expect(page.locator('.hd-nav a[href="students.html"]')).toBeVisible();
        await expect(page.locator('.tabbar')).toBeHidden();
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

for (const url of ['/', '/services.html', '/rent.html', '/students.html', '/contact.html']) {
  test('keyboard focus is never hidden behind the header or tab bar (WCAG 2.2) ' + url, async ({page}) => {
    await page.setViewportSize({width:390,height:844});
    await page.emulateMedia({reducedMotion: 'reduce'});
    await page.goto(url);
    const hidden = [];
    for (let i = 0; i < 40; i++) {
      await page.keyboard.press('Tab');
      await page.waitForTimeout(250); // any correction runs once scrolling has stopped
      const state = await page.evaluate(() => {
        const el = document.activeElement;
        if (!el || el === document.body || el.closest('.hd, .tabbar, .skip')) return null;
        const r = el.getBoundingClientRect();
        const x = Math.min(innerWidth - 1, Math.max(0, r.left + r.width / 2)), y = r.top + r.height / 2;
        const top = y >= 0 && y < innerHeight ? document.elementFromPoint(x, y) : null;
        return (!top || top.closest('.hd, .tabbar')) ? (el.textContent || el.name || el.tagName).trim().slice(0, 40) : null;
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

test('with motion on, every section that fades in ends up visible', async ({page}) => {
  await page.emulateMedia({reducedMotion: 'no-preference'});
  for (const url of ['/', '/services.html', '/rent.html', '/about.html', '/contact.html']) {
    await page.goto(url);
    await expect(page.locator('html')).toHaveClass(/reveal-on/);
    await page.evaluate(async () => {
      for (let y = 0; y < document.documentElement.scrollHeight; y += 300) { window.scrollTo(0, y); await new Promise(r => setTimeout(r, 60)); }
    });
    await expect.poll(() => page.locator('[data-reveal]:not(.in)').count(), {message: url}).toBe(0);
    await page.waitForTimeout(900); // the fade takes 0.8s
    const faint = await page.locator('[data-reveal]').evaluateAll(els => els.filter(el => parseFloat(getComputedStyle(el).opacity) < 0.99).length);
    expect(faint, url).toBe(0);
  }
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

test('home: a short front door with a tile for each part of the site', async ({page}) => {
  await page.setViewportSize({width:390,height:844});
  await page.goto('/');
  const hero = page.locator('.hero');
  await expect(hero.locator('h1')).toContainText('London property');
  await expect(hero.locator('a[href="contact.html"]')).toBeVisible();
  await expect.poll(() => hero.locator('img').evaluate(e => e.naturalWidth)).toBeGreaterThan(0);
  const tiles = page.locator('.tile');
  expect(await tiles.evaluateAll(els => els.map(el => el.getAttribute('href'))))
    .toEqual(['buy.html', 'sell.html', 'rent.html', 'invest.html', 'students.html', 'about.html']);
  // The first row of tiles starts on the opening screen, above the tab bar.
  const first = await tiles.first().boundingBox();
  const bar = await page.locator('.tabbar').boundingBox();
  expect(first.y).toBeLessThan(bar.y - 60);
  await expect(page.locator('.fine')).toContainText('not available listings');
  await tapBelowTheFold(page.locator('.tile[href="students.html"]'));
  await expect(page).toHaveURL(/students\.html/);
});

test('about: Alaa Qadir profile covers how she works, with nothing invented', async ({page}) => {
  await page.setViewportSize({width:390,height:844});
  await page.goto('/');
  await expect(page.locator('.tile[href="about.html"]')).toContainText('Meet Alaa');
  await page.goto('/about.html');
  await expect(page).toHaveTitle(/Alaa Qadir/);
  await expect(page.locator('h1')).toContainText('Alaa');
  await expect(page.locator('#story-title')).toHaveText('Not a typical estate agency.');
  for (const quality of ['one-to-one service', 'Well connected', 'Direct negotiation', 'Client care', 'Complete discretion']) {
    await expect(page.locator('.card h3', {hasText: new RegExp(quality, 'i')})).toHaveCount(1);
  }
  await expect(page.locator('#tenants')).toContainText('negotiating directly with landlords');
  expect(await page.locator('.whos .who').evaluateAll(els => els.map(el => el.getAttribute('href'))))
    .toEqual(['buy.html', 'rent.html', 'sell.html', 'rent.html', 'invest.html', 'students.html']);
  // Figures and client comments appear only once real ones are supplied.
  await expect(page.locator('.stats')).toHaveCount(0);
  const ld = await page.locator('script[type="application/ld+json"]').textContent();
  const profile = JSON.parse(ld).find(x => x['@type'] === 'ProfilePage');
  expect(profile.mainEntity.name).toBe('Alaa Qadir');
  expect(profile.mainEntity.jobTitle).toBe('Senior Property Consultant');
});

test('services: a tile for each service, and each service has its own page', async ({page}) => {
  await page.setViewportSize({width:390,height:844});
  await page.goto('/services.html');
  const services = [['buy', 'buy.html', 'Buy'], ['sell', 'sell.html', 'Sell'], ['let', 'rent.html', 'Rent'],
                    ['invest', 'invest.html', 'Invest'], ['advisory', 'advisory.html', 'Advisory']];
  for (const [id, href] of services) await expect(page.locator('.tile#' + id)).toHaveAttribute('href', href);
  await expect(page.locator('#process .steps li')).toHaveCount(3);
  await expect(page.locator('#areas .tags li')).toHaveCount(11);
  await expect(page.locator('.callout a[href="students.html"]')).toBeVisible();
  // Old links to a section of the services page still land on that service's tile.
  await page.goto('/services.html#let');
  await expect(page.locator('#let')).toBeInViewport();
  for (const [i, [, href, name]] of services.entries()) {
    await page.goto('/' + href);
    await expect(page.locator('h1')).toBeVisible();
    await expect(page.locator('.crumbs a[href="services.html"]')).toBeVisible();
    await expect(page.locator('.crumbs [aria-current="page"]')).toHaveText(name);
    await expect(page.locator('.tabbar a[href="services.html"]')).toHaveAttribute('aria-current', 'true');
    await expect(page.locator('.pager a.more')).toHaveAttribute('href', services[(i + 1) % services.length][1]);
    await expect(page.locator('.cta a[href="contact.html"]')).toBeVisible();
    const ld = JSON.parse(await page.locator('script[type="application/ld+json"]').textContent());
    expect(ld.find(x => x['@type'] === 'Service').url).toBe('https://crownsmere.com/' + href);
    expect(ld.find(x => x['@type'] === 'BreadcrumbList').itemListElement.map(x => x.name)).toEqual(['Home', 'Services', name]);
  }
});

test('no page calls the advice impartial or independent', async ({page}) => {
  // Crownsmere is paid by commission, sometimes by the other side of a deal.
  for (const [url] of pages) {
    await page.goto(url);
    expect(await page.locator('main').innerText(), url).not.toMatch(/impartial|independent advice/i);
  }
});

test('phones and tablets: the header and the tab bar stay on screen while scrolling', async ({page}) => {
  await page.setViewportSize({width:390,height:844});
  await page.goto('/services.html');
  for (const top of [0, 1400, 600]) {
    await page.evaluate(y => window.scrollTo({top: y, behavior: 'instant'}), top);
    await expect(page.locator('.hd-mark')).toBeInViewport();
    await expect(page.locator('.tabbar')).toBeInViewport();
  }
});

test('tab bar: five tabs on every page, the current one marked, and each tab opens its page', async ({page}) => {
  await page.setViewportSize({width:390,height:844});
  const current = {'/': 'index.html', '/services.html': 'services.html', '/buy.html': 'services.html', '/about.html': 'about.html',
                   '/students.html': 'students.html', '/contact.html': 'contact.html', '/privacy.html': null};
  for (const [url, tab] of Object.entries(current)) {
    await page.goto(url);
    const marked = page.locator('.tabbar a[aria-current]');
    if (tab) {
      await expect(marked, url).toHaveCount(1);
      await expect(marked, url).toHaveAttribute('href', tab);
    } else {
      await expect(marked, url).toHaveCount(0);
    }
  }
  // Arabic labels, read right to left, on the Arabic student page.
  await page.goto('/students-ar.html');
  const ar = page.locator('.tabbar');
  await expect(ar).toHaveAttribute('dir', 'rtl');
  await expect(ar).toContainText('الرئيسية');
  await expect(ar.locator('a[aria-current="page"]')).toHaveAttribute('href', 'students-ar.html');
  // Each tab opens its page.
  await page.goto('/');
  for (const href of ['services.html', 'about.html', 'students.html', 'contact.html', 'index.html']) {
    await page.locator('.tabbar a[href="' + href + '"]').click();
    await expect(page).toHaveURL(new RegExp(href.replace('.', '\\.') + '$'));
  }
  // On computers the header navigation takes over.
  await page.setViewportSize({width:1280,height:800});
  await expect(page.locator('.tabbar')).toBeHidden();
  await expect(page.locator('.hd-nav')).toBeVisible();
});

test('the tab bar steps aside while a form field is being filled in', async ({page}) => {
  await page.setViewportSize({width:390,height:844});
  await page.goto('/contact.html');
  const bar = page.locator('.tabbar');
  await expect(bar).toBeInViewport();
  await page.locator('#f-when').focus();
  await expect(bar).not.toBeInViewport();
  await page.locator('#f-when').blur();
  await expect(bar).toBeInViewport();
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
    const small = await page.locator('.btn:visible, .tabbar a:visible, .choice span:visible, .tile:visible').evaluateAll(els =>
      els.filter(el => el.getBoundingClientRect().height < 44).map(el => el.textContent.trim().slice(0, 30)));
    expect(small, url + ' touch targets').toEqual([]);
  }
});

test('without JavaScript the navigation and forms still work', async ({browser}) => {
  const ctx = await browser.newContext({javaScriptEnabled: false, viewport: {width:390,height:844}});
  const page = await ctx.newPage();
  await page.goto('http://127.0.0.1:8765/');
  await expect(page.locator('.tabbar a[href="services.html"]')).toBeVisible();
  await expect(page.locator('.tiles')).toBeVisible();
  await page.locator('.tabbar a[href="services.html"]').click();
  await expect(page).toHaveURL(/services\.html$/);
  await expect(page.locator('.tile[href="rent.html"]')).toBeVisible();
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
