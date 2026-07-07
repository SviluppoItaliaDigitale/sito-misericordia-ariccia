/* Misericordia di Ariccia — Pulsante "copia" (es. IBAN).
   Copia negli appunti il valore in data-copia. Nessuna dipendenza. */
(function () {
  "use strict";
  document.querySelectorAll("[data-copia]").forEach(function (btn) {
    btn.addEventListener("click", function () {
      var testo = btn.getAttribute("data-copia");
      var esito = function () {
        var orig = btn.getAttribute("data-label") || btn.textContent;
        if (!btn.getAttribute("data-label")) btn.setAttribute("data-label", orig);
        btn.classList.add("copiato");
        btn.textContent = "✓ Copiato!";
        setTimeout(function () {
          btn.classList.remove("copiato");
          btn.textContent = btn.getAttribute("data-label");
        }, 2000);
      };
      if (navigator.clipboard && navigator.clipboard.writeText) {
        navigator.clipboard.writeText(testo).then(esito, function () { fallback(testo, esito); });
      } else {
        fallback(testo, esito);
      }
    });
  });

  function fallback(testo, esito) {
    try {
      var ta = document.createElement("textarea");
      ta.value = testo; ta.setAttribute("readonly", "");
      ta.style.position = "absolute"; ta.style.left = "-9999px";
      document.body.appendChild(ta); ta.select();
      document.execCommand("copy");
      document.body.removeChild(ta);
      esito();
    } catch (e) {
      alert("Copia manuale: " + testo);
    }
  }
})();
