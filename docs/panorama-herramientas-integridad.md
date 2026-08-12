# Panorama de herramientas de integridad de backups (mercado, nube y nuestro lab)

Documento de referencia para el seminario **92-EAN**. Aclara **qué hace la industria**,
**qué hacemos nosotros** con software libre, **qué formatos** aplican en cada caso, y
**qué ofrecen AWS y Azure de forma nativa** (incluidas bases de datos como RDS y Azure SQL).
El objetivo es que no haya confusiones entre lo comercial, lo nativo de nube y el ejercicio del curso.

## 1. Mercado vs. lo que haremos en los talleres

| Capacidad | Herramienta del mercado | Cómo lo hacen | Qué hacemos nosotros (open source) | Sesión |
|---|---|---|---|---|
| **Detección de cifrado/corrupción en el CONTENIDO del backup** | **CyberSense** (Index Engines; motor de **Dell PowerProtect Cyber Recovery**) | Análisis **byte a byte**, **200+ estadísticos** (entropía, similitud, cabecera, cifrado parcial) + **ML** (7.500+ variantes, 120 M muestras) | Entropía global y por bloques + magic + hashing difuso + **IsolationForest** (`extraer_features.py` + `score.py`) | **1–2** |
| **Detección de anomalías en snapshots** | **Rubrik** (Anomaly/Radar), **Cohesity** (DataHawk) | ML sobre metadatos y contenido | Scoring de anomalías con **scikit-learn** | **2** |
| **Detección de variantes/familias** | Motores de firmas + ML (los "7.500 variantes") | Firmas + heurística + ML | Reglas **YARA/Sigma** generadas con LLM y validadas con `yara`/`sigma-cli` | **3** |
| **Bóveda inmutable / aislada** | **Dell PowerProtect Cyber Recovery** (vault aislado) | Vault air-gapped + WORM | **MinIO Object Lock**, `restic`/Borg, ZFS, **AIDE/Wazuh** | **4** |
| **Recuperación validada + forense** | Orquestación del producto | Restauración automatizada + reportes | **RAG** + **Velociraptor** + **TheHive** + métricas RTO/RPO | **5** |
| **Integridad por hash / FIM** | **Tripwire** (histórico), Veeam (verificación) | Hashes baseline / test-restore | `sha256sum` + **AIDE/Wazuh** | **1, 4** |

> **Idea central para los asistentes:** cada taller construye, con software libre y criterio
> humano, **una pieza de lo que un producto comercial hace en caja negra**. No competimos con
> CyberSense; **entendemos y replicamos su capacidad** para poder auditarla y no depender de licencias.

## 2. Qué formatos aplican en estos casos de uso (para no confundir)

| Categoría | Formatos / artefactos típicos |
|---|---|
| **Datos que se analizan** | Archivos sueltos; imágenes de disco/VM (**VMDK, VHD/VHDX, RAW**); **snapshots**; objetos de **S3/Blob**; **dumps de base de datos** (`.bak` de SQL Server, `.sql`, snapshots de RDS/Azure SQL) |
| **Reglas e inteligencia (CTI)** | **YARA** (`.yar`), **Sigma** (YAML), **CTI/STIX** (JSON) |
| **Salidas del análisis** | **CSV/JSON** (features, scores), **hashes SHA-256** (manifiestos de integridad), reportes |
| **Inmutabilidad (WORM)** | **S3 Object Lock** (modos *Governance*/*Compliance*), **Azure Blob immutability** (retención temporal / *legal hold*), **AWS Backup Vault Lock**, **Azure immutable vault** |

> Nota: la entropía y el magic number se calculan sobre **bytes**, así que aplican a
> *cualquier* formato (por eso funcionan igual en un `.docx`, un dump `.bak` o un objeto de S3).
> Las reglas YARA/Sigma trabajan sobre contenido y sobre logs, respectivamente.

## 3. ¿AWS y Azure tienen herramientas de este calibre? (incluye RDS y Azure SQL)

Sí y no — hay que separar tres capacidades:

| Capacidad | AWS (nativo) | Azure (nativo) |
|---|---|---|
| **Backup gestionado de BD** | RDS/Aurora: backups automáticos, snapshots, **PITR** | Azure SQL DB / Managed Instance: backups automáticos, **PITR**, **LTR** |
| **Inmutabilidad del backup (WORM)** | **AWS Backup Vault Lock** (+ *logically air-gapped vault*); **S3 Object Lock** | **Backup immutability automática para Azure SQL** (2026); **Azure Backup immutable vault** |
| **Detección de amenazas a nivel de ACTIVIDAD** | **GuardDuty RDS Protection** (accesos/consultas anómalas) | **Microsoft Defender for SQL** (acceso anómalo, inyección, fuerza bruta) |
| **Escaneo de MALWARE sobre backups** | **GuardDuty Malware Protection for AWS Backup** (incluye backups continuos de S3) — por **firmas** | **Defender for Cloud + Azure Backup**: alerta operaciones sospechosas (borrado masivo, desactivar soft-delete) |
| **Análisis de INTEGRIDAD de contenido (entropía / cifrado parcial, tipo CyberSense)** | **No nativo** → terceros (CyberSense, Elastio, Rubrik) **o hazlo tú** | **No nativo** → terceros **o hazlo tú** |

### La conclusión que evita la confusión

- Para una **base de datos** (RDS o Azure SQL) **sí** tienes, de fábrica: backups con
  **PITR**, **inmutabilidad (WORM)** y **detección de amenazas a nivel de actividad**
  (GuardDuty / Defender for SQL). Con eso proteges *el acceso* y *la copia*.
- Lo que **NO** te dan de forma nativa es el **análisis de integridad del contenido del
  backup** (¿los datos dentro del respaldo están cifrados/corruptos por ransomware?, con
  entropía, cifrado parcial, similitud). Ese es exactamente el nicho de **CyberSense /
  Elastio / Rubrik**… y **lo que replicamos en el laboratorio** con entropía + scoring.
- Por eso la arquitectura recomendada es **combinar**: inmutabilidad nativa de la nube
  (Vault Lock / immutable vault) **+** una capa de **análisis de integridad** (comercial
  o, como aquí, open source) **+** detección de amenazas (GuardDuty / Defender).

> En breve: la nube te da la **bóveda** y la **alarma de la puerta**; el **análisis de si el
> contenido del respaldo está sano** lo pones tú (o un tercero). El curso te enseña a ponerlo.

---

*Fuentes: Index Engines (CyberSense), AWS (Backup Vault Lock, GuardDuty Malware Protection for
Backup, GuardDuty RDS Protection), Microsoft (Azure SQL backup immutability, Defender for SQL,
Azure Backup threat detection). Nombres y features pueden cambiar; verificar en la documentación oficial.*
