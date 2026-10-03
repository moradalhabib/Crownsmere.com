(function () {
  "use strict";

  var root = document.documentElement;
  var reduce = window.matchMedia("(prefers-reduced-motion: reduce)").matches;
  root.classList.remove("no-js");

  /* ---------- Footer year ---------- */
  document.querySelectorAll("[data-year]").forEach(function (el) {
    el.textContent = new Date().getFullYear();
  });

  /* ---------- Intro: monogram reveal (home page, once per visit) ---------- */
  var intro = document.querySelector(".intro");
  function ready() { root.classList.add("ready"); }
  if (intro) {
    var seen = false;
    try { seen = sessionStorage.getItem("crownsmere-intro") === "1"; } catch (e) {}
    if (seen || reduce) {
      intro.classList.add("done");
      ready();
    } else {
      document.body.style.overflow = "hidden";
      intro.classList.add("play");
      var finish = function () {
        if (intro.classList.contains("done")) return;
        intro.classList.add("done");
        document.body.style.overflow = "";
        try { sessionStorage.setItem("crownsmere-intro", "1"); } catch (e) {}
      };
      setTimeout(ready, 2700);
      setTimeout(finish, 3700);
      intro.addEventListener("click", function () { ready(); finish(); });
    }
  } else {
    ready();
  }

  /* ---------- Header state ---------- */
  var hd = document.querySelector(".hd");
  function onScrollHeader() { hd && hd.classList.toggle("is-scrolled", window.scrollY > 40); }
  window.addEventListener("scroll", onScrollHeader, { passive: true });
  onScrollHeader();

  /* ---------- Menu ---------- */
  var menuBtn = document.querySelector(".hd-menu");
  var menu = document.getElementById("menu");
  if (menuBtn && menu) {
    var label = menuBtn.querySelector("span");
    var setMenu = function (open) {
      root.classList.toggle("menu-open", open);
      menuBtn.setAttribute("aria-expanded", String(open));
      label.textContent = open ? "Close" : "Menu";
      if (open) menu.removeAttribute("inert"); else menu.setAttribute("inert", "");
    };
    menu.setAttribute("inert", "");
    menuBtn.addEventListener("click", function () {
      setMenu(!root.classList.contains("menu-open"));
    });
    document.addEventListener("keydown", function (e) {
      if (e.key === "Escape" && root.classList.contains("menu-open")) { setMenu(false); menuBtn.focus(); }
    });
    menu.querySelectorAll("a").forEach(function (a) {
      a.addEventListener("click", function () { setMenu(false); });
    });
  }

  /* ---------- Reveal on scroll ---------- */
  var revealEls = document.querySelectorAll("[data-reveal]");
  if ("IntersectionObserver" in window && !reduce) {
    var io = new IntersectionObserver(function (entries) {
      entries.forEach(function (en) {
        if (en.isIntersecting) { en.target.classList.add("in"); io.unobserve(en.target); }
      });
    }, { rootMargin: "0px 0px -10% 0px", threshold: 0.08 });
    revealEls.forEach(function (el) { io.observe(el); });
  } else {
    revealEls.forEach(function (el) { el.classList.add("in"); });
  }

  /* ---------- Scroll-driven details ---------- */
  var heroPx = document.querySelector(".hero-media .px");
  var progress = document.querySelector(".progress");
  var journey = document.querySelector(".journey");
  var track = journey && journey.querySelector(".journey-track");
  var bar = journey && journey.querySelector(".journey-progress i");
  var wide = window.matchMedia("(min-width: 901px)");

  function sizeJourney() {
    if (!journey) return;
    if (!wide.matches || reduce) { journey.style.height = ""; track.style.transform = ""; return; }
    var dist = track.scrollWidth - window.innerWidth;
    journey.style.height = (dist + window.innerHeight) + "px";
  }

  var ticking = false;
  function onScroll() {
    if (ticking) return;
    ticking = true;
    requestAnimationFrame(function () {
      ticking = false;
      var y = window.scrollY;
      if (progress) {
        var total = document.documentElement.scrollHeight - window.innerHeight;
        progress.style.transform = "scaleX(" + (total > 0 ? Math.min(1, y / total) : 0) + ")";
      }
      if (heroPx && !reduce && y < window.innerHeight * 1.2) heroPx.style.transform = "translate3d(0," + (y * -0.12) + "px,0)";
      if (journey && wide.matches && !reduce) {
        var rect = journey.getBoundingClientRect();
        var max = journey.offsetHeight - window.innerHeight;
        var p = Math.min(1, Math.max(0, -rect.top / max));
        var dist = track.scrollWidth - window.innerWidth;
        track.style.transform = "translate3d(" + (-dist * p) + "px,0,0)";
        if (bar) bar.style.transform = "scaleX(" + p + ")";
      }
    });
  }
  window.addEventListener("scroll", onScroll, { passive: true });
  window.addEventListener("resize", function () { sizeJourney(); onScroll(); });
  window.addEventListener("load", function () { sizeJourney(); onScroll(); });
  if (document.fonts && document.fonts.ready) document.fonts.ready.then(function () { sizeJourney(); onScroll(); });
  sizeJourney();
  onScroll();

  /* ---------- Cursor ring ---------- */
  if (window.matchMedia("(hover: hover) and (pointer: fine)").matches && !reduce) {
    var c = document.createElement("div");
    c.className = "cursor";
    c.setAttribute("aria-hidden", "true");
    document.body.appendChild(c);
    var mx = 0, my = 0, cx = 0, cy = 0, running = false;
    var loop = function () {
      cx += (mx - cx) * 0.18;
      cy += (my - cy) * 0.18;
      c.style.transform = "translate3d(" + cx + "px," + cy + "px,0)";
      if (Math.abs(mx - cx) > 0.1 || Math.abs(my - cy) > 0.1) requestAnimationFrame(loop);
      else running = false;
    };
    window.addEventListener("mousemove", function (e) {
      mx = e.clientX; my = e.clientY;
      c.classList.add("on");
      if (!running) { running = true; requestAnimationFrame(loop); }
    });
    document.addEventListener("mouseleave", function () { c.classList.remove("on"); });
    document.addEventListener("mouseover", function (e) {
      c.classList.toggle("hover", !!e.target.closest("a, button, .plate, input, textarea, select"));
    });
  }

  /* ---------- Services sub-navigation: highlight the section in view ---------- */
  var subLinks = document.querySelectorAll(".subnav a");
  if (subLinks.length && "IntersectionObserver" in window) {
    var byId = {};
    subLinks.forEach(function (a) { byId[a.getAttribute("href").slice(1)] = a; });
    var spy = new IntersectionObserver(function (entries) {
      entries.forEach(function (en) {
        if (!en.isIntersecting) return;
        subLinks.forEach(function (a) { a.removeAttribute("aria-current"); });
        var link = byId[en.target.id];
        if (link) {
          link.setAttribute("aria-current", "true");
          link.scrollIntoView({ block: "nearest", inline: "center", behavior: reduce ? "auto" : "smooth" });
        }
      });
    }, { rootMargin: "-45% 0px -50% 0px" });
    Object.keys(byId).forEach(function (id) { var el = document.getElementById(id); if (el) spy.observe(el); });
  }

  /* ---------- Magnetic primary buttons (desktop) ---------- */
  if (window.matchMedia("(hover: hover) and (pointer: fine)").matches && !reduce) {
    document.querySelectorAll(".btn-gold").forEach(function (btn) {
      btn.addEventListener("mousemove", function (e) {
        var r = btn.getBoundingClientRect();
        var dx = e.clientX - (r.left + r.width / 2);
        var dy = e.clientY - (r.top + r.height / 2);
        btn.style.transform = "translate(" + dx * 0.12 + "px," + dy * 0.22 + "px)";
      });
      btn.addEventListener("mouseleave", function () { btn.style.transform = ""; });
    });
  }

  /* ---------- Brief form: three guided steps, then send ----------
     Submissions are delivered to the address in data-endpoint (hello@crownsmere.com).
     Without JavaScript, all three steps show as one long form. */
  var form = document.querySelector("form.letter-form");
  if (form) {
    var status = form.querySelector(".form-status");
    var letter = form.closest(".letter");
    var tel = form.querySelector('input[type="tel"]');
    var steps = Array.prototype.slice.call(form.querySelectorAll(".step"));
    var navItems = form.querySelectorAll(".steps-nav li");
    var counter = form.querySelector(".step-count");
    var current = 0;
    var sending = false;

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
    form.addEventListener("input", function () { if (form.querySelector(".invalid")) markInvalid(form); });
    form.addEventListener("change", function () { if (form.querySelector(".invalid")) markInvalid(form); });

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
        var top = letter.getBoundingClientRect().top + window.scrollY - 90;
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

    form.addEventListener("submit", function (e) {
      e.preventDefault();
      if (sending) return;
      checkPhone();
      if (!markInvalid(form) || !form.checkValidity()) {
        say("Kindly complete the marked fields.", true);
        var first = form.querySelector("input:invalid, select:invalid, textarea:invalid");
        var owner = first && first.closest(".step");
        if (owner && form.classList.contains("stepped")) show(steps.indexOf(owner), false);
        if (first) first.focus();
        return;
      }

      letter.classList.remove("sealed");
      void letter.offsetWidth;
      letter.classList.add("sealed");

      var data = {};
      new FormData(form).forEach(function (v, k) { data[k] = typeof v === "string" ? v.trim() : v; });

      var done = function () {
        form.reset();
        form.classList.add("sent");
        say("Your brief has been received. Alaa will be in touch with you personally.");
        var panel = form.querySelector(".sent-panel");
        if (panel) panel.focus();
      };

      // Honeypot: bots fill hidden fields. Pretend all is well and send nothing.
      if (data._honey) { done(); return; }
      delete data._honey;

      var endpoint = form.getAttribute("data-endpoint");
      if (!endpoint) { say("Online enquiries open shortly. Kindly email hello@crownsmere.com.", true); return; }

      sending = true;
      say("Sending your brief\u2026");
      fetch(endpoint, {
        method: "POST",
        headers: { "Content-Type": "application/json", Accept: "application/json" },
        body: JSON.stringify(data)
      })
        .then(function (r) { return r.json().catch(function () { return {}; }).then(function (j) { return { ok: r.ok, j: j }; }); })
        .then(function (res) {
          if (!res.ok || String(res.j.success) === "false") throw new Error(res.j.message || "failed");
          done();
        })
        .catch(function () {
          say("The message could not be sent just now. Kindly try again, or email hello@crownsmere.com.", true);
        })
        .then(function () { sending = false; });
    });
  }
})();
