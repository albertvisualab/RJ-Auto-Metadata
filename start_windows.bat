@echo off
echo Iniciant RJ Auto Metadata (Entorn Local)...
echo ==============================================

echo [INFO] Comprovant dependències del sistema a Windows...
where exiftool >nul 2>nul
IF %ERRORLEVEL% NEQ 0 (
    echo [INFO] ExifTool no trobat. Intentant instal.lar-lo via Winget...
    winget install -e --id OliverBetz.ExifTool --accept-package-agreements --accept-source-agreements
)

where gswin64c >nul 2>nul
IF %ERRORLEVEL% NEQ 0 (
    echo [INFO] Ghostscript no trobat. Intentant instal.lar-lo via Winget...
    winget install -e --id ArtifexSoftware.GhostScript --accept-package-agreements --accept-source-agreements
)

IF NOT EXIST "venv" (
    echo [INFO] Primera execucio detectada.
    echo [INFO] Creant entorn virtual encapsulat (venv)...
    python -m venv venv
    
    echo [INFO] Instal.lant dependencies de Python dins de venv...
    venv\Scripts\pip install --no-cache-dir -r requirements.txt
    echo [INFO] Instal.lacio completada.
) ELSE (
    echo [INFO] Entorn virtual detectat.
)

echo [INFO] Arrencant l'aplicacio...
venv\Scripts\python gui.py

pause
