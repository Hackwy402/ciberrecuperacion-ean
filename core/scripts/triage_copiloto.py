#!/usr/bin/env python3
"""
triage_copiloto.py — Copiloto de triage de ransomware (Sesión 1+)
Universidad Ean · Ciber-Recuperación (92-EAN)

Analiza una alerta/log y entrega un triage estructurado usando el modelo que
tengas configurado (local u hosted) a través de llm_client.py. El mismo comando
funciona para los 3 setups del curso; solo cambia el .env.

    python scripts/triage_copiloto.py data/alerta_ejemplo.json
    python scripts/triage_copiloto.py data/alerta_ejemplo.json --datos-sinteticos

IMPORTANTE (principio del curso): el LLM es un COPILOTO de análisis, no un
piloto automático. Toda técnica y acción sugerida se valida antes de ejecutar.
"""
import argparse
import json
import os
import sys

# Permite 'import llm_client' al correr desde la raíz del repo
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from llm_client import LLMClient, LLMConfigError  # noqa: E402

SYSTEM_PROMPT = (
    "Eres un analista de ciberseguridad senior especializado en respuesta a "
    "incidentes y ciber-recuperacion. Analizas alertas y logs, y respondes SIEMPRE "
    "en espanol, tecnico y conciso. NO inventes datos que no esten en la evidencia. "
    "Si algo no se puede determinar, dilo. Recuerda que tus conclusiones deben ser "
    "validadas por un analista humano antes de actuar."
)

USER_TEMPLATE = """Analiza la siguiente evidencia de seguridad y entrega un triage inicial.

EVIDENCIA (JSON):
{evidencia}

Responde EXACTAMENTE con estas secciones numeradas:
1. RESUMEN (2-3 lineas: que esta pasando).
2. TECNICAS MITRE ATT&CK (IDs + nombre + una linea de justificacion cada una).
3. HIPOTESIS (es ransomware? en que fase? por que).
4. IMPACTO EN LA RECUPERACION (se afectan backups o la capacidad de recuperar?).
5. ACCIONES INMEDIATAS (3 a 5 pasos priorizados).
6. NIVEL DE CONFIANZA (bajo/medio/alto) y QUE FALTA VERIFICAR.
"""


def main():
    ap = argparse.ArgumentParser(description="Copiloto de triage con LLM (backend configurable).")
    ap.add_argument("evidencia", help="Ruta a un archivo JSON (alerta/log) a analizar.")
    ap.add_argument("--datos-sinteticos", action="store_true",
                    help="Confirma que la evidencia NO es real/PII (habilita backends hosted).")
    args = ap.parse_args()

    if not os.path.exists(args.evidencia):
        sys.exit(f"[ERROR] No existe el archivo: {args.evidencia}")

    with open(args.evidencia, "r", encoding="utf-8") as f:
        evidencia = json.load(f)

    try:
        cli = LLMClient.from_env()
    except LLMConfigError as e:
        sys.exit(f"[ERROR de configuración] {e}")

    print("=" * 66)
    print(f"  COPILOTO DE TRIAGE  |  backend: {cli.backend}  |  modelo: {cli.model}")
    tipo = "LOCAL (privado)" if cli.is_local else "HOSTED (los datos salen de tu equipo)"
    print(f"  Modo: {tipo}")
    print("=" * 66)

    # Barrera forense: si el backend es hosted, exige confirmación de dato no sensible
    if not cli.is_local and not args.datos_sinteticos:
        sys.exit(
            "\n[SEGURIDAD] Estás usando un backend HOSTED, pero no confirmaste que la\n"
            "evidencia sea sintética/no sensible. Si es evidencia real o PII, cambia a\n"
            "Ollama (local) en tu .env. Si es dato de laboratorio, repite el comando con\n"
            "  --datos-sinteticos\n"
        )

    prompt = USER_TEMPLATE.format(evidencia=json.dumps(evidencia, ensure_ascii=False, indent=2))
    print("Consultando al modelo... (puede tardar según tu backend/hardware)\n")

    try:
        respuesta = cli.chat(SYSTEM_PROMPT, prompt, allow_remote_data=args.datos_sinteticos)
    except LLMConfigError as e:
        sys.exit(f"[ERROR] {e}")
    except Exception as e:
        sys.exit(
            f"[ERROR] Falló la consulta al backend '{cli.backend}': {e}\n"
            f"Sugerencia: valida con  python scripts/llm_client.py --check"
        )

    print(respuesta)
    print("\n" + "-" * 66)
    print("RECORDATORIO: esto es un COPILOTO. Valida cada técnica y cada acción")
    print("antes de ejecutarla. El LLM puede equivocarse o alucinar detalles.")
    print("-" * 66)


if __name__ == "__main__":
    main()
