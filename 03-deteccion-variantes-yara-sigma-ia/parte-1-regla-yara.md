# Parte 1 · Del informe CTI a la regla YARA (a mano)

**Taller Sesión 3 · Ciber-Recuperación (92-EAN)** · Duración: 30 min
Entorno: **Ubuntu** (VM local, Azure o WSL2) desde la terminal.

> En la Sesión 2 encontraste **qué** estaba dañado en el backup. Hoy cazas al
> **responsable y sus variantes**: conviertes un informe de inteligencia (CTI)
> en una regla **YARA** que detecta la familia aunque el actor recompile.

## 0. Genera el dataset del caso e instala YARA

```bash
cd 03-deteccion-variantes-yara-sigma-ia
python3 scripts/generar_dataset.py
sudo apt install -y yara        # motor YARA de línea de comandos
```

> Sin permisos para instalar: usa el fallback `python3 scripts/buscar_iocs.py
> datasets/caso3/muestras` — aplica la misma lógica de la regla del lab.

## 1. Lee el informe como analista (5 min)

Abre [`datasets/caso3/informe-cti-locked3d.md`](datasets/caso3/informe-cti-locked3d.md)
y responde en papel:

- ¿Qué indicadores **sobreviven** de la v3 a la v3.1? ¿Cuáles murieron?
- ¿Cuál es el indicador más **barato de cambiar** para el actor? ¿Y el más caro?
- ¿Qué documento **legítimo** podría contener alguno de estos strings?

Esa jerarquía (mutex y cabecera > strings > dominios) es la que tu regla debe reflejar.

## 2. Escribe la regla

Crea `reglas/locked3d.yar` (carpeta nueva) partiendo de este esqueleto:

```yara
rule Locked3D_familia
{
    meta:
        author = "TU NOMBRE"
        description = "Familia Locked3D v3/v3.1 (lab 92-EAN, muestras sinteticas)"
        reference = "informe-cti-locked3d.md"

    strings:
        $magic = { 4C 33 44 21 }              // cabecera L3D! (hex)
        $core  = "L0CK3D-CORE" ascii          // nombre interno v3
        $mutex = "L3D_MUTEX" ascii
        $nota  = "LEEME_RESCATE.txt" ascii
        // TODO: agrega el dominio .onion del informe

    condition:
        $magic at 0 or 2 of ($core, $mutex, $nota)   // ¿por que no "any of them"?
}
```

Dos decisiones de diseño para discutir **antes** de validar:

1. `$magic at 0` — la cabecera solo cuenta si está **al inicio** (en la build
   empacada no lo está: ¿la regla aún la caza? ¿por qué?).
2. `2 of (...)` en vez de `any of them` — un solo string no es evidencia
   suficiente (pista: piensa en el runbook de TI).

## 3. Valida contra las muestras

```bash
yara -r -s reglas/locked3d.yar datasets/caso3/muestras/
```

Resultado esperado: **4 detecciones** (`variante_a`, `variante_b`,
`variante_c_v31`, `empacada`) y **ningún benigno**. Con `-s` ves *qué* string
disparó en cada una — verifica que la v3.1 cayó por `magic + mutex` aunque
cambió el core y el dominio.

## 4. Prueba de falsos positivos (la parte que separa juniors de seniors)

`runbook_ti.txt` es un documento **legítimo** de TI que menciona la nota de
rescate. Cambia tu condición a `any of them`, vuelve a correr y observa el
falso positivo. Vuelve a `2 of` y confirma que desaparece.

```bash
python3 scripts/buscar_iocs.py datasets/caso3/muestras --min 1   # simula "any of them"
python3 scripts/buscar_iocs.py datasets/caso3/muestras --min 2   # tu regla
```

**Regla de oro:** una firma se valida contra lo malicioso **y** contra lo
benigno. Un FP en producción cuesta credibilidad (y madrugadas del SOC).

> ✅ **Checkpoint Parte 1:** tienes `reglas/locked3d.yar` detectando las 4
> variantes con 0 falsos positivos, y sabes justificar cada decisión de la
> condición. Sigue la Parte 2: del binario al **comportamiento**.
