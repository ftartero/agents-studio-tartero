#!/bin/bash
# Doppio click su macOS per avviare l'ascoltatore della hotkey globale di STOP
# (default: Ctrl+Alt+S, dove Alt = tasto Opzione). Premendo la combinazione da
# QUALUNQUE finestra viene creato il file STOP e tutti gli script di
# cattura/trascrizione si fermano entro pochi secondi. Alternativa comoda a
# stop_now.sh (che resta il fallback a doppio click).
#
# PRIMO AVVIO: macOS chiedera' di autorizzare il Terminale/Python in
# Impostazioni di Sistema > Privacy e sicurezza > Monitoraggio input
# (ed eventualmente Accessibilita'). Senza quell'autorizzazione la hotkey non
# viene ricevuta. Se il file non parte al doppio click: da Terminale esegui una
# volta  chmod +x stop_hotkey.command
cd "$(dirname "$0")"
VENV="$HOME/Library/Application Support/StudioTartero/ReportCall/venv"
"$VENV/bin/python" scripts/stop_hotkey.py --root . --hotkey ctrl+alt+s
