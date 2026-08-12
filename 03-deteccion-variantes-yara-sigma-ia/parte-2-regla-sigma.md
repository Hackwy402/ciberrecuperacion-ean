# Parte 2 · Sigma: detectar el comportamiento en los logs

**Taller Sesión 3 · Ciber-Recuperación (92-EAN)** · Duración: 25 min

> La firma estática muere cuando el actor recompila. El **comportamiento**
> (borrar shadow copies, limpiar logs) es mucho más caro de cambiar: es lo que
> el ransomware **tiene** que hacer. Eso se caza con **Sigma** sobre los logs.

## 1. Conoce los eventos

El dataset trae 15 eventos `process_creation` simulados (formato JSONL, campos
al estilo Sysmon):

```bash
cd 03-deteccion-variantes-yara-sigma-ia
head -3 datasets/caso3/logs/eventos.jsonl | python3 -m json.tool
grep -c vssadmin datasets/caso3/logs/eventos.jsonl     # ¿cuántos usan vssadmin?
```

Fíjate: hay **cinco** eventos con `vssadmin`, pero solo **uno** es malicioso.
El agente de backup (`svc_backup` en `SRV-BACKUP`) lo usa legítimamente todos
los días. Tu regla tiene que distinguirlos.

## 2. Escribe la regla Sigma

Crea `reglas/vssadmin_delete_shadows.yml`:

```yaml
title: Borrado de shadow copies (vssadmin delete shadows)
status: experimental
description: Anti-recuperacion tipica de ransomware (MITRE T1490)
logsource:
  category: process_creation
  product: windows
detection:
  seleccion:
    Image|endswith: '\vssadmin.exe'
    CommandLine|contains|all:
      - 'delete'
      - 'shadows'
  condition: seleccion
level: high
```

La clave está en `contains|all`: no basta con que corra `vssadmin.exe`
(eso lo hace el backup); tiene que ser **delete + shadows** en el mismo comando.

## 3. Caza en los logs

```bash
python3 scripts/cazar_en_logs.py reglas/vssadmin_delete_shadows.yml datasets/caso3/logs/eventos.jsonl
```

Esperado: **1 hit** — `FIN-PC-07`, usuario `luis.rojas`,
`vssadmin delete shadows /all /quiet`. Cero hits en `SRV-BACKUP` (que ejecuta
`list`/`create`, no `delete`).

Ahora **rompe la regla a propósito**: quita el bloque `CommandLine|contains|all`
y vuelve a correr. ¿Cuántos hits? ¿Cuáles son falsos positivos? Es el mismo
principio de la Parte 1 (`any of` vs `2 of`), ahora en comportamiento.

## 4. Ejercicio: tu segunda regla

El informe CTI lista otro comportamiento de la cadena: **limpieza de logs**
con `wevtutil cl` (anti-forense, T1070.001). Escribe
`reglas/wevtutil_limpieza.yml` tú solo y valídala.

- Esperado: **2 hits** en `FIN-PC-07` (`cl System` y `cl Security`).
- Trampa: `WS-DEV-03` usa `wevtutil qe` (consultar) — legítimo. Tu selección
  debe exigir el subcomando `cl`, no solo el binario.

## 5. Sigma en el mundo real (referencia)

Nuestro script es un mini-motor didáctico. En producción, la misma regla `.yml`
se **convierte** al lenguaje de tu SIEM con [sigma-cli](https://github.com/SigmaHQ/sigma-cli):

```bash
pip install sigma-cli pysigma-backend-splunk   # opcional, no lo necesitas para el lab
sigma convert -t splunk reglas/vssadmin_delete_shadows.yml
```

Una regla, N plataformas (Splunk, Elastic, Sentinel…) — por eso Sigma es "el
YARA de los logs". El repositorio comunitario [SigmaHQ](https://github.com/SigmaHQ/sigma)
trae miles de reglas listas; compara la tuya con
`rules/windows/process_creation/proc_creation_win_vssadmin_delete_shadow_copies.yml`.

> ✅ **Checkpoint Parte 2:** dos reglas Sigma funcionando (shadow copies +
> wevtutil) con los hits correctos y sin marcar al backup legítimo. Sigue la
> Parte 3: que el copiloto de IA escriba el borrador — y tú lo audites.
