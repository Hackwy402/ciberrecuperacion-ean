#!/usr/bin/env python3
"""Mini-motor Sigma para el lab: evalúa una regla Sigma contra eventos JSONL.

Soporta el subconjunto de Sigma que usamos en la Sesión 3:
  - selecciones con campos y modificadores: |contains, |endswith, |startswith,
    |contains|all, o igualdad exacta (sin modificador)
  - valores escalares o listas (lista sin 'all' = basta con una coincidencia)
  - condition con: nombres de selección, and, or, not, paréntesis

En producción usarías sigma-cli para convertir la regla al lenguaje de tu
SIEM (Splunk, Elastic, Sentinel). Este script existe para que veas el
"motor" por dentro y valides reglas sin montar un SIEM.

Uso:
    python3 cazar_en_logs.py <regla.yml> <eventos.jsonl>

Sin dependencias: solo stdlib (parser YAML mínimo para reglas del lab).
"""
import json
import re
import sys
from pathlib import Path


def _limpiar(valor: str) -> str:
    valor = valor.strip()
    if len(valor) >= 2 and valor[0] == valor[-1] and valor[0] in "'\"":
        valor = valor[1:-1]
    return valor


def parsear_regla(texto: str) -> tuple[str, dict, str]:
    """Extrae (titulo, selecciones, condition) del subconjunto YAML del lab."""
    titulo, selecciones, condition = "(sin titulo)", {}, ""
    en_detection, seleccion_actual, campo_lista = False, None, None
    for cruda in texto.splitlines():
        if not cruda.strip() or cruda.lstrip().startswith("#"):
            continue
        indent = len(cruda) - len(cruda.lstrip())
        linea = cruda.strip()
        if indent == 0:
            en_detection = linea.startswith("detection:")
            if linea.startswith("title:"):
                titulo = _limpiar(linea.split(":", 1)[1])
            continue
        if not en_detection:
            continue
        if indent == 2:
            clave, _, resto = linea.partition(":")
            if clave == "condition":
                condition = resto.strip()
                seleccion_actual = None
            else:
                seleccion_actual = clave
                selecciones[clave] = {}
            campo_lista = None
        elif indent == 4 and seleccion_actual:
            if linea.startswith("- "):
                selecciones[seleccion_actual][campo_lista].append(_limpiar(linea[2:]))
            else:
                campo, _, valor = linea.partition(":")
                campo = campo.strip()
                if valor.strip():
                    selecciones[seleccion_actual][campo] = _limpiar(valor)
                    campo_lista = None
                else:
                    selecciones[seleccion_actual][campo] = []
                    campo_lista = campo
        elif indent >= 6 and seleccion_actual and campo_lista and linea.startswith("- "):
            selecciones[seleccion_actual][campo_lista].append(_limpiar(linea[2:]))
    if not selecciones or not condition:
        raise SystemExit("regla invalida: falta detection con selecciones y condition")
    return titulo, selecciones, condition


def _coincide_campo(evento: dict, campo_mod: str, esperado) -> bool:
    partes = campo_mod.split("|")
    campo, mods = partes[0], partes[1:]
    real = str(evento.get(campo, "")).lower()
    valores = [esperado] if isinstance(esperado, str) else list(esperado)
    valores = [v.lower() for v in valores]
    if "contains" in mods:
        pruebas = [v in real for v in valores]
    elif "endswith" in mods:
        pruebas = [real.endswith(v) for v in valores]
    elif "startswith" in mods:
        pruebas = [real.startswith(v) for v in valores]
    else:
        pruebas = [real == v for v in valores]
    return all(pruebas) if "all" in mods else any(pruebas)


def coincide_seleccion(evento: dict, campos: dict) -> bool:
    return all(_coincide_campo(evento, c, v) for c, v in campos.items())


def evaluar_condition(condition: str, resultados: dict) -> bool:
    tokens = re.findall(r"\(|\)|\w+", condition)
    permitidos = {"and", "or", "not", "(", ")"}
    expr = []
    for t in tokens:
        if t in permitidos:
            expr.append(t)
        elif t in resultados:
            expr.append(str(resultados[t]))
        else:
            raise SystemExit(f"condition usa '{t}' pero no existe esa seleccion")
    return bool(eval(" ".join(expr), {"__builtins__": {}}))  # solo True/False/and/or/not


def main() -> None:
    if len(sys.argv) != 3:
        raise SystemExit(f"uso: {sys.argv[0]} <regla.yml> <eventos.jsonl>")
    regla, eventos_path = Path(sys.argv[1]), Path(sys.argv[2])
    titulo, selecciones, condition = parsear_regla(regla.read_text(encoding="utf-8"))

    print(f"regla     : {titulo}")
    print(f"condition : {condition}\n")

    coincidencias, por_host = [], {}
    with eventos_path.open(encoding="utf-8") as f:
        for linea in f:
            evento = json.loads(linea)
            resultados = {n: coincide_seleccion(evento, c) for n, c in selecciones.items()}
            if evaluar_condition(condition, resultados):
                coincidencias.append(evento)
                por_host[evento.get("host", "?")] = por_host.get(evento.get("host", "?"), 0) + 1

    for ev in coincidencias:
        print(f"[HIT] {ev.get('ts')}  {ev.get('host'):<10} {ev.get('user', ''):<12} "
              f"{ev.get('CommandLine')}")
    print(f"\n{len(coincidencias)} coincidencia(s)" +
          (f" — por host: {por_host}" if por_host else " — la regla no disparo"))


if __name__ == "__main__":
    main()
