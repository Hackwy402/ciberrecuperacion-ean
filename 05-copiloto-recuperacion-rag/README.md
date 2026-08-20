# Sesión 5 · Investigación de incidente y monitoreo de backups

Sesión de **cierre del módulo**, con enfoque de **equipo azul**: investigar un
ataque de ransomware real, custodiar las copias y responder con un **informe
forense**. Los alumnos entran por navegador a un **Wazuh** (SIEM) con el incidente
pre-cargado, hacen **hunting con Velociraptor** (DFIR) en su propia VM, y
**monitorean su bóveda** (MinIO WORM) viendo el ataque rebotar y alertar en el SIEM.

Caso: la familia **Locked3D** (el mismo actor del curso) comprometió `FIN-PC-07` y
cifró un backup de base de datos en `SRV-DB-01`. ¿Qué pasó, qué copia sirve para
restaurar, y cómo se custodia el backup?

## Flujo del taller

1. **Parte 1 — Triage en Wazuh:** [`parte-1-triage-wazuh.md`](parte-1-triage-wazuh.md)
   Reconstruye la **kill chain** y sus técnicas **MITRE ATT&CK**; identifica paciente
   cero y el backup objetivo.
2. **Parte 2 — Hunting con Velociraptor:** [`parte-2-hunting-velociraptor.md`](parte-2-hunting-velociraptor.md)
   DFIR en el endpoint: identifica el **backup corrupto vs el limpio** con evidencia
   (hash + entropía + YARA).
3. **Parte 3 — Monitoreo + informe:** [`parte-3-monitoreo-e-informe.md`](parte-3-monitoreo-e-informe.md)
   Ataca tu propia bóveda WORM y ve la alerta en el SIEM; entrega el **informe**.

## Entregable

Un **informe de respuesta a incidente** por persona, estilo forense (línea de
tiempo, hipótesis, hallazgos, técnicas MITRE, backup corrupto vs limpio,
recomendaciones). Plantilla: [`PLANTILLA-informe-incidente.md`](PLANTILLA-informe-incidente.md).
Se entrega en [`informes/`](informes/) con el nombre `nombre-y-dependencia.md`
(o `.pdf`) — ver [`informes/README.md`](informes/README.md).

## Contenido

```
05-copiloto-recuperacion-rag/
├── parte-1-triage-wazuh.md            # SIEM: kill chain + MITRE
├── parte-2-hunting-velociraptor.md    # DFIR: backup corrupto vs limpio
├── parte-3-monitoreo-e-informe.md     # WORM + SIEM + entrega del informe
├── PLANTILLA-informe-incidente.md     # plantilla forense del informe
├── SOLUCION-docente.md                # (no se publica) guía de búsqueda y respuesta + rúbrica
├── informes/                          # entregas individuales (nombre-y-dependencia)
├── velociraptor-alumno/               # script de siembra + arranque para la VM del alumno
├── despliegue-ec2/                    # bundle para montar el SOC (Wazuh+MinIO) en AWS
├── anexo-copiloto-rag/                # anexo OPCIONAL: copiloto RAG de apoyo (no evaluado)
├── scripts/                           # scripts del anexo RAG (sin dependencias)
└── diapositivas/                      # deck de teoría + guía de lab (PDF)
```

## Conceptos

Cómo **operan los atacantes** (ransomware como operación por etapas), la
**kill chain** y **MITRE ATT&CK** (T1204.002, T1059.001, **T1490**, **T1070.001**,
**T1486**, T1071), **qué tipos de backup monitorear** (full/incremental, snapshots,
WORM, offline, nube), cómo el **blue team custodia** las copias (3-2-1-1-0,
inmutabilidad, monitoreo SIEM, FIM), y **detección basada en comportamiento** con
Wazuh + hunting DFIR con Velociraptor.

Montaje del SOC (docente): ver [`despliegue-ec2/README-despliegue.md`](despliegue-ec2/README-despliegue.md).
El caso es **100 % sintético** (la familia Locked3D no existe). El anexo RAG es
material de apoyo opcional, no el centro de la sesión.
