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

  /* Apparizione dolce degli elementi allo scroll */
  var rivelabili = document.querySelectorAll(".rivela");
  if ("IntersectionObserver" in window && !riduciMotion && rivelabili.length) {
    var oss = new IntersectionObserver(function (voci) {
      voci.forEach(function (v) {
        if (v.isIntersecting) { v.target.classList.add("visibile"); oss.unobserve(v.target); }
      });
    }, { threshold: 0.15 });
    rivelabili.forEach(function (el) { oss.observe(el); });
  } else {
    rivelabili.forEach(function (el) { el.classList.add("visibile"); });
  }
  /* Rete di sicurezza: dopo 2,5s tutto visibile comunque */
  setTimeout(function () {
    rivelabili.forEach(function (el) { el.classList.add("visibile"); });
  }, 2500);

  /* Contatori animati nella fascia dei numeri */
  function animaContatore(el) {
    var fine = parseInt(el.dataset.conta, 10) || 0;
    if (riduciMotion) { el.textContent = fine; return; }
    var durata = 1400, t0 = null;
    function passo(t) {
      if (!t0) t0 = t;
      var quota = Math.min((t - t0) / durata, 1);
      el.textContent = Math.floor(quota * quota * fine); /* ease-in */
      if (quota < 1) requestAnimationFrame(passo); else el.textContent = fine;
    }
    requestAnimationFrame(passo);
  }
  var contatori = document.querySelectorAll("[data-conta]");
  if ("IntersectionObserver" in window && contatori.length) {
    var ossC = new IntersectionObserver(function (voci) {
      voci.forEach(function (v) {
        if (v.isIntersecting) { animaContatore(v.target); ossC.unobserve(v.target); }
      });
    }, { threshold: 0.6 });
    contatori.forEach(function (el) { ossC.observe(el); });
  } else {
    contatori.forEach(animaContatore);
  }

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
