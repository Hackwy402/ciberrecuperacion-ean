#!/usr/bin/env python3
"""
generar_dataset.py — Crea un "backup" sintético para el análisis forense (Sesión 1)
Universidad Ean · Ciber-Recuperación (92-EAN)

Genera una carpeta que simula un respaldo tras un incidente de ransomware,
con archivos limpios, archivos con extensión que no coincide con su contenido,
un archivo cifrado (alta entropía), una nota de rescate y un manifiesto de
hashes "buenos" para verificar integridad.

TODO es sintético: NO es evidencia real. Sirve para practicar el análisis a mano.

Uso:
    python3 generar_dataset.py            # crea ./datasets/backup_caso1
"""
import base64
import hashlib
import os

BASE = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "datasets", "backup_caso1")

# Bytes "aleatorios" deterministas (sin depender de os.urandom) para reproducibilidad
def pseudo_random(n, seed=1337):
    out = bytearray()
    x = seed & 0xFFFFFFFF
    for _ in range(n):
        x = (1103515245 * x + 12345) & 0xFFFFFFFF   # LCG clásico
        out.append((x >> 16) & 0xFF)
    return bytes(out)

def w(path, data, mode="wb"):
    full = os.path.join(BASE, path)
    os.makedirs(os.path.dirname(full), exist_ok=True)
    b = data if isinstance(data, (bytes, bytearray)) else data.encode("utf-8")
    with open(full, "wb") as f:
        f.write(b)

def main():
    os.makedirs(BASE, exist_ok=True)

    # 1) Archivos legítimos ------------------------------------------------
    w("clientes.csv",
      "id,nombre,ciudad,plan\n1,Ana Ruiz,Bogota,oro\n2,Luis Paez,Medellin,plata\n3,Sara Nino,Cali,oro\n")
    w("config.ini",
      "[backup]\nfrecuencia=diaria\nretencion=30\ndestino=/srv/backups\n")
    w("notas_equipo.txt",
      "Recordar validar la integridad del respaldo antes de restaurar.\nUltima prueba de restauracion: hace 6 meses (pendiente repetir).\n")

    # 2) Extensión que NO coincide con el contenido -----------------------
    #    'factura_2024.pdf' que en realidad es una imagen PNG (magic distinto)
    png_1x1 = base64.b64decode(
        "iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAQAAAC1HAwCAAAAC0lEQVR42mNk"
        "+M8AAAMBAQDJ/pLvAAAAAElFTkSuQmCC")
    w("factura_2024.pdf", png_1x1)
    #    'reporte.xlsx' que en realidad es texto plano
    w("reporte.xlsx", "Esto es texto plano, no un Excel real. Ojo con la extension.\n")

    # 3) Archivo CIFRADO (alta entropia) con extensión de ransomware ------
    w("respaldo_db.sql.locked3d", pseudo_random(200000, seed=98765))

    # 4) Nota de rescate --------------------------------------------------
    w("README_RECOVER.txt",
      "!!! TUS ARCHIVOS FUERON CIFRADOS !!!\n"
      "Para recuperarlos escribe a recover@darkmail.onion\n"
      "No apagues el equipo. Tienes 72 horas. -LOCKED3D team\n")

    # 5) Copia 'restaurada' MANIPULADA (para practicar hashing) -----------
    #    igual que clientes.csv pero con una fila alterada -> hash distinto
    w("clientes_restaurado.csv",
      "id,nombre,ciudad,plan\n1,Ana Ruiz,Bogota,oro\n2,Luis Paez,Medellin,ORO\n3,Sara Nino,Cali,oro\n")

    # 6) Manifiesto de hashes "buenos" (de los archivos legitimos) --------
    buenos = ["clientes.csv", "config.ini", "notas_equipo.txt"]
    lines = []
    for name in buenos:
        with open(os.path.join(BASE, name), "rb") as f:
            h = hashlib.sha256(f.read()).hexdigest()
        lines.append(f"{h}  {name}")
    # incluimos el hash "bueno" de clientes.csv para comparar contra el restaurado
    w("hashes-buenos.txt", "\n".join(lines) + "\n", mode="w")

    print("Dataset creado en:", os.path.normpath(BASE))
    for root, _, files in os.walk(BASE):
        for fn in sorted(files):
            p = os.path.join(root, fn)
            print(f"  {os.path.relpath(p, BASE):28s} {os.path.getsize(p):>8d} bytes")

if __name__ == "__main__":
    main()
