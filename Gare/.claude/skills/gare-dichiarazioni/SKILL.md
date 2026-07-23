---
name: gare-dichiarazioni
description: "Skill documentale dell'Agente Gare: redige le dichiarazioni standard di gara (domanda di partecipazione, requisiti generali art. 94-98 D.Lgs. 36/2023, tracciabilità dei flussi finanziari) e le dichiarazioni RTI, producendo .docx. Usa questa skill nel flusso Agente Gare (Cowork) per generare le dichiarazioni a partire da SCHEDA-SOCIETA, SCHEDA-GARA ed eventuale composizione RTI. Non si attiva nel lavoro documentale tecnico ordinario."
---

# Dichiarazioni di gara (Agente Gare)

Questa skill redige le **dichiarazioni standard di gara** e le dichiarazioni **RTI**, producendo `.docx`. Gira nella **sessione principale** (non è un worker).

> **Stili e identità visiva**: applica sempre la skill `brand-studio` per foglio A4, font, colori, margini, header/footer, tabelle dati e firma di qualsiasi documento `.docx` prodotto con questa skill.

## Input

- **SCHEDA-SOCIETA** — dati societari (ragione sociale, CF/P.IVA, sede, rappresentante legale, ecc.).
- **SCHEDA-GARA** — dati della gara (stazione appaltante, CIG, oggetto, importo).
- **Eventuale composizione RTI** (ruolo mandataria/mandanti, componenti, quote %).

## Dichiarazioni prodotte

- **Domanda di partecipazione** alla procedura.
- **Dichiarazione sui requisiti generali** — assenza dei motivi di esclusione ai sensi degli **artt. 94-98 D.Lgs. 36/2023**.
- **Dichiarazione di tracciabilità dei flussi finanziari** (L. 136/2010): conto dedicato, impegno all'indicazione del CIG.

## RTI

Quando è presente una composizione RTI:

- genera **un documento per ciascun componente** (mandataria e mandanti);
- **documenta la composizione** del raggruppamento (ruoli e quote %), come richiesto dalla lex specialis.

## Output

`.docx` (uno o più, secondo il caso singolo/RTI) nella cartella output della gara.

> Il presente documento è una **bozza da verificare** prima della presentazione: confermare i dati e le sottoscrizioni richieste.
