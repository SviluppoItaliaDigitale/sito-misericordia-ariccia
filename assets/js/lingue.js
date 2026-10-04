/* Misericordia di Ariccia — Menù lingue.
   I collegamenti [data-tl] aprono la pagina corrente tradotta
   automaticamente nella lingua scelta (traduttore esterno del browser/Google).
   Nessuno script di terze parti caricato sul sito: solo link in uscita. */
(function () {
  "use strict";
  var url = encodeURIComponent(window.location.href);
  var origine = document.documentElement.lang === "en" ? "en" : "it"; // pagine /en/ già in inglese
  document.querySelectorAll("a[data-tl]").forEach(function (a) {
    var code = a.getAttribute("data-tl");
    a.href = "https://translate.google.com/translate?sl=" + origine + "&tl=" + code + "&u=" + url;
    a.target = "_blank";
    a.rel = "noopener nofollow";
  });
})();
