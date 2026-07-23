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
- **_Common** — risorse condivise tra più agenti (vedi [`_Common/README.md`](_Common/README.md))

### Skill condivise

Le skill usate da più agenti stanno in **una sola copia** in `_Common`, accanto
alle cartelle-progetto. Attualmente:

- `ricerca-fonti-locali` — worker di ricerca in file locali, condiviso da
  **Normativa**, **Guide Software** e **Letteratura Tecnica**.

Gli agenti la caricano leggendone il `SKILL.md` per percorso relativo
(`../_Common/.claude/skills/ricerca-fonti-locali/SKILL.md`), valido identico su
Windows e Mac.

## Versionamento e release

Le modifiche si sviluppano direttamente su `main`. Le release sono **per singolo
agente**: ogni agente ha la sua linea di versioni indipendente, con changelog
che contiene solo le sue modifiche (più le risorse condivise in `_Common`).

I tag usano il formato `<slug-agente>/vMAJOR.MINOR.PATCH`
([versionamento semantico](https://semver.org/lang/it/)):

| Agente | Slug | Esempio di tag |
|---|---|---|
| Gare | `gare` | `gare/v1.1.0` |
| Normativa | `normativa` | `normativa/v1.0.0` |
| Guide Software | `guide-software` | `guide-software/v1.0.0` |
| Letteratura Tecnica | `letteratura-tecnica` | `letteratura-tecnica/v1.0.0` |
| Lavori | `lavori` | `lavori/v1.0.0` |
| Prezziari | `prezziari` | `prezziari/v1.0.0` |
| Report Call | `report-call` | `report-call/v1.0.0` |

In più, `studio` indica uno **snapshot completo** di tutti gli agenti insieme
(tag globale `vMAJOR.MINOR.PATCH`, changelog dell'intero repository).

### Come fare una release

**Da computer locale** — crea e pusha il tag:

```bash
git tag gare/v1.1.0
git push origin gare/v1.1.0
```

**Da GitHub** — Actions → *Release* → *Run workflow*: scegli l'agente dal menu e
indica la versione. In entrambi i casi parte il workflow
[`.github/workflows/release.yml`](.github/workflows/release.yml), che crea la
release intitolata all'agente (es. *"Gare — gare/v1.1.0"*) con il changelog
filtrato sulla sua cartella.

### Come numerare (semver)

- `PATCH` (`…/v1.0.1`) → correzioni piccole, refusi, ritocchi a una skill.
- `MINOR` (`…/v1.1.0`) → nuova skill, nuova funzionalità, aggiunte.
- `MAJOR` (`…/v2.0.0`) → revisioni che cambiano il modo di lavorare dell'agente.

Suggerimento: prefissa i commit con l'area (`Gare:`, `Normativa:`, `Report Call:`…)
così il changelog di ogni release resta pulito e leggibile.
