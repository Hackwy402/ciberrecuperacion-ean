#!/usr/bin/env bash
# =====================================================================
#  corromper_demo.sh — Aplica corrupción (cifrado) y mide el salto de
#  entropía de Shannon. Sesión 2 · Ciber-Recuperación (92-EAN)
#
#  Idea: "corromper" datos con OpenSSL (como haría un ransomware) hace
#  que los bytes se vuelvan casi aleatorios -> la entropía salta a ~8.
#  Es la señal que un perito forense usa para detectar cifrado.
#
#  Funciona en macOS y Linux (OpenSSL viene de fábrica; entropia.py no
#  tiene dependencias). Uso:  bash scripts/corromper_demo.sh
# =====================================================================
set -euo pipefail
DIR="$(cd "$(dirname "$0")" && pwd)"
ENT="$DIR/entropia.py"
TMP="$(mktemp -d)"
CLAVE="DemoClave123"

echo "============================================================"
echo "  DEMO · Corrupción de datos y entropía de Shannon"
echo "============================================================"

echo ""
echo "== 1) Archivo LEGIBLE (baja entropía) =="
seq 1 5000 > "$TMP/plano.txt"
python3 "$ENT" "$TMP/plano.txt"

echo ""
echo "== 2) 'Corrupción' = cifrar con OpenSSL (simula ransomware) =="
openssl enc -aes-256-cbc -pbkdf2 -salt -in "$TMP/plano.txt" -out "$TMP/plano.locked" -k "$CLAVE"
echo "   -> generado plano.locked (extensión típica de ransomware)"

echo ""
echo "== 3) MISMA medida, ahora la entropía salta a ~8 =="
python3 "$ENT" "$TMP/plano.locked"

echo ""
echo "------------------------------------------------------------"
echo "Conclusión: la corrupción por cifrado dispara la entropía de"
echo "Shannon (~8 bits/byte). Es la base para detectar backups"
echo "cifrados a escala — sin abrir el archivo."
echo "Archivos de la demo en: $TMP"
echo "------------------------------------------------------------"
