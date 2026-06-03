@echo off
echo Desinstal.lant RJ Auto Metadata (Entorn Local)...
echo ==================================================

IF EXIST "venv" (
    echo [INFO] Esborrant la capsula virtual de Python (venv)...
    rmdir /s /q venv
    echo [INFO] Dependencies de Python esborrades.
) ELSE (
    echo [INFO] No s'ha trobat cap entorn virtual (venv) per esborrar.
)

set /p resposta="[PREGUNTA] Vols desinstal.lar ExifTool i Ghostscript del teu PC? (s/n): "
IF /I "%resposta%"=="s" (
    echo [INFO] Desinstal.lant ExifTool...
    winget uninstall --id OliverBetz.ExifTool
    echo [INFO] Desinstal.lant Ghostscript...
    winget uninstall --id ArtifexSoftware.GhostScript
    echo [INFO] Dependencies del sistema esborrades.
) ELSE (
    echo [INFO] S'han mantingut ExifTool i Ghostscript al sistema.
)

echo ==================================================
echo Desinstal.lacio completada. Ara pots esborrar aquesta carpeta.
pause
