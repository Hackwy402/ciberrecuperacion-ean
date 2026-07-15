#!/usr/bin/env python3
"""
entropia.py — Calcula la entropía de Shannon de archivos (Sesión 1)
Universidad Ean · Ciber-Recuperación (92-EAN)

La entropía mide "qué tan aleatorios" son los bytes de un archivo:
  - Texto normal / config:   ~ 3.5 a 5.0 bits/byte
  - Ejecutables / comprimidos: ~ 6 a 7 bits/byte
  - Cifrado / ransomware:    ~ 7.9 a 8.0 bits/byte  (casi máximo)

Un salto súbito a ~8.0 es una señal fuerte de cifrado. Es una de las
técnicas base para detectar corrupción de backups SIN necesidad de IA.

Uso:
    python3 entropia.py archivo1 archivo2 ...
    python3 entropia.py *
"""
import math
import sys
import os

def entropia(path):
    with open(path, "rb") as f:
        data = f.read()
    if not data:
        return 0.0, 0
    freq = [0] * 256
    for b in data:
        freq[b] += 1
    n = len(data)
    h = 0.0
    for c in freq:
        if c:
            p = c / n
            h -= p * math.log2(p)
    return h, n

def veredicto(h):
    if h >= 7.5:
        return "CIFRADO / muy aleatorio  <-- sospechoso"
    if h >= 6.0:
        return "comprimido / binario"
    return "texto / datos normales"

def main():
    args = [a for a in sys.argv[1:] if os.path.isfile(a)]
    if not args:
        print("Uso: python3 entropia.py <archivos...>")
        sys.exit(1)
    print(f"{'ARCHIVO':30s} {'ENTROPIA':>9s}  VEREDICTO")
    print("-" * 70)
    for path in args:
        h, n = entropia(path)
        print(f"{os.path.basename(path):30s} {h:9.3f}  {veredicto(h)}")

if __name__ == "__main__":
    main()
