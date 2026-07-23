"""
stop_hotkey.py  (cross-platform: Windows / macOS / Linux)
---------------------------------------------------------
Ascoltatore di una combinazione di tasti GLOBALE per fermare tutto da qualunque
finestra, senza dover cercare stop_now.bat / stop_now.sh. Alla pressione della
hotkey (default Ctrl+Alt+S) crea il file STOP alla radice del progetto: gli
script Python di cattura/trascrizione lo leggono ogni 1-2s e si fermano da soli.

E' un'ALTERNATIVA COMODA agli stop a doppio click, non un sostituto: quelli
restano il fallback garantito. Questo processo termina da solo appena STOP
compare (creato dalla hotkey o dallo stop a doppio click), quindi non resta
mai appeso.

BACKEND (scelto in automatico in base al sistema operativo)
----------------------------------------------------------
- Windows            -> libreria 'keyboard' (di norma nessun privilegio admin).
- macOS / Linux      -> libreria 'pynput' ('keyboard' su Mac vorrebbe sudo).
Forzabile con --backend keyboard|pynput.

USO
---
    python stop_hotkey.py --root <cartella_progetto> --hotkey ctrl+alt+s

Note macOS: pynput usa gli eventi globali della tastiera; la PRIMA volta il
sistema chiede di autorizzare l'app (Terminale / Python) in
Impostazioni di Sistema > Privacy e sicurezza > Monitoraggio input (e/o
Accessibilita'). Senza quell'autorizzazione la hotkey non viene ricevuta.
Note Windows: se la hotkey non risponde, avviare il .bat "come amministratore".
"""

import argparse
import platform
import time
from pathlib import Path


def write_stop(stopfile: Path) -> None:
    stopfile.parent.mkdir(parents=True, exist_ok=True)
    stopfile.write_text("", encoding="utf-8")


def _to_pynput_hotkey(hotkey: str) -> str:
    """Traduce 'ctrl+alt+s' nel formato pynput '<ctrl>+<alt>+s'."""
    mods = {"ctrl", "control", "alt", "option", "shift", "cmd", "command", "win", "super"}
    alias = {"control": "ctrl", "option": "alt", "command": "cmd", "win": "cmd", "super": "cmd"}
    parts = []
    for raw in hotkey.split("+"):
        k = raw.strip().lower()
        if k in mods:
            k = alias.get(k, k)
            parts.append(f"<{k}>")
        else:
            parts.append(k)
    return "+".join(parts)


def _run_keyboard(hotkey: str, on_stop, stopfile: Path):
    import keyboard
    keyboard.add_hotkey(hotkey, on_stop)
    print(f"[stop_hotkey] (backend keyboard) In ascolto: premi '{hotkey}' per fermare. (STOP -> {stopfile})")
    while not stopfile.exists():
        time.sleep(0.5)


def _run_pynput(hotkey: str, on_stop, stopfile: Path):
    from pynput import keyboard as pk
    combo = _to_pynput_hotkey(hotkey)
    listener = pk.GlobalHotKeys({combo: on_stop})
    listener.start()
    print(f"[stop_hotkey] (backend pynput) In ascolto: premi '{hotkey}' per fermare. (STOP -> {stopfile})")
    try:
        while not stopfile.exists():
            time.sleep(0.5)
    finally:
        listener.stop()


def choose_backend(explicit: str) -> str:
    if explicit != "auto":
        return explicit
    return "keyboard" if platform.system() == "Windows" else "pynput"


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--root", default=".", help="Cartella di progetto (dove creare STOP)")
    parser.add_argument("--stopfile", default="STOP", help="Nome del file di stop, relativo a --root")
    parser.add_argument("--hotkey", default="ctrl+alt+s", help="Combinazione di tasti globale")
    parser.add_argument("--backend", default="auto", choices=["auto", "keyboard", "pynput"])
    parser.add_argument("--self-test", action="store_true",
                        help="Non attende tasti: invoca subito il callback e verifica la scrittura di STOP")
    args = parser.parse_args()

    root = Path(args.root).resolve()
    stopfile = (root / args.stopfile)

    def on_stop():
        write_stop(stopfile)
        print(f"[stop_hotkey] Hotkey premuta -> creato {stopfile}. Gli script si fermeranno entro pochi secondi.")

    if args.self_test:
        backend = choose_backend(args.backend)
        on_stop()
        ok = stopfile.exists()
        stopfile.unlink(missing_ok=True)  # ripulisce il test
        print(f"[stop_hotkey] SELF-TEST backend={backend} hotkey pynput='{_to_pynput_hotkey(args.hotkey)}' -> {'OK' if ok else 'FALLITO'}")
        return

    backend = choose_backend(args.backend)
    # Se STOP e' gia' presente (es. creato da stop_now), esci subito.
    if stopfile.exists():
        print("[stop_hotkey] STOP gia' presente, esco.")
        return

    if backend == "keyboard":
        _run_keyboard(args.hotkey, on_stop, stopfile)
    else:
        _run_pynput(args.hotkey, on_stop, stopfile)
    print("[stop_hotkey] STOP presente, esco.")


if __name__ == "__main__":
    main()
