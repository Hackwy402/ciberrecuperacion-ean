#!/usr/bin/env bash
# =====================================================================
#  check-requisitos.sh — Verifica el entorno para el laboratorio 92-EAN
#  Universidad Ean · Sesión 1 · Ciber-Recuperación
#
#  Uso:   bash scripts/check-requisitos.sh
#  Compatible con Linux y macOS. En Windows, ejecutar dentro de WSL2.
# =====================================================================
set -u

# ---- colores ----
G="\033[0;32m"; R="\033[0;31m"; Y="\033[0;33m"; B="\033[0;34m"; N="\033[0m"
ok(){   echo -e "  ${G}[OK]${N} $1"; }
warn(){ echo -e "  ${Y}[!]${N}  $1"; }
err(){  echo -e "  ${R}[X]${N}  $1"; }
hdr(){  echo -e "\n${B}== $1 ==${N}"; }

FAIL=0

echo -e "${B}==============================================${N}"
echo -e "${B}  Chequeo de requisitos — Laboratorio 92-EAN ${N}"
echo -e "${B}==============================================${N}"

# ---------- 1. Sistema operativo ----------
hdr "Sistema operativo"
OS="$(uname -s)"
echo "  Detectado: $OS $(uname -m)"

# ---------- 2. Memoria RAM ----------
hdr "Memoria RAM (mínimo 16 GB)"
RAM_GB=0
if [ "$OS" = "Linux" ]; then
  RAM_KB=$(grep MemTotal /proc/meminfo | awk '{print $2}')
  RAM_GB=$(( RAM_KB / 1024 / 1024 ))
elif [ "$OS" = "Darwin" ]; then
  RAM_B=$(sysctl -n hw.memsize)
  RAM_GB=$(( RAM_B / 1024 / 1024 / 1024 ))
fi
if   [ "$RAM_GB" -ge 32 ]; then ok "RAM: ${RAM_GB} GB (recomendado)"
elif [ "$RAM_GB" -ge 16 ]; then warn "RAM: ${RAM_GB} GB (suficiente; 32 GB recomendado)"
elif [ "$RAM_GB" -gt 0 ];  then err "RAM: ${RAM_GB} GB — INSUFICIENTE (mínimo 16 GB)"; FAIL=1
else warn "No se pudo determinar la RAM automáticamente."
fi

# ---------- 3. Espacio en disco ----------
hdr "Espacio libre en disco (mínimo 100 GB)"
DISK_GB=$(df -Pk . | awk 'NR==2{print int($4/1024/1024)}')
if   [ "${DISK_GB:-0}" -ge 100 ]; then ok "Disco libre: ${DISK_GB} GB"
elif [ "${DISK_GB:-0}" -ge 40 ];  then warn "Disco libre: ${DISK_GB} GB — justo; libera espacio si es posible."
else err "Disco libre: ${DISK_GB} GB — INSUFICIENTE (mínimo 100 GB)"; FAIL=1
fi

# ---------- 4. CPU / virtualización ----------
hdr "CPU y virtualización"
CPUS=$(getconf _NPROCESSORS_ONLN 2>/dev/null || echo "?")
echo "  vCPUs disponibles: $CPUS"
[ "${CPUS:-0}" -ge 4 ] 2>/dev/null && ok "CPUs suficientes (>=4)" || warn "Se recomiendan 4 vCPU o más."
if [ "$OS" = "Linux" ]; then
  if grep -Eq 'vmx|svm' /proc/cpuinfo; then ok "Virtualización por hardware (VT-x/AMD-V) habilitada."
  else warn "No se detectó VT-x/AMD-V. Habilítalo en la BIOS si usarás VMs."; fi
fi

# ---------- 5. Docker ----------
hdr "Docker"
if command -v docker >/dev/null 2>&1; then
  DV=$(docker --version 2>/dev/null)
  ok "Docker instalado: $DV"
  if docker info >/dev/null 2>&1; then ok "El daemon de Docker está corriendo."
  else err "Docker instalado pero el daemon NO responde (¿Docker Desktop abierto?)."; FAIL=1; fi
  if docker compose version >/dev/null 2>&1; then ok "Docker Compose v2: $(docker compose version | head -1)"
  else err "Falta 'docker compose' (v2). Instala Docker Compose."; FAIL=1; fi
else
  err "Docker NO está instalado."; FAIL=1
fi

# ---------- 6. Herramientas auxiliares ----------
hdr "Herramientas auxiliares"
for tool in git python3 curl; do
  if command -v "$tool" >/dev/null 2>&1; then ok "$tool: $($tool --version 2>&1 | head -1)"
  else warn "$tool no encontrado (recomendado para el curso)."; fi
done

# ---------- 7. Conectividad ----------
hdr "Conectividad (descarga de imágenes y modelos)"
if curl -s --max-time 8 -o /dev/null -w "%{http_code}" https://registry.ollama.ai 2>/dev/null | grep -qE '2|3|4'; then
  ok "Salida a internet OK (registro de Ollama alcanzable)."
else
  warn "No se pudo confirmar salida a internet; verifica tu red/proxy."
fi

# ---------- Resumen ----------
echo ""
echo -e "${B}==============================================${N}"
if [ "$FAIL" -eq 0 ]; then
  echo -e "${G}  RESULTADO: entorno LISTO para el laboratorio.${N}"
  echo -e "  Siguiente paso:  ${B}docker compose up -d${N}"
else
  echo -e "${R}  RESULTADO: hay requisitos por resolver (ver [X] arriba).${N}"
  echo -e "  Corrige los puntos marcados y vuelve a ejecutar este script."
fi
echo -e "${B}==============================================${N}"
exit $FAIL
