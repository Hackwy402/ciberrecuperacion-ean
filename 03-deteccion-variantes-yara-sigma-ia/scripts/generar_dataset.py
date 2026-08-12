#!/usr/bin/env python3
"""Genera el dataset sintético de la Sesión 3 (caso Locked3D).

Crea datasets/caso3/ con:
  - muestras/            "binarios" sintéticos: 4 variantes de la familia Locked3D
                         + archivos benignos (incluye una trampa de falso positivo)
  - logs/eventos.jsonl   eventos process_creation simulados (cadena de ataque + ruido normal)

100% sintético: ningún archivo es malware real ni ejecuta nada.
Determinista (semilla fija) para que todo el curso vea lo mismo.
Sin dependencias: solo stdlib.
"""
import json
import random
from pathlib import Path

BASE = Path(__file__).resolve().parent.parent / "datasets" / "caso3"
MUESTRAS = BASE / "muestras"
LOGS = BASE / "logs"

MAGIC = b"L3D!"  # 4C 33 44 21 — cabecera de la familia (ver informe CTI)

rng = random.Random(92)


def cuerpo_aleatorio(n: int) -> bytearray:
    return bytearray(rng.randrange(256) for _ in range(n))


def muestra_binaria(nombre: str, strings: list[bytes], *, magic: bool = True,
                    tamano: int = 4096) -> None:
    """Simula un binario: cabecera opcional + cuerpo pseudoaleatorio con strings incrustados."""
    cuerpo = cuerpo_aleatorio(tamano)
    paso = tamano // (len(strings) + 1)
    for i, s in enumerate(strings, start=1):
        off = i * paso
        cuerpo[off:off + len(s)] = s
    datos = (MAGIC if magic else b"MZ\x90\x00") + bytes(cuerpo)
    (MUESTRAS / nombre).write_bytes(datos)


def archivo_texto(nombre: str, contenido: str) -> None:
    (MUESTRAS / nombre).write_text(contenido, encoding="utf-8")


def generar_muestras() -> None:
    MUESTRAS.mkdir(parents=True, exist_ok=True)

    # --- Familia Locked3D (4 variantes) -------------------------------------
    muestra_binaria("variante_a.bin", [
        b"L0CK3D-CORE-v3",
        b"Global\\L3D_MUTEX",
        b"descifra-tus-archivos.onion",
        b"LEEME_RESCATE.txt",
    ])
    # v3 "recortada": el actor quito el dominio .onion
    muestra_binaria("variante_b.bin", [
        b"L0CK3D-CORE-v3",
        b"Global\\L3D_MUTEX",
        b"LEEME_RESCATE.txt",
    ])
    # v3.1: renombro el core y cambio la infraestructura, conserva magic y mutex
    muestra_binaria("variante_c_v31.bin", [
        b"L3D-CORE-v3.1",
        b"Global\\L3D_MUTEX",
        b"descifra-express.onion",
    ])
    # "empacada": sin la cabecera L3D! al inicio (simula un packer), strings visibles a medias
    muestra_binaria("empacada.bin", [
        b"Global\\L3D_MUTEX",
        b"LEEME_RESCATE.txt",
    ], magic=False, tamano=6144)

    # --- Benignos -------------------------------------------------------------
    muestra_binaria("benigno_util.bin", [
        b"CopyrightUtilidades SA",
        b"config.ini",
        b"error: archivo no encontrado",
    ], magic=False)
    archivo_texto("benigno_notas.txt", (
        "Notas reunion equipo TI - marzo\n"
        "- Renovar certificados del portal\n"
        "- Revisar cuota de OneDrive de contabilidad\n"
        "- Agendar mantenimiento del servidor de impresion\n"
    ))
    # Trampa de falso positivo: documento legitimo que MENCIONA los IOCs
    archivo_texto("runbook_ti.txt", (
        "RUNBOOK TI - Respuesta a ransomware (borrador)\n"
        "Si un usuario reporta archivos renombrados y una nota llamada\n"
        "LEEME_RESCATE.txt en el escritorio, aislar el equipo de la red,\n"
        "NO apagarlo, y avisar al equipo de ciber-recuperacion.\n"
        "Verificar si hay copias shadow disponibles con: vssadmin list shadows\n"
    ))
    archivo_texto("acta_comite.txt", (
        "Acta comite de seguridad - abril\n"
        "Se aprueba el presupuesto para la boveda inmutable de backups\n"
        "y la renovacion de licencias del EDR.\n"
    ))


