/* Assistente per chi vuole diventare volontario: domande fisse e nessun
   invio al sito. Alla fine prepara il messaggio con le risposte, che la persona controlla e
   invia lei (WhatsApp, email o testo da copiare). Le domande stanno in assistente-volontari-dati.js.
   Uso: <div id="av" data-assistente-volontari></div> e AssistenteVolontari(elemento, dati). */
(function () {
  "use strict";

  function crea(tag, classe, testo) {
    var el = document.createElement(tag);
    if (classe) el.className = classe;
    if (testo !== undefined) el.textContent = testo;
    return el;
  }

  window.AssistenteVolontari = function (radice, D) {
    if (!radice || !D) return;
    radice.innerHTML = "";
    var chat = crea("div", "av-chat");
    chat.setAttribute("aria-live", "polite");
    var barra = crea("form", "av-barra");
    barra.hidden = true;
    var etich = crea("label", "visually-hidden visivamente-nascosto", "La tua risposta");
    etich.setAttribute("for", "av-testo");
    var campo = crea("input");
    campo.id = "av-testo"; campo.type = "text"; campo.setAttribute("autocomplete", "off");
    var invia = crea("button", D.classeBottone || "btn btn-primary", "Invia");
    invia.type = "submit";
    barra.appendChild(etich); barra.appendChild(campo); barra.appendChild(invia);
    radice.appendChild(chat); radice.appendChild(barra);

    var attesa = null;
    // Finché la persona non tocca l'assistente, niente scorrimento né fuoco: la pagina non deve saltare da sola.
    var attivo = false;
    radice.addEventListener("click", function () { attivo = true; }, true);
    radice.addEventListener("keydown", function () { attivo = true; }, true);

    function scorri(el) {
      if (!attivo) return;
      try { el.scrollIntoView({ block: "nearest", behavior: "smooth" }); } catch (e) { try { el.scrollIntoView(false); } catch (e2) {} }
    }
    function dice(t, chi) {
      var d = crea("div", "av-msg " + (chi === "io" ? "av-io" : "av-bot"), t);
      chat.appendChild(d); scorri(d); return d;
    }
    function aggiungi(el) { chat.appendChild(el); scorri(el); return el; }
    function fuoco(el) { if (!attivo) return; try { el.focus({ preventScroll: true }); } catch (e) { try { el.focus(); } catch (e2) {} } }

    function chiediTesto(d) {
      barra.hidden = false; campo.value = "";
      campo.type = d.tipo || "text";
      campo.maxLength = d.max || 200;
      campo.setAttribute("inputmode", d.tipo === "tel" ? "tel" : d.tipo === "email" ? "email" : "text");
      campo.setAttribute("autocomplete", d.autocompleta || "off");
      if (d.facoltativa) {
        var b = crea("div", "av-scelte av-salta");
        var s = crea("button", D.classeBottoneChiaro || "btn btn-outline-primary", "Salta");
        s.type = "button";
        s.onclick = function () { rispondi("—", "Salto questa domanda"); };
        b.appendChild(s); aggiungi(b);
      }
      fuoco(campo);
    }
    barra.addEventListener("submit", function (e) {
      e.preventDefault();
      var v = campo.value.trim();
      if (v) rispondi(v);
    });
    function rispondi(v, mostra) {
      var s = chat.querySelectorAll(".av-salta");
      for (var i = 0; i < s.length; i++) s[i].parentNode.removeChild(s[i]);
      barra.hidden = true; dice(mostra || v, "io");
      if (attesa) { var f = attesa; attesa = null; f(v); }
    }

    function avvia() {
      chat.innerHTML = ""; barra.hidden = true; attesa = null;
      var a = {}, i = 0;
      dice(D.saluto);

      function prosegui() {
        while (i < D.domande.length && D.domande[i].se && !D.domande[i].se(a)) i++;
        if (i >= D.domande.length) return concludi(a);
        var d = D.domande[i];
        dice(typeof d.q === "function" ? d.q(a) : d.q);
        if (d.t === "testo") {
          attesa = function (v) {
            var esito = d.v ? d.v(v) : true;
            if (esito !== true) { dice(esito); return setTimeout(prosegui, 200); }
            a[d.k] = v; i++; dopo(d, v);
          };
          return chiediTesto(d);
        }
        var multi = d.t === "multi";
        var box = crea("div", "av-scelte");
        box.setAttribute("role", "group");
        box.setAttribute("aria-label", multi ? "Scegli una o più risposte, poi premi Conferma" : "Scegli una risposta");
        var bottoni = [];
        d.o.forEach(function (o) {
          var b = crea("button", "av-scelta", o);
          b.type = "button";
          if (multi) b.setAttribute("aria-pressed", "false");
          bottoni.push(b); box.appendChild(b);
        });
        var conferma = null;
        if (multi) {
          conferma = crea("button", D.classeBottone || "btn btn-primary", "Conferma");
          conferma.type = "button"; conferma.disabled = true;
          box.appendChild(conferma);
        }
        bottoni.forEach(function (b) {
          b.onclick = function () {
            if (!multi) {
              box.parentNode.removeChild(box); dice(b.textContent, "io");
              var fine = d.ferma && d.ferma[b.textContent];
              if (fine) { dice(typeof fine === "function" ? fine(a) : fine); return ricomincia(); }
              a[d.k] = b.textContent; i++; return dopo(d, b.textContent);
            }
            var nessuna = d.esclusiva && b.textContent === d.esclusiva;
            var acceso = b.getAttribute("aria-pressed") !== "true";
            b.setAttribute("aria-pressed", acceso ? "true" : "false");
            if (acceso) bottoni.forEach(function (x) {
              if (x !== b && (nessuna || x.textContent === d.esclusiva)) x.setAttribute("aria-pressed", "false");
            });
            conferma.disabled = !box.querySelector('[aria-pressed="true"]');
          };
        });
        if (conferma) conferma.onclick = function () {
          var v = bottoni.filter(function (b) { return b.getAttribute("aria-pressed") === "true"; })
            .map(function (b) { return b.textContent; }).join(", ");
          box.parentNode.removeChild(box); dice(v, "io"); a[d.k] = v; i++; dopo(d, v);
        };
        aggiungi(box);
        fuoco(bottoni[0]);
      }

      function dopo(d, v) {
        var nota = d.dopo ? d.dopo(v, a) : "";
        if (nota) dice(nota);
        setTimeout(prosegui, nota ? 450 : 250);
      }

      function concludi(a) {
        (D.chiusura(a) || []).forEach(function (t) { dice(t); });
        var righe = [D.intestazione];
        D.domande.forEach(function (d) {
          if (d.etichetta && a[d.k] !== undefined && a[d.k] !== "—") righe.push(d.etichetta + ": " + a[d.k]);
        });
        var testo = righe.join("\n");
        dice("Ecco il messaggio con le tue risposte. Controllalo e invialo tu: il sito non lo riceve e non lo salva.");
        var anteprima = crea("pre", "av-anteprima", testo);
        anteprima.setAttribute("tabindex", "0");
        anteprima.setAttribute("aria-label", "Il messaggio che invierai");
        aggiungi(anteprima);
        var box = crea("div", "av-scelte av-invio");
        D.canali.forEach(function (c) {
          var link = crea("a", (c.principale ? D.classeBottone : D.classeBottoneChiaro) || "btn btn-primary", c.testo);
          link.href = c.indirizzo(testo, a);
          if (c.nuovaScheda) { link.target = "_blank"; link.rel = "noopener"; }
          box.appendChild(link);
        });
        var copia = crea("button", D.classeBottoneChiaro || "btn btn-outline-primary", "Copia il testo");
        copia.type = "button";
        copia.onclick = function () { copiaTesto(testo, anteprima); };
        box.appendChild(copia);
        aggiungi(box);
        if (D.dopoInvio) dice(D.dopoInvio);
        ricomincia();
        var primo = box.querySelector("a");
        if (primo) fuoco(primo);
      }

      prosegui();
    }

    function copiaTesto(testo, anteprima) {
      function riuscito() { dice("Testo copiato. Incollalo in un messaggio a " + D.recapitoCopia + " e invialo."); }
      function aMano() {
        try {
          var r = document.createRange(); r.selectNodeContents(anteprima);
          var s = window.getSelection(); s.removeAllRanges(); s.addRange(r);
        } catch (e) {}
        dice("Non siamo riusciti a copiarlo da soli: il testo è selezionato qui sopra, copialo a mano.");
      }
      if (navigator.clipboard && navigator.clipboard.writeText) {
        navigator.clipboard.writeText(testo).then(riuscito, aMano);
        return;
      }
      try {
        var t = document.createElement("textarea");
        t.value = testo; t.setAttribute("readonly", ""); t.style.position = "fixed"; t.style.opacity = "0";
        document.body.appendChild(t); t.select();
        var ok = document.execCommand("copy");
        document.body.removeChild(t);
        if (ok) riuscito(); else aMano();
      } catch (e) { aMano(); }
    }

    function ricomincia() {
      var b = crea("div", "av-scelte");
      var r = crea("button", D.classeBottoneChiaro || "btn btn-outline-primary", "Ricomincia da capo");
      r.type = "button"; r.onclick = avvia;
      b.appendChild(r); aggiungi(b);
    }

    avvia();
  };
})();
