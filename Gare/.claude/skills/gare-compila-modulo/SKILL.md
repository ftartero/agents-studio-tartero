---
name: gare-compila-modulo
description: "Skill documentale dell'Agente Gare: compila un singolo modulo/allegato di gara con i dati disponibili e produce un .docx, senza modificare l'originale su Drive. Usa questa skill nel flusso Agente Gare (Cowork) per riempire un modulo a partire dal modulo stesso (dalla modulistica) e da SCHEDA-SOCIETA / DGUE-BASE / SCHEDA-GARA. Non si attiva nel lavoro documentale tecnico ordinario."
---

# Compila modulo di gara (Agente Gare)

Questa skill compila un **singolo modulo/allegato** di gara e produce un `.docx`. Gira nella **sessione principale** (non è un worker).

> **Stili e identità visiva**: applica sempre la skill `brand-studio` per foglio A4, font, colori, margini, header/footer, tabelle dati e firma di qualsiasi documento `.docx` prodotto con questa skill.

## Input

- **Il modulo** da compilare (individuato dalla skill/worker `gare-lettura-modulistica`).
- **SCHEDA-SOCIETA**, **DGUE-BASE**, **SCHEDA-GARA** — fonti dei dati.

## Procedura

- Riempi i **campi** del modulo con i **dati disponibili** dalle fonti di contesto.
- **NON modificare l'originale su Drive**: produci un nuovo `.docx` compilato.
- **Segnala i campi mancanti** (dati non disponibili) come lacune evidenziate, senza inventarli.
- Rispetta la struttura e le dichiarazioni del modulo originale (non alterarne il testo prestampato).

> **Nota operativa (orchestratore)**: per "compila tutti i moduli" l'orchestratore può fare **fan-out di un worker per modulo** usando questa stessa skill; ogni istanza compila un modulo.

## Output

`.docx` del modulo compilato nella cartella output della gara.

> Il presente documento è una **bozza da verificare**: confermare i dati e colmare i campi segnalati come mancanti prima della presentazione.
