# Parte 4 · Notebook — integridad sobre un dataset real (Colab/Jupyter)

**Taller Sesión 2 · Ciber-Recuperación (92-EAN)** · Extensión (~25 min)

Aplicamos lo de la Sesión 2 a un **dataset real de salud** (Alzheimer, Kaggle) en un
**notebook**. Es un gran cierre porque es **PHI**: refuerza que el dato sensible se
analiza **local**, no se manda a un modelo público.

> Notebook: [`notebooks/integridad_dataset_kaggle.ipynb`](notebooks/integridad_dataset_kaggle.ipynb)
> Dataset: `rabieelkharoua/alzheimers-disease-dataset` (2149 pacientes × 35 columnas).

## Cómo abrirlo

**Opción A — Google Colab:**
1. Sube el `.ipynb` a Colab (o ábrelo desde GitHub: *File → Open notebook → GitHub*).
2. La primera celda instala y descarga el dataset con `kagglehub` (necesitas cuenta de Kaggle).

**Opción B — Jupyter local / en tu VM:**
```bash
pip install pandas scikit-learn matplotlib jupyter
jupyter notebook   # abre integridad_dataset_kaggle.ipynb
```
Si ya descargaste el CSV, deja `alzheimers_disease_data.csv` junto al notebook: lo carga solo.

## Qué hace el notebook (5 secciones)

1. **Integridad del archivo:** huella **SHA-256** (detecta manipulación) y **entropía** del archivo;
   demuestra que "cifrar = corromper" dispara la entropía a ~8 (como en la Parte 3).
2. **Calidad/integridad tabular:** nulos, duplicados, **clave única** (`PatientID`), y **reglas de
   dominio** (rangos clínicos, banderas binarias en {0,1}). El dataset original sale **todo en cero**
   = línea base *conocida-buena*.
3. **Detección de anomalías (IsolationForest):** el **mismo método de la Parte 2**, ahora sobre
   registros de pacientes → prioriza los más "raros" para revisión.
4. **Simular corrupción y detectarla:** inyecta errores (edad 999, BMI negativo, MMSE fuera de rango,
   binario inválido, nulos, duplicados) y comprueba que **las reglas y el hash** lo detectan.
5. **Regla forense (PHI):** solo se envía a un copiloto **local** un **resumen agregado y sin
   identificadores** — nunca las filas de pacientes. Mapea a OWASP LLM01.

## Nota importante

El **dataset no se versiona** en este repo (licencia de Kaggle + tamaño): el notebook lo descarga
con `kagglehub` o lo lee localmente. Los archivos que genera (`dataset_trabajo.csv`,
`dataset_corrupto.csv`, imágenes) son temporales y están en `.gitignore`.

> ✅ **Checkpoint Parte 4:** corriste el notebook, verificaste la integridad del dataset real,
> detectaste la corrupción inyectada y entiendes por qué el PHI se analiza local.
