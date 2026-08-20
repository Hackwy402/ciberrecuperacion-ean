# Informe de respuesta a incidente

> Plantilla forense · Sesión 5 · Ciber-Recuperación (92-EAN). Reemplaza el texto en
> _cursiva_. Sé conciso y basa cada afirmación en **evidencia** (hash, captura,
> query, timestamp). Un informe se lee de arriba (para dirección) hacia abajo (para
> el analista que continúa).

---

## 0. Portada / metadatos

| Campo | Valor |
|---|---|
| Analista | _Nombre y dependencia laboral_ |
| Fecha del informe | _AAAA-MM-DD_ |
| Caso / ticket | _ID del caso_ |
| Clasificación (TLP) | _TLP:CLEAR / AMBER / RED_ |
| Sistemas afectados | _p. ej. FIN-PC-07, SRV-DB-01_ |
| Estado | _En curso / Contenido / Recuperado_ |

## 1. Resumen ejecutivo

_3–5 líneas, sin jerga, para dirección. Qué pasó, qué impacto tuvo, si hay copia
limpia para recuperar y cuál es la recomendación principal. Ejemplo: «El actor
Locked3D comprometió FIN-PC-07 vía phishing, inhibió la recuperación y cifró un
backup de la base de datos en SRV-DB-01. Existe una copia limpia verificada del
2026-08-18. Se recomienda restaurar desde ella y no pagar el rescate.»_

## 2. Alcance y método

- **Alcance:** _qué se investigó (hosts, backups, ventana temporal)._
- **Fuentes de evidencia:** _SIEM (Wazuh), DFIR (Velociraptor), consola MinIO._
- **Limitaciones:** _lo que no se pudo determinar y por qué._

## 3. Línea de tiempo (timeline)

_Ordenada, en hora local. Cada fila con su fuente (regla/artefacto)._

| Hora | Evento | Host | Evidencia (regla / artefacto / hash) |
|---|---|---|---|
| _03:05_ | _Documento señuelo abre Word_ | _FIN-PC-07_ | _rule 100213 / …_ |
| _03:05_ | _PowerShell ofuscado (-enc)_ | _FIN-PC-07_ | _rule 100213_ |
| _03:12_ | _vssadmin delete shadows_ | _FIN-PC-07_ | _rule 100210_ |
| _…_ | _…_ | _…_ | _…_ |

## 4. Hipótesis

_Las hipótesis que consideraste y el veredicto. Muestra el razonamiento, no solo la
conclusión._

| # | Hipótesis | Evidencia a favor / en contra | Veredicto |
|---|---|---|---|
| H1 | _El vector inicial fue phishing_ | _Word → PowerShell → payload_ | _Confirmada_ |
| H2 | _Solo se afectó la estación del usuario_ | _cifrado también en SRV-DB-01_ | _Refutada_ |
| H3 | _El backup del 2026-08-19 sirve para restaurar_ | _entropía 8.0 + hit YARA_ | _Refutada (corrupto)_ |

## 5. Hallazgos técnicos

### 5.1 Cadena de ataque (kill chain)
_Descripción paso a paso: acceso inicial → ejecución → anti-recuperación →
anti-forense → impacto → C2._

### 5.2 Indicadores de compromiso (IOCs)
| Tipo | Valor |
|---|---|
| Proceso | _l3d_core.exe_ |
| Extensión de cifrado | _.locked3d_ |
| Nota de rescate | _LEEME_RESCATE.txt_ |
| Dominio C2 | _descifra-express.onion_ |
| Usuario comprometido | _CORP\luis.rojas_ |

### 5.3 Estado de los backups (lo crítico)
| Backup | Hash SHA-256 | Entropía | YARA | Estado |
|---|---|---|---|---|
| _produccion_2026-08-18.bak_ | _…_ | _~5_ | _sin hit_ | **limpio (restaurar de aquí)** |
| _produccion_2026-08-19.bak.locked3d_ | _…_ | _~8.0_ | _hit Locked3D_ | **corrupto / cifrado** |

## 6. Técnicas MITRE ATT&CK

| Táctica | Técnica | ID | Dónde se observó |
|---|---|---|---|
| Ejecución | Archivo malicioso | T1204.002 | _…_ |
| Ejecución | PowerShell | T1059.001 | _…_ |
| Impacto | Inhibir la recuperación | T1490 | _vssadmin / bcdedit_ |
| Evasión | Borrar logs de eventos | T1070.001 | _wevtutil cl_ |
| Impacto | Cifrado para impacto | T1486 | _.locked3d_ |
| C2 | Protocolo de aplicación | T1071 | _.onion_ |

## 7. Impacto

_Datos/servicios afectados, RPO/RTO estimados, si hubo exfiltración, riesgo residual._

## 8. Recomendaciones

- **Recuperación:** _restaurar desde la copia limpia verificada (cuál, de cuándo),
  en entorno aislado, verificando hashes antes de reconectar._
- **Contención / erradicación:** _aislar hosts, rotar credenciales, bloquear IOCs._
- **Monitoreo de backups (blue team):** _qué vigilar de aquí en adelante —
  intentos de borrado sobre la bóveda, cambios de retención, operaciones masivas._
- **Lecciones aprendidas:** _qué falló y qué endurecer (MFA, EDR, segmentación)._

## 9. Anexos

_Capturas del SIEM, salidas de Velociraptor, hashes completos, queries usadas._

---
_Firma:_ _Nombre · dependencia · fecha_
