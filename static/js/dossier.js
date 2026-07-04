/* Misericordia di Ariccia — interazioni del dossier
   (la barra di lettura e le particelle sono gestite da animazioni.js) */
(function () {
  "use strict";
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
      btn.textContent = apri ? "Comprimi tutto" : "Espandi tutto";
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
        if (tutteAperte) { btn.setAttribute("aria-expanded", "true"); btn.textContent = "Comprimi tutto"; }
        else if (nessunaAperta) { btn.setAttribute("aria-expanded", "false"); btn.textContent = "Espandi tutto"; }
      });
    });
  });
})();
