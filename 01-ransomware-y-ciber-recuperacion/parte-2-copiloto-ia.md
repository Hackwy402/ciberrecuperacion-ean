# Parte 2 · El copiloto de IA (lleva el modelo a la data)

**Taller Sesión 1 · Ciber-Recuperación (92-EAN)**
Duración sugerida: 25 min.

> **Principio forense:** llevamos **el modelo a la data**, no la data al modelo.
> El análisis corre **local**, sobre tu propia máquina; la evidencia **no sale**
> hacia un servicio público. El modelo es un **copiloto** que resume, correlaciona
> y sugiere — el analista (tú, en la Parte 1) ya hizo el trabajo de mirar.

## 1. Confirma que tu modelo local está listo

```bash
cd core
make check          # debe decir [OK] con backend ollama (local)
```

Si usas Setup 2/3 (API hosted) recuerda: **solo datos sintéticos**. Con evidencia
real, el backend DEBE ser local (ver `docs/matriz-datos-backend.md`).

## 2. Del hallazgo humano al triage asistido

Ya tienes tus `hallazgos.txt` de la Parte 1. Ahora pídele al copiloto que los
estructure y los mapee a MITRE ATT&CK. Usamos la alerta sintética que resume el caso:

```bash
make triage         # corre sobre data/alerta_ejemplo.json (dato sintético)
```

Compara la salida del modelo con **tu** análisis manual:

1. ¿El modelo llegó a lo mismo que tú (cifrado = T1486, sabotaje/retos de recuperación)?
2. ¿Se le escapó algo que **tú** sí viste con los comandos?
3. ¿Inventó algún dato que **no** estaba en la evidencia? (alucinación)

> Este contraste es la lección central: la IA es rápida, pero **tu análisis manual
> es el control de calidad**. Copiloto, no piloto.

## 3. Por qué local y no un modelo público (para exponer en clase)

- **Cadena de custodia:** la evidencia no debe salir de tu entorno controlado.
- **Confidencialidad / PII:** enviar un backup a un API público es una fuga.
- **Retención del proveedor:** no controlas qué guarda ni por cuánto tiempo.
- **Contaminación:** un tercero en el flujo debilita el valor probatorio.

Por eso el modelo **viene a la data**: corre en tu máquina, offline si hace falta.
Mapea a **OWASP LLM01** (divulgación de información sensible).

## 4. Reto opcional

Modifica el dataset (agrega otro archivo cifrado o con extensión falsa con
`scripts/generar_dataset.py`), vuelve a hacer el análisis manual y luego el asistido.
¿El copiloto se adapta? ¿Tú lo detectas primero?

> **Checkpoint Parte 2:** corriste el copiloto **local** sobre tus hallazgos,
> lo contrastaste críticamente con tu análisis manual y puedes explicar por qué
> la evidencia no se manda a un modelo público.
