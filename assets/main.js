(function () {
  "use strict";

  var root = document.documentElement;
  var reduce = window.matchMedia("(prefers-reduced-motion: reduce)").matches;
  root.classList.remove("no-js");

  /* ---------- Footer year ---------- */
  document.querySelectorAll("[data-year]").forEach(function (el) {
    el.textContent = new Date().getFullYear();
  });

  function ready() { root.classList.add("ready"); }
  ready();

  /* ---------- 3D gold crest (home hero). Falls back to the flat monogram without WebGL ---------- */
  var crestCanvas = document.querySelector(".crest-canvas");
  if (crestCanvas) {
    var hero = crestCanvas.closest(".hero3d");
    var gl = null;
    try { gl = document.createElement("canvas").getContext("webgl2") || document.createElement("canvas").getContext("webgl"); } catch (e) {}
    var saveData = navigator.connection && navigator.connection.saveData;
    if (gl && !saveData) {
      import("./vendor/crest.min.js").then(function (m) {
        if (m.mountCrest(crestCanvas, hero)) requestAnimationFrame(function () { hero.classList.add("crest-on"); });
      }).catch(function () {});
    }
  }

  /* ---------- Smooth, weighted scrolling (desktop only; off for reduced motion) ---------- */
  var lenis = null;
  if (!reduce && window.matchMedia("(hover: hover) and (pointer: fine)").matches) {
    var ls = document.createElement("script");
    ls.src = (document.currentScript ? document.currentScript.src.replace(/main\.js.*$/, "") : "assets/") + "vendor/lenis.min.js";
    ls.onload = function () {
      if (!window.Lenis) return;
      lenis = new window.Lenis({ duration: 1.15, smoothWheel: true, anchors: { offset: -90 } });
      var raf = function (t) { lenis.raf(t); requestAnimationFrame(raf); };
      requestAnimationFrame(raf);
    };
    document.head.appendChild(ls);
  }

  /* ---------- Header state ---------- */
  var hd = document.querySelector(".hd");
  function onScrollHeader() {
    if (!hd) return;
    hd.classList.toggle("is-scrolled", window.scrollY > 40);
  }
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

  /* ---------- Split headings into words (they rise in, one after another) ---------- */
  var splitWords = function (el) {
    var n = 0;
    var walk = function (node) {
      Array.prototype.slice.call(node.childNodes).forEach(function (child) {
        if (child.nodeType === 3) {
          var frag = document.createDocumentFragment();
          child.textContent.split(/(\s+)/).forEach(function (part) {
            if (!part) return;
            if (/^\s+$/.test(part)) { frag.appendChild(document.createTextNode(" ")); return; }
            var outer = document.createElement("span");
            outer.className = "sw";
            var inner = document.createElement("span");
            inner.textContent = part;
            inner.style.setProperty("--i", n++);
            outer.appendChild(inner);
            frag.appendChild(outer);
          });
          node.replaceChild(frag, child);
        } else if (child.nodeType === 1) {
          walk(child);
        }
      });
    };
    walk(el);
    el.classList.add("split");
  };
  if (!reduce) document.querySelectorAll("[data-split]").forEach(splitWords);

  /* ---------- Scroll-lit statement: words light up as you read ---------- */
  var lit = [];
  document.querySelectorAll("[data-highlight]").forEach(function (el) {
    if (reduce) return;
    var words = [];
    Array.prototype.slice.call(el.childNodes).forEach(function (child) {
      if (child.nodeType !== 3) return;
      var frag = document.createDocumentFragment();
      child.textContent.split(/(\s+)/).forEach(function (part) {
        if (!part) return;
        if (/^\s+$/.test(part)) { frag.appendChild(document.createTextNode(" ")); return; }
        var w = document.createElement("span");
        w.className = "hw";
        w.textContent = part;
        words.push(w);
        frag.appendChild(w);
      });
      el.replaceChild(frag, child);
    });
    lit.push({ el: el, words: words });
  });

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
  var arch = document.querySelector(".arch");
  if (arch && reduce) arch.classList.add("static");
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
      var vh = window.innerHeight;
      if (arch && !reduce) {
        var ar = arch.getBoundingClientRect();
        var ap = Math.min(1, Math.max(0, -ar.top / Math.max(1, arch.offsetHeight - vh) * 1.15));
        arch.style.setProperty("--p", ap.toFixed(4));
      }
      lit.forEach(function (o) {
        var r = o.el.getBoundingClientRect();
        var prog = Math.min(1, Math.max(0, (vh * 0.85 - r.top) / (r.height + vh * 0.35)));
        var upto = Math.round(prog * o.words.length);
        // words stay lit once read
        for (var k = o.done || 0; k < upto; k++) o.words[k].classList.add("lit");
        o.done = Math.max(o.done || 0, upto);
      });
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
    var lab = document.createElement("b");
    c.appendChild(lab);
    document.addEventListener("mouseover", function (e) {
      var labelled = e.target.closest("[data-cursor]");
      var text = labelled && !e.target.closest(".brief-flip, .leaflet-control") ? labelled.getAttribute("data-cursor") : "";
      lab.textContent = text;
      c.classList.toggle("label", !!text);
      c.classList.toggle("hover", !text && !!e.target.closest("a, button, input, textarea, select, .chip"));
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

  /* ---------- Online map (Leaflet + OpenStreetMap), loaded only when needed ---------- */
  var mapEl = document.getElementById("map");
  if (mapEl) {
    var pins = [];
    try { pins = JSON.parse(mapEl.getAttribute("data-pins") || "[]"); } catch (e) {}
    var markers = {};

    var pair = function (slug, on) {
      var m = markers[slug];
      var li = document.querySelector('.area[data-area="' + slug + '"]');
      if (m && m.getElement()) m.getElement().classList.toggle("hl", on);
      if (li) li.classList.toggle("hl", on);
    };

    var initMap = function () {
      if (!window.L || mapEl.classList.contains("leaflet-container")) return;
      var touch = window.matchMedia("(pointer: coarse)").matches;
      var map = L.map(mapEl, {
        scrollWheelZoom: false,
        dragging: !touch,          // keep one-finger page scrolling on phones; pinch still zooms
        tap: false,
        zoomSnap: 0.25,
        attributionControl: true
      });
      L.tileLayer("https://tile.openstreetmap.org/{z}/{x}/{y}.png", {
        maxZoom: 18,
        minZoom: 10,
        attribution: '&copy; <a href="https://www.openstreetmap.org/copyright" rel="noopener">OpenStreetMap</a> contributors'
      }).addTo(map);
      var bounds = [];
      pins.forEach(function (p) {
        var icon = L.divIcon({ className: "pin pin-" + p.slug, html: "<span>" + p.n + "</span>", iconSize: [34, 34], iconAnchor: [17, 17], popupAnchor: [0, -16] });
        var m = L.marker([p.lat, p.lng], { icon: icon, title: p.name, alt: p.name, keyboard: true, riseOnHover: true }).addTo(map);
        var content = document.createElement("div");
        content.textContent = p.name;
        var small = document.createElement("small");
        small.textContent = "Neighbourhood " + p.n;
        content.appendChild(small);
        m.bindPopup(content, { closeButton: true, autoPanPadding: [24, 24] });
        m.on("mouseover", function () { pair(p.slug, true); });
        m.on("mouseout", function () { pair(p.slug, false); });
        m.on("popupopen", function () { pair(p.slug, true); });
        m.on("popupclose", function () { pair(p.slug, false); });
        markers[p.slug] = m;
        bounds.push([p.lat, p.lng]);
      });
      if (bounds.length) map.fitBounds(bounds, { padding: [36, 36] });
      document.dispatchEvent(new CustomEvent("crownsmere:map"));
      window.addEventListener("resize", function () { map.invalidateSize(); });

      document.querySelectorAll(".area[data-area]").forEach(function (li) {
        var slug = li.getAttribute("data-area");
        li.addEventListener("mouseenter", function () { pair(slug, true); });
        li.addEventListener("mouseleave", function () { pair(slug, false); });
        li.addEventListener("click", function () {
          var m = markers[slug];
          if (!m) return;
          map.flyTo(m.getLatLng(), Math.max(map.getZoom(), 14), { duration: reduce ? 0 : 0.9 });
          m.openPopup();
          if (window.innerWidth < 900) mapEl.scrollIntoView({ block: "center", behavior: reduce ? "auto" : "smooth" });
        });
      });
    };

    var loadLeaflet = function () {
      if (window.L) { initMap(); return; }
      var sc = document.createElement("script");
      sc.src = "assets/vendor/leaflet/leaflet.js";
      sc.onload = initMap;
      document.head.appendChild(sc);
    };

    if ("IntersectionObserver" in window) {
      var mio = new IntersectionObserver(function (entries) {
        if (entries.some(function (en) { return en.isIntersecting; })) { mio.disconnect(); loadLeaflet(); }
      }, { rootMargin: "600px 0px" });
      mio.observe(mapEl);
    } else {
      loadLeaflet();
    }
  }

  /* ---------- Neighbourhood matcher: "What matters to you?" ---------- */
  var chips = document.querySelectorAll(".chip[data-tag]");
  if (chips.length) {
    var areaList = document.querySelector(".areas");
    var out = document.querySelector(".matcher-out");
    var clearBtn = document.querySelector(".matcher-clear");
    var defaultMsg = out ? out.textContent : "";
    var applyMatch = function () {
      var chosen = [];
      chips.forEach(function (ch) { if (ch.getAttribute("aria-pressed") === "true") chosen.push(ch.getAttribute("data-tag")); });
      var items = Array.prototype.slice.call(document.querySelectorAll(".area[data-tags]"));
      var scored = items.map(function (li) {
        var tags = li.getAttribute("data-tags").split(" ");
        return { li: li, slug: li.getAttribute("data-area"), name: li.querySelector(".an").textContent, score: chosen.filter(function (t) { return tags.indexOf(t) > -1; }).length };
      });
      var best = Math.max.apply(null, scored.map(function (x) { return x.score; }).concat([0]));
      var filtering = chosen.length > 0;
      if (areaList) areaList.classList.toggle("filtering", filtering);
      if (mapEl) mapEl.classList.toggle("filtering", filtering);
      var winners = [];
      scored.forEach(function (x) {
        var hit = filtering && best > 0 && x.score === best;
        x.li.classList.toggle("match", hit);
        document.querySelectorAll(".pin-" + x.slug).forEach(function (pin) { pin.classList.toggle("match", hit); });
        if (hit) winners.push(x.name);
      });
      if (clearBtn) clearBtn.hidden = !filtering;
      if (!out) return;
      if (!filtering) { out.textContent = defaultMsg; return; }
      if (!winners.length) { out.textContent = "No single neighbourhood has all of that, which is exactly when a personal search helps."; return; }
      out.innerHTML = "";
      out.appendChild(document.createTextNode(winners.length === 1 ? "Your best match: " : "Your best matches: "));
      var b = document.createElement("b");
      b.textContent = winners.length > 1 ? winners.slice(0, -1).join(", ") + " and " + winners[winners.length - 1] : winners[0];
      out.appendChild(b);
      out.appendChild(document.createTextNode("."));
    };
    chips.forEach(function (ch) {
      ch.addEventListener("click", function () {
        ch.setAttribute("aria-pressed", ch.getAttribute("aria-pressed") === "true" ? "false" : "true");
        applyMatch();
      });
    });
    if (clearBtn) clearBtn.addEventListener("click", function () {
      chips.forEach(function (ch) { ch.setAttribute("aria-pressed", "false"); });
      applyMatch();
    });
    document.addEventListener("crownsmere:map", applyMatch);
  }

  /* ---------- Briefs: cards turn over, and lean towards the pointer ---------- */
  document.querySelectorAll(".brief").forEach(function (card) {
    var inner = card.querySelector(".brief-inner");
    var front = card.querySelector(".brief-front");
    var back = card.querySelector(".brief-back");
    var flip = function (focusNext) {
      var on = !card.classList.contains("flipped");
      card.classList.toggle("flipped", on);
      front.setAttribute("aria-hidden", on ? "true" : "false");
      back.setAttribute("aria-hidden", on ? "false" : "true");
      front.querySelector("[data-flip]").tabIndex = on ? -1 : 0;
      back.querySelector("[data-flip]").tabIndex = on ? 0 : -1;
      if (focusNext) (on ? back : front).querySelector("[data-flip]").focus({ preventScroll: true });
    };
    card.querySelectorAll("[data-flip]").forEach(function (btn) {
      btn.addEventListener("click", function (e) { e.stopPropagation(); flip(true); });
    });
    card.addEventListener("click", function () { flip(false); });
    if (!reduce && window.matchMedia("(hover: hover) and (pointer: fine)").matches) {
      card.addEventListener("mousemove", function (e) {
        var r = card.getBoundingClientRect();
        inner.style.setProperty("--ry", (((e.clientX - r.left) / r.width) - 0.5) * 14 + "deg");
        inner.style.setProperty("--rx", (0.5 - ((e.clientY - r.top) / r.height)) * 10 + "deg");
      });
      card.addEventListener("mouseleave", function () { inner.style.setProperty("--rx", "0deg"); inner.style.setProperty("--ry", "0deg"); });
    }
  });

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

    /* The brief, composed into a letter as the visitor answers */
    var pvBody = document.querySelector("[data-pv-body]");
    var pvName = document.querySelector("[data-pv-name]");
    var pvDate = document.querySelector("[data-pv-date]");
    var preview = document.querySelector(".preview");
    if (pvDate) {
      try { pvDate.textContent = new Date().toLocaleDateString("en-GB", { day: "numeric", month: "long", year: "numeric" }); } catch (e) {}
    }
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
      if (!pvBody) return "";
      var req = val("request"), areas = val("areas"), budget = val("budget_or_value"), when = val("timeframe");
      var brief = val("brief"), name = val("name"), how = val("preferred_contact"), time = val("best_time");
      var paras = [];
      if (req) {
        var line = OPEN[req] || req;
        if (areas) line += (req === "Sell privately" || req === "Let my property" ? ", in " : " in ") + areas;
        if (budget && budget !== "Prefer not to say") {
          if (budget.indexOf("Monthly") === 0) line += ", on a monthly rent";
          else line += (req === "Sell privately" || req === "Let my property" ? ", valued at " : ", with a budget of ") + budget.replace(/^(Under|Over) /, function (m) { return m.toLowerCase(); });
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
      pvBody.innerHTML = "";
      if (!paras.length) {
        var empty = document.createElement("p");
        empty.className = "pv-empty";
        empty.textContent = "Your letter will compose itself here as you answer.";
        pvBody.appendChild(empty);
      } else {
        paras.forEach(function (t) { var p = document.createElement("p"); p.textContent = t; pvBody.appendChild(p); });
      }
      if (pvName) pvName.textContent = name || "\u00a0";
      return "Dear Alaa,\n\n" + paras.join("\n\n") + "\n\nWith kind regards,\n" + name;
    };
    var composeTimer = 0;
    var queueCompose = function () { clearTimeout(composeTimer); composeTimer = setTimeout(compose, 120); };
    form.addEventListener("input", queueCompose);
    form.addEventListener("change", queueCompose);
    compose();

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
      data.letter = compose();

      var done = function () {
        if (preview) preview.classList.add("sealed");
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
