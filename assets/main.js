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
  var archive = document.querySelector(".journey");
  var track = archive && archive.querySelector(".journey-track");
  var bar = archive && archive.querySelector(".journey-progress i");
  var wide = window.matchMedia("(min-width: 901px)");

  function sizeArchive() {
    if (!archive) return;
    if (!wide.matches || reduce) { archive.style.height = ""; track.style.transform = ""; return; }
    var dist = track.scrollWidth - window.innerWidth;
    archive.style.height = (dist + window.innerHeight) + "px";
  }

  var ticking = false;
  function onScroll() {
    if (ticking) return;
    ticking = true;
    requestAnimationFrame(function () {
      ticking = false;
      var y = window.scrollY;
      if (heroPx && !reduce && y < window.innerHeight * 1.2) heroPx.style.transform = "translate3d(0," + (y * -0.12) + "px,0)";
      if (archive && wide.matches && !reduce) {
        var rect = archive.getBoundingClientRect();
        var max = archive.offsetHeight - window.innerHeight;
        var p = Math.min(1, Math.max(0, -rect.top / max));
        var dist = track.scrollWidth - window.innerWidth;
        track.style.transform = "translate3d(" + (-dist * p) + "px,0,0)";
        if (bar) bar.style.transform = "scaleX(" + p + ")";
      }
    });
  }
  window.addEventListener("scroll", onScroll, { passive: true });
  window.addEventListener("resize", function () { sizeArchive(); onScroll(); });
  window.addEventListener("load", function () { sizeArchive(); onScroll(); });
  if (document.fonts && document.fonts.ready) document.fonts.ready.then(function () { sizeArchive(); onScroll(); });
  sizeArchive();
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

  /* ---------- Request-to-be-contacted form ----------
     Submissions are delivered to the address in data-endpoint (hello@crownsmere.com). */
  var form = document.querySelector("form.letter-form");
  if (form) {
    var status = form.querySelector(".form-status");
    var letter = form.closest(".letter");
    var tel = form.querySelector('input[type="tel"]');
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

    var markInvalid = function () {
      form.querySelectorAll(".field, .choices, .consent").forEach(function (el) {
        var bad = el.querySelector("input:invalid, select:invalid, textarea:invalid");
        el.classList.toggle("invalid", !!bad);
      });
    };
    form.addEventListener("input", function () { if (form.querySelector(".invalid")) markInvalid(); });

    form.addEventListener("submit", function (e) {
      e.preventDefault();
      if (sending) return;
      checkPhone();
      markInvalid();
      if (!form.checkValidity()) {
        say("Kindly complete the marked fields.", true);
        form.reportValidity();
        return;
      }

      letter.classList.remove("sealed");
      void letter.offsetWidth;
      letter.classList.add("sealed");

      var data = {};
      new FormData(form).forEach(function (v, k) { data[k] = typeof v === "string" ? v.trim() : v; });

      // Honeypot: bots fill hidden fields. Pretend all is well and send nothing.
      if (data._honey) { form.reset(); say("Thank you. Your request has been received."); return; }
      delete data._honey;

      var endpoint = form.getAttribute("data-endpoint");
      if (!endpoint) { say("Online enquiries open shortly. Kindly email hello@crownsmere.com or call +44 7384 190760.", true); return; }

      sending = true;
      say("Sending your request\u2026");
      fetch(endpoint, {
        method: "POST",
        headers: { "Content-Type": "application/json", Accept: "application/json" },
        body: JSON.stringify(data)
      })
        .then(function (r) { return r.json().catch(function () { return {}; }).then(function (j) { return { ok: r.ok, j: j }; }); })
        .then(function (res) {
          if (!res.ok || String(res.j.success) === "false") throw new Error(res.j.message || "failed");
          form.reset();
          say("Thank you. Your request has been received, and Alaa will be in touch with you personally.");
        })
        .catch(function () {
          say("The post appears delayed. Kindly try again presently, or write to hello@crownsmere.com.", true);
        })
        .then(function () { sending = false; });
    });
  }
})();
