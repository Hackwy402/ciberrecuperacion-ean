# Parte 3 · El copiloto de IA escribe la regla — y tú la auditas

**Taller Sesión 3 · Ciber-Recuperación (92-EAN)** · Duración: 25 min

> Ya sabes escribir YARA y Sigma a mano. Ahora el flujo profesional: el LLM
> **local** redacta el borrador desde el informe CTI (en segundos), y tú lo
> **validas con las herramientas** antes de desplegarlo. Copiloto, no piloto.

## 1. Del informe al borrador YARA (LLM local)

El informe CTI puede contener detalles sensibles de la víctima → **modelo
local** (regla datos→backend del curso):

```bash
cd 03-deteccion-variantes-yara-sigma-ia
ollama run llama3.1:8b "Eres analista de deteccion. A partir de este informe CTI, escribe UNA regla YARA que detecte TODAS las variantes de la familia (v3 y v3.1) sin falsos positivos en documentos legitimos que solo mencionen los IOCs. Prioriza los indicadores estables entre variantes. Devuelve solo la regla, sin explicacion: $(cat datasets/caso3/informe-cti-locked3d.md)"
```

Guarda la salida como `reglas/locked3d_ia.yar`. **No la corrijas todavía.**

## 2. Audita el borrador (aquí está el aprendizaje)

Pasa la regla del modelo por el mismo banco de pruebas de la Parte 1:

```bash
yara -r -s reglas/locked3d_ia.yar datasets/caso3/muestras/
```

Revisa con checklist de analista:

| Pregunta | Falla típica del LLM |
|---|---|
| ¿Compila? (`yara` no da error de sintaxis) | modificadores inventados, llaves mal cerradas |
| ¿Caza las **4** variantes (incluida la empacada)? | exige `$magic at 0` con AND: pierde la empacada |
| ¿0 falsos positivos (runbook)? | usa `any of them`: marca el runbook de TI |
| ¿Los strings existen en el informe? | **alucina** IOCs que ningún informe menciona |
| ¿Priorizó mutex/cabecera sobre el dominio? | pesa igual indicadores frágiles y estables |

Anota qué encontró bien y qué corregiste **tú**: esa diferencia es tu valor
como analista.

## 3. Itera con el copiloto (feedback dirigido)

No corrijas a mano: dale al modelo el **resultado de la validación** y pide la
corrección (como harías en un code review):

```bash
ollama run llama3.1:8b "Esta regla YARA tiene un problema: marca como maliciosa la build empacada... no, al reves: NO detecta la build empacada (la cabecera no esta al offset 0) y ademas dispara con un runbook legitimo que solo menciona LEEME_RESCATE.txt. Corrigela: la cabecera al offset 0 debe ser suficiente POR SI SOLA, y si no esta, exige AL MENOS 2 strings. Regla actual: $(cat reglas/locked3d_ia.yar)"
```

Vuelve a validar. Repite hasta que pase el banco completo. Dos o tres
iteraciones dirigidas suelen bastar — **el validador manda, no el modelo**.

## 4. Ahora el borrador Sigma

Mismo flujo para el comportamiento:

```bash
ollama run llama3.1:8b "Escribe una regla Sigma (YAML, logsource process_creation) que detecte el borrado de shadow copies descrito en este informe, SIN marcar el uso legitimo de vssadmin por agentes de backup (list/create). Devuelve solo el YAML: $(cat datasets/caso3/informe-cti-locked3d.md)"
```

Valídala con el mini-motor:

```bash
python3 scripts/cazar_en_logs.py reglas/sigma_ia.yml datasets/caso3/logs/eventos.jsonl
```

¿Dio el hit de `FIN-PC-07` sin tocar a `SRV-BACKUP`? Si usó campos o
modificadores que nuestro mini-motor no soporta, es una conversación
interesante: el LLM conoce el estándar completo — ¿la regla es válida aunque
**tu** herramienta no la ejecute?

## 5. Cierre de la sesión

El pipeline que te llevas:

```
informe CTI ──▶ borrador (LLM local, segundos) ──▶ validación (yara / motor + banco
                                                    de muestras y benignos) ──▶ TÚ
                                                    decides ──▶ despliegue
```

- El LLM aporta **velocidad** (borrador en segundos, recall del estándar).
- El banco de pruebas aporta **verdad** (compila, caza, no da FP).
- Tú aportas **criterio** (jerarquía de IOCs, costo de un FP, decisión final).

Sin los tres, no hay detección confiable. Esta es la base de la Sesión 4:
cuando la detección dispara, la recuperación sale de una **bóveda inmutable**.

> ✅ **Checkpoint Parte 3:** una regla YARA y una Sigma generadas por el
> copiloto, auditadas por ti, iteradas con feedback dirigido y pasando el
> banco de pruebas completo.
