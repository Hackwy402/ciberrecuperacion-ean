# Sesión 2 · Análisis de integridad de datos

Del análisis **a mano** (Sesión 1) al análisis **a escala**: puntuar un backup
completo para hallar qué está corrupto/cifrado y cuál copia está limpia.

## Flujo del taller (dos tiempos)

1. **Setup:** usa el entorno del kit (`../core`); `make check` en verde.
2. **Parte 1 — Análisis a escala:** [`parte-1-analisis-a-escala.md`](parte-1-analisis-a-escala.md)
   Entropía global y **por bloques** (cifrado parcial), magic vs. extensión y hashing difuso → `features.csv`.
3. **Parte 2 — Scoring + IA:** [`parte-2-scoring-ia.md`](parte-2-scoring-ia.md)
   **IsolationForest** (scikit-learn) prioriza + reglas clasifican + copiloto local resume.
4. **Parte 3 — Corrupción + nube:** [`parte-3-corrupcion-y-nube.md`](parte-3-corrupcion-y-nube.md)
   Provocar corrupción con **OpenSSL** y medir el salto de entropía, uso **forense** de
   la entropía, y llevar el backup a la nube con inmutabilidad (**AWS** / **Azure**).
5. **Parte 4 — Notebook (dataset real):** [`parte-4-notebook-integridad-real.md`](parte-4-notebook-integridad-real.md)
   Integridad, reglas de calidad y anomalías (IsolationForest) sobre un dataset de salud real
   (Kaggle) en **Colab/Jupyter**; refuerza el análisis **local** de datos sensibles (PHI).

## Contenido

```
02-analisis-de-integridad-datos/
├── parte-1-analisis-a-escala.md
├── parte-2-scoring-ia.md
├── SOLUCION-docente.md
├── scripts/
│   ├── generar_dataset.py      # backup sintético a escala (~27 archivos)
│   ├── extraer_features.py     # señales de integridad -> features.csv (sin dependencias)
│   ├── score.py                # IsolationForest + clasificación por reglas
│   ├── entropia.py             # entropía de Shannon de un archivo
│   └── corromper_demo.sh       # cifra con OpenSSL y muestra el salto de entropía
└── datasets/
    └── backup_caso2/           # se genera con generar_dataset.py
```

Backups en la nube (AWS/Azure, herramientas nativas): [`../docs/backups-nube-aws-azure.md`](../docs/backups-nube-aws-azure.md)

## Conceptos

Entropía de Shannon (global y por bloques), cifrado parcial, magic number vs.
extensión, hashing difuso (concepto de ssdeep/TLSH), detección de anomalías con
scikit-learn (IsolationForest) y la combinación **ML + reglas + criterio humano**.

Requiere el entorno de `../core` (scikit-learn, numpy). `extraer_features.py` no
tiene dependencias; `score.py` necesita el venv del kit activado.
