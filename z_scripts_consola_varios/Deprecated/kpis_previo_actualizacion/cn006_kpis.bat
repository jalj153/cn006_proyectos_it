@echo off
cls
@echo Partes de horas CN006
@echo .
@echo Los mensajes anteriores haste este fueron generados por el batch
@echo. 
@echo. 
@echo on

python cn006_kpis.py --pAmbiente PROD --pDebug True

@echo off
@echo ***
pause



		