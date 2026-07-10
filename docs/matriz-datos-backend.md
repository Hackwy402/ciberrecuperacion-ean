# Matriz de decisión · clasificación de datos → backend permitido

> Regla de oro del curso: **el tipo de dato decide el backend, no la máquina.**
> El copiloto es una ayuda; la responsabilidad forense es del analista.

## La matriz

| Clasificación del dato | Ejemplos | Backend permitido | Por qué |
|---|---|---|---|
| **Evidencia / Confidencial** | Logs de un caso real, PII, IOCs privados, datos de cliente, muestras de malware | **Solo LOCAL** (Ollama, air-gapped) | Cadena de custodia y confidencialidad; el dato no puede salir del entorno controlado |
| **Interno / Restringido** | Configs, hostnames, topología interna anonimizada | Local; hosted **solo** tras redacción/anonimización | Reduce superficie de fuga |
| **Sintético / Laboratorio** | `data/alerta_ejemplo.json`, datasets de práctica | Local **o** hosted free (Groq/OpenRouter) | No es evidencia; ideal para aprender sin riesgo |
| **Público** | IOCs ya publicados, reportes CTI abiertos, CVEs | Cualquiera | Ya es información pública |

## Cómo lo hace cumplir el laboratorio

- El copiloto (`triage_copiloto.py`) **bloquea** el envío a un backend hosted si no marcas el dato como sintético (`--datos-sinteticos`). Es una barrera para obligar a pensar, no un candado.
- El `.gitignore` excluye `evidence/` para que la evidencia real **nunca** entre al repositorio.
- Si el backend es hosted, `make check` te recuerda no enviar evidencia real.

## Buenas prácticas cuando SÍ debes usar hosted (caso real)

1. **Clasifica primero.** Si hay duda, trátalo como confidencial → local.
2. **Anonimiza/redacta** antes de enviar (IPs, nombres, IDs).
3. **Elige proveedores con no-retención / ZDR** (zero data retention) y revisa su política de datos.
4. **Minimiza:** envía solo el fragmento necesario, no el log completo.
5. **Registra la decisión** (qué se envió, a dónde, por qué) — trazabilidad forense.

## Encaje con el marco del curso

Esto operacionaliza **OWASP LLM Top 10 – LLM01 (divulgación de información sensible)** y el principio "los datos nunca salen de la bóveda" del módulo. La elección del modelo **es** una decisión de ciber-recuperación y forense, no un detalle técnico.
