# Changelog — Report Call

Modifiche rilevanti alle istruzioni, agli script e ai subagenti dell'agente
**Report Call**. Formato ispirato a
[Keep a Changelog](https://keepachangelog.com/it/1.1.0/);
[versionamento semantico](https://semver.org/lang/it/). Le versioni
corrispondono ai tag `report-call/vX.Y.Z` e alle relative release.

## [1.0.0] — 2026-07-23

### Aggiunto
- Prima release dell'agente per la registrazione, trascrizione e reportistica
  delle call: istruzioni (`CLAUDE.md`), subagenti `monitor` e `report-writer`,
  script di acquisizione/trascrizione (`record_chunks.py`, `transcribe_watch.py`,
  `enroll_voice.py`, `stop_hotkey.py`, `beep.py`) e comandi di stop.
- Usa la rubrica vocale condivisa in `_Common/voice_directory` (`embeddings.json`,
  `names.json`), persistente tra le sessioni.
