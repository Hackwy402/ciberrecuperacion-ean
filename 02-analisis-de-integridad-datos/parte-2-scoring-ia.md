# Parte 2 · Scoring con scikit-learn + copiloto de IA

**Taller Sesión 2 · Ciber-Recuperación (92-EAN)** · Duración: 25 min

> Ya tienes las señales (`features.csv`). Ahora un modelo de **anomalías** las
> combina para **priorizar** qué revisar, y una **clasificación por reglas** las
> etiqueta. El copiloto de IA local resume y recomienda. El analista decide.

## 1. Activa el entorno (trae scikit-learn)

```bash
source ../../core/.venv/bin/activate      # el venv del kit (Sesión 1)
# si no existe:  cd ../../core && bash setup.sh --cloud && cd -
```

## 2. Puntúa el backup (IsolationForest)

```bash
python3 ../../scripts/score.py features.csv --top 16
```

Salida: cada archivo con un **`corrupcion_score` (0–100)**, si el ML lo marca como
**anomalía**, y una **`clasificacion`** por reglas (`cifrado_total`,
`cifrado_parcial`, `extension_falsa`, `casi_duplicado`, `limpio`). Se guarda en `scores.csv`.

## 3. Lee el resultado con criterio

Tres capas que se complementan (ninguna basta sola):

1. **ML (score / anomalía):** te dice **dónde mirar primero** en miles de archivos.
2. **Reglas (clasificación):** te dice **qué tipo** de problema es.
3. **Tú:** confirmas y decides la acción de recuperación.

Preguntas de discusión:

- ¿Dónde **coinciden** el ML y las reglas? ¿Dónde **discrepan**? (p. ej. un
  casi-duplicado legítimo con score alto = falso positivo del ML).
- ¿Qué archivos **limpios** sirven para recuperar? (score bajo + `limpio`).
- El cifrado **parcial** ¿lo habrías visto solo con la entropía global? (no: hizo
  falta la señal por bloques).

## 4. Copiloto de IA local sobre el resultado (lleva el modelo a la data)

Deja que el modelo **local** resuma el scoring y recomiende — sin que los datos salgan:

```bash
ollama run llama3.1:8b "Eres analista de ciber-recuperacion. Con esta tabla de scoring de un backup, dime: (1) que archivos priorizar, (2) su tipo de problema, (3) que copia esta limpia para recuperar. No inventes nada fuera de la tabla: $(cat scores.csv)"
```

(Escribe `/bye` para salir.) Contrasta la respuesta del modelo con **tu** lectura de
la tabla: ¿coincide?, ¿se le escapó el cifrado parcial?, ¿alucinó algún archivo?

> Si estás en un setup **hosted** (Azure/Groq), recuerda: aquí el dato es
> **sintético**. Con evidencia real, el modelo va **local** (regla datos→backend).

## 5. Cierre

El aporte de la Sesión 2: pasar de mirar archivos **uno por uno** a **puntuar el
backup completo** para hallar rápido lo corrupto y **la copia limpia** — la base
para una recuperación con integridad (Sesiones 4 y 5).

> ✅ **Checkpoint Parte 2:** generaste `scores.csv`, interpretaste ML + reglas,
> corriste el copiloto **local** y lo contrastaste con tu análisis.
