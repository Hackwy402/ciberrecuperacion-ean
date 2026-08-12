#!/usr/bin/env python3
"""
extraer_features.py — Extrae señales de integridad de cada archivo (Sesión 2)
Universidad Ean · Ciber-Recuperación (92-EAN)

Recorre una carpeta y calcula, por archivo, las señales que usaremos para
detectar corrupción/cifrado a escala. Escribe un CSV que luego puntúa score.py.

Señales:
  - size                : tamaño en bytes
  - entropy             : entropia de Shannon global (0..8)
  - chunk_ent_max/min   : entropia por bloques (detecta cifrado PARCIAL)
  - chunk_ent_std       : variacion entre bloques (mixto = parcial)
  - printable_ratio     : proporcion de bytes imprimibles (texto vs binario)
  - magic_mismatch      : 1 si el tipo real (magic) NO coincide con la extension
  - max_similarity      : mayor similitud difusa con OTRO archivo (0..1)

Sin dependencias externas (solo stdlib). Uso:
    python3 extraer_features.py datasets/backup_caso2 -o features.csv
"""
import argparse
import csv
import math
import os

# ---- entropia de Shannon ------------------------------------------------
def entropy(data):
    if not data:
        return 0.0
    freq = [0] * 256
    for b in data:
        freq[b] += 1
    n = len(data)
    h = 0.0
    for c in freq:
        if c:
            p = c / n
            h -= p * math.log2(p)
    return h

def chunk_entropies(data, nchunks=16):
    if len(data) < nchunks:
        return [entropy(data)]
    step = len(data) // nchunks
    return [entropy(data[i*step:(i+1)*step]) for i in range(nchunks)]

def printable_ratio(data):
    if not data:
        return 0.0
    p = sum(1 for b in data if 32 <= b < 127 or b in (9, 10, 13))
    return p / len(data)

# ---- deteccion de tipo por magic (tabla minima, sin libmagic) -----------
MAGICS = [
    (b"\x89PNG\r\n\x1a\n", "png"),
    (b"%PDF", "pdf"),
    (b"PK\x03\x04", "zip"),      # tambien docx/xlsx/pptx (son zip)
    (b"\xff\xd8\xff", "jpg"),
    (b"GIF8", "gif"),
    (b"\x1f\x8b", "gz"),
    (b"Rar!", "rar"),
]
# extensiones que en realidad son contenedores ZIP
ZIP_EXT = {"docx", "xlsx", "pptx", "zip", "jar", "apk"}

def detect_magic(data):
    head = data[:16]
    for sig, name in MAGICS:
        if head.startswith(sig):
            return name
    # ¿texto?
    if printable_ratio(data[:2048]) > 0.90:
        return "text"
    return "bin"

def ext_of(name):
    e = name.rsplit(".", 1)
    return e[-1].lower() if len(e) == 2 else ""

def magic_mismatch(name, data):
    ext = ext_of(name)
    magic = detect_magic(data)
    if not ext:
        return 0
    # familias esperadas
    text_ext = {"txt", "csv", "ini", "log", "md", "json", "sql", "html"}
    if ext in ZIP_EXT:
        return 0 if magic == "zip" else 1
    if ext in text_ext:
        return 0 if magic == "text" else 1
    if ext in {"png", "pdf", "jpg", "gif"}:
        return 0 if magic == ext else 1
    # extensiones de ransomware u otras: si es texto legible, no es "cifrado"
    return 0

# ---- similitud difusa (k-gram shingling + Jaccard, pura Python) ----------
def shingles(data, k=4, cap=4000):
    s = set()
    n = min(len(data), 65536)   # muestrea hasta 64 KB para velocidad
    for i in range(0, n - k):
        s.add(hash(bytes(data[i:i+k])) & 0xFFFFFFFF)
        if len(s) >= cap:
            break
    return s

def jaccard(a, b):
    if not a or not b:
        return 0.0
    inter = len(a & b)
    union = len(a | b)
    return inter / union if union else 0.0

# ---- recorrido ----------------------------------------------------------
def walk(base):
    files = []
    for root, _, names in os.walk(base):
        for nm in sorted(names):
            p = os.path.join(root, nm)
            files.append((os.path.relpath(p, base), p))
    return files

def main():
    ap = argparse.ArgumentParser(description="Extrae features de integridad a un CSV.")
    ap.add_argument("carpeta", help="Carpeta del backup a analizar.")
    ap.add_argument("-o", "--out", default="features.csv", help="CSV de salida.")
    args = ap.parse_args()

    files = walk(args.carpeta)
    datas, shs, rows = {}, {}, []
    for rel, p in files:
        with open(p, "rb") as f:
            d = f.read()
        datas[rel] = d
        shs[rel] = shingles(d)

    for rel, p in files:
        d = datas[rel]
        ce = chunk_entropies(d)
        # similitud maxima con otro archivo
        best = 0.0
        for rel2 in datas:
            if rel2 == rel:
                continue
            sim = jaccard(shs[rel], shs[rel2])
            if sim > best:
                best = sim
        rows.append({
            "archivo": rel,
            "size": len(d),
            "entropy": round(entropy(d), 4),
            "chunk_ent_max": round(max(ce), 4),
            "chunk_ent_min": round(min(ce), 4),
            "chunk_ent_std": round((sum((x - sum(ce)/len(ce))**2 for x in ce)/len(ce))**0.5, 4),
            "printable_ratio": round(printable_ratio(d), 4),
            "magic_mismatch": magic_mismatch(rel, d),
            "max_similarity": round(best, 4),
        })

    cols = ["archivo", "size", "entropy", "chunk_ent_max", "chunk_ent_min",
            "chunk_ent_std", "printable_ratio", "magic_mismatch", "max_similarity"]
    with open(args.out, "w", newline="", encoding="utf-8") as f:
        wtr = csv.DictWriter(f, fieldnames=cols)
        wtr.writeheader()
        wtr.writerows(rows)
    print(f"[OK] {len(rows)} archivos analizados -> {args.out}")
    print("Vista rapida (entropia y señales):")
    for r in sorted(rows, key=lambda x: -x["entropy"])[:8]:
        print(f"  {r['archivo']:34s} ent={r['entropy']:.2f} "
              f"stdBloques={r['chunk_ent_std']:.2f} magicFalso={r['magic_mismatch']} "
              f"simMax={r['max_similarity']:.2f}")

if __name__ == "__main__":
    main()
