@echo off
REM Avvia l'ascoltatore della hotkey globale di STOP (default: Ctrl+Alt+S).
REM Premendo la combinazione da QUALUNQUE finestra viene creato il file STOP e
REM tutti gli script di cattura/trascrizione si fermano entro pochi secondi.
REM Alternativa comoda a stop_now.bat (che resta il fallback a doppio click).
REM Questa finestra si chiude da sola appena STOP compare.
cd /d "%~dp0"
set VENV=%LOCALAPPDATA%\StudioTartero\ReportCall\venv
"%VENV%\Scripts\python.exe" scripts\stop_hotkey.py --root "%~dp0" --hotkey ctrl+alt+s
