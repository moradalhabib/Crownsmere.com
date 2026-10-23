/* Crownsmere Estate — site behaviour. No tracking and no third-party requests.
   Everything here is progressive: without JavaScript every page still works. */
(function () {
  "use strict";

  var root = document.documentElement;
  root.classList.remove("no-js");
  root.classList.add("js");
  var reduce = window.matchMedia("(prefers-reduced-motion: reduce)").matches;
  var phone = window.matchMedia("(max-width: 999px)");

  document.querySelectorAll("[data-year]").forEach(function (el) {
    el.textContent = new Date().getFullYear();
  });

  /* ---------- Header and quick-contact bar ----------
     On phones the header slides away while scrolling down and returns on the way up,
     and the quick-contact bar appears once the opening view has been scrolled past. */
  var hd = document.querySelector(".hd");
  var lastY = window.scrollY;
  function onScroll() {
    var y = window.scrollY;
    if (hd) {
      hd.classList.toggle("is-scrolled", y > 8);
      var menuOpen = root.classList.contains("menu-open");
      if (phone.matches && y > 170 && y > lastY + 1 && !menuOpen && !hd.contains(document.activeElement)) {
        hd.classList.add("is-hidden-on-scroll");
      } else if (!phone.matches || y < 120 || y < lastY - 1) {
        hd.classList.remove("is-hidden-on-scroll");
      }
    }
    root.classList.toggle("show-bar", y > Math.min(420, window.innerHeight * 0.5));
    lastY = y;
  }
  window.addEventListener("scroll", onScroll, { passive: true });
  onScroll();

  /* ---------- Mobile menu ---------- */
  var menuBtn = document.querySelector(".hd-menu");
  var menu = document.getElementById("menu");
  if (menuBtn && menu) {
    var label = menuBtn.querySelector("span");
    var focusables = function () {
      return [menuBtn].concat(Array.prototype.slice.call(menu.querySelectorAll("a[href], button")));
    };
    var setMenu = function (open) {
      root.classList.toggle("menu-open", open);
      menuBtn.setAttribute("aria-expanded", String(open));
      label.textContent = open ? "Close" : "Menu";
      if (open) menu.removeAttribute("inert"); else menu.setAttribute("inert", "");
    };
    menu.setAttribute("inert", "");
    menuBtn.addEventListener("click", function () {
      var open = !root.classList.contains("menu-open");
      setMenu(open);
      if (open) focusables()[1].focus({ preventScroll: true });
    });
    document.addEventListener("keydown", function (e) {
      if (!root.classList.contains("menu-open")) return;
      if (e.key === "Escape") {
        e.preventDefault();
        setMenu(false);
        menuBtn.focus({ preventScroll: true });
      } else if (e.key === "Tab") {
        // The open menu covers the page, so keep focus inside it (the close button included).
        var items = focusables(), first = items[0], last = items[items.length - 1];
        if (e.shiftKey && document.activeElement === first) { e.preventDefault(); last.focus(); }
        else if (!e.shiftKey && document.activeElement === last) { e.preventDefault(); first.focus(); }
      }
    });
    menu.addEventListener("click", function (e) { if (e.target.closest("a")) setMenu(false); });
    // Close the phone menu if the window becomes desktop width (some browsers update the media
    // query after the resize event, so check the width and listen for the query changing too).
    var closeOnDesktop = function () {
      if ((!phone.matches || window.innerWidth >= 1000) && root.classList.contains("menu-open")) setMenu(false);
    };
    window.addEventListener("resize", closeOnDesktop);
    if (phone.addEventListener) phone.addEventListener("change", closeOnDesktop);
  }

  /* ---------- Keep keyboard focus clear of the sticky header and quick-contact bar ----------
     WCAG 2.2 (2.4.11). The page's scroll padding handles this in most browsers; Safari can still
     leave a focused control under a bar. Checked only once scrolling has stopped, so it never
     fights a smooth scroll. */
  var quickBar = document.querySelector(".actionbar");
  var focusTimer = 0;
  document.addEventListener("focusin", function (e) {
    var el = e.target;
    if ([hd, menu, quickBar].some(function (x) { return x && x.contains(el); })) return;
    clearTimeout(focusTimer);
    var seenY = -1, still = 0, waited = 0;
    var check = function () {
      still = window.scrollY === seenY ? still + 1 : 0;
      seenY = window.scrollY;
      if (still < 3 && (waited += 40) < 1500) { focusTimer = setTimeout(check, 40); return; }
      var r = el.getBoundingClientRect();
      var top = hd ? hd.offsetHeight : 0; // the header returns when scrolling up, so allow for it
      var bottom = quickBar && quickBar.getClientRects().length
        ? Math.min(window.innerHeight, quickBar.getBoundingClientRect().top) : window.innerHeight;
      if (r.top < top) window.scrollBy(0, r.top - top - 12);
      else if (r.bottom > bottom) window.scrollBy(0, Math.min(r.bottom - bottom + 12, r.top - top - 12));
    };
    focusTimer = setTimeout(check, 40);
  });

  /* ---------- Gentle reveal as sections come into view ---------- */
  var revealEls = document.querySelectorAll("[data-reveal]");
  if ("IntersectionObserver" in window && !reduce && revealEls.length) {
    root.classList.add("reveal-on");
    var io = new IntersectionObserver(function (entries) {
      entries.forEach(function (en) {
        if (en.isIntersecting) { en.target.classList.add("in"); io.unobserve(en.target); }
      });
    }, { rootMargin: "0px 0px -8% 0px", threshold: 0.05 });
    revealEls.forEach(function (el) { io.observe(el); });
  }

  /* ---------- Brief form: three short steps, then a prepared email ----------
     Nothing is sent by the website: the visitor's own mail app opens with the
     brief written out, and they press Send. Without JavaScript the three steps
     show as one form that opens a mailto: draft. */
  var form = document.querySelector("form.letter-form");
  if (!form) return;

  var status = form.querySelector(".form-status");
  var card = form.closest(".form-card") || form;
  var tel = form.querySelector('input[type="tel"]');
  var steps = Array.prototype.slice.call(form.querySelectorAll(".step"));
  var navItems = form.querySelectorAll(".steps-nav li");
  var counter = form.querySelector(".step-count");
  var current = 0;

  var say = function (msg, isError) {
    status.textContent = msg;
    status.classList.toggle("error", !!isError);
  };

  var checkPhone = function () {
    if (!tel) return;
    var digits = tel.value.replace(/[^0-9]/g, "");
    var ok = !tel.value || (/^[0-9+()\-. ]+$/.test(tel.value) && digits.length >= 7 && digits.length <= 15);
    tel.setCustomValidity(ok ? "" : "Kindly enter a valid telephone number, including the country code if outside the UK.");
  };
  if (tel) tel.addEventListener("input", checkPhone);

  var markInvalid = function (scope) {
    var bad = false;
    scope.querySelectorAll(".field, .choices, .consent").forEach(function (el) {
      var invalid = !!el.querySelector("input:invalid, select:invalid, textarea:invalid");
      el.classList.toggle("invalid", invalid);
      bad = bad || invalid;
    });
    return !bad;
  };
  var recheck = function () { if (form.querySelector(".invalid")) markInvalid(form); };
  form.addEventListener("input", recheck);
  form.addEventListener("change", recheck);

  var show = function (index, focus) {
    current = Math.max(0, Math.min(steps.length - 1, index));
    steps.forEach(function (st, i) { st.classList.toggle("on", i === current); });
    navItems.forEach(function (li, i) {
      li.classList.toggle("on", i === current);
      li.classList.toggle("done", i < current);
    });
    if (counter) counter.textContent = "Step " + (current + 1) + " of " + steps.length;
    if (focus) {
      var title = steps[current].querySelector(".step-title");
      var headerSpace = hd ? hd.offsetHeight + 12 : 12;
      var top = card.getBoundingClientRect().top + window.scrollY - headerSpace;
      if (window.scrollY > top) window.scrollTo({ top: top, behavior: reduce ? "auto" : "smooth" });
      if (title) title.focus({ preventScroll: true });
    }
  };

  var stepIsValid = function (st) {
    checkPhone();
    var ok = markInvalid(st);
    if (!ok) {
      say("Kindly complete the marked fields.", true);
      var first = st.querySelector("input:invalid, select:invalid, textarea:invalid");
      if (first) first.focus();
    } else {
      say("");
    }
    return ok;
  };

  if (steps.length > 1) {
    form.classList.add("stepped");
    show(0, false);
    form.addEventListener("click", function (e) {
      if (e.target.closest("[data-next]")) {
        if (stepIsValid(steps[current])) show(current + 1, true);
      } else if (e.target.closest("[data-back]")) {
        say("");
        show(current - 1, true);
      }
    });
    // Enter in a single-line field moves to the next step rather than submitting early.
    form.addEventListener("keydown", function (e) {
      if (e.key === "Enter" && e.target.tagName === "INPUT" && e.target.type !== "checkbox" && current < steps.length - 1) {
        e.preventDefault();
        if (stepIsValid(steps[current])) show(current + 1, true);
      }
    });
  }

  /* The brief, written out as a short letter to Alaa */
  var val = function (name) {
    var el = form.querySelector('[name="' + name + '"]:checked') || form.querySelector('[name="' + name + '"]:not([type="radio"])');
    return el ? String(el.value || "").trim() : "";
  };
  var OPEN = {
    "Buy a home": "I am looking to buy a home", "Rent a home": "I am looking for a home to rent",
    "Sell privately": "I would like to sell my property privately", "Let my property": "I would like to let my property",
    "Invest": "I am looking to invest in property", "Seek advice": "I would value your independent advice on a property matter"
  };
  var WHEN = {
    "As soon as possible": "as soon as possible", "Within 3 months": "within the next three months",
    "3 to 6 months": "in the next three to six months", "6 to 12 months": "within the year",
    "When the right property appears": "whenever the right property appears"
  };
  var compose = function () {
    var req = val("request"), areas = val("areas"), budget = val("budget_or_value"), when = val("timeframe");
    var brief = val("brief"), name = val("name"), how = val("preferred_contact"), time = val("best_time");
    var owner = req === "Sell privately" || req === "Let my property";
    var paras = [];
    if (req) {
      var line = OPEN[req] || req;
      if (areas) line += (owner ? ", in " : " in ") + areas;
      if (budget && budget !== "Prefer not to say") {
        if (budget.indexOf("Monthly") === 0) line += ", on a monthly rent";
        else line += (owner ? ", valued at " : ", with a budget of ") + budget.replace(/^(Under|Over) /, function (m) { return m.toLowerCase(); });
      }
      if (WHEN[when]) line += ", " + WHEN[when];
      paras.push(line + ".");
    }
    if (brief) paras.push(brief);
    if (name || how) {
      var c = how && how !== "Either" ? "Please contact me by " + how.toLowerCase() : "Please contact me by telephone or email";
      if (time && time !== "Any time" && how !== "Email") c += ", ideally in the " + time.toLowerCase();
      paras.push(c + ".");
    }
    return "Dear Alaa,\n\n" + paras.join("\n\n") + "\n\nWith kind regards,\n" + name;
  };

  /* If the mail app does not open, the visitor can open the draft again, use webmail, or copy it. */
  var mailBackup = form.querySelector(".contact-mail-backup");
  var backupLink = mailBackup && mailBackup.querySelector("[data-contact-email]");
  var backupCopy = mailBackup && mailBackup.querySelector("[data-contact-copy]");
  var backupField = mailBackup && mailBackup.querySelector("[data-contact-text]");
  var backupFeedback = mailBackup && mailBackup.querySelector("[data-contact-feedback]");
  var backupLabel = mailBackup && mailBackup.querySelector(".contact-copy-label");
  if (backupCopy) {
    backupCopy.addEventListener("click", function () {
      var value = backupField ? backupField.value : "";
      if (!value) return;
      var copied = function () { if (backupFeedback) backupFeedback.textContent = "Copied. Paste your brief into an email to Alaa and press Send."; };
      var manual = function () {
        if (backupLabel) backupLabel.hidden = false;
        if (backupField) { backupField.focus(); backupField.select(); }
        if (backupFeedback) backupFeedback.textContent = "Select the letter below and copy it into your preferred email app.";
      };
      if (navigator.clipboard && navigator.clipboard.writeText) navigator.clipboard.writeText(value).then(copied, manual);
      else manual();
    });
  }

  form.addEventListener("submit", function (e) {
    e.preventDefault();
    checkPhone();
    if (!markInvalid(form) || !form.checkValidity()) {
      say("Kindly complete the marked fields.", true);
      var first = form.querySelector("input:invalid, select:invalid, textarea:invalid");
      var owner = first && first.closest(".step");
      if (owner && form.classList.contains("stepped")) show(steps.indexOf(owner), false);
      if (first) first.focus();
      return;
    }

    var data = {};
    new FormData(form).forEach(function (v, k) { data[k] = typeof v === "string" ? v.trim() : v; });
    if (data._honey) return; // A bot filled the hidden field.

    var fullName = String(data.name || "").replace(/[\r\n<>]/g, " ").trim().slice(0, 80);
    var subject = "Crownsmere Estate | Private Property Brief | " + fullName;
    var body = compose() + "\n\n" +
      "CONTACT DETAILS\n" +
      "Email: " + String(data.email || "") + "\n" +
      "Telephone: " + String(data.phone || "") + "\n" +
      "Preferred contact: " + String(data.preferred_contact || "Either") + "\n" +
      "Best time to call: " + String(data.best_time || "Any time") + "\n\n" +
      "Prepared at crownsmere.com/contact.html";
    var recipient = "alaa.qadir@crownsmere.com";
    var copyRecipient = "hello@crownsmere.com";
    var draft = "mailto:" + recipient + "?cc=" + encodeURIComponent(copyRecipient) +
      "&subject=" + encodeURIComponent(subject) + "&body=" + encodeURIComponent(body);
    if (backupLink) backupLink.href = draft;
    var q = function (o) { return Object.keys(o).map(function (k) { return k + "=" + encodeURIComponent(o[k]); }).join("&"); };
    var gmail = mailBackup && mailBackup.querySelector('[data-webmail="gmail"]');
    var outlook = mailBackup && mailBackup.querySelector('[data-webmail="outlook"]');
    if (gmail) gmail.href = "https://mail.google.com/mail/?" + q({ view: "cm", fs: "1", to: recipient, cc: copyRecipient, su: subject, body: body });
    if (outlook) outlook.href = "https://outlook.live.com/mail/0/deeplink/compose?" + q({ to: recipient, cc: copyRecipient, subject: subject, body: body });
    if (backupField) backupField.value = "To: " + recipient + "\nCc: " + copyRecipient + "\nSubject: " + subject + "\n\n" + body;
    if (backupFeedback) backupFeedback.textContent = "";
    if (backupLabel) backupLabel.hidden = true;
    if (mailBackup) mailBackup.hidden = false;
    say("Your email is ready. Review it in your mail app and press Send.");
    // Opened straight from the visitor's tap, so mobile browsers allow it.
    // window.crownsmereOpenDraft lets the browser tests capture the draft instead of opening a mail app.
    try { (window.crownsmereOpenDraft || function (url) { window.location.href = url; })(draft); }
    catch (err) { /* The visible email link and copy option remain. */ }
  });
})();
