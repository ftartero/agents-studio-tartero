---
name: gare-dgue
description: "Skill documentale dell'Agente Gare: compila il DGUE (Documento di Gara Unico Europeo) mappando i dati societari e di gara nelle parti II-III-IV-VI, e produce un .docx. Usa questa skill quando, nel flusso Agente Gare (Cowork), occorre generare il DGUE per una specifica gara a partire da DGUE-BASE.md, SCHEDA-GARA.md ed eventuale composizione RTI. Non si attiva nel lavoro documentale tecnico ordinario (relazioni, verbali, capitolati)."
---

# DGUE — Documento di Gara Unico Europeo (Agente Gare)

Questa skill compila il **DGUE** per una gara e produce un `.docx`. Gira nella **sessione principale** (non è un worker).

> **Stili e identità visiva**: applica sempre la skill `brand-studio` per foglio A4, font, colori, margini, header/footer, tabelle dati e firma di qualsiasi documento `.docx` prodotto con questa skill.

## Input

- **DGUE-BASE.md** — dati anagrafici e societari già consolidati.
- **SCHEDA-GARA.md** — dati della gara e requisiti (criteri di selezione).
- **Eventuale composizione RTI** (ruolo, componenti, quote %).

## Procedura — mappatura nelle parti del DGUE

- **Parte II — Informazioni sull'operatore economico**: dati identificativi, forma di partecipazione (singola / RTI / consorzio), rappresentanti.
- **Parte III — Motivi di esclusione**: dichiarazioni sull'assenza dei motivi di esclusione (art. 94-98 D.Lgs. 36/2023).
- **Parte IV — Criteri di selezione**: compilare secondo i **requisiti della SCHEDA-GARA** (idoneità, capacità economico-finanziaria con le soglie, capacità tecnico-professionale con servizi analoghi/risorse/abilitazioni).
- **Parte VI — Dichiarazioni finali**: sottoscrizione e dichiarazioni conclusive.

**Regola sulle lacune**: ogni dato mancante è una **lacuna segnalata**, **mai inventata**. Elenca le lacune in coda al documento (o in nota) così che l'orchestratore/utente le colmi.

**RTI**: quando è presente una composizione RTI, riporta i dati di ciascun componente nella Parte II e documenta la composizione (ruolo mandataria/mandanti, quote).

## Output

`.docx` denominato `[NomeGara]_DGUE_[YYYY-MM-DD].docx` nella **cartella output della gara**.

> Il presente documento è una **bozza da verificare** prima della presentazione: i dati vanno confermati e le lacune colmate.
