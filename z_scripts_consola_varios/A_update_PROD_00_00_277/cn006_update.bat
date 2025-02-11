@echo off
cls
@echo SCRIPT ACTUALIZACIÓN NUEVA VERSIÓN A PRODUCCIÓN
@echo SCRIPT ACTUALIZACIÓN NUEVA VERSIÓN A PRODUCCIÓN
@echo SCRIPT ACTUALIZACIÓN NUEVA VERSIÓN A PRODUCCIÓN
@echo SCRIPT ACTUALIZACIÓN NUEVA VERSIÓN A PRODUCCIÓN
@echo .
@echo Los mensajes anteriores fueron generados por el batch
@echo. 
@echo. 
@echo on

python cn006_update.py --pAmbiente PROD --pDebug True

@echo off
@echo. 
@echo. 
@echo ***
pause



		