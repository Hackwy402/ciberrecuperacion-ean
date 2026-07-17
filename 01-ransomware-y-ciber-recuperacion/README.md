# Sesión 1 · Ransomware y ciber-recuperación

Taller en **dos tiempos**: primero análisis forense **a mano** con comandos, luego
el **copiloto de IA local** sobre tus propios hallazgos.

## Flujo del taller

1. **Setup** (si no lo has hecho): sigue `../core/README.md` y deja `make check` en verde.
2. **Parte 1 — Forense a mano:** [`parte-1-forense-manual.md`](parte-1-forense-manual.md)
   Detectas cifrado, extensión falsa y manipulación **con comandos** (`file`, `sha256sum`, entropía).
3. **Parte 2 — Copiloto IA:** [`parte-2-copiloto-ia.md`](parte-2-copiloto-ia.md)
   Llevas **el modelo a la data** (local) y contrastas la IA con tu análisis manual.

## Contenido

```
01-ransomware-y-ciberrecuperacion/
├── parte-1-forense-manual.md      # análisis con comandos (Warp/Ubuntu)
├── parte-2-copiloto-ia.md         # análisis asistido por IA local
├── SOLUCION-docente.md            # respuestas esperadas (solo docente)
├── scripts/
│   ├── generar_dataset.py         # crea el "backup" sintético del caso
│   └── entropia.py                # entropía de Shannon (detección de cifrado)
└── datasets/
    └── backup_caso1/              # se genera con generar_dataset.py
```

## Objetivo

Que el participante **detecte corrupción de backups y encuentre la copia limpia**
combinando comandos forenses e IA responsable — sin exponer evidencia a modelos públicos.
