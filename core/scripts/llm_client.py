#!/usr/bin/env python3
"""
llm_client.py — Cliente de LLM agnóstico al backend (Sesión 1+)
Universidad Ean · Ciber-Recuperación (92-EAN)

Un solo código que funciona con:
  - Ollama  (modelo LOCAL, privado, air-gapped)
  - Groq    (API hosted, gratis y muy rápida)
  - OpenRouter (API hosted, modelos :free)
  - cualquier endpoint compatible con OpenAI (custom)

El backend se elige por variables de entorno (.env). Cambiar de "cerebro"
NO requiere tocar el código del análisis: es la palanca de equidad del taller.

Principio forense del curso:
  El TIPO DE DATO decide el backend permitido, no la máquina.
  Evidencia real / PII  -> SOLO backend local (Ollama).
  Datos sintéticos/lab  -> hosted free está bien.
Este cliente avisa si intentas mandar datos a un backend hosted sin confirmar.

Uso como módulo:
    from llm_client import LLMClient
    cli = LLMClient.from_env()
    print(cli.chat("system prompt", "user prompt"))

Uso como CLI de diagnóstico (no envía datos sensibles):
    python scripts/llm_client.py --check
"""
from __future__ import annotations
import json
import os
import sys
import urllib.request
import urllib.error

# Carga .env si python-dotenv está disponible (opcional, no obligatorio)
try:
    from dotenv import load_dotenv  # type: ignore
    load_dotenv()
except Exception:
    pass

# ---- Perfiles de backend: endpoint compatible con OpenAI y modelo por defecto ----
BACKENDS = {
    "ollama": {
        "base_url": "http://localhost:11434/v1",
        "api_key_env": "OLLAMA_API_KEY",     # Ollama no exige key; usa "ollama"
        "default_key": "ollama",
        "default_model": "llama3.1:8b",
        "local": True,
    },
    "groq": {
        "base_url": "https://api.groq.com/openai/v1",
        "api_key_env": "GROQ_API_KEY",
        "default_key": None,
        "default_model": "llama-3.3-70b-versatile",
        "local": False,
    },
    "openrouter": {
        "base_url": "https://openrouter.ai/api/v1",
        "api_key_env": "OPENROUTER_API_KEY",
        "default_key": None,
        "default_model": "meta-llama/llama-3.3-70b-instruct:free",
        "local": False,
    },
    "custom": {
        "base_url": None,     # obligatorio via LLM_BASE_URL
        "api_key_env": "LLM_API_KEY",
        "default_key": "sk-none",
        "default_model": None,  # obligatorio via LLM_MODEL
        "local": False,
    },
}


class LLMConfigError(Exception):
    pass


