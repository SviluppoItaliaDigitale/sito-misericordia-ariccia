/* Misericordia di Ariccia — Modulo "Richiedi un trasporto".
   Nessun invio a server: costruisce un'email precompilata (mailto:)
   che l'utente controlla e spedisce dalla propria casella. */
(function () {
  "use strict";

  var form = document.getElementById("form-prenota");
  if (!form) return;

  /* Pagina inglese (/en/richiedi-trasporto/): messaggio con etichette in inglese */
  var EN = document.documentElement.lang === "en";
  var T = EN ? {
    manca: "Please enter at least your name and phone number, so we can call you back.",
    intro: "Transport request from the website (English page)",
    nome: "Name", tel: "Phone", tipo: "Type of transport", persone: "Number of people",
    data: "Date", ora: "Time", partenza: "Pick-up", destinazione: "Destination", note: "Notes",
    fine: "I look forward to your confirmation. Thank you.", oggetto: "Transport request - "
  } : {
    manca: "Per favore inserisci almeno nome e telefono, così possiamo richiamarti.",
    intro: "Richiesta di trasporto dal sito",
    nome: "Nome e cognome", tel: "Telefono", tipo: "Tipo di trasporto", persone: "Numero di persone",
    data: "Data", ora: "Ora", partenza: "Partenza", destinazione: "Destinazione", note: "Note",
    fine: "Attendo conferma. Grazie.", oggetto: "Richiesta di trasporto - "
  };

  var DEST = "sede@misericordia-ariccia.it";
  var WA = "393484068657";

  function val(nome) {
    var el = form.elements[nome];
    return el && el.value ? el.value.trim() : "";
  }

  form.addEventListener("submit", function (e) {
    e.preventDefault();

    var nome = val("nome"), tel = val("tel");
    if (!nome || !tel) {
      alert(T.manca);
      (nome ? form.elements.tel : form.elements.nome).focus();
      return;
    }

    var righe = [
      T.intro,
      "",
      T.nome + ": " + nome,
      T.tel + ": " + tel,
      T.tipo + ": " + (val("tipo") || "-"),
      T.persone + ": " + (val("persone") || "-"),
      T.data + ": " + (val("data") || "-"),
      T.ora + ": " + (val("ora") || "-"),
      T.partenza + ": " + (val("partenza") || "-"),
      T.destinazione + ": " + (val("destinazione") || "-"),
      T.note + ": " + (val("note") || "-"),
      "",
      T.fine
    ];

    var oggetto = T.oggetto + nome;
    var corpo = righe.join("\n");
    if (e.submitter && e.submitter.hasAttribute("data-whatsapp")) {
      /* Stesso messaggio, ma su WhatsApp: funziona anche sui telefoni senza
         un'app di posta configurata. */
      window.open("https://wa.me/" + WA + "?text=" + encodeURIComponent(corpo), "_blank", "noopener");
      return;
    }
    var url = "mailto:" + DEST +
      "?subject=" + encodeURIComponent(oggetto) +
      "&body=" + encodeURIComponent(corpo);

    window.location.href = url;
  });
})();

/* Modulo "Assistenza sanitaria per eventi": stessa logica del trasporto,
   email precompilata senza alcun invio a server. */
(function () {
  "use strict";

  var form = document.getElementById("form-eventi");
  if (!form) return;

  var DEST = "sede@misericordia-ariccia.it";
  var WA = "393484068657";

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
      "Richiesta di assistenza sanitaria per evento dal sito",
      "",
      "Nome e cognome: " + nome,
      "Telefono: " + tel,
      "Ente o associazione: " + (val("ente") || "-"),
      "Tipo di evento: " + (val("evento") || "-"),
      "Data: " + (val("data") || "-"),
      "Orario: " + (val("orario") || "-"),
      "Luogo: " + (val("luogo") || "-"),
      "Partecipanti stimati: " + (val("partecipanti") || "-"),
      "Note: " + (val("note") || "-"),
      "",
      "Attendo un preventivo. Grazie."
    ];

    var oggetto = "Richiesta assistenza evento - " + nome;
    if (e.submitter && e.submitter.hasAttribute("data-whatsapp")) {
      window.open("https://wa.me/" + WA + "?text=" + encodeURIComponent(righe.join("\n")), "_blank", "noopener");
      return;
    }
    var url = "mailto:" + DEST +
      "?subject=" + encodeURIComponent(oggetto) +
      "&body=" + encodeURIComponent(righe.join("\n"));

    window.location.href = url;
  });
})();
