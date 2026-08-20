# Parte 1 · Construir el copiloto RAG (grounded vs alucinación)

**Taller Sesión 5 · Ciber-Recuperación (92-EAN)** · Duración: 25 min
Entorno: **Ubuntu** o **macOS**, con el entorno del `core` (Ollama local u otro backend).

> En la Sesión 4 dejaste la copia limpia en la bóveda. Hoy construyes el asistente
> que, en plena crisis, te dice CÓMO restaurarla — respondiendo con TUS runbooks
> y citando la fuente, no inventando.

## 0. Prepara el entorno

```bash
cd 05-copiloto-recuperacion-rag
python3 scripts/generar_corpus.py         # runbooks + alertas + incidente (sintético)
```

El "cerebro" del copiloto se elige en el `.env` del core (Sesión 1). Verifica tu backend:

```bash
python3 ../core/scripts/llm_client.py --check
```

Para datos reales usarías **Ollama local** (`LLM_BACKEND=ollama`, `llama3.1:8b`);
el corpus del lab es sintético, así que un backend hosted gratis también sirve.

## 1. Mira el retriever por dentro (sin LLM)

Antes de generar nada, comprueba QUÉ recupera. El retriever es TF-IDF puro
(stdlib, sin dependencias):

```bash
python3 scripts/rag_copiloto.py "¿cómo restauro la base de datos SRV-DB-01?" --solo-recuperar
```

Debe traer `runbook-restauracion-db.md` como fuente principal. Prueba otras:

```bash
python3 scripts/rag_copiloto.py "¿cómo aíslo un host comprometido?" --solo-recuperar -k 1
python3 scripts/rag_copiloto.py "¿debo pagar el rescate?" --solo-recuperar -k 1
```

Cada pregunta trae el runbook correcto. **Esa es la R de RAG**: recuperar el
documento relevante antes de responder.

## 2. El contraste: con RAG vs sin RAG (aquí está el aprendizaje)

Primero, el copiloto **con RAG** (responde desde los runbooks y cita la fuente):

```bash
python3 scripts/rag_copiloto.py "¿cómo restauro la base de datos SRV-DB-01?"
```

Fíjate en tres cosas de la salida:
- La respuesta contiene los pasos reales del runbook (no reiniciar, buscar la
  versión limpia en la bóveda, verificar hashes…).
- Cada afirmación cita `[runbook-restauracion-db.md]`.
- Al final, la **auditoría** confirma que las citas corresponden a fuentes reales.

Ahora el mismo modelo **sin RAG** (responde de memoria):

```bash
python3 scripts/rag_copiloto.py "¿cómo restauro la base de datos SRV-DB-01?" --sin-rag
```

Compara: sin el runbook en la mano, el LLM inventa un procedimiento genérico y
**plausible** — puede citar hosts o comandos que no existen en tu organización.
En una crisis, eso es peligroso. La diferencia entre las dos corridas es
exactamente el valor de RAG.

## 3. El guard de grounding: citar o callar

Pregunta algo que **no está** en tus runbooks:

```bash
python3 scripts/rag_copiloto.py "¿cuál es la capital de Francia?"
```

El retriever no encuentra nada por encima del umbral de relevancia → el copiloto
responde **"No está en mis runbooks."** en vez de inventar. Un asistente de
recuperación que dice "no sé" es más confiable que uno que siempre responde.

> ✅ **Checkpoint Parte 1:** tienes el copiloto respondiendo con citas a runbooks
> reales, viste la alucinación del modo `--sin-rag` y comprobaste que el guard de
> grounding calla cuando el corpus no cubre la pregunta. Sigue la Parte 2: usarlo
> en un incidente real y medir RTO/RPO.
