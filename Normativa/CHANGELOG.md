# Changelog — Normativa

Modifiche rilevanti alle istruzioni e alle skill dell'agente **Normativa**.
Formato ispirato a [Keep a Changelog](https://keepachangelog.com/it/1.1.0/);
[versionamento semantico](https://semver.org/lang/it/). Le versioni
corrispondono ai tag `normativa/vX.Y.Z` e alle relative release.

## [1.0.0] — 2026-07-23

### Aggiunto
- Prima release dell'agente per la ricerca e il monitoraggio della normativa
  tecnica: istruzioni (`CLAUDE.md`), skill di progetto
  `normativa-verifica-online` e script `scansiona.sh`.

### Modificato
- La skill di ricerca `ricerca-fonti-locali` è stata spostata nella cartella
  condivisa `_Common` (una sola copia comune agli agenti Normativa, Guide
  Software e Letteratura Tecnica). Le istruzioni ora la caricano dal percorso
  `../_Common/.claude/skills/ricerca-fonti-locali/SKILL.md`.