class LLMClient:
    def __init__(self, backend, base_url, model, api_key, is_local, temperature=0.2):
        self.backend = backend
        self.base_url = base_url.rstrip("/")
        self.model = model
        self.api_key = api_key
        self.is_local = is_local
        self.temperature = temperature

    # ---------------------------------------------------------------
    @classmethod
    def from_env(cls):
        backend = os.environ.get("LLM_BACKEND", "ollama").strip().lower()
        if backend not in BACKENDS:
            raise LLMConfigError(
                f"LLM_BACKEND='{backend}' no válido. Opciones: {', '.join(BACKENDS)}"
            )
        prof = BACKENDS[backend]

        base_url = os.environ.get("LLM_BASE_URL", "") or prof["base_url"]
        if not base_url:
            raise LLMConfigError(
                f"El backend '{backend}' requiere LLM_BASE_URL en el .env."
            )

        model = os.environ.get("LLM_MODEL", "") or prof["default_model"]
        if not model:
            raise LLMConfigError(
                f"El backend '{backend}' requiere LLM_MODEL en el .env."
            )

        # Clave: primero la genérica LLM_API_KEY, luego la específica del backend
        api_key = (
            os.environ.get("LLM_API_KEY")
            or os.environ.get(prof["api_key_env"])
            or prof["default_key"]
        )
        if not prof["local"] and not api_key:
            raise LLMConfigError(
                f"El backend '{backend}' necesita una API key. "
                f"Define {prof['api_key_env']} (o LLM_API_KEY) en el .env."
            )

        temp = float(os.environ.get("LLM_TEMPERATURE", "0.2"))
        return cls(backend, base_url, model, api_key, prof["local"], temp)

    # ---------------------------------------------------------------
    def _post(self, path, payload, timeout=300):
        url = f"{self.base_url}{path}"
        data = json.dumps(payload).encode("utf-8")
        headers = {"Content-Type": "application/json"}
        if self.api_key:
            headers["Authorization"] = f"Bearer {self.api_key}"
        # OpenRouter recomienda estos headers (opcionales)
        if self.backend == "openrouter":
            headers["HTTP-Referer"] = "https://universidadean.edu.co"
            headers["X-Title"] = "EAN 92 Ciber-recuperacion Lab"
        req = urllib.request.Request(url, data=data, headers=headers)
        with urllib.request.urlopen(req, timeout=timeout) as resp:
            return json.loads(resp.read().decode("utf-8"))

    # ---------------------------------------------------------------
    def chat(self, system_prompt, user_prompt, allow_remote_data=False):
        """Envía un turno system+user y devuelve el texto de respuesta.

        allow_remote_data: si el backend NO es local, debes pasar True para
        confirmar explícitamente que el contenido NO es evidencia/PII. Es una
        barrera de seguridad, no un candado: te obliga a pensar antes de enviar.
        """
        if not self.is_local and not allow_remote_data:
            raise LLMConfigError(
                "SEGURIDAD: estás usando un backend hosted ('%s') pero no confirmaste "
                "que el dato es NO sensible. Si es evidencia/PII, usa Ollama (local). "
                "Si es dato sintético/lab, llama chat(..., allow_remote_data=True)."
                % self.backend
            )
        payload = {
            "model": self.model,
            "messages": [
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt},
            ],
            "temperature": self.temperature,
            "stream": False,
        }
        body = self._post("/chat/completions", payload)
        try:
            return body["choices"][0]["message"]["content"].strip()
        except (KeyError, IndexError):
            raise LLMConfigError(f"Respuesta inesperada del backend: {json.dumps(body)[:300]}")

    # ---------------------------------------------------------------
    def check(self):
        """Diagnóstico: valida config y prueba conectividad SIN enviar datos sensibles."""
        print("=" * 60)
        print("  DIAGNÓSTICO DEL CLIENTE LLM")
        print("=" * 60)
        print(f"  Backend        : {self.backend}")
        print(f"  Endpoint       : {self.base_url}")
        print(f"  Modelo         : {self.model}")
        print(f"  Tipo           : {'LOCAL (privado)' if self.is_local else 'HOSTED (datos salen)'}")
        keymask = "(no requiere)" if self.is_local and self.api_key in (None, 'ollama') else \
                  ("*" * 6 + self.api_key[-4:] if self.api_key and len(self.api_key) > 4 else "(definida)")
        print(f"  API key        : {keymask}")
        print("-" * 60)
        try:
            body = self._post(
                "/chat/completions",
                {"model": self.model,
                 "messages": [{"role": "user", "content": "ping"}],
                 "max_tokens": 5, "temperature": 0},
                timeout=60,
            )
            _ = body["choices"][0]["message"]["content"]
            print("  [OK] Conectividad y modelo responden correctamente.")
            if not self.is_local:
                print("  [!]  Recuerda: backend HOSTED. NO envíes evidencia real ni PII.")
            return True
        except urllib.error.HTTPError as e:
            print(f"  [X] HTTP {e.code}: {e.reason}")
            if e.code in (401, 403):
                print("      -> Revisa tu API key en el .env.")
            elif e.code == 404:
                print("      -> El modelo no existe en este backend. Revisa LLM_MODEL.")
            return False
        except urllib.error.URLError as e:
            print(f"  [X] No se pudo contactar el endpoint: {e.reason}")
            if self.is_local:
                print("      -> ¿Está Ollama corriendo?  ollama serve  /  brew services start ollama")
            return False


def main():
    import argparse
    ap = argparse.ArgumentParser(description="Cliente LLM agnóstico (diagnóstico).")
    ap.add_argument("--check", action="store_true", help="Valida config y conectividad.")
    args = ap.parse_args()
    try:
        cli = LLMClient.from_env()
    except LLMConfigError as e:
        sys.exit(f"[ERROR de configuración] {e}")
    if args.check:
        ok = cli.check()
        sys.exit(0 if ok else 1)
    # sin flags: muestra la config resuelta
    cli.check()


if __name__ == "__main__":
    main()
