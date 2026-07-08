# =====================================================================
#  Makefile — atajos del laboratorio 92-EAN (Universidad Ean)
#  Escala entre sesiones: agregar tools no rompe estos comandos.
#
#  Requiere haber corrido antes:  bash setup.sh --local   (o --cloud)
# =====================================================================
PY := .venv/bin/python
PIP := .venv/bin/pip
MODEL ?= llama3.1:8b

.DEFAULT_GOAL := help

help: ## Muestra esta ayuda
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | \
	 awk 'BEGIN {FS = ":.*?## "}; {printf "  \033[36m%-14s\033[0m %s\n", $$1, $$2}'

check: ## Valida el backend LLM configurado en .env (sin enviar datos sensibles)
	$(PY) scripts/llm_client.py --check

requisitos: ## Verifica requisitos del equipo (RAM, disco, docker, red)
	bash scripts/check-requisitos.sh

triage: ## Corre el copiloto de triage sobre la alerta de ejemplo (dato sintético)
	$(PY) scripts/triage_copiloto.py data/alerta_ejemplo.json --datos-sinteticos

triage-local: ## Igual que 'triage' pero pensado para backend local (sin flag hosted)
	$(PY) scripts/triage_copiloto.py data/alerta_ejemplo.json

model: ## (Setup local) descarga el modelo de Ollama:  make model MODEL=llama3.1:8b
	ollama pull $(MODEL)

rebuild: ## Reinstala dependencias de Python tras agregar librerías a requirements.txt
	$(PIP) install --upgrade pip
	$(PIP) install -r requirements.txt

up: ## (Sesiones 4+) levanta los servicios docker del perfil por defecto
	docker compose up -d

up-local: ## Levanta servicios incluyendo Ollama en contenedor (perfil local)
	docker compose --profile local up -d

down: ## Detiene los servicios docker sin borrar datos
	docker compose down

clean-pyc: ## Limpia archivos .pyc / __pycache__
	find . -type d -name __pycache__ -exec rm -rf {} + 2>/dev/null || true

.PHONY: help check requisitos triage triage-local model rebuild up up-local down clean-pyc
