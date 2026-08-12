#!/usr/bin/env python3
"""
score.py — Puntúa la corrupción de un backup con scikit-learn (Sesión 2)
Universidad Ean · Ciber-Recuperación (92-EAN)

Toma el CSV de features y entrena un detector de anomalías (IsolationForest)
para asignar a cada archivo un SCORE de corrupción (0..100) y una bandera.
Ordena de más sospechoso a menos, para priorizar la revisión del analista.

La idea: en un backup de miles de archivos no puedes mirar uno por uno; el
modelo te dice DÓNDE mirar primero. La decisión final es del analista.

Uso:
    python3 score.py features.csv
    python3 score.py features.csv --top 15
"""
import argparse
import csv
import sys

try:
    import numpy as np
    from sklearn.ensemble import IsolationForest
    from sklearn.preprocessing import StandardScaler
except ImportError:
    sys.exit("Faltan dependencias. Activa el entorno del kit:  "
             "source ../../core/.venv/bin/activate  (o pip install scikit-learn numpy)")

FEATURES = ["size", "entropy", "chunk_ent_max", "chunk_ent_min",
            "chunk_ent_std", "printable_ratio", "magic_mismatch", "max_similarity"]

def clasificar(r):
    """Clasificación por reglas deterministas (complementa al score de ML)."""
    ent = float(r["entropy"]); std = float(r["chunk_ent_std"])
    cmin = float(r["chunk_ent_min"]); cmax = float(r["chunk_ent_max"])
    magic = int(float(r["magic_mismatch"])); sim = float(r["max_similarity"])
    if ent >= 7.5 and std < 0.5:
        return "cifrado_total"
    if cmax >= 7.5 and cmin < 6.0 and std >= 0.6:
        return "cifrado_parcial"
    if magic == 1:
        return "extension_falsa"
    if sim >= 0.6:
        return "casi_duplicado"
    return "limpio"

def load(csv_path):
    rows = []
    with open(csv_path, newline="", encoding="utf-8") as f:
        for r in csv.DictReader(f):
            rows.append(r)
    if not rows:
        sys.exit("El CSV está vacío. Corre primero extraer_features.py")
    X = np.array([[float(r[c]) for c in FEATURES] for r in rows], dtype=float)
    return rows, X

def main():
    ap = argparse.ArgumentParser(description="Scoring de corrupción con IsolationForest.")
    ap.add_argument("features_csv")
    ap.add_argument("--top", type=int, default=12, help="Cuántos sospechosos mostrar.")
    ap.add_argument("-o", "--out", default="scores.csv")
    args = ap.parse_args()

    rows, X = load(args.features_csv)
    Xs = StandardScaler().fit_transform(X)

    # contamination: proporcion esperada de anomalias (aprox). 'auto' tambien sirve.
    model = IsolationForest(n_estimators=200, contamination=0.25, random_state=42)
    model.fit(Xs)
    raw = model.score_samples(Xs)          # mayor = más normal
    flags = model.predict(Xs)              # -1 anomalia, 1 normal

    # normaliza a score 0..100 (100 = más sospechoso)
    lo, hi = raw.min(), raw.max()
    score = [int(round(100 * (hi - v) / (hi - lo))) if hi > lo else 0 for v in raw]

    for i, r in enumerate(rows):
        r["corrupcion_score"] = score[i]
        r["anomalia"] = "SI" if flags[i] == -1 else "no"
        r["clasificacion"] = clasificar(r)

    rows.sort(key=lambda r: -r["corrupcion_score"])

    # salida
    with open(args.out, "w", newline="", encoding="utf-8") as f:
        cols = ["archivo", "corrupcion_score", "anomalia", "clasificacion", "entropy",
                "chunk_ent_std", "magic_mismatch", "max_similarity", "size"]
        wtr = csv.DictWriter(f, fieldnames=cols, extrasaction="ignore")
        wtr.writeheader()
        wtr.writerows(rows)

    print("=" * 84)
    print("  SCORING DE CORRUPCIÓN DEL BACKUP  (100 = más sospechoso)")
    print("=" * 84)
    print(f"  {'ARCHIVO':34s} {'SCORE':>5s} {'ANOM':>4s}  {'CLASIFICACION':16s} {'ENT':>5s} {'stdBloq':>7s}")
    print("-" * 84)
    for r in rows[:args.top]:
        print(f"  {r['archivo']:34s} {r['corrupcion_score']:>5} {r['anomalia']:>4}  "
              f"{r['clasificacion']:16s} {float(r['entropy']):>5.2f} {float(r['chunk_ent_std']):>7.2f}")
    n_anom = sum(1 for r in rows if r["anomalia"] == "SI")
    print("-" * 84)
    print(f"  {n_anom} anómalos (ML) de {len(rows)}. Detalle completo -> {args.out}")
    print("  Reglas: cifrado_total (ent~8) · cifrado_parcial (bloques mixtos) ·")
    print("  extension_falsa (magic) · casi_duplicado (similitud) · limpio.")
    print("  El ML PRIORIZA dónde mirar; las reglas CLASIFICAN; el analista DECIDE.")

if __name__ == "__main__":
    main()
