const {test,expect}=require('@playwright/test');
/* General Crownsmere contact composer regression tests.
   All network delivery requests are mocked: no actual emails are sent. */
async function completeContactForm(page){
 await page.goto('/contact.html');
 const form=page.locator('form.letter-form');
 await expect(form).toBeVisible();
 await form.locator('input[name="request"][value="Rent a home"]').check();
 await form.locator('.step.on [data-next]').click();
 await expect(form.locator('.step.on')).toHaveAttribute('data-step','2');
 await form.locator('textarea[name="brief"]').fill('Synthetic Crownsmere quality assurance enquiry (not a client).');
 await form.locator('.step.on [data-next]').click();
 await expect(form.locator('.step.on')).toHaveAttribute('data-step','3');
 await form.locator('input[name="name"]').fill('Crownsmere QA Test');
 await form.locator('input[name="email"]').fill('qa-test@example.org');
 await form.locator('input[name="phone"]').fill('+447700900123');
 await form.locator('input[name="consent"]').check();
 return form;
}
test('existing general contact composer confirms valid FormSubmit JSON success',async({page})=>{
 let sentPayload;
 await page.route('https://formsubmit.co/ajax/**',route=>{
  sentPayload=JSON.parse(route.request().postData());
  return route.fulfill({status:200,contentType:'application/json',body:'{"success":"true"}'});
 });
 const form=await completeContactForm(page);
 await form.locator('button[type="submit"]').click();
 await expect(form).toHaveClass(/sent/);
 await expect(form.locator('.form-status')).toContainText('received');
 expect(sentPayload).toMatchObject({name:'Crownsmere QA Test',request:'Rent a home',source:'crownsmere.com/contact'});
 expect(sentPayload).toHaveProperty('letter');
});
test('existing contact composer rejects HTTP 200 HTML challenge and keeps data',async({page})=>{
 await page.route('https://formsubmit.co/ajax/**',route=>route.fulfill({status:200,contentType:'text/html',body:'<!doctype html>Just a moment...'}));
 const form=await completeContactForm(page);
 await form.locator('button[type="submit"]').click();
 await expect(form.locator('.form-status')).toHaveClass(/error/);
 await expect(form).not.toHaveClass(/sent/);
 await expect(form.locator('input[name="name"]')).toHaveValue('Crownsmere QA Test');
});
test('existing contact composer rejects JSON with missing success indicator',async({page})=>{
 await page.route('https://formsubmit.co/ajax/**',route=>route.fulfill({status:200,contentType:'application/json',body:'{}'}));
 const form=await completeContactForm(page);
 await form.locator('button[type="submit"]').click();
 await expect(form.locator('.form-status')).toHaveClass(/error/);
 await expect(form).not.toHaveClass(/sent/);
});
