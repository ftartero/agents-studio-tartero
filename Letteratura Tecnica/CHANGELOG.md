# Changelog — Letteratura Tecnica

Modifiche rilevanti alle istruzioni e alle skill dell'agente **Letteratura
Tecnica**. Formato ispirato a
[Keep a Changelog](https://keepachangelog.com/it/1.1.0/);
[versionamento semantico](https://semver.org/lang/it/). Le versioni
corrispondono ai tag `letteratura-tecnica/vX.Y.Z` e alle relative release.

## [1.0.0] — 2026-07-23

### Aggiunto
- Prima release dell'agente per la ricerca nella letteratura tecnica e nei
  testi di biblioteca: istruzioni (`CLAUDE.md`).

### Modificato
- La skill di ricerca `ricerca-fonti-locali` è stata spostata nella cartella
  condivisa `_Common` (una sola copia comune agli agenti Letteratura Tecnica,
  Guide Software e Normativa). Le istruzioni ora la caricano dal percorso
  `../_Common/.claude/skills/ricerca-fonti-locali/SKILL.md`.
