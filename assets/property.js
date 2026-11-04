/* Crownsmere listings: no third-party requests, no tracker and no form server. */
(function () {
  "use strict";

  const filters = document.querySelector(".property-filters");
  if (filters) {
    const cards = Array.from(document.querySelectorAll("[data-property-grid] .property-card"));
    const count = document.querySelector("[data-property-count]");
    const noMatch = document.querySelector("[data-filter-empty]");
    filters.addEventListener("submit", function (event) { event.preventDefault(); });
    function apply() {
      const type = filters.querySelector('[data-filter="type"]').value;
      const area = filters.querySelector('[data-filter="area"]').value;
      const beds = Number(filters.querySelector('[data-filter="beds"]').value);
      let shown = 0;
      cards.forEach(function (card) {
        const matches = (type === "all" || card.dataset.type === type) &&
          (area === "all" || card.dataset.area === area) &&
          Number(card.dataset.beds || 0) >= beds;
        card.hidden = !matches;
        if (matches) shown += 1;
      });
      if (count) count.textContent = shown + (shown === 1 ? " property available" : " properties available");
      if (noMatch) noMatch.hidden = shown !== 0 || cards.length === 0;
    }
    filters.addEventListener("change", apply);
    apply();
  }

  const form = document.querySelector("[data-property-enquiry]");
  if (!form) return;

  const ready = form.querySelector("[data-property-ready]");
  const reopen = form.querySelector("[data-property-mailto]");
  const copy = form.querySelector("[data-property-copy]");
  const feedback = form.querySelector("[data-property-feedback]");
  let draft = "";
  let plain = "";

  function safe(value, max) {
    return String(value || "").replace(/[\r\n<>]/g, " ").trim().slice(0, max);
  }
  function query(params) {
    return Object.keys(params).map(function (key) {
      return encodeURIComponent(key) + "=" + encodeURIComponent(params[key]);
    }).join("&");
  }
  form.addEventListener("submit", function (event) {
    event.preventDefault();
    if (!form.reportValidity()) return;
    const data = new FormData(form);
    const name = safe(data.get("name"), 90);
    const email = safe(data.get("email"), 180);
    const phone = safe(data.get("phone"), 35);
    const message = safe(data.get("message"), 1500);
    const reference = safe(form.dataset.ref, 80);
    const title = safe(form.dataset.title, 150);
    const subject = "Crownsmere | Property enquiry " + reference;
    const body = "PROPERTY ENQUIRY\n" +
      "Reference: " + reference + "\n" +
      "Property: " + title + "\n\n" +
      "CLIENT DETAILS\n" +
      "Name: " + name + "\n" +
      "Email: " + email + "\n" +
      "Phone: " + (phone || "Not supplied") + "\n\n" +
      "Message:\n" + (message || "Please contact me about this property.") + "\n\n" +
      "I agree to be contacted about this property. No introduction to another agent is authorised by this message.\n\n" +
      "Prepared on crownsmere.com";
    const to = "alaa.qadir@crownsmere.com";
    const cc = "hello@crownsmere.com";
    draft = "mailto:" + to + "?" + query({cc: cc, subject: subject, body: body});
    plain = "To: " + to + "\nCc: " + cc + "\nSubject: " + subject + "\n\n" + body;
    if (reopen) reopen.href = draft;
    if (ready) ready.hidden = false;
    if (feedback) feedback.textContent = "The email is ready; please send it from your email application.";
    try {
      (window.crownsmereOpenDraft || function (url) { window.location.href = url; })(draft);
    } catch (error) {
      if (feedback) feedback.textContent = "Your email application did not open. Use Open prepared email or Copy enquiry.";
    }
  });
  if (copy) {
    copy.addEventListener("click", async function () {
      if (!plain) return;
      try {
        await navigator.clipboard.writeText(plain);
        if (feedback) feedback.textContent = "Enquiry copied. Paste it into your email application and send to Alaa.";
      } catch (error) {
        if (feedback) {
          feedback.textContent = plain;
          feedback.style.whiteSpace = "pre-wrap";
          feedback.style.overflowWrap = "anywhere";
        }
      }
    });
  }
})();
