# Laboratorio Ciber-Recuperación · 92-EAN

Entorno del módulo **Gestión de Ciber-Recuperación** (Universidad Ean · Educación Continua).
Un solo laboratorio, **tres formas de correrlo** según tu equipo, y un **cerebro de IA intercambiable** (modelo local o API gratuita) sin tocar el código. Escalable para todas las sesiones del curso.

## La idea en una frase

Separamos el **entorno** (dónde corre) del **modelo** (qué lo piensa). Cambias de modelo con una sola variable en `.env`; el análisis es idéntico para todos. Y el **tipo de dato decide el backend** (regla forense del curso).

## Elige tu setup

| Setup | Para quién | Cerebro | Guía |
|---|---|---|---|
| **1 · Local privado** | Laptop capaz, manejas evidencia real, máxima privacidad | Modelo **local** (Ollama), air-gapped | [docs/SETUP-1-local-vm.md](docs/SETUP-1-local-vm.md) |
| **2 · Cloud (prefiere nube)** | Comodidad, free trial de DigitalOcean/Linode | API **hosted** free (Groq/OpenRouter) | [docs/SETUP-2y3-cloud.md](docs/SETUP-2y3-cloud.md) |
| **3 · Sin permisos** | PC de trabajo donde no puedes instalar nada | Todo en un droplet + API **hosted** free | [docs/SETUP-2y3-cloud.md](docs/SETUP-2y3-cloud.md) |

Recomendación de modelos: [config/modelos-recomendados.md](config/modelos-recomendados.md) ·
Regla forense datos→backend: [docs/matriz-datos-backend.md](docs/matriz-datos-backend.md)

## Arranque rápido

```bash
# 1. Entra a un Ubuntu (VM local, WSL2 o droplet cloud) y clona/descomprime el repo
cd ciberrecuperacion-lab

# 2. Bootstrap idempotente según tu setup
bash setup.sh --local      # Setup 1  (instala Ollama + modelo local)
bash setup.sh --cloud      # Setup 2/3 (usarás API hosted; edita .env con tu key)

# 3. Valida el backend y corre el copiloto de triage
make check
make triage
```

`make help` lista todos los atajos.

## Estructura

```
ciberrecuperacion-lab/
├── setup.sh                  # bootstrap idempotente (--local | --cloud | --with-docker)
├── Makefile                  # atajos: check, triage, model, rebuild, up...
├── .env.example              # elige backend: ollama | groq | openrouter
├── requirements.txt          # dependencias pineadas (crece por sesión)
├── docker-compose.yml        # capa de servicios (perfil 'local' = Ollama; usada en S4+)
├── scripts/
│   ├── llm_client.py         # cliente LLM agnóstico (núcleo) + 'make check'
│   ├── triage_copiloto.py    # copiloto de triage (usa el cliente)
│   └── check-requisitos.sh   # verificación del equipo
├── config/  modelos-recomendados.md
├── docs/    SETUP-1..., SETUP-2y3..., matriz-datos-backend.md
├── data/    alerta_ejemplo.json      (dato SINTÉTICO de práctica)
├── evidence/  (git-ignored: evidencia real nunca se versiona)
└── notebooks/ (a partir de la Sesión 2)
```

## Cómo escala entre sesiones (sin romper nada)

- **Nuevas librerías:** agrégalas a `requirements.txt` y corre `make rebuild`. El resto sigue igual.
- **Nuevos servicios** (MinIO, Wazuh… en S4+): se suman como servicios en `docker-compose.yml`; no afectan el núcleo.
- **Nuevos scripts/notebooks:** van en `scripts/` o `notebooks/` sin tocar lo existente.
- El `.env` y `evidence/` están fuera del control de versiones: tu configuración y tu evidencia nunca se pisan al actualizar.

## Principio que no se negocia

El LLM es un **copiloto de análisis, no un piloto automático**. Acelera el triage; el analista valida cada técnica MITRE y cada acción. La IA agiliza la detección y la resiliencia, sin reemplazar el criterio del investigador.

Universidad Ean · Código de módulo **92-EAN**
