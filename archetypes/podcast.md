---
# Puntata del podcast. Di norma il file lo scrive scripts/podcast-auto/pubblica-puntata.py,
# solo dopo la trascrizione e il controllo dei fatti (scripts/podcast-auto/README.md).
title: "{{ replace .File.ContentBaseName "-" " " | title }}"
date: {{ .Date }}
# Una frase (al massimo 160 caratteri) che dice di che cosa parla la puntata.
description: ""
# Numero progressivo della puntata.
episodio: 0
# File audio in static/podcast/episodi/ (AAC 64 kbps mono, senza metadati).
audio: "/podcast/episodi/AAAA-MM-GG-id-podcast.m4a"
# Durata misurata sul file (ffprobe), per esempio "7 min 12 s".
durata: ""
italianoSemplice: |
  **Questa è una puntata del podcast della Misericordia di Ariccia.**

  Puoi ascoltarla. Sotto c'è tutto il testo della puntata.

  In emergenza chiama il **112**.
draft: true
---

Trascrizione completa e verificata della puntata (obbligatoria: è l'alternativa testuale all'audio).

## Per approfondire sul nostro sito

- [Titolo della pagina](/percorso/)

In emergenza chiama il **112**. La Misericordia di Ariccia fa trasporti programmati, non soccorso d'emergenza.
