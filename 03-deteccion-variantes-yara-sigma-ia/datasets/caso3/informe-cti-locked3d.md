# Informe CTI · Familia de ransomware **Locked3D** (v3 / v3.1)

> **⚠️ Documento 100% sintético para el lab 92-EAN.** La "familia Locked3D" no
> existe; sus IOCs solo aparecen en las muestras sintéticas de este curso.
> Es el mismo actor del caso de la Sesión 2 (archivos `.locked3d`).

**TLP:CLEAR (sintético) · Fecha: abril 2025 · Fuente: equipo CTI interno (simulado)**

## Resumen ejecutivo

Locked3D es una familia de ransomware observada en pymes de la región. Cifra
documentos y les añade la extensión **`.locked3d`**, deja una nota de rescate
llamada **`LEEME_RESCATE.txt`** en cada carpeta afectada y elimina las copias
shadow de Windows antes de cifrar para impedir la recuperación local. En marzo
se observó la variante **v3.1**, recompilada con otro nombre interno y nueva
infraestructura, que **evade las firmas basadas solo en strings de la v3**.

## Indicadores estáticos (para YARA)

| Indicador | Valor | v3 | v3.1 |
|---|---|---|---|
| Cabecera del binario (offset 0) | hex `4C 33 44 21` (ASCII `L3D!`) | ✔ | ✔ |
| Nombre interno del core | string `L0CK3D-CORE-v3` | ✔ | ✖ (usa `L3D-CORE-v3.1`) |
| Mutex de infección única | string `Global\L3D_MUTEX` | ✔ | ✔ |
| Nombre de la nota de rescate | string `LEEME_RESCATE.txt` | ✔ | variable |
| Dominio de pago (Tor) | string `descifra-tus-archivos.onion` | ✔ | ✖ (rota dominios) |

Notas del analista:

- La **cabecera `L3D!`** y el **mutex** son los indicadores más estables entre
  variantes (cuestan más de cambiar que un string o un dominio).
- Se han visto builds **empacadas** (packer) donde la cabecera no queda al
  offset 0, pero los strings del mutex y la nota siguen visibles en memoria/disco.
- Cuidado con falsos positivos: documentación interna de TI puede **mencionar**
  la nota de rescate o comandos del actor sin ser maliciosa.

## Comportamiento observado (para Sigma · `process_creation`)

Cadena típica post-ejecución (todas las variantes):

1. Documento señuelo (Word) lanza **PowerShell ofuscado** (`-nop -w hidden -enc …`).
2. El payload `l3d_core.exe` corre desde `%TEMP%`.
3. **Anti-recuperación:** `vssadmin delete shadows /all /quiet`
   y `bcdedit /set {default} recoveryenabled No`.
4. **Anti-forense:** limpieza de logs con `wevtutil cl System` / `wevtutil cl Security`.
5. Cifrado masivo y despliegue de la nota de rescate.

Contexto legítimo conocido: los agentes de backup corporativos ejecutan
`vssadmin list shadows` / `vssadmin create shadow` de forma rutinaria — una
regla de comportamiento debe **distinguir borrar de listar/crear**.

## MITRE ATT&CK (referencia)

| Táctica | Técnica |
|---|---|
| Ejecución | T1204.002 (archivo malicioso), T1059.001 (PowerShell) |
| Impacto | T1486 (cifrado), T1490 (inhibir recuperación) |
| Evasión de defensas | T1070.001 (borrar logs de eventos) |
