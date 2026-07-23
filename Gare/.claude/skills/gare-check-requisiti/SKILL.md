---
name: gare-check-requisiti
description: "Procedura e template del check requisiti dell'Agente Gare, caricata dall'orchestratore in FASE 2. Confronta i requisiti della SCHEDA-GARA con i dati societari disponibili (context/ e cartelle collegate) e genera CHECK-REQUISITI.md con semaforo di partecipabilità. Da usare SOLO nel flusso Agente Gare (Cowork) per la verifica di ammissibilità di una specifica gara. NON è un worker (non restituisce JSON) e non è una skill documentale .docx; non si attiva nel lavoro documentale normale."
---

# Check requisiti di gara — Agente Gare

Questa skill è la **procedura e il template del check requisiti**, caricata dall'orchestratore dell'Agente Gare in **FASE 2**. Confronta i **requisiti della SCHEDA-GARA** con i dati disponibili in `context/` e nelle cartelle collegate (SCHEDA-SOCIETA, bilanci, visure, curriculum, assicurazione, elenco servizi) e genera il file **`CHECK-REQUISITI.md`**.

Non è un worker: **non** restituisce JSON. Non è una skill documentale: **non** produce un `.docx`. Verifica la partecipabilità e produce il documento di sintesi con il semaforo.

## Procedura

1. Leggi i requisiti dalla **SCHEDA-GARA** (generali, economico-finanziari con soglie, tecnico-professionali con soglie, documentazione richiesta).
2. Recupera i **dati disponibili** da `context/` (SCHEDA-SOCIETA, DGUE-BASE, ELENCO-SERVIZI) e, se necessario, dai documenti nelle cartelle collegate (via `device_list_dir` + `device_stage_files` + `Read`).
3. Per **ogni** requisito confronta *richiesto* vs *disponibile* e assegna lo stato: ✅ soddisfatto / ⚠️ soddisfatto con riserva o da aggiornare / ❌ non soddisfatto o mancante.
4. Determina il **semaforo generale** e le **azioni necessarie** prima della presentazione.
5. Scrivi il risultato in `CHECK-REQUISITI.md` secondo il template sotto.

## Template `CHECK-REQUISITI.md`

```markdown
## CHECK REQUISITI — [Nome gara]

### Requisiti generali (art. 94-98 D.Lgs. 36/2023)
[✅ / ⚠️ / ❌] Requisito — stato — nota

### Requisiti economico-finanziari
[✅ / ⚠️ / ❌] Fatturato globale: richiesto [X] — disponibile [Y]
[✅ / ⚠️ / ❌] Fatturato specifico SIA: richiesto [X] — disponibile [Y]

### Requisiti tecnico-professionali
[✅ / ⚠️ / ❌] Servizi analoghi: richiesto [X] — disponibili [Y]
[✅ / ⚠️ / ❌] Risorse umane: richiesto [X] — disponibili [Y]
[✅ / ⚠️ / ❌] Abilitazioni/iscrizioni: [dettaglio]

### Documentazione richiesta
[✅ disponibile / ⚠️ da aggiornare / ❌ mancante] — nome documento — fonte (cartella collegata)

### SEMAFORO GENERALE
🟢 PARTECIPAZIONE CONSIGLIATA / 🟡 PARTECIPAZIONE POSSIBILE CON RISERVE / 🔴 REQUISITI NON SODDISFATTI

### Azioni necessarie prima della presentazione
- [ ] [azione — scadenza]
```

## Regole

- Ogni valutazione deve poggiare su **dati reali**: se un dato manca, lo stato è ⚠️ o ❌, **mai** ✅ presunto.
- Il **semaforo generale** è 🔴 se anche un solo requisito essenziale è ❌; 🟡 se ci sono ⚠️ risolvibili; 🟢 solo se tutti i requisiti essenziali sono ✅.
- Le **azioni necessarie** elencano cosa reperire/aggiornare e con quale scadenza (dallo scadenzario della SCHEDA-GARA).
