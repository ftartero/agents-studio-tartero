---
name: gare-offerta-tecnica
description: "Skill documentale dell'Agente Gare: redige la bozza dell'offerta tecnica strutturata sui criteri di valutazione del disciplinare (OEPV), attingendo ai servizi analoghi dello studio, e produce un .docx. Usa questa skill nel flusso Agente Gare (Cowork) per generare l'offerta tecnica a partire da SCHEDA-GARA (criterio + criteri di valutazione), ELENCO-SERVIZI e disciplinare. Non si attiva nel lavoro documentale tecnico ordinario (relazioni di progetto)."
---

# Offerta tecnica (Agente Gare)

Questa skill redige la **bozza dell'offerta tecnica** e produce un `.docx`. Gira nella **sessione principale** (non è un worker).

> **Stili e identità visiva**: applica sempre la skill `brand-studio` per foglio A4, font, colori, margini, header/footer, tabelle dati e firma di qualsiasi documento `.docx` prodotto con questa skill.

## Input

- **SCHEDA-GARA** — criterio di aggiudicazione (OEPV) e **criteri/sub-criteri di valutazione** del disciplinare, con i relativi punteggi.
- **ELENCO-SERVIZI** — servizi analoghi e referenze dello studio.
- **Disciplinare** di gara (per i vincoli redazionali: numero pagine/caratteri, indice richiesto, ecc.).

## Procedura

- Struttura l'offerta con **una sezione per ciascun criterio di valutazione** del disciplinare, seguendo l'ordine e i pesi indicati.
- Per ogni criterio attingi ai **servizi analoghi** e alle competenze dello studio pertinenti.
- Mantieni **voce unica e coerente** in tutto il documento.
- **Segnala i punti che richiedono input dello studio** (dati, scelte progettuali, referenze specifiche) come note evidenziate, senza inventarli.

> **Nota operativa (orchestratore)**: per offerte molto lunghe l'orchestratore può dispacciare **un worker per criterio** e poi assemblare le sezioni. Il **default** di questa skill è la **stesura singola e coerente**.

## Output

`.docx` dell'offerta tecnica nella cartella output della gara.

> Il presente documento è una **bozza da verificare** e completare con gli input dello studio prima della presentazione.
