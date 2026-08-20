# Parte 1 · Triage del incidente en Wazuh (SIEM)

**Taller Sesión 5 · Ciber-Recuperación (92-EAN)** · Duración: 25 min
Rol: eres el analista de guardia del SOC. Herramienta: **Wazuh** (por navegador).

> A las 3 a. m. saltaron alertas. El actor **Locked3D** (el mismo de la S3) está
> dentro. Tu trabajo ahora **no** es recuperar todavía: es **entender qué pasó** —
> reconstruir la cadena de ataque (kill chain) y decidir a qué backups apuntó.

## 0. Entra al SOC

Tu docente te dará la **URL del dashboard** y tu **usuario/clave** (read-only):

```
https://<IP-del-SOC>        usuario: alumnoNN     clave: EanSOC2026-xxxx
```

Acepta el certificado autofirmado. Vas a **Threat Hunting → Events** (o *Discover*),
índice `wazuh-alerts-*`. Todo lo que investigas ya está ahí: no modificas nada, solo
consultas — como un analista real con permisos de lectura.

## 1. Encuentra el incidente (5 min)

En la barra de búsqueda (DQL), filtra las alertas del actor:

```
rule.groups: locked3d
```

Deberías ver **10 alertas**. Ordena por tiempo ascendente. Responde en tu bitácora:

- ¿Cuántos **hosts** están afectados? (pista: agrupa por `data.win.system.computer`)
- ¿Cuál es el **paciente cero** (donde empezó) y cuál el **objetivo final**?
- ¿Qué **nivel** tienen las alertas más críticas (`rule.level`)?

## 2. Reconstruye la kill chain (10 min)

Cada alerta es un eslabón. Usando `rule.description`, `rule.mitre.id` y el
`timestamp`, ordena la secuencia del ataque. Complétala en tu bitácora:

| # | Hora | Qué pasó | Técnica MITRE |
|---|---|---|---|
| 1 | 03:05 | Documento señuelo abre… | T1204.002 |
| 2 | | PowerShell ofuscado (`-enc`) | T1059.001 |
| 3 | | Payload desde `%TEMP%` | |
| 4 | | Borrado de shadow copies | **T1490** |
| 5 | | `bcdedit` recuperación deshabilitada | |
| 6 | | Limpieza de logs de eventos | **T1070.001** |
| 7 | | Cifrado de archivos `.locked3d` | **T1486** |
| 8 | | Nota de rescate | |
| 9 | | Conexión a dominio `.onion` | T1071 |

Preguntas de analista:
- ¿Por qué el atacante **borra shadow copies y deshabilita la recuperación ANTES**
  de cifrar? ¿Qué te dice eso sobre su objetivo?
- ¿Por qué **limpia los logs**? ¿Qué intenta impedir (y qué te habría pasado si no
  tuvieras un SIEM que ya los recibió)?

## 3. Sigue el rastro hasta los BACKUPS (10 min)

El actor no fue solo por la estación del usuario. Filtra:

```
rule.groups: locked3d and data.win.system.computer: SRV-DB-01
```

Fíjate en el evento de cifrado sobre `D:\backups\db\...`: **el atacante cifró una
copia de backup en el servidor de base de datos**. Ese es el hilo que sigues en la
Parte 2 (hunting) para responder: **¿qué backup quedó corrupto y cuál sirve para
restaurar?**

Anota los **IOCs** que ves (los usarás en el informe): el proceso `l3d_core.exe`,
la extensión `.locked3d`, la nota `LEEME_RESCATE.txt`, el dominio
`descifra-express.onion`, el usuario y los hosts.

> ✅ **Checkpoint Parte 1:** tienes la kill chain reconstruida con sus técnicas
> MITRE, identificaste paciente cero (FIN-PC-07) y el objetivo (SRV-DB-01 con un
> backup cifrado), y una lista de IOCs. Sigue la Parte 2: **hunting** en el
> endpoint para confirmar qué backup está corrupto.
