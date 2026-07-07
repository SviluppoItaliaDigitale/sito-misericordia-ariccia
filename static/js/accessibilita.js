/* Misericordia di Ariccia — Strumenti di accessibilità.
   Applica preferenze come classi su <html> e le salva in localStorage.
   Nessuna dipendenza esterna. */
(function () {
  "use strict";

  var CHIAVE = "mise-a11y";
  var html = document.documentElement;

  /* Stato predefinito */
  var stato = {
    scala: 100,        // percentuale font-size radice (90–170)
    dyslexia: false,   // testo ad alta leggibilità
    spacing: false,    // spaziatura aumentata
    links: false,      // evidenzia link
    grayscale: false,  // scala di grigi
    contrast: false,   // contrasto elevato
    invert: false,     // colori invertiti
    noanim: false,     // ferma animazioni
    cursore: false,    // cursore grande
    guida: false       // riga guida di lettura
  };

  /* Carica preferenze salvate */
  try {
    var salvato = JSON.parse(localStorage.getItem(CHIAVE) || "{}");
    for (var k in salvato) { if (k in stato) stato[k] = salvato[k]; }
  } catch (e) { /* localStorage non disponibile */ }

  function salva() {
    try { localStorage.setItem(CHIAVE, JSON.stringify(stato)); } catch (e) {}
  }

  /* Applica lo stato corrente al documento */
  function applica() {
    /* dimensione testo */
    if (stato.scala !== 100) { html.style.fontSize = stato.scala + "%"; }
    else { html.style.fontSize = ""; }

    html.classList.toggle("a11y-dyslexia", stato.dyslexia);
    html.classList.toggle("a11y-spacing", stato.spacing);
    html.classList.toggle("a11y-links", stato.links);
    html.classList.toggle("a11y-no-anim", stato.noanim);
    html.classList.toggle("a11y-cursore", stato.cursore);
    html.classList.toggle("a11y-guida", stato.guida);

    /* filtri visivi combinati */
    var filtri = [];
    if (stato.grayscale) filtri.push("grayscale(1)");
    if (stato.contrast) filtri.push("contrast(1.4)");
    if (stato.invert) filtri.push("invert(1) hue-rotate(180deg)");
    if (filtri.length) {
      html.style.setProperty("--a11y-filtro", filtri.join(" "));
      html.classList.add("a11y-filtri");
    } else {
      html.style.removeProperty("--a11y-filtro");
      html.classList.remove("a11y-filtri");
    }
  }

  /* Applica subito (prima ancora del DOM completo per ridurre lo sfarfallio) */
  applica();

  /* Costruisce il pannello a DOM pronto */
  function crea() {
    var apri = document.createElement("button");
    apri.id = "a11y-apri";
    apri.type = "button";
    apri.setAttribute("aria-label", "Apri gli strumenti di accessibilità");
    apri.setAttribute("aria-expanded", "false");
    apri.innerHTML =
      '<svg viewBox="0 0 24 24" aria-hidden="true" focusable="false" fill="currentColor">' +
      '<circle cx="12" cy="3.6" r="2"/>' +
      '<path d="M21 8.5c0 .6-.4 1-1 1.1l-4.5.7v3.1l1.9 6.1c.2.6-.2 1.2-.8 1.4-.6.2-1.2-.1-1.4-.7L12.6 15h-1.2l-1.6 5.2c-.2.6-.8.9-1.4.7-.6-.2-1-.8-.8-1.4L9.5 13.4V10.3L5 9.6C4.4 9.5 4 9.1 4 8.5c0-.7.6-1.2 1.3-1.1L11 8.2c.7.1 1.3.1 2 0l5.7-.8c.7-.1 1.3.4 1.3 1.1z"/>' +
      '</svg>';

    var pannello = document.createElement("div");
    pannello.className = "a11y-pannello";
    pannello.id = "a11y-pannello";
    pannello.setAttribute("role", "dialog");
    pannello.setAttribute("aria-label", "Strumenti di accessibilità");
    pannello.setAttribute("aria-modal", "false");
    pannello.hidden = true;

    var opzioni = [
      { k: "dyslexia",  ic: "🔤", et: "Testo leggibile", nota: "dislessia" },
      { k: "spacing",   ic: "↔️", et: "Più spaziatura" },
      { k: "links",     ic: "🔗", et: "Evidenzia link" },
      { k: "contrast",  ic: "◐", et: "Contrasto alto" },
      { k: "invert",    ic: "🌗", et: "Colori invertiti" },
      { k: "grayscale", ic: "⬜", et: "Scala di grigi" },
      { k: "guida",     ic: "📏", et: "Guida di lettura" },
      { k: "cursore",   ic: "🖱️", et: "Cursore grande" },
      { k: "noanim",    ic: "⏸️", et: "Ferma animazioni" }
    ];

    var htmlOpz = opzioni.map(function (o) {
      return '<button type="button" class="a11y-opz" data-k="' + o.k + '" aria-pressed="false">' +
        '<span class="ic" aria-hidden="true">' + o.ic + '</span>' +
        '<span>' + o.et + '</span>' +
        (o.nota ? '<span class="stato">' + o.nota + '</span>' : '') +
        '</button>';
    }).join("");

    pannello.innerHTML =
      '<div class="a11y-testata">' +
        '<h2><span aria-hidden="true">♿</span> Accessibilità</h2>' +
        '<button type="button" class="a11y-chiudi" aria-label="Chiudi">×</button>' +
      '</div>' +
      '<p class="a11y-intro">Personalizza la lettura del sito. Le impostazioni restano salvate su questo dispositivo.</p>' +
      '<div class="a11y-testo">' +
        '<span class="a11y-etichetta">Dimensione testo</span>' +
        '<button type="button" class="a11y-step" data-azione="meno" aria-label="Riduci il testo">−</button>' +
        '<span class="a11y-livello" id="a11y-livello">100%</span>' +
        '<button type="button" class="a11y-step" data-azione="piu" aria-label="Ingrandisci il testo">+</button>' +
      '</div>' +
      '<div class="a11y-griglia">' + htmlOpz + '</div>' +
      '<button type="button" class="a11y-reset">↺ Reimposta tutto</button>' +
      '<p class="a11y-nota">Conforme alle preferenze di lettura · nessun dato inviato online</p>';

    var guida = document.createElement("div");
    guida.id = "a11y-guida";
    guida.setAttribute("aria-hidden", "true");

    document.body.appendChild(apri);
    document.body.appendChild(pannello);
    document.body.appendChild(guida);

    /* Aggiorna la UI del pannello in base allo stato */
    function aggiornaUI() {
      pannello.querySelector("#a11y-livello").textContent = stato.scala + "%";
      pannello.querySelectorAll(".a11y-opz").forEach(function (b) {
        b.setAttribute("aria-pressed", stato[b.dataset.k] ? "true" : "false");
      });
    }
    aggiornaUI();

    function apriPannello() {
      pannello.hidden = false;
      pannello.classList.add("aperto");
      apri.setAttribute("aria-expanded", "true");
      var primo = pannello.querySelector(".a11y-chiudi");
      if (primo) primo.focus();
    }
    function chiudiPannello() {
      pannello.classList.remove("aperto");
      pannello.hidden = true;
      apri.setAttribute("aria-expanded", "false");
      apri.focus();
    }
    function toggle() { pannello.classList.contains("aperto") ? chiudiPannello() : apriPannello(); }

    apri.addEventListener("click", toggle);
    pannello.querySelector(".a11y-chiudi").addEventListener("click", chiudiPannello);

    /* dimensione testo */
    pannello.querySelectorAll(".a11y-step").forEach(function (b) {
      b.addEventListener("click", function () {
        var d = b.dataset.azione === "piu" ? 10 : -10;
        stato.scala = Math.min(170, Math.max(90, stato.scala + d));
        applica(); salva(); aggiornaUI();
      });
    });

    /* interruttori */
    pannello.querySelectorAll(".a11y-opz").forEach(function (b) {
      b.addEventListener("click", function () {
        var k = b.dataset.k;
        stato[k] = !stato[k];
        applica(); salva(); aggiornaUI();
      });
    });

    /* reset */
    pannello.querySelector(".a11y-reset").addEventListener("click", function () {
      stato = { scala: 100, dyslexia: false, spacing: false, links: false,
        grayscale: false, contrast: false, invert: false, noanim: false, cursore: false, guida: false };
      applica(); salva(); aggiornaUI();
    });

    /* chiusura con ESC */
    document.addEventListener("keydown", function (e) {
      if (e.key === "Escape" && pannello.classList.contains("aperto")) chiudiPannello();
    });

    /* riga guida che segue il mouse */
    document.addEventListener("mousemove", function (e) {
      if (stato.guida) guida.style.top = (e.clientY - 17) + "px";
    }, { passive: true });
  }

  if (document.readyState === "loading") {
    document.addEventListener("DOMContentLoaded", crea);
  } else {
    crea();
  }
})();
