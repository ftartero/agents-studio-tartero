Rubrica vocale persistente — si popola automaticamente durante le call,
NON serve creare nulla qui a mano (a meno che tu non voglia correggere un
nome direttamente in names.json).

- embeddings.json → impronte vocali (vettori numerici, MAI audio)
- names.json      → mappa id speaker -> nome, con grado di confidenza

Per azzerare la rubrica: cancella il contenuto di questa cartella.
Per rimuovere una sola persona: elimina la entry con il suo "id" da
ENTRAMBI i file (embeddings.json e names.json), oppure usa in chat il
comando "dimentica speaker [N]".

Nota privacy: questi file associano impronte vocali a nomi di persone
reali, e persistono tra call diverse anche in giorni diversi — vedi la
sezione dedicata in ISTRUZIONI.md per le implicazioni da considerare,
specie con partecipanti esterni allo studio.
