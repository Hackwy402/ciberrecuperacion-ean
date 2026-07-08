# Setup 2 y 3 · Cloud — droplet Ubuntu + modelo hosted (API free)

Estos dos casos comparten **el mismo sustrato técnico** (un servidor Ubuntu en la nube al que entras por SSH/consola web) y cambian solo en el *por qué*:

- **Setup 2 — prefiere la nube:** usa el free trial de **DigitalOcean** (o Linode) por comodidad.
- **Setup 3 — máquina de trabajo sin permisos:** no puede instalar nada en su PC → hace **todo en el droplet** desde el navegador. Nada se instala en el equipo corporativo.

En ambos, como un droplet free-tier es pequeño (no corre modelos grandes), el "cerebro" es una **API hosted gratuita** (Groq u OpenRouter). Por eso aquí **solo se usan datos sintéticos** del laboratorio (ver `docs/matriz-datos-backend.md`).

## Paso a paso

### 1. Crear el droplet

- **DigitalOcean:** crea un Droplet → imagen **Ubuntu 24.04** → plan básico. Con el free trial tienes crédito de sobra para el curso.
- **Linode/Akamai:** equivalente, imagen Ubuntu 24.04.
- Entra por **la consola web** del proveedor (no necesitas instalar SSH en tu PC de trabajo) o por `ssh root@IP` si puedes.

> Setup 3 (sin permisos): la consola web del navegador es tu terminal. No instalas nada localmente.

### 2. Clonar el laboratorio y ejecutar el bootstrap

```bash
git clone <URL-del-repo> ciberrecuperacion-lab
cd ciberrecuperacion-lab
bash setup.sh --cloud
```

Instala Python + venv + dependencias. **No** instala Ollama (el droplet no corre el modelo).

### 3. Conseguir una API key gratuita y configurarla

Elige una:

- **Groq** (recomendada: rápida y gratis, sin tarjeta): crea cuenta en `console.groq.com` → API Keys.
- **OpenRouter** (modelos `:free`): crea cuenta en `openrouter.ai` → Keys.

Edita el `.env`:

```bash
nano .env
```

Para Groq:
```
LLM_BACKEND=groq
GROQ_API_KEY=gsk_tu_clave
LLM_MODEL=llama-3.3-70b-versatile
```

Para OpenRouter:
```
LLM_BACKEND=openrouter
OPENROUTER_API_KEY=sk-or-v1-tu_clave
LLM_MODEL=meta-llama/llama-3.3-70b-instruct:free
```

### 4. Validar y probar

```bash
make check      # confirma que la API responde
make triage     # corre el copiloto (usa --datos-sinteticos automáticamente)
```

## Nota de seguridad (importante)

Con backend hosted, el contenido **sale de tu equipo** hacia el proveedor. En este laboratorio está bien porque la alerta es **sintética**. En un caso real, evidencia y PII van **solo** por Setup 1 (local). El copiloto te frena si intentas mandar datos a un backend hosted sin marcarlos como sintéticos.

## Opción avanzada: droplet grande con Ollama

Si tu droplet tiene ≥8 GB RAM (con créditos del trial), puedes correr el modelo **en el droplet** y mantener privacidad:

```bash
bash setup.sh --local     # instala Ollama también en el droplet
```

Así el "cloud" se comporta como el Setup 1 (local respecto al droplet).
