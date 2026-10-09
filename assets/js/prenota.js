/* Misericordia di Ariccia — Moduli "Richiedi un trasporto" e
   "Assistenza sanitaria per eventi".
   Nessun invio a server: il modulo prepara il messaggio e lo apre
   nell'app di posta (mailto:) o in WhatsApp; l'utente lo controlla e lo
   spedisce lui. In più «Copia il testo» lo mette negli appunti, per chi
   non ha un'app di posta configurata o non riesce ad aprire WhatsApp. */
(function () {
  "use strict";

  var EN = document.documentElement.lang === "en";
  var DEST = "sede@misericordia-ariccia.it";
  var WA = "393484068657";

  var COMUNE = EN ? {
    manca: "Please enter at least your name and phone number, so we can call you back.",
    aperto: "Your app should now be open with the message ready: remember to press Send there. If nothing opened, use «Copy the text» or call us on 348 4068657.",
    copiato: "Text copied. Paste it into an email to " + DEST + " or a WhatsApp message to 348 4068657, then send it.",
    noCopia: "We could not copy the text automatically: select it below and copy it by hand."
  } : {
    manca: "Per favore inserisci almeno nome e telefono, così possiamo richiamarti.",
    aperto: "Ora dovrebbe essersi aperta la tua app con il messaggio pronto: ricordati di premere Invia. Se non si è aperto nulla, usa «Copia il testo» oppure chiamaci al 348 4068657.",
    copiato: "Testo copiato. Incollalo in un'email a " + DEST + " o in un messaggio WhatsApp al 348 4068657, poi invialo.",
    noCopia: "Non siamo riusciti a copiare il testo da soli: selezionalo qui sotto e copialo a mano."
  };

  var MODULI = {
    "form-prenota": {
      campi: ["nome", "tel", "tipo", "persone", "data", "ora", "partenza", "destinazione", "note"],
      T: EN ? {
        intro: "Transport request from the website (English page)",
        nome: "Name", tel: "Phone", tipo: "Type of transport", persone: "Number of people",
        data: "Date", ora: "Time", partenza: "Pick-up", destinazione: "Destination", note: "Notes",
        fine: "I look forward to your confirmation. Thank you.", oggetto: "Transport request - "
      } : {
        intro: "Richiesta di trasporto dal sito",
        nome: "Nome e cognome", tel: "Telefono", tipo: "Tipo di trasporto", persone: "Numero di persone",
        data: "Data", ora: "Ora", partenza: "Partenza", destinazione: "Destinazione", note: "Note",
        fine: "Attendo conferma. Grazie.", oggetto: "Richiesta di trasporto - "
      }
    },
    "form-eventi": {
      campi: ["nome", "tel", "ente", "evento", "data", "orario", "luogo", "partecipanti", "note"],
      T: EN ? {
        intro: "Request for event medical cover from the website (English page)",
        nome: "Name", tel: "Phone", ente: "Organisation or association", evento: "Type of event",
        data: "Date", orario: "Times", luogo: "Venue", partecipanti: "Expected attendance", note: "Notes",
        fine: "I look forward to your quote. Thank you.", oggetto: "Event medical cover request - "
      } : {
        intro: "Richiesta di assistenza sanitaria per evento dal sito",
        nome: "Nome e cognome", tel: "Telefono", ente: "Ente o associazione", evento: "Tipo di evento",
        data: "Data", orario: "Orario", luogo: "Luogo", partecipanti: "Partecipanti stimati", note: "Note",
        fine: "Attendo un preventivo. Grazie.", oggetto: "Richiesta assistenza evento - "
      }
    }
  };

  Object.keys(MODULI).forEach(function (id) {
    var form = document.getElementById(id);
    if (form) prepara(form, MODULI[id]);
  });

  function prepara(form, conf) {
    var T = conf.T;

    /* Riga di stato letta dagli screen reader (aria-live) */
    var stato = document.createElement("p");
    stato.className = "pf-stato";
    stato.setAttribute("role", "status");
    stato.setAttribute("aria-live", "polite");
    var invio = form.querySelector(".pf-invio");
    invio.parentNode.insertBefore(stato, invio.nextSibling);

    /* Pulsante «Copia il testo» accanto a email e WhatsApp */
    var copia = document.createElement("button");
    copia.type = "button";
    copia.className = "btn btn-outline-secondary btn-lg";
    copia.textContent = EN ? "📋 Copy the text" : "📋 Copia il testo";
    invio.appendChild(copia);

    function val(nome) {
      var el = form.elements[nome];
      return el && el.value ? el.value.trim() : "";
    }

    function messaggio() {
      var nome = val("nome"), tel = val("tel");
      if (!nome || !tel) {
        alert(COMUNE.manca);
        (nome ? form.elements.tel : form.elements.nome).focus();
        return null;
      }
      var righe = [T.intro, ""];
      conf.campi.forEach(function (c) { righe.push(T[c] + ": " + (val(c) || "-")); });
      righe.push("", T.fine);
      return { oggetto: T.oggetto + nome, corpo: righe.join("\n") };
    }

    function mostra(testo, conTesto) {
      stato.textContent = testo;
      var vecchio = form.querySelector(".pf-testo");
      if (vecchio) vecchio.remove();
      if (conTesto) {
        var area = document.createElement("textarea");
        area.className = "pf-testo form-control";
        area.rows = 8;
        area.readOnly = true;
        area.value = conTesto;
        stato.parentNode.insertBefore(area, stato.nextSibling);
        area.focus();
        area.select();
      }
    }

    copia.addEventListener("click", function () {
      var m = messaggio();
      if (!m) return;
      if (navigator.clipboard && window.isSecureContext) {
        navigator.clipboard.writeText(m.corpo).then(
          function () { mostra(COMUNE.copiato); },
          function () { mostra(COMUNE.noCopia, m.corpo); }
        );
      } else {
        mostra(COMUNE.noCopia, m.corpo);
      }
    });

    form.addEventListener("submit", function (e) {
      e.preventDefault();
      var m = messaggio();
      if (!m) return;
      if (e.submitter && e.submitter.hasAttribute("data-whatsapp")) {
        /* Stesso messaggio su WhatsApp: funziona anche sui telefoni senza
           un'app di posta configurata. */
        window.open("https://wa.me/" + WA + "?text=" + encodeURIComponent(m.corpo), "_blank", "noopener");
      } else {
        window.location.href = "mailto:" + DEST +
          "?subject=" + encodeURIComponent(m.oggetto) +
          "&body=" + encodeURIComponent(m.corpo);
      }
      mostra(COMUNE.aperto);
    });
  }
})();
