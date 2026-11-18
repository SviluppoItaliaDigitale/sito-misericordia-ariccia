/* ============================================================
   MODALITÀ AULA (Misericordia di Ariccia, 18/11/2026)
   Ripresa dal sito della Protezione Civile di Genzano di Roma, stesso autore
   (modalita-aula.js v1.0 del 06/10/2026, «Proietta» del 16/10/2026), su
   richiesta di Alessandro: «Prendi spunto dal sito della protezione civile di
   Genzano per quanto riguarda la proiezione delle pagine tipo slide e lim».
   Trasforma la pagina in schermate a tutto schermo, con testo grande e senza
   menu, da proiettare sulla LIM: una schermata per sezione (h2), le sezioni
   lunghe proseguono, le immagini con didascalia hanno la loro; tastiera
   (frecce, Pagina su/giù, Inizio/Fine, Esc), pulsanti grandi per il dito,
   A− e A+, «Proietta» su un altro schermo con la Presentation API dove c'è.
   JavaScript entro ECMAScript 2018: deve partire sui browser delle LIM.
   ============================================================ */
(function () {
  'use strict';

  var MAX_CARATTERI = 650;   // oltre, la sezione prosegue su un'altra schermata
  var MAX_BLOCCHI = 5;
  var SALTA = '.strumenti-articolo, .indice-pagina, script, style, noscript, .no-aula, ' +
              '.tts-wrapper, .page-tools, .visually-hidden, [hidden], .sc-scarica, .sc-lim, .condividi';
  var DIMENSIONI = [1, 1.2, 1.45];
  var INTERATTIVI = 'button, iframe, input, select, textarea, canvas, video, audio, form';

  // comandi marcati .no-aula (per esempio «Guarda l'animazione» delle
  // illustrazioni) non rendono interattivo il riquadro: in aula si tolgono
  function interattivo(el) {
    if (el.matches(INTERATTIVI)) return true;
    var n = el.querySelectorAll(INTERATTIVI);
    for (var i = 0; i < n.length; i++) {
      if (!n[i].closest('.no-aula')) return true;
    }
    return false;
  }

  function pulisci(nodo) {
    var c = nodo.cloneNode(true);
    c.querySelectorAll(SALTA).forEach(function (n) { n.remove(); });
    c.querySelectorAll('[id]').forEach(function (n) { n.removeAttribute('id'); });
    if (c.removeAttribute) c.removeAttribute('id');
    c.querySelectorAll('img[loading="lazy"]').forEach(function (i) { i.removeAttribute('loading'); });
    // in aula le illustrazioni animate tornano al disegno fermo: lì non c'è il pulsante per fermarle
    c.querySelectorAll('img[data-statica]').forEach(function (i) {
      i.setAttribute('src', i.getAttribute('data-statica'));
      i.setAttribute('alt', i.getAttribute('data-alt-statica') || i.getAttribute('alt'));
    });
    return c;
  }

  function costruisci(sorgente) {
    var titolo = (document.querySelector('main h1, h1') || {}).textContent || document.title;
    var schermate = [];
    var corrente = { titolo: titolo.trim(), blocchi: [], apertura: true };
    function chiudi() {
      if (corrente.blocchi.length || corrente.apertura) schermate.push(corrente);
    }
    function lunghezza(s) {
      return s.blocchi.reduce(function (t, b) { return t + (b.textContent || '').length; }, 0);
    }
    Array.prototype.forEach.call(sorgente.children, function (el) {
      if (el.matches(SALTA)) return;
      if (el.tagName === 'H2') {
        chiudi();
        corrente = { titolo: el.textContent.trim(), blocchi: [] };
        return;
      }
      // riquadri interattivi (mappe da caricare, moduli, giochi): copiati in
      // una schermata non funzionerebbero, restano nella pagina
      if (interattivo(el)) return;
      var c = pulisci(el);
      if (!c.textContent.trim() && !c.querySelector('img, svg, table')) return;
      if (el.tagName === 'FIGURE' || el.classList.contains('galleria')) {
        chiudi();
        schermate.push({ titolo: corrente.titolo, blocchi: [c], figura: true });
        corrente = { titolo: corrente.titolo, blocchi: [], segue: true };
        return;
      }
      if (corrente.blocchi.length &&
          (lunghezza(corrente) + c.textContent.length > MAX_CARATTERI || corrente.blocchi.length >= MAX_BLOCCHI)) {
        chiudi();
        corrente = { titolo: corrente.titolo, blocchi: [], segue: true };
      }
      corrente.blocchi.push(c);
    });
    chiudi();
    // le schermate di sola continuazione rimaste vuote non servono
    return schermate.filter(function (s) { return s.blocchi.length || s.apertura; });
  }

  var SEGNO_SCHERMO = '#aula-schermo';
  var puoProiettare = 'PresentationRequest' in window && window.isSecureContext;

  function apri(btn, schermo) {
    var sorgente = document.querySelector(btn.getAttribute('data-aula-sorgente'));
    if (!sorgente) return;
    var schermate = costruisci(sorgente);
    var indice = 0, dimensione = 0;
    var collegamento = null;   // lato docente: la proiezione in corso

    var box = document.createElement('div');
    box.className = 'aula';
    box.setAttribute('role', 'dialog');
    box.setAttribute('aria-modal', 'true');
    box.setAttribute('aria-label', 'Modalità Aula: ' + schermate[0].titolo);
    box.innerHTML =
      '<div class="aula-barra">' +
        '<span class="aula-contatore"></span>' +
        '<span class="aula-annuncio" aria-live="polite"></span>' +
        '<span class="aula-comandi">' +
          (puoProiettare && !schermo ?
            '<button type="button" class="aula-btn aula-btn-proietta" data-azione="proietta" aria-pressed="false">' +
              '<svg aria-hidden="true" width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round"><path d="M2 16a5 5 0 0 1 5 5M2 12a9 9 0 0 1 9 9M2 8V5a2 2 0 0 1 2-2h16a2 2 0 0 1 2 2v14a2 2 0 0 1-2 2h-6"/><path d="M2 20.5h.01"/></svg><span class="aula-btn-testo"> Proietta</span></button>' : '') +
          '<button type="button" class="aula-btn" data-azione="meno" aria-label="Testo più piccolo">A−</button>' +
          '<button type="button" class="aula-btn" data-azione="piu" aria-label="Testo più grande">A+</button>' +
          '<button type="button" class="aula-btn" data-azione="esci">Esci <span class="aula-tasto">Esc</span></button>' +
        '</span>' +
      '</div>' +
      '<div class="aula-schermata"></div>' +
      '<div class="aula-navigazione">' +
        '<button type="button" class="aula-btn aula-btn-grande" data-azione="indietro">‹ Indietro</button>' +
        '<button type="button" class="aula-btn aula-btn-grande aula-btn-avanti" data-azione="avanti">Avanti ›</button>' +
      '</div>';
    var area = box.querySelector('.aula-schermata');
    var contatore = box.querySelector('.aula-contatore');
    var annuncio = box.querySelector('.aula-annuncio');
    var btnIndietro = box.querySelector('[data-azione="indietro"]');
    var btnAvanti = box.querySelector('[data-azione="avanti"]');
    var btnProietta = box.querySelector('[data-azione="proietta"]');
    if (schermo) box.classList.add('aula-schermo');

    function invia() {
      if (collegamento && collegamento.state === 'connected') {
        try {
          var corsa = area.scrollHeight - area.clientHeight;
          collegamento.send(JSON.stringify({
            h: area.innerHTML, k: area.className, c: contatore.innerHTML, d: dimensione,
            s: corsa > 0 ? area.scrollTop / corsa : 0
          }));
        } catch (e) { /* schermo perso */ }
      }
    }
    // lo schermo segue anche lo scorrimento e le risposte aperte o chiuse
    var attesa = false;
    function inviaPresto() {
      if (!collegamento || attesa) return;
      attesa = true;
      setTimeout(function () { attesa = false; invia(); }, 60);
    }
    if (!schermo) {
      area.addEventListener('scroll', inviaPresto, { passive: true });
      area.addEventListener('toggle', inviaPresto, true);
    }
    function scala(d) {
      dimensione = Math.max(0, Math.min(DIMENSIONI.length - 1, d));
      box.style.setProperty('--aula-scala', DIMENSIONI[dimensione]);
    }
    function statoProiezione(attiva, messaggio) {
      if (!btnProietta) return;
      btnProietta.querySelector('.aula-btn-testo').textContent = attiva ? ' Ferma proiezione' : ' Proietta';
      btnProietta.setAttribute('aria-pressed', attiva ? 'true' : 'false');
      if (messaggio) annuncio.textContent = messaggio;
    }
    function proietta() {
      if (collegamento) { collegamento.terminate(); return; }
      var url = location.href.split('#')[0] + SEGNO_SCHERMO;
      new PresentationRequest([url]).start().then(function (c) {
        collegamento = c;
        statoProiezione(true);
        c.addEventListener('connect', function () {
          invia();
          statoProiezione(true, 'Proiezione avviata: usa questo dispositivo come telecomando');
        });
        function chiusa() {
          if (collegamento !== c) return;
          collegamento = null;
          statoProiezione(false, 'Proiezione terminata');
        }
        c.addEventListener('close', chiusa);
        c.addEventListener('terminate', chiusa);
        if (c.state === 'connected') invia();
      }).catch(function (e) {
        // annullato dal docente: nessun messaggio
        if (e && (e.name === 'AbortError' || e.name === 'NotAllowedError')) return;
        annuncio.textContent = 'Nessuno schermo disponibile: controlla che sia acceso e sulla stessa rete';
        if (btnProietta) btnProietta.title = annuncio.textContent;
      });
    }

    function mostra(i, focus) {
      indice = Math.max(0, Math.min(schermate.length - 1, i));
      var s = schermate[indice];
      area.textContent = '';
      area.classList.toggle('aula-apertura', !!s.apertura);
      area.classList.toggle('aula-figura', !!s.figura);
      var h = document.createElement(s.apertura ? 'h1' : 'h2');
      h.className = 'aula-titolo';
      h.tabIndex = -1;
      h.textContent = s.titolo;
      if (s.segue) {
        var segue = document.createElement('span');
        segue.className = 'aula-segue';
        segue.textContent = ' (continua)';
        h.appendChild(segue);
      }
      area.appendChild(h);
      s.blocchi.forEach(function (b) { area.appendChild(b.cloneNode(true)); });
      if (indice === schermate.length - 1) {
        var fine = document.createElement('p');
        fine.className = 'aula-fine';
        fine.textContent = 'Fine. La pagina completa è su ' + location.host + location.pathname;
        area.appendChild(fine);
      }
      area.scrollTop = 0;
      contatore.innerHTML = '<span class="aula-contatore-parola">Schermata </span>' + (indice + 1) + ' di ' + schermate.length;
      btnIndietro.disabled = indice === 0;
      btnAvanti.disabled = indice === schermate.length - 1;
      // con le frecce il fuoco va al titolo; con i pulsanti resta sul pulsante
      // (si può premere Avanti più volte) e il titolo nuovo si annuncia
      if (focus !== false) { annuncio.textContent = ''; h.focus(); }
      else if (!schermo) annuncio.textContent = 'Schermata ' + (indice + 1) + ' di ' + schermate.length + ': ' + h.textContent;
      invia();
    }
    function esci() {
      if (collegamento) collegamento.terminate();
      document.removeEventListener('keydown', tasti, true);
      if (document.fullscreenElement && document.exitFullscreen) document.exitFullscreen().catch(function () {});
      box.remove();
      document.documentElement.classList.remove('aula-aperta');
      btn.focus();
    }
    function tasti(e) {
      var t = e.target;
      var dentroCampo = t && (t.tagName === 'SUMMARY' || t.tagName === 'BUTTON' || t.tagName === 'A' || t.isContentEditable);
      if (e.key === 'Escape') { e.preventDefault(); esci(); return; }
      if (e.key === 'Tab') {     // il fuoco resta nella finestra
        var f = box.querySelectorAll('button:not([disabled]), a[href], summary, [tabindex="-1"]');
        var tab = Array.prototype.filter.call(f, function (n) { return n.tabIndex >= 0; });
        if (!tab.length) return;
        var primo = tab[0], ultimo = tab[tab.length - 1];
        if (e.shiftKey && (t === primo || !box.contains(t))) { e.preventDefault(); ultimo.focus(); }
        else if (!e.shiftKey && (t === ultimo || !box.contains(t))) { e.preventDefault(); primo.focus(); }
        return;
      }
      if (e.key === 'ArrowRight' || e.key === 'PageDown' || (e.key === ' ' && !dentroCampo)) { e.preventDefault(); mostra(indice + 1); }
      else if (e.key === 'ArrowLeft' || e.key === 'PageUp') { e.preventDefault(); mostra(indice - 1); }
      else if (e.key === 'Home' && !dentroCampo) { e.preventDefault(); mostra(0); }
      else if (e.key === 'End' && !dentroCampo) { e.preventDefault(); mostra(schermate.length - 1); }
    }
    box.addEventListener('click', function (e) {
      var b = e.target.closest('[data-azione]');
      if (!b) return;
      var a = b.getAttribute('data-azione');
      if (a === 'avanti') mostra(indice + 1, false);
      else if (a === 'indietro') mostra(indice - 1, false);
      else if (a === 'esci') esci();
      else if (a === 'proietta') proietta();
      else if (a === 'piu' || a === 'meno') { scala(dimensione + (a === 'piu' ? 1 : -1)); invia(); }
    });

    document.body.appendChild(box);
    document.documentElement.classList.add('aula-aperta');
    if (schermo) {
      // lo schermo della classe: niente comandi, segue il telecomando
      mostra(0, false);
      var ultimo = null;
      return {
        vai: function (dati) {
          if (!dati || typeof dati.h !== 'string') return;
          if (typeof dati.d === 'number') scala(dati.d);
          if (typeof dati.k === 'string') area.className = dati.k;   // apertura centrata, figura
          if (dati.h !== ultimo) {   // contenuto della stessa pagina, composto dal dispositivo del docente
            area.innerHTML = dati.h;
            ultimo = dati.h;
          }
          if (typeof dati.c === 'string') contatore.innerHTML = dati.c;
          var corsa = area.scrollHeight - area.clientHeight;
          area.scrollTop = corsa > 0 && typeof dati.s === 'number' ? dati.s * corsa : 0;
        }
      };
    }
    document.addEventListener('keydown', tasti, true);
    if (box.requestFullscreen) box.requestFullscreen().catch(function () {});
    mostra(0);
  }

  // pagina aperta sullo schermo della classe dal pulsante «Proietta»
  function avviaSchermo(btn) {
    var vista = apri(btn, true);
    if (!vista) return;
    var ricevitore = navigator.presentation && navigator.presentation.receiver;
    if (!ricevitore) return;
    function ascolta(c) {
      c.addEventListener('message', function (e) {
        try { vista.vai(JSON.parse(e.data)); } catch (err) { /* messaggio non valido */ }
      });
    }
    ricevitore.connectionList.then(function (lista) {
      lista.connections.forEach(ascolta);
      lista.addEventListener('connectionavailable', function (e) { ascolta(e.connection); });
    });
  }

  function avvia() {
    document.querySelectorAll('.btn-modalita-aula').forEach(function (btn) {
      var sorgente = document.querySelector(btn.getAttribute('data-aula-sorgente'));
      if (!sorgente || sorgente.querySelectorAll(':scope > h2').length < 2) return;
      btn.hidden = false;
      btn.addEventListener('click', function () { apri(btn); });
      if (location.hash === SEGNO_SCHERMO && navigator.presentation && navigator.presentation.receiver) avviaSchermo(btn);
    });
  }
  if (document.readyState === 'loading') document.addEventListener('DOMContentLoaded', avvia);
  else avvia();
})();