EVENTOS = [
    # --- Ruido normal de oficina ---------------------------------------------
    {"ts": "2025-04-08T08:02:11", "host": "WS-ANA-01", "user": "ana.perez",
     "ParentImage": "C:\\Windows\\explorer.exe",
     "Image": "C:\\Program Files\\Microsoft Office\\WINWORD.EXE",
     "CommandLine": "WINWORD.EXE /n \"informe_ventas.docx\""},
    {"ts": "2025-04-08T08:15:40", "host": "WS-ANA-01", "user": "ana.perez",
     "ParentImage": "C:\\Windows\\explorer.exe",
     "Image": "C:\\Program Files\\Google\\Chrome\\chrome.exe",
     "CommandLine": "chrome.exe https://intranet.local/portal"},
    {"ts": "2025-04-08T09:01:05", "host": "SRV-BACKUP", "user": "svc_backup",
     "ParentImage": "C:\\Program Files\\BackupPro\\agente.exe",
     "Image": "C:\\Windows\\System32\\vssadmin.exe",
     "CommandLine": "vssadmin list shadows"},
    {"ts": "2025-04-08T09:01:09", "host": "SRV-BACKUP", "user": "svc_backup",
     "ParentImage": "C:\\Program Files\\BackupPro\\agente.exe",
     "Image": "C:\\Windows\\System32\\vssadmin.exe",
     "CommandLine": "vssadmin create shadow /for=C:"},
    {"ts": "2025-04-08T09:30:00", "host": "WS-DEV-03", "user": "carlos.gomez",
     "ParentImage": "C:\\Windows\\explorer.exe",
     "Image": "C:\\Windows\\System32\\wevtutil.exe",
     "CommandLine": "wevtutil qe Application /c:20 /f:text"},
    {"ts": "2025-04-08T10:12:33", "host": "WS-DEV-03", "user": "carlos.gomez",
     "ParentImage": "C:\\Windows\\System32\\cmd.exe",
     "Image": "C:\\Windows\\System32\\ping.exe",
     "CommandLine": "ping -n 4 srv-backup.local"},
    # --- Cadena de ataque en FIN-PC-07 ----------------------------------------
    {"ts": "2025-04-08T11:47:02", "host": "FIN-PC-07", "user": "luis.rojas",
     "ParentImage": "C:\\Windows\\explorer.exe",
     "Image": "C:\\Program Files\\Microsoft Office\\WINWORD.EXE",
     "CommandLine": "WINWORD.EXE /n \"factura_urgente.doc\""},
    {"ts": "2025-04-08T11:47:31", "host": "FIN-PC-07", "user": "luis.rojas",
     "ParentImage": "C:\\Program Files\\Microsoft Office\\WINWORD.EXE",
     "Image": "C:\\Windows\\System32\\WindowsPowerShell\\v1.0\\powershell.exe",
     "CommandLine": "powershell.exe -nop -w hidden -enc SQBFAFgAIAAoAE4AZQB3AC0ATwBiAGoA..."},
    {"ts": "2025-04-08T11:48:10", "host": "FIN-PC-07", "user": "luis.rojas",
     "ParentImage": "C:\\Windows\\System32\\WindowsPowerShell\\v1.0\\powershell.exe",
     "Image": "C:\\Users\\luis.rojas\\AppData\\Local\\Temp\\l3d_core.exe",
     "CommandLine": "l3d_core.exe --instalar"},
    {"ts": "2025-04-08T11:48:44", "host": "FIN-PC-07", "user": "luis.rojas",
     "ParentImage": "C:\\Users\\luis.rojas\\AppData\\Local\\Temp\\l3d_core.exe",
     "Image": "C:\\Windows\\System32\\vssadmin.exe",
     "CommandLine": "vssadmin delete shadows /all /quiet"},
    {"ts": "2025-04-08T11:48:51", "host": "FIN-PC-07", "user": "luis.rojas",
     "ParentImage": "C:\\Users\\luis.rojas\\AppData\\Local\\Temp\\l3d_core.exe",
     "Image": "C:\\Windows\\System32\\bcdedit.exe",
     "CommandLine": "bcdedit /set {default} recoveryenabled No"},
    {"ts": "2025-04-08T11:49:15", "host": "FIN-PC-07", "user": "luis.rojas",
     "ParentImage": "C:\\Users\\luis.rojas\\AppData\\Local\\Temp\\l3d_core.exe",
     "Image": "C:\\Windows\\System32\\wevtutil.exe",
     "CommandLine": "wevtutil cl System"},
    {"ts": "2025-04-08T11:49:18", "host": "FIN-PC-07", "user": "luis.rojas",
     "ParentImage": "C:\\Users\\luis.rojas\\AppData\\Local\\Temp\\l3d_core.exe",
     "Image": "C:\\Windows\\System32\\wevtutil.exe",
     "CommandLine": "wevtutil cl Security"},
    # --- Mas ruido posterior ---------------------------------------------------
    {"ts": "2025-04-08T12:03:22", "host": "WS-ANA-01", "user": "ana.perez",
     "ParentImage": "C:\\Windows\\explorer.exe",
     "Image": "C:\\Windows\\System32\\notepad.exe",
     "CommandLine": "notepad.exe notas.txt"},
    {"ts": "2025-04-08T12:41:57", "host": "SRV-BACKUP", "user": "svc_backup",
     "ParentImage": "C:\\Program Files\\BackupPro\\agente.exe",
     "Image": "C:\\Windows\\System32\\vssadmin.exe",
     "CommandLine": "vssadmin list writers"},
]


def generar_logs() -> None:
    LOGS.mkdir(parents=True, exist_ok=True)
    with (LOGS / "eventos.jsonl").open("w", encoding="utf-8") as f:
        for ev in EVENTOS:
            f.write(json.dumps(ev, ensure_ascii=False) + "\n")


def main() -> None:
    generar_muestras()
    generar_logs()
    n_muestras = len(list(MUESTRAS.iterdir()))
    n_eventos = sum(1 for _ in (LOGS / "eventos.jsonl").open())
    print(f"[ok] {MUESTRAS}  ({n_muestras} archivos)")
    print(f"[ok] {LOGS / 'eventos.jsonl'}  ({n_eventos} eventos)")
    print("Dataset sintetico del caso Locked3D listo. Nada aqui es malware real.")


if __name__ == "__main__":
    main()
