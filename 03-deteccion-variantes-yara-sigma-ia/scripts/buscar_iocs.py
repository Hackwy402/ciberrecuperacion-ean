#!/usr/bin/env python3
"""Mini-motor de triage por IOCs — fallback cuando no hay `yara` instalado.

Escanea un directorio buscando las señales del informe CTI de Locked3D
(cabecera hex al offset 0 + strings) y aplica la misma lógica de la regla
del lab: veredicto FAMILIA si tiene la cabecera al inicio O ≥2 señales.

Uso:
    python3 buscar_iocs.py <directorio> [--min 2]

Sin dependencias: solo stdlib. Es didáctico, no un reemplazo de YARA.
"""
import argparse
from pathlib import Path

MAGIC = bytes.fromhex("4C334421")  # "L3D!" al offset 0

SENALES = {
    "core_v3": b"L0CK3D-CORE",
    "mutex": b"L3D_MUTEX",
    "nota_rescate": b"LEEME_RESCATE.txt",
    "onion": b"descifra-tus-archivos",
}


def escanear(ruta: Path, minimo: int) -> tuple[list[str], bool, bool]:
    datos = ruta.read_bytes()
    encontradas = [nombre for nombre, patron in SENALES.items() if patron in datos]
    tiene_magic = datos.startswith(MAGIC)
    es_familia = tiene_magic or len(encontradas) >= minimo
    return encontradas, tiene_magic, es_familia


def main() -> None:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("directorio", type=Path)
    ap.add_argument("--min", type=int, default=2,
                    help="señales string mínimas para marcar familia (default: 2)")
    args = ap.parse_args()

    archivos = sorted(p for p in args.directorio.rglob("*") if p.is_file())
    if not archivos:
        raise SystemExit(f"no hay archivos en {args.directorio}")

    ancho = max(len(p.name) for p in archivos)
    print(f"{'archivo':<{ancho}}  magic@0  señales                      veredicto")
    print("-" * (ancho + 55))
    detecciones = 0
    for p in archivos:
        senales, magic, familia = escanear(p, args.min)
        veredicto = "** LOCKED3D **" if familia else "limpio"
        detecciones += familia
        print(f"{p.name:<{ancho}}  {'si' if magic else '--':<7}  "
              f"{','.join(senales) or '-':<28}  {veredicto}")
    print(f"\n{detecciones}/{len(archivos)} archivos marcados como familia Locked3D "
          f"(regla: magic@0 O >= {args.min} señales)")


if __name__ == "__main__":
    main()
