/* Domande dell'assistente «Diventa volontario» della Misericordia di Ariccia (motore in
   assistente-volontari.js). Dati presi dalla pagina /diventa-volontario/ (età 16-80, attività,
   percorso, recapiti) e dalle indicazioni di Alessandro del 18/11/2026 (patente B per l'ambulanza,
   formatore interno per gli autisti, documenti chiesti solo al colloquio). */
(function () {
  "use strict";
  var radice = document.querySelector("[data-assistente-volontari]");
  if (!radice || !window.AssistenteVolontari) return;

  var WA = "393484068657";
  var EMAIL = "sede@misericordia-ariccia.it";
  var telefono = function (x) {
    return /^[+0-9][0-9 .\/()-]{5,}$/.test(x) && x.replace(/\D/g, "").length >= 6 ||
      "Mi sembra incompleto: scrivi solo il numero, per esempio 333 1234567.";
  };
  var email = function (x) {
    return x === "—" || /^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(x) || "Controlla l'email: manca qualcosa.";
  };
  var giovane = function (a) { return a.eta === "Da 18 a 28 anni"; };
  var trasporti = function (a) { return /Trasporti/.test(a.attivita || ""); };

  window.AssistenteVolontari(radice, {
    classeBottone: "btn av-btn",
    classeBottoneChiaro: "btn av-btn av-btn-chiaro",
    saluto: "Ciao! Sono l'assistente della Misericordia di Ariccia per chi vuole diventare volontario. Ti faccio qualche domanda: ci vogliono 3 o 4 minuti.",
    intestazione: "VOLONTARIO\nVorrei diventare volontario della Misericordia di Ariccia. Ecco le mie risposte all'assistente del sito:",
    recapitoCopia: "348 4068657 (WhatsApp) o a " + EMAIL,
    domande: [
      { k: "privacy", t: "scelta",
        q: "Prima di cominciare: le risposte restano sul tuo telefono o computer, il sito non le riceve e non le salva. Alla fine preparo un messaggio, che controlli e invii tu. Lo leggerà una persona della Misericordia, solo per ricontattarti.",
        o: ["Ho capito, cominciamo", "Non ora"],
        ferma: { "Non ora": "Va bene. Quando vuoi puoi ricominciare, oppure scrivere VOLONTARIO su WhatsApp al 348 4068657." } },
      { k: "eta", t: "scelta", etichetta: "Età",
        q: "Quanti anni hai?",
        o: ["Meno di 16 anni", "16 o 17 anni", "Da 18 a 28 anni", "Da 29 a 80 anni", "Più di 80 anni"],
        ferma: {
          "Meno di 16 anni": "Grazie per il tuo interesse! Si può diventare volontari dai 16 anni: ti aspettiamo appena li compi.",
          "Più di 80 anni": "Grazie di cuore! Il Movimento delle Misericordie accoglie volontari dai 16 agli 80 anni. Per parlarne o per sostenerci in un altro modo chiamaci al 328 8105399."
        },
        dopo: function (v) {
          return v === "16 o 17 anni" ? "Perfetto: si può cominciare dai 16 anni. Visto che sei minorenne, quando ci incontriamo ti spieghiamo che cosa serve, anche da parte dei tuoi genitori." : "";
        } },
      { k: "nome", t: "testo", max: 120, etichetta: "Nome e cognome", autocompleta: "name",
        q: "Come ti chiami? Scrivi nome e cognome." },
      { k: "comune", t: "testo", max: 120, etichetta: "Comune", autocompleta: "address-level2",
        q: "In che comune abiti?" },
      { k: "attivita", t: "multi", etichetta: "Mi interessa",
        q: "Che cosa ti piacerebbe fare? Puoi sceglierne più di una.",
        o: ["Trasporti sanitari e sociali", "Centro di Ascolto e Banco Alimentare", "Assistenza a eventi e manifestazioni", "Formazione e corsi", "Non lo so ancora"],
        esclusiva: "Non lo so ancora",
        dopo: function (v) {
          return v === "Non lo so ancora" ? "Nessun problema: ne parliamo insieme e troviamo il posto giusto per te." : "";
        } },
      { k: "patente", t: "scelta", etichetta: "Patente B", se: trasporti,
        q: "Hai la patente B?",
        o: ["Sì", "No"],
        dopo: function (v) {
          return v === "Sì"
            ? "Bene: per guidare l'ambulanza basta la patente B. Ti prepara alla guida il nostro formatore interno per gli autisti."
            : "Nessun problema: non serve guidare l'ambulanza. Sui trasporti c'è posto anche per chi accompagna e assiste le persone.";
        } },
      { k: "esperienza", t: "multi", etichetta: "Esperienze e corsi",
        q: "Hai già qualche esperienza o corso? Puoi sceglierne più di uno.",
        o: ["Corso di primo soccorso", "BLSD (uso del defibrillatore)", "Soccorritore", "Altro volontariato", "Nessuna, voglio imparare"],
        esclusiva: "Nessuna, voglio imparare",
        dopo: function (v) {
          return /Nessuna/.test(v) ? "Va benissimo: non servono competenze, la formazione la facciamo insieme." : "";
        } },
      { k: "giorni", t: "multi", etichetta: "Quando sono disponibile",
        q: "Quando potresti esserci? Puoi sceglierne più di uno.",
        o: ["Mattina nei giorni feriali", "Pomeriggio nei giorni feriali", "Sera", "Sabato", "Domenica e festivi", "Di notte"] },
      { k: "tempo", t: "scelta", etichetta: "Tempo che posso dedicare",
        q: "Quanto tempo pensi di poter dedicare?",
        o: ["Qualche ora al mese", "Una volta a settimana", "Più volte a settimana", "Ne parliamo insieme"] },
      { k: "scu", t: "scelta", etichetta: "Servizio Civile Universale", se: giovane,
        q: "Hai tra i 18 e i 28 anni: ti interessa anche il Servizio Civile Universale, un anno retribuito al servizio della comunità?",
        o: ["Sì, mi interessa", "No, solo volontariato", "Voglio saperne di più"],
        dopo: function (v) {
          return v === "No, solo volontariato" ? "" : "Trovi tutto nella pagina Servizio Civile Universale del sito: te ne parliamo anche quando ci sentiamo.";
        } },
      { k: "telefono", t: "testo", max: 40, tipo: "tel", etichetta: "Telefono", autocompleta: "tel", v: telefono,
        q: "Il tuo numero di telefono, per richiamarti." },
      { k: "email", t: "testo", max: 160, tipo: "email", etichetta: "Email", autocompleta: "email", facoltativa: true, v: email,
        q: "La tua email, se vuoi lasciarla." },
      { k: "note", t: "testo", max: 600, etichetta: "Note", facoltativa: true,
        q: "Vuoi aggiungere qualcosa su di te?" }
    ],
    chiusura: function (a) {
      return [
        "Grazie, " + a.nome + "! Ci siamo quasi.",
        "Dopo il tuo messaggio ti ricontattiamo per conoscerci. In quell'occasione ti chiederemo i documenti e le dichiarazioni necessari per l'iscrizione, anche sulla salute e sull'assenza di condanne penali."
      ];
    },
    canali: [
      { testo: "Invia su WhatsApp", principale: true, nuovaScheda: true,
        indirizzo: function (t) { return "https://wa.me/" + WA + "?text=" + encodeURIComponent(t); } },
      { testo: "Invia per email",
        indirizzo: function (t, a) { return "mailto:" + EMAIL + "?subject=" + encodeURIComponent("Diventare volontario - " + a.nome) + "&body=" + encodeURIComponent(t); } }
    ],
    dopoInvio: "Ricordati di premere Invia nell'app che si apre. Se preferisci parlarci a voce, per le iscrizioni chiama il 328 8105399."
  });
})();
