/* Misericordia di Ariccia — interazioni del dossier
   (la barra di lettura e le particelle sono gestite da animazioni.js) */
(function () {
  "use strict";
  var T = document.documentElement.lang === "en"
    ? { espandi: "Expand all", comprimi: "Collapse all" }
    : { espandi: "Espandi tutto", comprimi: "Comprimi tutto" };
  var dossier = document.querySelector("[data-dossier]");
  if (!dossier) return;

  /* ---- 1. Indice: evidenzia la sezione corrente (scroll-spy) ---- */
  var link = Array.prototype.slice.call(document.querySelectorAll(".dsr-indice-link"));
  var sezioni = link
    .map(function (a) {
      var id = a.getAttribute("href");
      return id && id.charAt(0) === "#" ? document.querySelector(id) : null;
    })
    .filter(Boolean);

  if (sezioni.length && "IntersectionObserver" in window) {
    var attivo = null;
    function segna(el) {
      if (attivo === el) return;
      attivo = el;
      link.forEach(function (a) {
        a.classList.toggle("attivo", a.getAttribute("href") === "#" + el.id);
      });
    }
    var visibili = new Map();
    var obs = new IntersectionObserver(function (entries) {
      entries.forEach(function (e) { visibili.set(e.target, e.isIntersecting ? e.intersectionRatio : 0); });
      // sezione più visibile in questo momento
      var best = null, bestR = 0;
      visibili.forEach(function (r, el) { if (r > bestR) { bestR = r; best = el; } });
      if (best) segna(best);
    }, { rootMargin: "-45% 0px -45% 0px", threshold: [0, 0.25, 0.5, 0.75, 1] });
    sezioni.forEach(function (s) { visibili.set(s, 0); obs.observe(s); });
  }

  /* ---- 2. "Espandi tutto" / "Comprimi tutto" per ciascun capitolo ---- */
  document.querySelectorAll("[data-dsr-espandi]").forEach(function (btn) {
    var capitolo = btn.closest(".dsr-capitolo");
    if (!capitolo) return;
    btn.addEventListener("click", function () {
      var opere = capitolo.querySelectorAll("[data-dsr-opera]");
      var apri = btn.getAttribute("aria-expanded") !== "true";
      opere.forEach(function (o) { o.open = apri; });
      btn.setAttribute("aria-expanded", apri ? "true" : "false");
      btn.textContent = apri ? T.comprimi : T.espandi;
    });
  });

  /* ---- 3. Se l'utente apre/chiude a mano, tieni coerente l'etichetta ---- */
  document.querySelectorAll(".dsr-capitolo").forEach(function (capitolo) {
    var btn = capitolo.querySelector("[data-dsr-espandi]");
    if (!btn) return;
    var opere = capitolo.querySelectorAll("[data-dsr-opera]");
    opere.forEach(function (o) {
      o.addEventListener("toggle", function () {
        var tutteAperte = Array.prototype.every.call(opere, function (x) { return x.open; });
        var nessunaAperta = Array.prototype.every.call(opere, function (x) { return !x.open; });
        if (tutteAperte) { btn.setAttribute("aria-expanded", "true"); btn.textContent = T.comprimi; }
        else if (nessunaAperta) { btn.setAttribute("aria-expanded", "false"); btn.textContent = T.espandi; }
      });
    });
  });

  /* ---- 4. Linea del tempo animata: il filo si disegna mentre scorri, i punti
     compaiono, le foto si svelano. Solo con GSAP e movimento attivo
     (niente con prefers-reduced-motion o «Ferma animazioni»). ---- */
  var linea = document.querySelector(".dsr-timeline");
  var ridotto = (window.matchMedia && window.matchMedia("(prefers-reduced-motion: reduce)").matches) ||
    document.documentElement.classList.contains("a11y-no-anim");
  if (linea && window.gsap && window.ScrollTrigger && !ridotto) {
    var filo = document.createElement("span");
    filo.className = "dsr-tl-filo";
    filo.setAttribute("aria-hidden", "true");
    linea.appendChild(filo);
    var disegna = function (p) { filo.style.transform = "translateX(-50%) scaleY(" + p + ")"; };
    ScrollTrigger.create({
      trigger: linea, start: "top 70%", end: "bottom 70%",
      onUpdate: function (st) { disegna(st.progress); }
    });
    linea.querySelectorAll(".dsr-tl-item").forEach(function (li) {
      var punto = li.querySelector(".dsr-tl-punto");
      var anno = li.querySelector(".dsr-tl-anno");
      var foto = li.querySelector(".dsr-tl-foto img");
      var t = gsap.timeline({ scrollTrigger: { trigger: li, start: "top 85%", once: true } });
      if (punto) t.from(punto, { scale: 0, duration: .5, ease: "back.out(3)" }, 0);
      if (anno) t.from(anno, { x: -24, opacity: 0, duration: .6, ease: "power2.out" }, .1);
      if (foto) t.fromTo(foto, { clipPath: "inset(0 0 100% 0)", scale: 1.12 },
        { clipPath: "inset(0 0 0% 0)", scale: 1, duration: 1.1, ease: "power3.out" }, .2);
    });
    // «Ferma animazioni» a pagina aperta: il filo resta disegnato per intero
    document.addEventListener("mise:movimento", function (e) {
      if (e.detail && e.detail.fermo) disegna(1);
    });
  }
})();
