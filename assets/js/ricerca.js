/* Misericordia di Ariccia — Ricerca nel sito (client-side).
   Legge un indice JSON generato da Hugo (/index.json) e filtra
   titoli, sezioni e contenuti. Nessuna dipendenza esterna. */
(function () {
  "use strict";

  var indice = null;      // array di pagine
  var caricamento = null; // promise di fetch
  var URL_INDICE = document.currentScript && document.currentScript.dataset.indice
    ? document.currentScript.dataset.indice : "index.json";

  /* Overlay */
  var overlay = document.createElement("div");
  overlay.className = "cerca-overlay";
  overlay.id = "cerca-overlay";
  overlay.innerHTML =
    '<div class="cerca-box" role="dialog" aria-label="Cerca nel sito" aria-modal="true">' +
      '<div class="cerca-testata">' +
        '<svg viewBox="0 0 24 24" aria-hidden="true" fill="none" stroke="currentColor" stroke-width="2">' +
          '<circle cx="11" cy="11" r="7"/><line x1="16.5" y1="16.5" x2="21" y2="21"/></svg>' +
        '<input id="cerca-input" type="search" autocomplete="off" placeholder="Cerca nel sito…" ' +
          'aria-label="Cerca nel sito" aria-controls="cerca-risultati">' +
        '<button type="button" class="cerca-chiudi" aria-label="Chiudi la ricerca">×</button>' +
      '</div>' +
      '<div class="cerca-risultati" id="cerca-risultati" role="listbox"></div>' +
      '<p class="cerca-suggerimento">Suggerimento: prova con “trasporto”, “volontario”, “5x1000”, “servizio civile”.</p>' +
    '</div>';

  var input, risultati, chiudiBtn;

  function normalizza(s) {
    return (s == null ? "" : String(s)).toLowerCase()
      .normalize("NFD").replace(/[̀-ͯ]/g, ""); // rimuove gli accenti
  }

  function evidenzia(testo, termini) {
    /* HTML-escape del testo, poi avvolge le corrispondenze in <mark> */
    var div = document.createElement("div");
    div.textContent = testo == null ? "" : String(testo);
    var safe = div.innerHTML;
    termini.forEach(function (t) {
      if (!t) return;
      var re = new RegExp("(" + t.replace(/[.*+?^${}()|[\]\\]/g, "\\$&") + ")", "ig");
      safe = safe.replace(re, "<mark>$1</mark>");
    });
    return safe;
  }

  function estratto(contenuto, termini) {
    var norm = normalizza(contenuto);
    var pos = -1;
    for (var i = 0; i < termini.length; i++) {
      pos = norm.indexOf(termini[i]);
      if (pos > -1) break;
    }
    if (pos < 0) pos = 0;
    var inizio = Math.max(0, pos - 45);
    var frammento = contenuto.substr(inizio, 160).trim();
    return (inizio > 0 ? "…" : "") + frammento + "…";
  }

  function caricaIndice() {
    if (caricamento) return caricamento;
    caricamento = fetch(URL_INDICE, { credentials: "same-origin" })
      .then(function (r) { return r.ok ? r.json() : []; })
      .then(function (dati) { indice = Array.isArray(dati) ? dati : []; return indice; })
      .catch(function () { indice = []; return indice; });
    return caricamento;
  }

  function cerca(q) {
    var termini = normalizza(q).split(/\s+/).filter(Boolean);
    if (!termini.length) { mostraVuoto("Scrivi una parola per cercare tra le pagine del sito."); return; }
    if (!indice) { mostraVuoto("Caricamento…"); return; }

    var trovati = indice.map(function (p) {
      var fascio = normalizza((p.title || "") + " " + (p.section || "") + " " + (p.content || ""));
      var titoloN = normalizza(p.title || "");
      var punteggio = 0;
      for (var i = 0; i < termini.length; i++) {
        var t = termini[i];
        if (fascio.indexOf(t) === -1) { punteggio = -1; break; }
        if (titoloN.indexOf(t) > -1) punteggio += 5;
        punteggio += 1;
      }
      return { p: p, punteggio: punteggio };
    }).filter(function (x) { return x.punteggio > 0; })
      .sort(function (a, b) { return b.punteggio - a.punteggio; })
      .slice(0, 12);

    if (!trovati.length) { mostraVuoto("Nessun risultato per «" + q + "». Prova con un'altra parola."); return; }

    risultati.innerHTML = trovati.map(function (x) {
      var p = x.p;
      return '<a class="cerca-ris" role="option" href="' + p.url + '">' +
        (p.section ? '<span class="sez">' + evidenzia(p.section, termini) + '</span>' : '') +
        '<span class="tit">' + evidenzia(p.title || p.url, termini) + '</span>' +
        '<p class="estratto">' + evidenzia(estratto(p.content || "", termini), termini) + '</p>' +
        '</a>';
    }).join("");
  }

  function mostraVuoto(msg) {
    risultati.innerHTML = '<p class="cerca-vuoto">' + msg + '</p>';
  }

  function apri() {
    overlay.classList.add("aperto");
    document.body.style.overflow = "hidden";
    caricaIndice().then(function () { if (input.value.trim()) cerca(input.value); });
    setTimeout(function () { input.focus(); }, 30);
    if (!input.value.trim()) mostraVuoto("Scrivi una parola per cercare tra le pagine del sito.");
  }
  function chiudi() {
    overlay.classList.remove("aperto");
    document.body.style.overflow = "";
  }

  function inizializza() {
    document.body.appendChild(overlay);
    input = overlay.querySelector("#cerca-input");
    risultati = overlay.querySelector("#cerca-risultati");
    chiudiBtn = overlay.querySelector(".cerca-chiudi");

    var timer;
    input.addEventListener("input", function () {
      clearTimeout(timer);
      timer = setTimeout(function () { cerca(input.value); }, 120);
    });

    /* frecce su/giù + invio per navigare i risultati */
    input.addEventListener("keydown", function (e) {
      var voci = Array.prototype.slice.call(risultati.querySelectorAll(".cerca-ris"));
      if (!voci.length) return;
      var idx = voci.indexOf(risultati.querySelector(".cerca-ris.attivo"));
      if (e.key === "ArrowDown") { e.preventDefault(); idx = Math.min(voci.length - 1, idx + 1); }
      else if (e.key === "ArrowUp") { e.preventDefault(); idx = Math.max(0, idx - 1); }
      else if (e.key === "Enter" && idx > -1) { e.preventDefault(); voci[idx].click(); return; }
      else return;
      voci.forEach(function (v) { v.classList.remove("attivo"); });
      if (voci[idx]) { voci[idx].classList.add("attivo"); voci[idx].scrollIntoView({ block: "nearest" }); }
    });

    chiudiBtn.addEventListener("click", chiudi);
    overlay.addEventListener("click", function (e) { if (e.target === overlay) chiudi(); });
    document.addEventListener("keydown", function (e) {
      if (e.key === "Escape" && overlay.classList.contains("aperto")) chiudi();
      /* scorciatoia: "/" apre la ricerca */
      if (e.key === "/" && !/^(INPUT|TEXTAREA|SELECT)$/.test(document.activeElement.tagName)) {
        e.preventDefault(); apri();
      }
    });

    /* collega tutti i pulsanti "Cerca" della pagina */
    document.querySelectorAll("[data-cerca-apri]").forEach(function (b) {
      b.addEventListener("click", function (e) { e.preventDefault(); apri(); });
    });
  }

  if (document.readyState === "loading") {
    document.addEventListener("DOMContentLoaded", inizializza);
  } else {
    inizializza();
  }
})();
