#!/bin/bash
# Doppio click (o "./stop_now.sh" da terminale) per fermare TUTTO all'istante,
# indipendentemente da cosa sta facendo Cowork in quel momento.
# Crea il file STOP nella stessa cartella: record_chunks.py e transcribe_watch.py
# lo controllano ogni 1-2 secondi e si fermano da soli appena lo vedono.
cd "$(dirname "$0")"
touch STOP
echo "STOP creato. Gli script si fermeranno entro pochi secondi."
