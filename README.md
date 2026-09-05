# Sito web — Misericordia di Ariccia

Sito web della **Confraternita di Misericordia di Ariccia ODV**, organizzazione di
volontariato attiva dal 1994 nei Castelli Romani.

🌐 **Online**: https://www.misericordia-ariccia.it/

## Tecnologia

- **Hugo 0.154.5** (extended), sito statico: niente database, niente cookie,
  niente tracker, font auto-ospitati.
- **Deploy** automatico con GitHub Actions su Aruba (FTPS):
  `.github/workflows/deploy.yml` — a ogni push su `main` e ogni notte
  (Liturgia del giorno); `guardiano-liturgia.yml` è la rete di sicurezza.
- **Performance**: CSS e JS in un solo bundle minificato con impronta nel
  nome (cache un anno), immagini con copia WebP e dimensioni esplicite,
  font precaricati, compressione e cache in `static/.htaccess`.
- **SEO**: titoli e descrizioni per pagina, dati strutturati Schema.org
  (organizzazione, briciole, servizi, articoli, FAQ), sitemap e hreflang.

## Struttura del repository

```
sito-misericordia-ariccia/
├── hugo.toml                ← configurazione (menu, contatti, titoli SEO)
├── content/                 ← pagine (news/, servizi/, dossier/, en/…)
├── layouts/                 ← template Hugo (baseof, home, partial, render hook)
├── assets/                  ← CSS, JS, librerie (Hugo Pipes)
├── static/                  ← img/, fonts/, documenti/, .htaccess, robots.txt
├── data/annunci.yaml        ← barra annunci in alto
├── scripts/                 ← ottimizza-immagini.py (JPEG + WebP)
├── contenuti/               ← testi e bozze
└── docs/                    ← appunti di progetto, inventario, benchmark
```

## Lavorare in locale

```bash
CGO_ENABLED=0 go install github.com/gohugoio/hugo@v0.154.5   # se manca
hugo server                       # anteprima su http://localhost:1313
hugo --minify                     # build in public/
python3 scripts/ottimizza-immagini.py static/img/news   # dopo nuove foto
```

Il flusso editoriale completo (articolo + grafica + testi social) è
descritto in `CLAUDE.md`.

## Riferimenti

- **Associazione:** Confraternita di Misericordia di Ariccia ODV — C.F. 90031910582
- **Sede legale:** Via Beata Rosa Venerini, 6 — 00072 Ariccia (RM)
- **Email:** sede@misericordia-ariccia.it

---

*Sviluppo a cura di Sviluppo Italia Digitale. Nessuna credenziale o dato riservato va inserito in questo repository.*
