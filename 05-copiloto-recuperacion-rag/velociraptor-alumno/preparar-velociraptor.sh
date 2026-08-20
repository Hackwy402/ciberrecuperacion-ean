#!/usr/bin/env bash
# =====================================================================
#  preparar-velociraptor.sh — Prepara la VM del alumno para el hunting
#  DFIR de la Sesión 5 (92-EAN). Descarga Velociraptor, siembra los
#  backups sintéticos del caso y arranca la GUI local.
#
#  Uso (en la VM Ubuntu del alumno):
#      bash preparar-velociraptor.sh
#  Luego abre https://127.0.0.1:8889  (usuario admin / clave password)
#
#  100% sintético: los "backups" son archivos de muestra. Nada ejecuta
#  malware real. La familia Locked3D es ficticia (del curso).
# =====================================================================
set -euo pipefail
VELO_VERSION="0.77.2"
LAB="$HOME/backups-lab"          # el "servidor de backups" que vas a investigar
BIN="$HOME/velociraptor"

# --- 1. Detectar plataforma y descargar el binario ------------------
os=$(uname -s | tr '[:upper:]' '[:lower:]')     # linux / darwin
arch=$(uname -m)
case "$arch" in
  x86_64|amd64) arch=amd64 ;;
  aarch64|arm64) arch=arm64 ;;
  *) echo "arquitectura no soportada: $arch"; exit 1 ;;
esac
ASSET="velociraptor-v${VELO_VERSION}-${os}-${arch}"
if [ ! -x "$BIN" ]; then
  echo "==> Descargando $ASSET"
  curl -sL -o "$BIN" "https://github.com/Velocidex/velociraptor/releases/download/v${VELO_VERSION}/${ASSET}"
  chmod +x "$BIN"
fi
"$BIN" version | head -2

# --- 2. Sembrar los backups del caso --------------------------------
echo "==> Sembrando backups sintéticos en $LAB"
mkdir -p "$LAB"

# Backup LIMPIO (anterior al incidente): texto legible, entropía baja
cat > "$LAB/produccion_2026-08-18.bak" <<'SQL'
-- Volcado de base de datos (backup nocturno LIMPIO)
-- Fecha: 2026-08-18 00:00
INSERT INTO clientes VALUES (1,'ACME S.A.',3100000);
INSERT INTO nomina  VALUES ('a.perez','analista',4200000);
INSERT INTO balance VALUES ('caja',1200000,0);
SQL

# Backup CIFRADO por Locked3D: cabecera de familia + mutex + bytes aleatorios
#   (entropía alta ~8.0). La cabecera 'L3D!' + 'L3D_MUTEX' hace que la regla
#   YARA de la Sesión 3 lo identifique como la familia.
{ printf 'L3D!'; printf 'Global\\L3D_MUTEX'; head -c 65536 /dev/urandom; } \
  > "$LAB/produccion_2026-08-19.bak.locked3d"

# Nota de rescate
cat > "$LAB/LEEME_RESCATE.txt" <<'TXT'
== LOCKED3D ==
Tus copias de seguridad han sido cifradas.
Para recuperarlas, contacta: descifra-express.onion
No intentes restaurar sin la clave: perderas los datos.
TXT

# Regla YARA de la Sesión 3 (para el hunting con Velociraptor)
mkdir -p "$LAB/reglas"
cat > "$LAB/reglas/locked3d.yar" <<'YAR'
rule Locked3D_familia
{
    strings:
        $magic = { 4C 33 44 21 }            // cabecera L3D!
        $mutex = "L3D_MUTEX" ascii
        $nota  = "LEEME_RESCATE.txt" ascii
    condition:
        $magic at 0 or 2 of ($mutex, $nota)
}
YAR

echo "   backups sembrados:"
ls -la "$LAB"

# --- 3. Arrancar la GUI de Velociraptor -----------------------------
echo "==> Arrancando Velociraptor GUI en https://127.0.0.1:8889"
echo "    Usuario: admin   Clave: password   (acepta el certificado autofirmado)"
echo "    (Ctrl+C para detener al terminar el lab)"
exec "$BIN" gui --nobrowser
