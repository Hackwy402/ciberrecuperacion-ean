# Parte 2 · El copiloto en crisis + métricas RTO/RPO

**Taller Sesión 5 · Ciber-Recuperación (92-EAN)** · Duración: 25 min

> Simulacro: son las 3 a. m., Locked3D cifró `SRV-DB-01` (el mismo actor de la
> S3). Tú eres quien está de guardia. Usarás el copiloto para conducir la
> recuperación desde la bóveda de la S4 — y luego medirás si lo hiciste bien.

## 1. Conduce el incidente con el copiloto

Haz las preguntas que harías de verdad, en orden. El copiloto responde con el
runbook correcto y citado:

```bash
# ¿Qué hago primero?
python3 scripts/rag_copiloto.py "acabo de detectar ransomware en un host, ¿qué hago primero?"

# ¿De dónde restauro?
python3 scripts/rag_copiloto.py "¿cómo recupero una copia limpia desde la bóveda inmutable?"

# ¿Y la base de datos?
python3 scripts/rag_copiloto.py "¿cómo restauro SRV-DB-01 sin dañar la evidencia?"
```

Cada respuesta debe citar su fuente (`[runbook-aislamiento.md]`,
`[runbook-boveda-worm.md]`, `[runbook-restauracion-db.md]`). Ese rastro es lo que
te permite **auditar** al copiloto: no le crees porque suena bien, sino porque
puedes ver de qué runbook salió cada paso.

## 2. Mide la recuperación: RTO y RPO

Restaurar no basta — hay que saber **cuánto tardaste** (RTO) y **cuánto dato
perdiste** (RPO). El incidente quedó registrado en `datasets/caso5/incidente.json`:

```bash
python3 scripts/metricas_rto_rpo.py
```

Lee la salida:
- **RPO (dato perdido)** = incidente − último backup limpio. Aquí ~3h: lo que se
  trabajó entre el backup nocturno y el cifrado. Backups más frecuentes → RPO menor.
- **RTO (tiempo caído)** = servicio restaurado − incidente. Aquí <3h, dentro del
  objetivo de 4h del runbook.
- El **desglose del RTO** muestra dónde se fue el tiempo: detectar, contener,
  **decidir** y restaurar.

## 3. Interpreta: ¿dónde ayuda el copiloto?

Mira el tramo **"decidir"** (aislamiento → inicio de restauración). Es el tiempo
en que alguien tiene que recordar/buscar el procedimiento correcto. Es justo el
tramo que el copiloto acorta: respuesta inmediata y citada en vez de hojear un
PDF de 40 páginas a las 3 a. m.

Prueba a mover el objetivo y ver cuándo "falla" la métrica:

```bash
python3 scripts/metricas_rto_rpo.py --rto-objetivo 2      # ahora el RTO EXCEDE
echo "exit: $?"                                            # 1 = no cumplió el objetivo
```

Esto conecta con la Sesión 2: el "0" de la regla **3-2-1-1-0** es la verificación
de integridad; RTO/RPO son las métricas que le ponen número a "¿recuperé lo
bastante rápido y reciente?".

> ✅ **Checkpoint Parte 2:** condujiste el incidente con el copiloto citando
> runbooks reales y calculaste RTO (~2.9h) y RPO (~3.2h) del caso, entendiendo qué
> tramo acorta el copiloto. Sigue la Parte 3: alguien intenta **secuestrar** tu
> copiloto.
