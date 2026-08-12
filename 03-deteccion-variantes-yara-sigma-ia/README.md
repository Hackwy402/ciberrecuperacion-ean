# Sesión 3 · Detección de variantes con IA (YARA / Sigma)

De encontrar lo dañado (Sesión 2) a **cazar a la familia responsable**: reglas
**YARA** (estático) y **Sigma** (comportamiento en logs) escritas a mano y luego
generadas por el copiloto de IA local — con validación obligatoria.

Caso: la familia **Locked3D** — el mismo actor de la Sesión 2 (`.locked3d`,
`LEEME_RESCATE.txt`) — saca una variante **v3.1** que evade las firmas de la v3.

## Flujo del taller (dos tiempos)

1. **Setup:** entorno del kit (`../core`); `make check` en verde. Para YARA real:
   `sudo apt install -y yara` (hay fallback en Python si no puedes instalar).
2. **Parte 1 — YARA a mano:** [`parte-1-regla-yara.md`](parte-1-regla-yara.md)
   Del informe CTI a la regla: jerarquía de IOCs, `magic at 0 or 2 of`,
   4 variantes cazadas y la trampa de falso positivo (runbook de TI).
3. **Parte 2 — Sigma en logs:** [`parte-2-regla-sigma.md`](parte-2-regla-sigma.md)
   El comportamiento que el ransomware no puede evitar: `vssadmin delete shadows`
   y `wevtutil cl`, distinguiendo el uso legítimo del agente de backup.
4. **Parte 3 — Copiloto + auditoría:** [`parte-3-copiloto-ia-reglas.md`](parte-3-copiloto-ia-reglas.md)
   El LLM local redacta el borrador desde el CTI; tú lo auditas con el banco de
   pruebas, iteras con feedback dirigido y decides. Copiloto, no piloto.

## Contenido

```
03-deteccion-variantes-yara-sigma-ia/
├── parte-1-regla-yara.md
├── parte-2-regla-sigma.md
├── parte-3-copiloto-ia-reglas.md
├── SOLUCION-docente.md            # (no se publica)
├── scripts/
│   ├── generar_dataset.py         # muestras sintéticas + logs del caso (sin dependencias)
│   ├── buscar_iocs.py             # fallback de YARA: triage por IOCs (sin dependencias)
│   └── cazar_en_logs.py           # mini-motor Sigma sobre JSONL (sin dependencias)
├── datasets/caso3/
│   ├── informe-cti-locked3d.md    # informe CTI sintético (materia prima del lab)
│   ├── muestras/                  # 4 variantes + benignos (generado)
│   └── logs/eventos.jsonl         # 15 eventos process_creation (generado)
└── diapositivas/
```

## Conceptos

Ciclo CTI → detección, anatomía de una regla YARA (strings/hex/condition),
jerarquía de IOCs (pirámide del dolor: mutex/cabecera > strings > dominios),
Sigma como "YARA de los logs" y su conversión multi-SIEM (sigma-cli), falsos
positivos como costo operativo, y generación de reglas con LLM **local** +
validación con herramientas (**el validador manda, no el modelo**).

MITRE ATT&CK del caso: T1204.002, T1059.001, T1486, T1490, T1070.001.

Los datasets son **100% sintéticos**: la familia "Locked3D" no existe y ninguna
muestra es ejecutable ni malware real. Requiere el entorno de `../core` solo
para la Parte 3 (Ollama); los scripts del lab no tienen dependencias.
