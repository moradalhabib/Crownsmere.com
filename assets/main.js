(function () {
  "use strict";

  var root = document.documentElement;
  var reduce = window.matchMedia("(prefers-reduced-motion: reduce)").matches;
  root.classList.remove("no-js");

  /* ---------- Roman numerals ---------- */
  function roman(n) {
    var map = [[1000, "M"], [900, "CM"], [500, "D"], [400, "CD"], [100, "C"], [90, "XC"],
      [50, "L"], [40, "XL"], [10, "X"], [9, "IX"], [5, "V"], [4, "IV"], [1, "I"]];
    var out = "";
    map.forEach(function (p) { while (n >= p[0]) { out += p[1]; n -= p[0]; } });
    return out;
  }
  document.querySelectorAll("[data-year]").forEach(function (el) {
    el.textContent = roman(new Date().getFullYear());
  });

  /* ---------- Intro: wax seal (home page, once per visit) ---------- */
  var intro = document.querySelector(".intro");
  function ready() { root.classList.add("ready"); }
  if (intro) {
    var seen = false;
    try { seen = sessionStorage.getItem("crownsmere-sealed") === "1"; } catch (e) {}
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
        try { sessionStorage.setItem("crownsmere-sealed", "1"); } catch (e) {}
      };
      setTimeout(ready, 2500);
      setTimeout(finish, 3300);
      intro.addEventListener("click", function () { ready(); finish(); });
    }
  } else {
    ready();
  }

  /* ---------- London clock ---------- */
  var clock = document.querySelector("[data-clock]");
  if (clock) {
    var fmt;
    try {
      fmt = new Intl.DateTimeFormat("en-GB", { hour: "2-digit", minute: "2-digit", timeZone: "Europe/London" });
    } catch (e) {
      fmt = new Intl.DateTimeFormat("en-GB", { hour: "2-digit", minute: "2-digit" });
    }
    var tick = function () { clock.textContent = fmt.format(new Date()); };
    tick();
    setInterval(tick, 15000);
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
  var crest = document.querySelector(".hero .crest .spin");
  var ghost = document.querySelector(".motto .ghost");
  var archive = document.querySelector(".archive");
  var track = archive && archive.querySelector(".archive-track");
  var bar = archive && archive.querySelector(".archive-progress i");
  var wide = window.matchMedia("(min-width: 801px)");

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
      if (crest && !reduce) crest.style.transform = "rotate(" + (y * 0.04) + "deg)";
      if (ghost && !reduce) {
        var r = ghost.getBoundingClientRect();
        ghost.style.transform = "translate(-50%, -50%) rotate(" + ((r.top - window.innerHeight / 2) * -0.05) + "deg)";
      }
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

  /* ---------- Correspondence form ----------
     Set data-endpoint on the form (e.g. a Formspree URL) to deliver letters. */
  var form = document.querySelector("form.letter-form");
  if (form) {
    var status = form.querySelector(".form-status");
    var letter = form.closest(".letter");
    form.addEventListener("submit", function (e) {
      e.preventDefault();
      if (!form.reportValidity()) return;
      var endpoint = form.getAttribute("data-endpoint");
      letter.classList.remove("sealed");
      void letter.offsetWidth;
      letter.classList.add("sealed");
      if (!endpoint) {
        status.textContent = "Our correspondence desk opens shortly. Kindly write again soon.";
        return;
      }
      status.textContent = "Sealing your letter…";
      fetch(endpoint, { method: "POST", body: new FormData(form), headers: { Accept: "application/json" } })
        .then(function (r) {
          if (!r.ok) throw new Error(r.status);
          form.reset();
          status.textContent = "Your letter has been sealed and sent. We shall reply in due course.";
        })
        .catch(function () {
          status.textContent = "The post appears delayed. Kindly try again presently.";
        });
    });
  }
})();
