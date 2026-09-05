/* ============================================================
   Misericordia di Ariccia ODV — Orchestratore delle animazioni
   GSAP + ScrollTrigger + SplitText + particles.js (auto-ospitati)
   ------------------------------------------------------------
   Effetti (ispirati a Salient e Hub, riscritti nel brand):
   1. Titoli che si svelano riga/parola/carattere (SplitText)
   2. Ingressi allo scroll (fade/zoom/blur/flip) singoli e a gruppi
   3. Parallasse su foto ed elementi
   4. Contatori che salgono mentre contano
   5. Sottolineatura disegnata a mano
   6. Parole che ruotano nel titolo
   7. Tilt 3D leggero sulle card
   8. Particelle nell'hero
   9. Barre che crescono
   Tutto si disattiva con prefers-reduced-motion.
   ============================================================ */
(function () {
  "use strict";

  window.__animOK = true; // segnala alla rete di sicurezza in <head> che il JS gira

  var riduci = window.matchMedia && window.matchMedia("(prefers-reduced-motion: reduce)").matches;
  var hover = !window.matchMedia || window.matchMedia("(hover: hover)").matches;
  var haGSAP = window.gsap && window.ScrollTrigger;

  // Questi due non hanno bisogno di GSAP e devono girare anche se GSAP manca:
  if (!riduci) avviaBarraLettura();  // barra di avanzamento lettura in cima
  avviaSkeletonImg();                // immagini che sfumano quando caricate

  // Niente moto: assicura tutto visibile, scrivi i numeri finali ed esci con grazia.
  if (riduci || !haGSAP) {
    document.documentElement.classList.remove("anim-pronto");
    document.querySelectorAll("[data-conta]").forEach(function (el) {
      el.textContent = parseInt(el.getAttribute("data-conta"), 10) || 0;
    });
    document.querySelectorAll(".barra-cresce > span[data-barra]").forEach(function (s) {
      s.style.width = (parseFloat(s.getAttribute("data-barra")) || 0) + "%";
    });
    return;
  }

  try {
    gsap.registerPlugin(ScrollTrigger);
    var haSplit = !!window.SplitText;
    if (haSplit) gsap.registerPlugin(SplitText);

    /* ---- 1. Titoli SPLIT: riga / parola / carattere ---- */
    if (haSplit) {
      document.querySelectorAll("[data-split]").forEach(function (el) {
        var modo = el.getAttribute("data-split") || "words"; // words | chars | lines
        var tipo = modo === "chars" ? "chars,words" : (modo === "lines" ? "lines" : "words");
        var split;
        try { split = new SplitText(el, { type: tipo, linesClass: "riga-maschera" }); }
        catch (e) { el.style.opacity = 1; return; }
        var pezzi = split[modo] || split.words;
        gsap.set(el, { opacity: 1 });
        if (modo === "lines") {
          gsap.from(pezzi, {
            yPercent: 118, duration: .95, ease: "power3.out", stagger: .13,
            scrollTrigger: { trigger: el, start: "top 86%" }
          });
        } else {
          gsap.from(pezzi, {
            y: 30, opacity: 0, duration: .7, ease: "power3.out",
            stagger: modo === "chars" ? .02 : .06,
            scrollTrigger: { trigger: el, start: "top 86%" }
          });
        }
      });
    }

    /* ---- 2a. Ingressi singoli allo scroll [data-anim] ---- */
    document.querySelectorAll("[data-anim]").forEach(function (el) {
      var ritardo = parseFloat(el.getAttribute("data-anim-delay")) || 0;
      gsap.to(el, {
        opacity: 1, x: 0, y: 0, scale: 1, rotationX: 0, filter: "blur(0px)",
        duration: .9, delay: ritardo, ease: "power3.out",
        scrollTrigger: { trigger: el, start: "top 88%" }
      });
    });

    /* ---- 2b. Ingressi a gruppo con stagger [data-anim-group] ---- */
    document.querySelectorAll("[data-anim-group]").forEach(function (g) {
      gsap.to(g.children, {
        opacity: 1, y: 0, duration: .8, ease: "power3.out", stagger: .12,
        scrollTrigger: { trigger: g, start: "top 85%" }
      });
    });

    /* ---- 3. Parallasse [data-parallax="0.2"] ---- */
    document.querySelectorAll("[data-parallax]").forEach(function (el) {
      var f = parseFloat(el.getAttribute("data-parallax")) || 0.18;
      var area = el.closest("[data-parallax-area]") || el.parentElement;
      gsap.to(el, {
        yPercent: f * 100, ease: "none",
        scrollTrigger: { trigger: area, start: "top bottom", end: "bottom top", scrub: true }
      });
    });

    /* ---- 4. Contatori che salgono ---- */
    document.querySelectorAll("[data-conta]").forEach(function (el) {
      var fine = parseInt(el.getAttribute("data-conta"), 10) || 0;
      var obj = { v: 0 };
      ScrollTrigger.create({
        trigger: el, start: "top 88%", once: true,
        onEnter: function () {
          gsap.from(el, { yPercent: 35, opacity: 0, duration: .6, ease: "power2.out" });
          gsap.to(obj, {
            v: fine, duration: 1.7, ease: "power2.out",
            onUpdate: function () { el.textContent = Math.floor(obj.v); },
            onComplete: function () { el.textContent = fine; }
          });
        }
      });
    });

    /* ---- 5. Sottolineatura disegnata a mano ---- */
    document.querySelectorAll(".tratto-mano").forEach(function (t) {
      ScrollTrigger.create({
        trigger: t, start: "top 85%", once: true,
        onEnter: function () { t.classList.add("disegnato"); }
      });
    });

    /* ---- 6. Parole che ruotano nel titolo ---- */
    document.querySelectorAll(".parole-rotanti").forEach(function (box) {
      var spans = box.querySelectorAll("span");
      if (spans.length < 2) return;
      var i = 0;
      gsap.set(spans, { yPercent: 100, opacity: 0 });
      gsap.set(spans[0], { yPercent: 0, opacity: 1 });
      setInterval(function () {
        var cur = spans[i], nxt = spans[(i + 1) % spans.length];
        gsap.to(cur, { yPercent: -100, opacity: 0, duration: .5, ease: "power2.in" });
        gsap.fromTo(nxt, { yPercent: 100, opacity: 0 },
                         { yPercent: 0, opacity: 1, duration: .55, ease: "power2.out" });
        i = (i + 1) % spans.length;
      }, 2300);
    });

    /* ---- 7. Tilt 3D leggero (solo con mouse) ---- */
    if (hover) {
      document.querySelectorAll("[data-tilt]").forEach(function (c) {
        var max = 7;
        c.addEventListener("pointermove", function (e) {
          var r = c.getBoundingClientRect();
          var px = (e.clientX - r.left) / r.width - .5;
          var py = (e.clientY - r.top) / r.height - .5;
          c.style.transform = "perspective(720px) rotateY(" + (px * max) + "deg) rotateX(" + (-py * max) + "deg)";
        });
        c.addEventListener("pointerleave", function () { c.style.transform = ""; });
      });
    }

    /* ---- 8. Barre che crescono ---- */
    document.querySelectorAll(".barra-cresce > span[data-barra]").forEach(function (s) {
      gsap.to(s, {
        width: (parseFloat(s.getAttribute("data-barra")) || 0) + "%",
        duration: 1.4, ease: "power2.out",
        scrollTrigger: { trigger: s, start: "top 92%", once: true }
      });
    });

    /* ---- Ricalcolo posizioni quando i font sono pronti ---- */
    if (document.fonts && document.fonts.ready) {
      document.fonts.ready.then(function () { ScrollTrigger.refresh(); });
    }
    window.addEventListener("load", function () { ScrollTrigger.refresh(); });

  } catch (err) {
    // Qualcosa è andato storto: mostra tutto, niente schermate vuote.
    document.documentElement.classList.remove("anim-pronto");
    if (window.console) console.warn("Animazioni disattivate:", err);
  }

  /* ---- 9. Particelle nell'hero ---- */
  avviaParticelle(false);

  function avviaParticelle(spente) {
    var nodo = document.getElementById("hero-particelle");
    if (!nodo || spente || !window.particlesJS) return;
    particlesJS("hero-particelle", {
      particles: {
        number: { value: 46, density: { enable: true, value_area: 900 } },
        color: { value: ["#f2e433", "#7fd6f3", "#ffffff"] },
        shape: { type: "circle" },
        opacity: { value: .5, random: true, anim: { enable: true, speed: .6, opacity_min: .15 } },
        size: { value: 3, random: true },
        line_linked: { enable: true, distance: 140, color: "#7fd6f3", opacity: .22, width: 1 },
        move: { enable: true, speed: 1.1, direction: "none", random: true, out_mode: "out" }
      },
      interactivity: {
        detect_on: "canvas",
        events: { onhover: { enable: true, mode: "grab" }, onclick: { enable: false }, resize: true },
        modes: { grab: { distance: 160, line_linked: { opacity: .4 } } }
      },
      retina_detect: true
    });
  }

  /* ---- 10. Barra di avanzamento lettura (scroll indicator) ----
     Animata via scaleX (solo transform). Si auto-inserisce se manca. */
  function avviaBarraLettura() {
    var barra = document.querySelector(".barra-lettura");
    if (!barra) {
      barra = document.createElement("div");
      barra.className = "barra-lettura";
      barra.setAttribute("aria-hidden", "true");
      document.body.insertBefore(barra, document.body.firstChild);
    }
    var inCoda = false;
    function aggiorna() {
      var h = document.documentElement;
      var max = h.scrollHeight - h.clientHeight;
      var y = h.scrollTop || window.pageYOffset || 0;
      var p = max > 0 ? y / max : 0;
      if (p < 0) p = 0; else if (p > 1) p = 1;
      barra.style.transform = "scaleX(" + p + ")";
      inCoda = false;
    }
    window.addEventListener("scroll", function () {
      if (!inCoda) { inCoda = true; requestAnimationFrame(aggiorna); }
    }, { passive: true });
    window.addEventListener("resize", aggiorna, { passive: true });
    aggiorna();
  }

  /* ---- 11. Immagini con skeleton: sfumano quando sono caricate ----
     <img data-skeleton ...> resta a opacità 0 finché non è pronta. */
  function avviaSkeletonImg() {
    var imgs = document.querySelectorAll("img[data-skeleton]");
    Array.prototype.forEach.call(imgs, function (img) {
      if (img.complete && img.naturalWidth > 0) { img.classList.add("caricata"); return; }
      img.addEventListener("load", function () { img.classList.add("caricata"); });
      img.addEventListener("error", function () { img.classList.add("caricata"); });
    });
  }
})();
