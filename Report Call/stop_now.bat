@echo off
REM Doppio click per fermare TUTTO all'istante, indipendentemente da cosa
REM sta facendo Cowork in quel momento.
cd /d "%~dp0"
type nul > STOP
echo STOP creato. Gli script si fermeranno entro pochi secondi.
pause
