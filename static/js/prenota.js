/* Misericordia di Ariccia — Modulo "Richiedi un trasporto".
   Nessun invio a server: costruisce un'email precompilata (mailto:)
   che l'utente controlla e spedisce dalla propria casella. */
(function () {
  "use strict";

  var form = document.getElementById("form-prenota");
  if (!form) return;

  var DEST = "sede@misericordia-ariccia.it";

  function val(nome) {
    var el = form.elements[nome];
    return el && el.value ? el.value.trim() : "";
  }

  form.addEventListener("submit", function (e) {
    e.preventDefault();

    var nome = val("nome"), tel = val("tel");
    if (!nome || !tel) {
      alert("Per favore inserisci almeno nome e telefono, così possiamo richiamarti.");
      (nome ? form.elements.tel : form.elements.nome).focus();
      return;
    }

    var righe = [
      "Richiesta di trasporto dal sito",
      "",
      "Nome e cognome: " + nome,
      "Telefono: " + tel,
      "Tipo di trasporto: " + (val("tipo") || "-"),
      "Numero di persone: " + (val("persone") || "-"),
      "Data: " + (val("data") || "-"),
      "Ora: " + (val("ora") || "-"),
      "Partenza: " + (val("partenza") || "-"),
      "Destinazione: " + (val("destinazione") || "-"),
      "Note: " + (val("note") || "-"),
      "",
      "Attendo conferma. Grazie."
    ];

    var oggetto = "Richiesta di trasporto - " + nome;
    var corpo = righe.join("\n");
    var url = "mailto:" + DEST +
      "?subject=" + encodeURIComponent(oggetto) +
      "&body=" + encodeURIComponent(corpo);

    window.location.href = url;
  });
})();
