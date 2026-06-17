/* Misericordia di Ariccia — interazioni del sito (vanilla + Bootstrap) */
(function () {
  "use strict";
  var riduciMotion = window.matchMedia("(prefers-reduced-motion: reduce)").matches;

  /* Ombra alla barra di navigazione quando si scorre */
  var nav = document.querySelector(".navbar-mise");
  if (nav) {
    window.addEventListener("scroll", function () {
      nav.classList.toggle("scrolled", window.scrollY > 10);
    }, { passive: true });
  }

  /* Le apparizioni allo scroll e i contatori sono gestiti da animazioni.js (GSAP). */

  /* Pulsante torna-su */
  var tornaSu = document.getElementById("torna-su");
  if (tornaSu) {
    window.addEventListener("scroll", function () {
      tornaSu.classList.toggle("mostra", window.scrollY > 600);
    }, { passive: true });
    tornaSu.addEventListener("click", function () {
      window.scrollTo({ top: 0, behavior: riduciMotion ? "auto" : "smooth" });
    });
  }

  /* Tooltip Bootstrap (dove richiesti) */
  if (window.bootstrap) {
    document.querySelectorAll('[data-bs-toggle="tooltip"]').forEach(function (el) {
      new bootstrap.Tooltip(el);
    });
  }

  /* Lightbox: le immagini dei contenuti si aprono ingrandite in un modale */
  var modaleEl = document.getElementById("lightbox");
  if (modaleEl && window.bootstrap) {
    var modale = new bootstrap.Modal(modaleEl);
    var img = modaleEl.querySelector("img");
    var didascalia = modaleEl.querySelector(".modal-didascalia");
    document.querySelectorAll(".contenuto img").forEach(function (mini) {
      mini.style.cursor = "zoom-in";
      mini.setAttribute("role", "button");
      mini.setAttribute("tabindex", "0");
      function apri() {
        img.src = mini.src; img.alt = mini.alt || "";
        didascalia.textContent = mini.alt || "";
        modale.show();
      }
      mini.addEventListener("click", apri);
      mini.addEventListener("keydown", function (e) { if (e.key === "Enter" || e.key === " ") { e.preventDefault(); apri(); } });
    });
  }
})();
