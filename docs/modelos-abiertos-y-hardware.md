# Modelos: abierto vs. público, y cuál usar según tu hardware

Referencia del curso para elegir el "cerebro" del copiloto de forma responsable.

## Modelo abierto vs. modelo público (no son lo mismo)

| | **Modelo de pesos abiertos** | **Modelo público (API)** |
|---|---|---|
| Qué es | Descargas los pesos y lo ejecutas **tú** | Consumes un servicio remoto por API |
| Dónde corre | En tu máquina / tu infraestructura | En los servidores del proveedor |
| La data | **No sale** de tu entorno | **Sale** hacia el proveedor |
| Ejemplos | Llama, Qwen, Mistral, Gemma, Foundation-Sec-8B | GPT-4o, Claude, Gemini (API) |
| Uso forense | **Apto para evidencia** (local, air-gapped) | Solo datos **no** sensibles / sintéticos |

> "Abierto" se refiere a que puedes **descargar y ejecutar** los pesos; "público"
> aquí significa **servicio de terceros**. Un modelo abierto puede correr local
> (privado) o servirse; lo que protege la evidencia es **dónde corre**, no la marca.

## Llevar el modelo a la data (principio)

En forense, la evidencia (backup, imagen de disco) no se mueve a un tercero: se
lleva **el modelo a la data**, corriendo local. Así preservas cadena de custodia,
confidencialidad y valor probatorio. Mapea a **OWASP LLM01** (divulgación sensible).

## ¿Qué modelo según tu hardware?

| Hardware | Modelo recomendado (Ollama) | Notas |
|---|---|---|
| 8 GB RAM, sin GPU | `llama3.2:3b` / `qwen2.5:3b` | Básico, para aprender el flujo |
| 16–24 GB RAM (p. ej. Mac M-series) | **`llama3.1:8b`** / `qwen2.5:7b` | **El del curso**: equilibrio calidad/privacidad |
| GPU 8–12 GB VRAM | 8B en GPU / `mistral-nemo` | Respuestas más rápidas |
| GPU 24 GB+ VRAM (workstation) | `qwen2.5:32b`, 70B cuantizado | Mejor razonamiento local |
| Servidor multi-GPU / 48 GB+ | `llama3.3:70b`, Foundation-Sec-8B-Reasoning | Nivel producción, aún **local** |

**Por qué el curso usa `llama3.1:8b`:** corre local en un equipo de 16–24 GB (como el
del docente), da buen seguimiento de instrucciones para el triage y mantiene la
privacidad. Es el mejor punto de "calidad suficiente + reproducible por todos".

**Si tuvieras más hardware** (solo como ejemplo, no requerido para el taller): con una
GPU de 24 GB podrías correr modelos de 30–70B cuantizados; con servidor, el
`Foundation-Sec-8B-Reasoning` de Cisco o un 70B — más razonamiento, **sin** dejar de ser local.

## Modelos abiertos en Hugging Face para este caso de uso

Especializados en ciberseguridad:

- **`fdtn-ai/Foundation-Sec-8B`** — modelo base de seguridad (Cisco Foundation AI), sobre Llama-3.1-8B.
- **`fdtn-ai/Foundation-Sec-8B-Instruct`** — variante *instruct*, copiloto de seguridad listo para usar.
- **`fdtn-ai/Foundation-Sec-8B-Reasoning`** — razonamiento de seguridad (más pesado).

Generales sólidos (sirven muy bien para el triage del curso):

- **`meta-llama/Llama-3.1-8B-Instruct`**, `Llama-3.2-3B-Instruct`
- **`Qwen/Qwen2.5-7B-Instruct`** (y 3B/14B/32B)
- **`mistralai/Mistral-7B-Instruct`**, `Mistral-Nemo`
- **`google/gemma-2-9b-it`**

> **Cómo ejecutarlos local:** lo más simple es **Ollama** (`ollama pull llama3.1:8b`).
> Para modelos de HF que no estén en el catálogo de Ollama (p. ej. Foundation-Sec-8B),
> se usa una versión **GGUF** con un `Modelfile` de Ollama, o `llama.cpp` directamente.
> Requiere cuenta gratuita de Hugging Face para descargar algunos pesos.

Nota: nombres, tamaños y disponibilidad cambian con el tiempo — verifica en huggingface.co.
