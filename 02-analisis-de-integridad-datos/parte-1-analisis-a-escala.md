# Parte 1 · Análisis de integridad a escala (comandos)

**Taller Sesión 2 · Ciber-Recuperación (92-EAN)** · Duración: 30 min
Entorno: **Ubuntu** (VM local, Azure o WSL2) desde la terminal.

> En la Sesión 1 revisaste 8 archivos a mano. Un backup real tiene **miles**.
> Aquí automatizamos las mismas señales forenses para puntuar el respaldo entero
> y saber **dónde mirar primero** — el paso previo a la recuperación con integridad.

## 0. Genera el backup del caso (a escala)

```bash
cd 02-analisis-de-integridad-datos
python3 scripts/generar_dataset.py
cd datasets/backup_caso2
ls -R | wc -l         # ¿cuántas entradas? demasiadas para mirar una por una
```

## 1. Confirma el concepto en UN archivo (a mano)

Antes de automatizar, mira el **cifrado parcial** — cabecera legítima, cuerpo cifrado:

```bash
head -c 120 manual_parcial.pdf           # se ve texto/PDF legible
tail -c 120 manual_parcial.pdf | od -c   # bytes aleatorios (cifrado) al final
# (od es universal; si tienes xxd, tail -c 120 manual_parcial.pdf | xxd sirve igual)
```

Ese contraste (inicio legible, final aleatorio) es la firma del **cifrado parcial**:
la entropía *global* no basta, hay que mirarla **por bloques**.

## 2. Extrae las señales de TODO el backup

```bash
python3 ../../scripts/extraer_features.py . -o features.csv
```

Genera `features.csv` con, por cada archivo:

| Señal | Qué detecta |
|---|---|
| `entropy` | cifrado total (~8.0) |
| `chunk_ent_std`, `chunk_ent_min/max` | cifrado **parcial** (bloques mixtos) |
| `magic_mismatch` | extensión que no coincide con el contenido |
| `printable_ratio` | binario vs. texto |
| `max_similarity` | casi-duplicados / variantes (hashing difuso) |

Ábrelo y ordénalo por entropía para ver los sospechosos:

```bash
column -s, -t features.csv | sort -k3 -r | head -12
```

## 3. Interpreta las señales (como investigador)

- **Entropía ~8 y `chunk_ent_std` ~0** → cifrado **total** (`.locked3d`, `.crypt`).
- **`chunk_ent_std` alto (bloques mixtos)** → cifrado **parcial** (`*_parcial.*`).
- **`magic_mismatch = 1`** → extensión falsa (`factura_2024.pdf` es PNG, etc.).
- **`max_similarity` alto entre varios** → variantes casi duplicadas (`facturas/*`).

## 4. Hashing difuso: agrupar variantes

Las cinco `facturas/factura_v*.txt` son casi iguales, salvo una con carga añadida.
El `max_similarity` alto las agrupa; la que **rompe** el grupo es la sospechosa.

```bash
grep factura features.csv | column -s, -t
```

> El **agente de Warp (OZ)** te ayuda a recordar comandos (`column`, `sort`, `xxd`),
> pero la lectura de las señales la haces tú.

> ✅ **Checkpoint Parte 1:** tienes `features.csv` y sabes leer, por columnas, qué
> archivos están cifrados (total/parcial), cuáles tienen extensión falsa y cuáles
> son variantes. Sigue la Parte 2 para puntuarlos automáticamente.
