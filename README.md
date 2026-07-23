# Agents Studio Tartero

Questo repository conserva le varie versioni degli agenti dello Studio Tartero,
con le relative istruzioni (`CLAUDE.md`) e skill.

## Struttura

Ogni cartella corrisponde a un agente/area di lavoro:

- **Gare** — gestione gare d'appalto (offerta tecnica, DGUE, requisiti, modulistica…)
- **Normativa** — ricerca e verifica normativa
- **Guide Software** — guide e documentazione software
- **Letteratura Tecnica** — fonti e letteratura tecnica
- **Lavori** — gestione lavori/commesse
- **Prezziari** — estrazione prezzi da prezziari
- **Report Call** — registrazione e trascrizione call, generazione report
- **_Common** — risorse condivise (es. voice directory)

## Versionamento e release

Le modifiche si sviluppano direttamente su `main`. Per storicizzare uno stato
degli agenti si crea un tag versione:

```bash
git tag v1.1.0
git push origin v1.1.0
```

Il push di un tag `v*` fa partire il workflow [`.github/workflows/release.yml`](.github/workflows/release.yml),
che crea automaticamente una **GitHub Release** con le note generate dai commit.

Si usa il [versionamento semantico](https://semver.org/lang/it/): `vMAJOR.MINOR.PATCH`.
