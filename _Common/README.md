# _Common — risorse condivise tra agenti

Questa cartella contiene le risorse usate da **più agenti**, tenute in **una
sola copia** per non doverle duplicare e aggiornare in più punti. Vive
**accanto** alle cartelle-progetto degli agenti (non dentro): dalla cartella di
un progetto la si raggiunge con il percorso relativo `../_Common`, valido
identico su Windows e Mac.

## Contenuto

- **`.claude/skills/ricerca-fonti-locali/`** — skill worker (sola lettura) che
  cerca un argomento in file locali montati (PDF/EPUB/DOCX) e restituisce i
  passaggi citati. Condivisa dagli agenti **Normativa**, **Guide Software** e
  **Letteratura Tecnica**. Gli orchestratori la caricano leggendone il
  `SKILL.md` per percorso:
  `../_Common/.claude/skills/ricerca-fonti-locali/SKILL.md`.

- **`voice_directory/`** — rubrica vocale condivisa (`embeddings.json`,
  `names.json`) usata dall'agente **Report Call**. Persiste tra sessioni
  diverse; non si sincronizza automaticamente tra computer, va copiata a mano
  su ogni nuova macchina.

## Nota

Le skill/risorse in `_Common` **non** sono registrate come skill invocabili in
Cowork: gli agenti le usano indicando ai worker il **percorso del file** da
leggere. Se in futuro una skill oggi in un singolo agente viene adottata da un
secondo agente, la si sposta qui e si aggiornano i percorsi nei rispettivi
`CLAUDE.md`.
