#!/bin/bash
echo "Iniciant RJ Auto Metadata (Entorn Local)..."
echo "=============================================="

# 1. Comprovar i instal·lar dependències del sistema (ExifTool i Ghostscript)
if ! command -v brew &> /dev/null; then
    echo "[AVÍS] Homebrew no està instal·lat. Et recomanem instal·lar-lo per gestionar les dependències del sistema."
else
    echo "[INFO] Comprovant dependències del sistema a Mac..."
    if ! command -v exiftool &> /dev/null; then
        echo "[INFO] Instal·lant ExifTool via Homebrew..."
        brew install exiftool
    fi
    if ! command -v gs &> /dev/null; then
        echo "[INFO] Instal·lant Ghostscript via Homebrew..."
        brew install ghostscript
    fi
fi

# 2. Comprovar i instal·lar dependències de Python (venv)
if [ ! -d "venv" ]; then
    echo "[INFO] Primera execucio detectada."
    echo "[INFO] Creant entorn virtual encapsulat (venv)..."
    python3 -m venv venv
    
    echo "[INFO] Instal.lant dependencies de Python dins de venv..."
    source venv/bin/activate
    pip install --no-cache-dir -r requirements.txt
    echo "[INFO] Instal.lacio completada."
else
    echo "[INFO] Entorn virtual detectat."
    source venv/bin/activate
fi

echo "[INFO] Arrencant l'aplicacio..."
python gui.py
