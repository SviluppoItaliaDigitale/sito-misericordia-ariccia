/* Misericordia di Ariccia — Strumenti di lettura accessibile per gli articoli.
   1) Ascolta l'articolo (sintesi vocale del browser)
   2) Versione in italiano semplice (mostra/nasconde)
   3) Scarica in Braille (traslitterazione Grado 1, file di testo)
   Nessuna dipendenza esterna. */
(function () {
  "use strict";

  var barra = document.querySelector("[data-lettura]");
  if (!barra) return;

  var articolo = document.querySelector(".pagina-corpo article.contenuto");
  var semplice = document.getElementById("testo-semplice");
  var titolo = (document.querySelector("h1") || {}).textContent || "articolo";

  /* Contenuto attualmente visibile (originale o versione semplice) */
  function contenutoAttivo() {
    if (semplice && !semplice.hidden) return semplice;
    return articolo;
  }
  function testoAttivo() {
    var el = contenutoAttivo();
    return el ? (el.innerText || el.textContent || "").replace(/\s+/g, " ").trim() : "";
  }

  /* ---------------- 1) LETTURA AD ALTA VOCE ---------------- */
  var synth = window.speechSynthesis;
  var btnAscolta = barra.querySelector('[data-lt="ascolta"]');

  if (btnAscolta && synth && typeof SpeechSynthesisUtterance !== "undefined") {
    var inLettura = false, inPausa = false;

    function vociItaliane() {
      var v = synth.getVoices() || [];
      return v.filter(function (x) { return /^it(-|_|$)/i.test(x.lang); });
    }
    function etichetta(stato) {
      var et = btnAscolta.querySelector(".et");
      if (et) et.textContent = stato;
      btnAscolta.setAttribute("aria-pressed", inLettura ? "true" : "false");
    }
    function stop() {
      inLettura = false; inPausa = false;
      try { synth.cancel(); } catch (e) {}
      etichetta("Ascolta");
    }
    function avvia() {
      stop();
      var testo = testoAttivo();
      if (!testo) return;
      /* spezza in frasi per gestire testi lunghi */
      var frasi = testo.match(/[^.!?]+[.!?]*/g) || [testo];
      var it = vociItaliane();
      inLettura = true; inPausa = false; etichetta("Ferma lettura");
      var i = 0;
      (function parlaProssima() {
        if (!inLettura || i >= frasi.length) { stop(); return; }
        var u = new SpeechSynthesisUtterance(frasi[i].trim());
        u.lang = "it-IT"; u.rate = 0.98; u.pitch = 1;
        if (it.length) u.voice = it[0];
        u.onend = function () { i++; parlaProssima(); };
        u.onerror = function () { i++; parlaProssima(); };
        synth.speak(u);
      })();
    }
    btnAscolta.addEventListener("click", function () {
      if (!inLettura) { avvia(); return; }
      /* seconda pressione: pausa/riprendi */
      if (inPausa) { synth.resume(); inPausa = false; etichetta("Ferma lettura"); }
      else { inLettura = false; stop(); }
    });
    /* alcuni browser caricano le voci in ritardo */
    if (typeof synth.onvoiceschanged !== "undefined") synth.onvoiceschanged = vociItaliane;
    window.addEventListener("beforeunload", stop);
  } else if (btnAscolta) {
    btnAscolta.style.display = "none"; // sintesi vocale non supportata
  }

  /* ---------------- 2) ITALIANO SEMPLICE ---------------- */
  var btnSemplice = barra.querySelector('[data-lt="semplice"]');
  if (btnSemplice && semplice && articolo) {
    btnSemplice.addEventListener("click", function () {
      var attiva = semplice.hidden; // se nascosto, lo attiviamo
      semplice.hidden = !attiva;
      articolo.hidden = attiva;
      btnSemplice.setAttribute("aria-pressed", attiva ? "true" : "false");
      var et = btnSemplice.querySelector(".et");
      if (et) et.textContent = attiva ? "Testo originale" : "Italiano semplice";
      if (attiva) semplice.scrollIntoView({ behavior: "smooth", block: "start" });
    });
  } else if (btnSemplice) {
    btnSemplice.style.display = "none";
  }

  /* ---------------- 3) SCARICA IN BRAILLE ---------------- */
  var btnBraille = barra.querySelector('[data-lt="braille"]');

  var BRAILLE = {
    "a": "⠁", "b": "⠃", "c": "⠉", "d": "⠙", "e": "⠑", "f": "⠋", "g": "⠛", "h": "⠓",
    "i": "⠊", "j": "⠚", "k": "⠅", "l": "⠇", "m": "⠍", "n": "⠝", "o": "⠕", "p": "⠏",
    "q": "⠟", "r": "⠗", "s": "⠎", "t": "⠞", "u": "⠥", "v": "⠧", "w": "⠺", "x": "⠭",
    "y": "⠽", "z": "⠵",
    "à": "⠁", "á": "⠁", "è": "⠑", "é": "⠑", "ì": "⠊", "í": "⠊",
    "ò": "⠕", "ó": "⠕", "ù": "⠥", "ú": "⠥",
    ",": "⠂", ";": "⠆", ":": "⠒", ".": "⠲", "?": "⠦", "!": "⠖",
    "'": "⠄", "’": "⠄", "-": "⠤", "–": "⠤", "(": "⠶", ")": "⠶",
    "/": "⠌", "«": "⠶", "»": "⠶", "\"": "⠶", "“": "⠶", "”": "⠶", " ": "⠀"
  };
  var NUM = { "1": "⠁", "2": "⠃", "3": "⠉", "4": "⠙", "5": "⠑", "6": "⠋", "7": "⠛", "8": "⠓", "9": "⠊", "0": "⠚" };
  var SEGNO_NUM = "⠼", SEGNO_MAIUSC = "⠠";

  function inBraille(testo) {
    var out = "", inNumero = false;
    for (var i = 0; i < testo.length; i++) {
      var ch = testo[i];
      var basso = ch.toLowerCase();
      if (ch >= "0" && ch <= "9") {
        if (!inNumero) { out += SEGNO_NUM; inNumero = true; }
        out += NUM[ch];
        continue;
      }
      inNumero = false;
      if (ch !== basso && BRAILLE[basso]) { out += SEGNO_MAIUSC + BRAILLE[basso]; continue; }
      if (BRAILLE[basso]) { out += BRAILLE[basso]; }
      else if (ch === "\n") { out += "\n"; }
      else { out += "⠀"; } // carattere non mappato → spazio braille
    }
    return out;
  }

  function scarica(nomeFile, contenuto) {
    var blob = new Blob([contenuto], { type: "text/plain;charset=utf-8" });
    var url = URL.createObjectURL(blob);
    var a = document.createElement("a");
    a.href = url; a.download = nomeFile;
    document.body.appendChild(a); a.click();
    document.body.removeChild(a);
    setTimeout(function () { URL.revokeObjectURL(url); }, 1000);
  }

  function slug(s) {
    return s.toLowerCase().normalize("NFD").replace(/[̀-ͯ]/g, "")
      .replace(/[^a-z0-9]+/g, "-").replace(/^-+|-+$/g, "").slice(0, 60) || "articolo";
  }

  if (btnBraille) {
    btnBraille.addEventListener("click", function () {
      var testo = (titolo + "\n\n" + testoAttivo()).replace(/\. /g, ".\n");
      var braille = inBraille(testo);
      var intestazione = "Braille (Grado 1, non contratto) — Misericordia di Ariccia\n" +
        "Documento generato dal sito per lettori Braille e display Braille.\n" +
        "----------------------------------------\n\n";
      scarica(slug(titolo) + "-braille.txt", intestazione + braille);
    });
  }
})();
