#!/bin/bash
echo "Desinstal·lant RJ Auto Metadata (Entorn Local)..."
echo "=================================================="

# 1. Esborrar l'entorn virtual de Python
if [ -d "venv" ]; then
    echo "[INFO] Esborrant la càpsula virtual de Python (venv)..."
    rm -rf venv
    echo "[INFO] Dependències de Python esborrades."
else
    echo "[INFO] No s'ha trobat cap entorn virtual (venv) per esborrar."
fi

# 2. Desinstal·lar dependències del sistema via Homebrew
if command -v brew &> /dev/null; then
    read -p "[PREGUNTA] Vols desinstal·lar ExifTool i Ghostscript del teu Mac? (s/n): " resposta
    if [[ "$resposta" == "s" || "$resposta" == "S" ]]; then
        echo "[INFO] Desinstal·lant ExifTool..."
        brew uninstall exiftool
        echo "[INFO] Desinstal·lant Ghostscript..."
        brew uninstall ghostscript
        echo "[INFO] Dependències del sistema esborrades."
    else
        echo "[INFO] S'han mantingut ExifTool i Ghostscript al sistema."
    fi
fi

echo "=================================================="
echo "Desinstal·lació completada. Ara pots esborrar aquesta carpeta."
