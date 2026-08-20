#!/usr/bin/env python3
"""metricas_rto_rpo.py — Calcula RTO y RPO de la línea de tiempo del incidente.

RPO (Recovery Point Objective): dato perdido = incidente − último backup limpio.
RTO (Recovery Time Objective): tiempo caído = servicio restaurado − incidente.

Lee datasets/caso5/incidente.json. Sin dependencias: solo stdlib.

Uso:
  python3 scripts/metricas_rto_rpo.py
  python3 scripts/metricas_rto_rpo.py --rto-objetivo 4 --rpo-objetivo 24
"""
import argparse
import json
from datetime import datetime
from pathlib import Path

BASE = Path(__file__).resolve().parent.parent / "datasets" / "caso5"


def parse(ts: str) -> datetime:
    return datetime.fromisoformat(ts)


def fmt(delta) -> str:
    total = int(delta.total_seconds())
    h, r = divmod(total, 3600)
    m, _ = divmod(r, 60)
    return f"{h}h {m:02d}m"


def main() -> None:
    ap = argparse.ArgumentParser(description="RTO/RPO del incidente (92-EAN)")
    ap.add_argument("--rto-objetivo", type=float, default=4.0, help="RTO objetivo en horas")
    ap.add_argument("--rpo-objetivo", type=float, default=24.0, help="RPO objetivo en horas")
    args = ap.parse_args()

    datos = json.loads((BASE / "incidente.json").read_text(encoding="utf-8"))
    hitos = {e["hito"]: e for e in datos["eventos"]}

    req = ["ultimo_backup_limpio", "incidente", "servicio_restaurado"]
    faltan = [h for h in req if h not in hitos]
    if faltan:
        raise SystemExit(f"faltan hitos en incidente.json: {faltan}")

    t_backup = parse(hitos["ultimo_backup_limpio"]["ts"])
    t_incid = parse(hitos["incidente"]["ts"])
    t_rest = parse(hitos["servicio_restaurado"]["ts"])

    rpo = t_incid - t_backup
    rto = t_rest - t_incid
    rpo_h = rpo.total_seconds() / 3600
    rto_h = rto.total_seconds() / 3600

    print(f"Caso: {datos['caso']}")
    print("=" * 58)
    print("Línea de tiempo:")
    for e in datos["eventos"]:
        print(f"  {e['ts']}  {e['hito']:<24} {e['nota']}")
    print("=" * 58)
    print(f"RPO (dato perdido) : {fmt(rpo)}  = {rpo_h:.2f} h   "
          f"[{'OK' if rpo_h <= args.rpo_objetivo else 'EXCEDE'} objetivo {args.rpo_objetivo}h]")
    print(f"RTO (tiempo caído) : {fmt(rto)}  = {rto_h:.2f} h   "
          f"[{'OK' if rto_h <= args.rto_objetivo else 'EXCEDE'} objetivo {args.rto_objetivo}h]")
    print("=" * 58)

    # Desglose útil del RTO: dónde se fue el tiempo
    if "deteccion" in hitos and "aislamiento" in hitos:
        t_det = parse(hitos["deteccion"]["ts"])
        t_ais = parse(hitos["aislamiento"]["ts"])
        print("Desglose del RTO:")
        print(f"  detectar   (incidente→detección) : {fmt(t_det - t_incid)}")
        print(f"  contener   (detección→aislamiento): {fmt(t_ais - t_det)}")
        if "restauracion_iniciada" in hitos:
            t_ini = parse(hitos["restauracion_iniciada"]["ts"])
            print(f"  decidir    (aislamiento→restaurar): {fmt(t_ini - t_ais)}")
            print(f"  restaurar  (restaurar→servicio)   : {fmt(t_rest - t_ini)}")
        print("\nDonde el copiloto ayuda: reduce 'decidir' (respuesta inmediata y")
        print("correcta) — el tramo que más se dispara cuando nadie recuerda el runbook.")

    excede = rto_h > args.rto_objetivo or rpo_h > args.rpo_objetivo
    raise SystemExit(1 if excede else 0)


if __name__ == "__main__":
    main()
