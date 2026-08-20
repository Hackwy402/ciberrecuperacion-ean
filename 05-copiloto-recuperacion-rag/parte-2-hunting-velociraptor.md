# Parte 2 · Hunting DFIR con Velociraptor

**Taller Sesión 5 · Ciber-Recuperación (92-EAN)** · Duración: 25 min
Herramienta: **Velociraptor** (local, en TU VM Ubuntu). Es DFIR real.

> El SIEM (Parte 1) te dijo que el atacante cifró un backup en `SRV-DB-01`. Ahora
> bajas al endpoint y lo confirmas con evidencia: **¿qué backup quedó corrupto y
> cuál sirve para restaurar?** No adivinas: lo pruebas con hash, entropía y YARA.

## 0. Prepara y arranca Velociraptor

En tu VM, desde la carpeta del lab:

```bash
bash velociraptor-alumno/preparar-velociraptor.sh
```

El script descarga Velociraptor, **siembra los backups del caso** en
`~/backups-lab/` y arranca la GUI. Abre **https://127.0.0.1:8889** (usuario
`admin`, clave `password`; acepta el certificado autofirmado).

En `~/backups-lab/` tienes el "servidor de backups" a investigar:
- `produccion_2026-08-18.bak` — copia de la noche anterior.
- `produccion_2026-08-19.bak.locked3d` — copia de la noche del incidente.
- `LEEME_RESCATE.txt` — apareció junto a los backups.
- `reglas/locked3d.yar` — la regla YARA de la Sesión 3.

## 1. Inventaría y hashea los backups (10 min)

En la GUI, ve a tu cliente (localhost) → **Collect Artifact** →
`Generic.Collectors.File`. Como *glob* usa:

```
/home/*/backups-lab/**
```

Marca el cálculo de **hash (SHA-256)**. Al terminar, revisa los resultados:
- ¿Qué archivos hay? ¿Cuál tiene una extensión sospechosa?
- Anota el **SHA-256** de cada backup (lo pones en el informe como evidencia).

## 2. Distingue el backup corrupto del limpio (10 min)

Dos señales objetivas de que un archivo está **cifrado** (no solo "raro"):

**(a) Entropía.** Un backup normal (texto/SQL) tiene entropía baja (~5); uno
cifrado se acerca a **8.0** (máxima aleatoriedad). Es exactamente el análisis de la
**Sesión 2**. Compruébalo (en una terminal, o con un artefacto de Velociraptor):

```bash
python3 - <<'PY'
import math,glob,os
from collections import Counter
for f in sorted(glob.glob(os.path.expanduser("~/backups-lab/*.bak*"))):
    b=open(f,'rb').read(); c=Counter(b); n=len(b)
    e=-sum((v/n)*math.log2(v/n) for v in c.values())
    print(f"{os.path.basename(f):<38} entropía={e:.2f} {'** CIFRADO **' if e>7.5 else 'limpio'}")
PY
```

**(b) YARA.** Confirma que es la **familia Locked3D** (no un archivo cualquiera).
En la GUI usa `Generic.Detection.Yara.Glob` con la regla `~/backups-lab/reglas/locked3d.yar`
y el glob `/home/*/backups-lab/**`. El `.locked3d` debe **dar hit** (cabecera `L3D!`
+ mutex); el `.bak` limpio, no.

Conclusión que debes poder defender con evidencia:
- **Corrupto:** `produccion_2026-08-19.bak.locked3d` (entropía ~8.0 + hit YARA Locked3D).
- **Limpio y restaurable:** `produccion_2026-08-18.bak` (entropía baja, sin hit).

## 3. Recolecta el resto de la evidencia (5 min)

Para el informe, recolecta también:
- La **nota de rescate** (`LEEME_RESCATE.txt`) — contenido y hash.
- El **momento** en que apareció el `.locked3d` (timestamp del archivo) — cruza con
  la línea de tiempo del SIEM (Parte 1).
- Opcional: `Generic.Collectors.File` sobre `/tmp` o `%TEMP%` buscando el
  `l3d_core.exe` de la kill chain.

> ✅ **Checkpoint Parte 2:** identificaste con **evidencia** (hash + entropía +
> YARA) cuál backup está corrupto y cuál sirve para restaurar, y confirmaste que es
> la familia Locked3D. Sigue la Parte 3: **monitorea tu bóveda** y **entrega el
> informe**.
