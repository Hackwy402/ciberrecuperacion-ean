# Parte 1 · Análisis forense a mano (comandos)

**Taller Sesión 1 · Ciber-Recuperación (92-EAN)**
Entorno: **Ubuntu** (VM local, WSL2 o droplet) desde la terminal (ideal: **Warp**).
Duración sugerida: 30 min.

> **Por qué primero a mano.** Antes de pedirle nada a un modelo, el analista tiene
> que saber mirar la evidencia con sus propias herramientas. La IA acelera; no
> reemplaza el criterio. Aquí detectamos corrupción y cifrado **con comandos**;
> en la Parte 2 usamos el modelo como copiloto sobre *nuestros* hallazgos.

## 0. Preparar el dataset

Descarga el repo y genera el "backup" sintético del caso (no es evidencia real):

```bash
cd 01-ransomware-y-ciber-recuperacion
python3 scripts/generar_dataset.py
cd datasets/backup_caso1
ls -la
```

Verás varios archivos de un respaldo, incluida una **nota de rescate**. Tu misión:
decir **qué archivos están sanos, cuáles fueron manipulados o cifrados, y si hay
una copia limpia** para recuperar.

> **Ayuda del agente de Warp (OZ):** puedes pedirle que te explique o recuerde un
> comando ("¿cómo veo el tipo real de un archivo?"). Úsalo para aprender los
> comandos — pero **la conclusión forense la sacas tú**.

## 1. Tipo real vs. extensión (magic number)

La extensión miente; el contenido no. `file` lee los *magic bytes*:

```bash
file *
```

Observa: `factura_2024.pdf` **no es un PDF** (es una imagen PNG) y `reporte.xlsx`
**no es un Excel** (es texto plano). Extensión ≠ contenido: primera señal de manipulación.

Míralo tú mismo en los primeros bytes:

```bash
xxd factura_2024.pdf | head -2      # verás la firma PNG:  .PNG........
head -c 16 reporte.xlsx | xxd       # texto, no la firma de un .xlsx (PK..)
```

## 2. Integridad con hashing (¿me cambiaron un archivo?)

El respaldo trae un manifiesto de hashes "buenos". Compara:

```bash
sha256sum clientes.csv clientes_restaurado.csv
cat hashes-buenos.txt
```

El `clientes.csv` coincide con su hash bueno; el `clientes_restaurado.csv` **no**
coincide con ninguno: fue alterado. Así se detecta manipulación sin abrir el archivo.
Para verificar todo un manifiesto de una vez:

```bash
sha256sum -c hashes-buenos.txt      # dice OK / FAILED por archivo
```

## 3. Entropía (¿está cifrado?)

El cifrado deja los bytes casi aleatorios (entropía ~8.0). Mídelo:

```bash
python3 ../../scripts/entropia.py *
```

`respaldo_db.sql.locked3d` marca **~8.0 → CIFRADO**; el resto ronda 4-5 (texto).
La entropía alta + la extensión `.locked3d` = archivo secuestrado por ransomware.

> Alternativa con herramienta dedicada (opcional): `sudo apt install ent && ent respaldo_db.sql.locked3d`

## 4. Contexto: nota de rescate y tiempos

```bash
cat README_RECOVER.txt              # la nota del atacante (IOC: contacto, alias)
strings README_RECOVER.txt          # extraer texto legible de cualquier archivo
stat respaldo_db.sql.locked3d       # fechas: ventana de modificación masiva
```

La nota confirma el actor (`LOCKED3D`) y el vector de extorsión. `stat` ayuda a
ubicar **cuándo** ocurrió el cifrado (útil para hallar la última copia limpia).

## 5. Tu conclusión (antes de la IA)

Responde con lo que hallaste, en tus palabras:

1. ¿Qué archivos están **cifrados**? (pista: entropía + extensión)
2. ¿Qué archivos tienen **extensión falsa**? (pista: `file`)
3. ¿Qué archivo fue **manipulado** según los hashes?
4. ¿Cuál copia usarías para **recuperar** y por qué?
5. ¿Qué IOCs sacaste de la nota de rescate?

Guarda tus hallazgos en un archivo de texto — lo usaremos en la Parte 2:

```bash
nano hallazgos.txt
```

> **Checkpoint Parte 1:** identificaste el archivo cifrado (entropía ~8), los dos
> con extensión falsa, el archivo manipulado (hash distinto) y los IOCs de la nota,
> **usando solo comandos**. Ya piensas como investigador; ahora sumamos el copiloto.
