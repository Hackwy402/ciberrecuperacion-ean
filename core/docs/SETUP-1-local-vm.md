# Setup 1 · Local privado — VM Ubuntu + modelo local

**Para quién:** participantes con laptop capaz (≥16 GB RAM) que quieren **máxima privacidad**. Los datos **nunca salen del equipo** — es el setup correcto cuando se maneja evidencia real.

**Idea:** una VM Ubuntu (o WSL2 en Windows) con Ollama corriendo un modelo local. El copiloto habla con `localhost`, air-gapped.

## Paso a paso

### 1. Tener un Ubuntu

- **Windows:** WSL2 → `wsl --install -d Ubuntu-24.04` (PowerShell como admin), reinicia y abre "Ubuntu".
- **Mac (Apple Silicon):** VM con [Multipass](https://multipass.run) → `multipass launch 24.04 --name ean --memory 8G --disk 40G` y luego `multipass shell ean`. (En Mac también puedes instalar Ollama nativo con `brew install ollama` para usar la GPU Metal — ver más abajo.)
- **Linux:** ya tienes Ubuntu/Debian nativo.

### 2. Clonar el laboratorio y ejecutar el bootstrap

```bash
git clone <URL-del-repo> ciberrecuperacion-lab   # o descomprime el .zip
cd ciberrecuperacion-lab
bash setup.sh --local
```

Esto instala Python + venv, dependencias, Ollama y descarga el modelo `llama3.1:8b`. Es idempotente.

### 3. Confirmar el backend y probar

```bash
make check      # valida que Ollama responde (LLM_BACKEND=ollama)
make triage     # corre el copiloto sobre la alerta de ejemplo
```

> El `.env` ya queda en `LLM_BACKEND=ollama`. No necesitas API key.

## Mac con Ollama nativo (mejor rendimiento)

Docker en Mac **no** usa la GPU. Si estás en Mac y quieres velocidad, corre Ollama nativo en el host y apunta el lab ahí. En tu `.env`:

```
LLM_BACKEND=ollama
LLM_BASE_URL=http://host.docker.internal:11434/v1   # si el código corre en contenedor
```

Si corres los scripts en un venv del propio Mac, `localhost:11434` funciona directo.

## Requisitos

| Recurso | Mínimo | Cómodo |
|---|---|---|
| RAM asignada a la VM | 8 GB (modelo 3b) | 16 GB (modelo 8b) |
| Disco | 30 GB | 40 GB+ |
| Modelo | `llama3.2:3b` | `llama3.1:8b` |

Si la VM va justa de RAM, cambia el modelo en `.env` a `llama3.2:3b` (`make model MODEL=llama3.2:3b`).
