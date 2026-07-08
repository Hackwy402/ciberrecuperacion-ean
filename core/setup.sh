#!/usr/bin/env bash
# =====================================================================
#  setup.sh — Bootstrap idempotente del laboratorio 92-EAN
#  Universidad Ean · Ciber-Recuperación
#
#  Objetivo: que los 3 setups del curso converjan al MISMO estado sobre
#  Ubuntu (VM local, WSL2 o droplet cloud). Es idempotente: puedes correrlo
#  las veces que quieras sin romper lo ya instalado.
#
#  Uso:
#    bash setup.sh --local        # Setup 1: instala Ollama + modelo local (privado)
#    bash setup.sh --cloud        # Setup 2/3: solo entorno; usarás API hosted
#    bash setup.sh --with-docker  # además instala Docker (para sesiones 4+)
#
#  Puedes combinar:  bash setup.sh --local --with-docker
# =====================================================================
set -euo pipefail

MODE="cloud"          # por defecto asume cloud (el más restrictivo)
WITH_DOCKER=0
MODEL="${LAB_MODEL:-llama3.1:8b}"

for arg in "$@"; do
  case "$arg" in
    --local) MODE="local" ;;
    --cloud) MODE="cloud" ;;
    --with-docker) WITH_DOCKER=1 ;;
    *) echo "Argumento no reconocido: $arg"; exit 2 ;;
  esac
done

G="\033[0;32m"; Y="\033[0;33m"; B="\033[0;34m"; N="\033[0m"
say(){ echo -e "${B}==>${N} $1"; }
ok(){  echo -e "${G}[OK]${N} $1"; }
warn(){ echo -e "${Y}[!]${N} $1"; }

SUDO=""
if [ "$(id -u)" -ne 0 ]; then SUDO="sudo"; fi

say "Modo de instalación: ${MODE}  (docker: $([ $WITH_DOCKER -eq 1 ] && echo sí || echo no))"

# ---------- 1. Paquetes base del sistema (Ubuntu/Debian) ----------
if command -v apt-get >/dev/null 2>&1; then
  say "Instalando paquetes base (python venv, pip, git, curl)..."
  $SUDO apt-get update -y -qq
  $SUDO apt-get install -y -qq python3 python3-venv python3-pip git curl ca-certificates
  ok "Paquetes base listos."
else
  warn "No se detectó apt. Este script está pensado para Ubuntu/Debian."
  warn "En macOS usa Homebrew (ver docs/). Continuo con lo que se pueda."
fi

# ---------- 2. Entorno virtual de Python ----------
if [ ! -d ".venv" ]; then
  say "Creando entorno virtual .venv ..."
  python3 -m venv .venv
fi
# shellcheck disable=SC1091
source .venv/bin/activate
say "Instalando dependencias de Python (requirements.txt)..."
pip install --quiet --upgrade pip
pip install --quiet -r requirements.txt
ok "Dependencias de Python instaladas en .venv"

# ---------- 3. Archivo .env ----------
if [ ! -f ".env" ]; then
  cp .env.example .env
  ok "Creado .env a partir de .env.example (edítalo según tu setup)."
else
  warn ".env ya existe: no lo sobrescribo."
fi

# ---------- 4. Ollama (solo modo local) ----------
if [ "$MODE" = "local" ]; then
  if ! command -v ollama >/dev/null 2>&1; then
    say "Instalando Ollama (modelo local, privado)..."
    curl -fsSL https://ollama.com/install.sh | sh
  else
    ok "Ollama ya está instalado."
  fi
  # arranca el servicio si systemd está disponible
  if command -v systemctl >/dev/null 2>&1; then
    $SUDO systemctl enable --now ollama 2>/dev/null || true
  fi
  say "Descargando modelo local: ${MODEL} (puede tardar)..."
  ollama pull "${MODEL}" || warn "No se pudo descargar ${MODEL}; hazlo luego con: ollama pull ${MODEL}"
  # deja el .env apuntando a ollama si aún tiene el default
  ok "Modo local listo. En .env: LLM_BACKEND=ollama, LLM_MODEL=${MODEL}"
else
  warn "Modo cloud: recuerda editar .env con tu backend hosted (groq u openrouter) y tu API key."
fi

# ---------- 5. Docker (opcional, para sesiones 4+) ----------
if [ "$WITH_DOCKER" -eq 1 ]; then
  if ! command -v docker >/dev/null 2>&1; then
    say "Instalando Docker Engine + Compose plugin..."
    curl -fsSL https://get.docker.com | $SUDO sh
    $SUDO usermod -aG docker "$USER" 2>/dev/null || true
    warn "Cierra y reabre la sesión (o 'newgrp docker') para usar docker sin sudo."
  else
    ok "Docker ya está instalado."
  fi
fi

echo ""
ok "Setup completado."
echo -e "${B}Siguientes pasos:${N}"
echo "  1) (cloud) edita .env con tu API key:   nano .env"
echo "  2) valida el backend:                    make check"
echo "  3) corre el copiloto de triage:          make triage"
