# Runbook del demo (docente) · comandos para local (Mac) y Ubuntu

Todo lo que necesitas ejecutar para dejar el demo de la Sesión 1 listo. Dos entornos:
tu **Mac (M-series)** con modelo local por GPU, y una **VM/contenedor Ubuntu** para
espejar la experiencia del estudiante y hacer el forense a mano.

---

## A. En tu Mac (modelo local, GPU) — Terminal/Warp, NO dentro del contenedor

```bash
# 1) Ollama nativo (usa la GPU Metal del M-series)
brew install ollama
brew services start ollama                 # queda en localhost:11434
ollama pull llama3.1:8b                     # modelo del curso
ollama pull llama3.2:3b                     # respaldo liviano para demostrar el caso "RAM justa"
curl http://localhost:11434                 # -> "Ollama is running"

# 2) Clona el repo del curso (o usa tu carpeta local)
git clone https://github.com/Hackwy402/ciberrecuperacion-ean.git
cd ciberrecuperacion-ean/core

# 3) Entorno de Python del kit (en Mac se hace a mano; setup.sh es para Ubuntu)
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
cp .env.example .env                        # queda en ollama + llama3.1:8b (local)

# 4) Verifica y corre el copiloto
make check                                  # [OK] backend ollama
make triage                                 # triage sobre la alerta sintética
```

> `make` viene con las Command Line Tools de Xcode. Si falta: `xcode-select --install`.

### (opcional) Demostrar Setup 2/3 (API hosted) en clase
```bash
# saca una key gratis en console.groq.com y prueba el cambio de "cerebro":
LLM_BACKEND=groq GROQ_API_KEY=gsk_xxx LLM_MODEL=llama-3.3-70b-versatile \
  python scripts/llm_client.py --check
```

---

## B. En la VM / contenedor Ubuntu (forense a mano + estudiante)

Si entras a un contenedor mínimo (`docker exec -it ubuntu bash`), primero instala lo básico:

```bash
apt update && apt install -y git python3 python3-venv python3-pip make curl file xxd binutils
```

Luego el entorno del kit:

```bash
git clone https://github.com/Hackwy402/ciberrecuperacion-ean.git
cd ciberrecuperacion-ean/core
bash setup.sh --cloud                       # entorno Python (sin instalar modelo en el contenedor)
```

### Apuntar el copiloto al Ollama de tu Mac (GPU) desde el contenedor
Edita `core/.env`:
```
LLM_BACKEND=ollama
LLM_BASE_URL=http://host.docker.internal:11434/v1
LLM_MODEL=llama3.1:8b
```
```bash
source .venv/bin/activate
make check
```

> `host.docker.internal` resuelve al host (tu Mac) desde Docker Desktop. Así el
> contenedor hace el análisis y el modelo corre con GPU en el Mac.

### Parte 1 — Forense a mano (el corazón del taller)
```bash
cd ../01-ransomware-y-ciber-recuperacion
python3 scripts/generar_dataset.py
cd datasets/backup_caso1

file *                                       # extensión vs contenido (magic number)
sha256sum -c hashes-buenos.txt               # integridad (OK / FAILED)
python3 ../../scripts/entropia.py *          # entropía (~8.0 = cifrado)
xxd factura_2024.pdf | head -2               # magic PNG bajo extensión .pdf
cat README_RECOVER.txt                       # nota de rescate (IOCs)
```

### Parte 2 — Copiloto de IA (local)
```bash
cd ../../../core
make triage                                  # el modelo local sobre los hallazgos
```

---

## C. Alternativa 100% en el Mac (sin contenedor)

Si prefieres hacer también el forense en el Mac (sin Ubuntu), funciona igual — solo
que `file`, `sha256sum`, `xxd` y `python3` ya están en macOS:

```bash
cd ciberrecuperacion-ean/01-ransomware-y-ciber-recuperacion
python3 scripts/generar_dataset.py
cd datasets/backup_caso1
file *; python3 ../../scripts/entropia.py *; sha256sum -c hashes-buenos.txt
```

---

## Checklist del demo listo

- [ ] `curl http://localhost:11434` responde en el Mac.
- [ ] `make check` en verde (Mac y, si lo usas, contenedor vía host.docker.internal).
- [ ] `python3 scripts/generar_dataset.py` crea `backup_caso1`.
- [ ] `file *` muestra el PNG disfrazado y `entropia.py` marca ~8.0 en el `.locked3d`.
- [ ] `make triage` responde con el copiloto local.
- [ ] (opcional) key de Groq lista para demostrar Setup 2/3.
