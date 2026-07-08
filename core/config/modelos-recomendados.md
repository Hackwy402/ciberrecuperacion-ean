# Modelos recomendados · seguro + efectivo para el taller

Objetivo: que **cualquiera que sea el modelo**, el alumno aprenda las bases del
análisis asistido por IA con resultados útiles y reproducibles. Recomendamos
modelos *instruct* (chat), con **temperatura baja (0.2)** para que la clase
compare resultados parecidos.

## Recomendación por setup

| Setup | Backend | Modelo recomendado | Alternativa liviana |
|---|---|---|---|
| 1 · Local privado (≥16 GB) | Ollama | `llama3.1:8b` | `qwen2.5:7b` |
| 1 · Local privado (RAM justa) | Ollama | `llama3.2:3b` | `qwen2.5:3b` |
| 2/3 · Cloud (Groq) | Groq | `llama-3.3-70b-versatile` | `llama-3.1-8b-instant` |
| 2/3 · Cloud (OpenRouter) | OpenRouter | `meta-llama/llama-3.3-70b-instruct:free` | `qwen/qwen-2.5-72b-instruct:free` |

**¿Por qué estos?** Son *instruct*, siguen instrucciones estructuradas (secciones
del triage), razonan bien sobre logs y son gratuitos o locales. Un 70B hosted da
mejor razonamiento; un 8B local da el mejor equilibrio **privacidad + calidad**.

## Qué hace "seguro" a un modelo en este taller

No se trata solo del modelo, sino de **cómo** lo usas:

1. **Instruct/chat, no base.** Los base no siguen instrucciones y alucinan más.
2. **Temperatura 0.1–0.2.** Reproducible y menos inventiva (clave en forense).
3. **Prompt con estructura fija** (las 6 secciones del triage) → salidas comparables.
4. **Copiloto, no piloto:** el modelo propone, el analista valida cada técnica MITRE y cada acción.
5. **Dato correcto → backend correcto** (ver `matriz-datos-backend.md`).

## Por qué NO recomendamos ciertas cosas para el taller

- **Modelos base o sin *instruct*:** no siguen el formato y alucinan.
- **Temperatura alta:** irrepetible; malo para comparar en clase y para evidencia.
- **Asistentes de IDE/terminal (Kiro, Claude Code, Warp) como "cerebro" del copiloto:** son para *construir/analizar* como analista, no para que el script los invoque como motor. Útiles, pero otro rol — y les aplica la misma regla forense de datos.

## Modelo especializado (opcional, avanzado)

Para quien quiera explorar el futuro de la detección con IA especializada:
**Foundation-Sec-8B** (modelo abierto orientado a ciberseguridad) puede correrse
local con Ollama/llama.cpp. Lo dejamos como reto para sesiones avanzadas; para las
bases, los modelos generales de la tabla son suficientes y más fáciles de servir.

> Nota: los nombres/versiones de modelos hosted y sus límites free cambian con el
> tiempo. Si un modelo deja de estar disponible, revisa la consola del proveedor
> (Groq / OpenRouter) y actualiza `LLM_MODEL` en tu `.env`.
