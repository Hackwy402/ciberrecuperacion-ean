# Parte 3 · Corrupción con OpenSSL, entropía forense y backups en la nube

**Taller Sesión 2 · Ciber-Recuperación (92-EAN)** · Extensión práctica (~25 min)

> Aquí **provocamos** la corrupción (como haría un ransomware) y la **medimos**
> con la entropía de Shannon, entendemos por qué los peritos la usan, y llevamos
> el backup **a la nube** con herramientas nativas (AWS para el docente, Azure para
> los estudiantes).

## A. Aplicar corrupción y medirla (OpenSSL + Shannon)

En macOS o Linux (OpenSSL viene de fábrica):

```bash
cd 02-analisis-de-integridad-datos

# opción rápida: script guiado
bash scripts/corromper_demo.sh
```

O paso a paso, para verlo tú mismo:

```bash
# 1) archivo legible -> baja entropía
seq 1 5000 > plano.txt
python3 scripts/entropia.py plano.txt            # ~3.3 bits/byte (texto)

# 2) "corromper" = cifrar (simula ransomware)
openssl enc -aes-256-cbc -pbkdf2 -salt -in plano.txt -out plano.locked -k DemoClave123

# 3) medir de nuevo: la entropía salta a ~8
python3 scripts/entropia.py plano.locked         # ~8.0 bits/byte = CIFRADO
```

**Alternativa con la herramienta `ent`** (opcional, en Mac: `brew install ent`):

```bash
ent plano.txt        # Entropy = ~3.3 bits per byte
ent plano.locked     # Entropy = ~7.99 bits per byte
```

La lección: **la corrupción por cifrado dispara la entropía**. Es exactamente lo que
`extraer_features.py` calcula para todo un backup — aquí lo ves en un archivo.

## B. ¿Los peritos forenses usan la entropía? Sí — y es importante

La entropía de Shannon es una técnica **estándar en forense digital y análisis de
malware**. Se usa para:

- **Detectar cifrado/compresión** dentro de un disco o archivo (ransomware, contenedores como VeraCrypt).
- **Identificar malware empaquetado (packed)**: los packers (UPX y similares) elevan la entropía de las secciones del ejecutable.
- **Localizar volúmenes ocultos y esteganografía** (zonas de alta entropía donde no deberían estar).
- **Carving y triage a escala**: es una señal *basada en contenido* que **no requiere abrir ni parsear** el archivo — ideal para priorizar miles de archivos.

Herramientas reales que la implementan: **`binwalk -E`** (gráfico de entropía),
el módulo **`math.entropy()` de YARA**, utilidades de Didier Stevens, y suites DFIR.
Hay respaldo académico (IEEE Security & Privacy, Lyda & Hamrock, "Using Entropy
Analysis to Find Encrypted and Packed Malware").

**Importancia y límite (esto es criterio forense):** la entropía es una señal
rápida y potente, pero **no un veredicto**: los archivos comprimidos legítimos
(.zip, .jpg) también tienen entropía alta. Por eso la combinamos con **magic
number** y **contexto** — como hace el scoring de la Parte 2. Señal, no sentencia.

## C. Llevar el backup a la nube (preview de la Sesión 4)

Subimos el backup a un almacenamiento **inmutable (WORM)** para que, aunque el
ransomware cifre una copia, la **copia buena no se pueda sobrescribir ni borrar**.
Cada quien usa su nube; el análisis (entropía/scoring) es el mismo tras descargar.

Flujo del ejercicio (idéntico en ambas nubes):

1. Generas el backup (`backup_caso2`).
2. Lo subes a un bucket/contenedor **con inmutabilidad activada**.
3. Simulas ransomware: cifras una copia con `openssl` → la entropía salta.
4. Intentas **sobrescribir la copia inmutable** → la nube lo **bloquea** (WORM).
5. Descargas y corres `extraer_features.py` + `score.py` → detectas lo corrupto y
   recuperas la **copia limpia** protegida.

Los comandos nativos de cada nube (AWS para el docente, Azure para los estudiantes)
están en **`../docs/backups-nube-aws-azure.md`**.

> **La idea que debe quedar clara:** la entropía **detecta** la corrupción; la
> **inmutabilidad** (S3 Object Lock / Azure Blob immutability) **impide** que el
> ransomware destruya la copia buena. Detección + inmutabilidad = recuperación con confianza.

> ✅ **Checkpoint Parte 3:** provocaste corrupción con OpenSSL y viste el salto de
> entropía; puedes explicar el uso forense; y subiste un backup a la nube con
> inmutabilidad, comprobando que la copia protegida no se puede sobrescribir.
