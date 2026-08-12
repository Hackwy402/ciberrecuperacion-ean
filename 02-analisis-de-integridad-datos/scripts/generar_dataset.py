#!/usr/bin/env python3
"""
generar_dataset.py — Backup sintético a escala para la Sesión 2
Universidad Ean · Ciber-Recuperación (92-EAN)

Crea una carpeta con ~40 archivos que simulan un respaldo tras un incidente,
mezclando:
  - archivos LIMPIOS (texto/CSV/config)
  - archivos con MAGIC FALSO (extension != contenido real)
  - archivos CIFRADOS por completo (entropia ~8.0)
  - archivos PARCIALMENTE cifrados (cabecera legitima + cuerpo aleatorio)
  - VARIANTES casi duplicadas (para hashing difuso) + una variante troyanizada

TODO es sintetico: NO es evidencia real.
Uso:  python3 generar_dataset.py     # crea ./datasets/backup_caso2
"""
import base64
import os

BASE = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "datasets", "backup_caso2")

def lcg(n, seed):
    out = bytearray(); x = seed & 0xFFFFFFFF
    for _ in range(n):
        x = (1103515245 * x + 12345) & 0xFFFFFFFF
        out.append((x >> 16) & 0xFF)
    return bytes(out)

def w(path, data):
    full = os.path.join(BASE, path)
    os.makedirs(os.path.dirname(full), exist_ok=True)
    b = data if isinstance(data, (bytes, bytearray)) else data.encode("utf-8", "replace")
    with open(full, "wb") as f:
        f.write(b)

PNG = base64.b64decode("iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAQAAAC1HAwCAAAAC0lEQVR42mNk+M8AAAMBAQDJ/pLvAAAAAElFTkSuQmCC")
PDF = b"%PDF-1.4\n1 0 obj<< /Type /Catalog >>endobj\ntrailer<< /Root 1 0 R >>\n%%EOF\n"
ZIP = b"PK\x03\x04" + b"\x00" * 26 + b"PK\x05\x06" + b"\x00" * 18  # zip vacio minimo

def factura(n, extra=""):
    return (f"FACTURA #{n}\nCliente: Empresa {n}\nConcepto: servicios de nube\n"
            f"Subtotal: {1000+n*7}\nIVA: {(1000+n*7)*0.19:.0f}\nTotal: {(1000+n*7)*1.19:.0f}\n{extra}")

def main():
    os.makedirs(BASE, exist_ok=True)

    # ---- 1) LIMPIOS -------------------------------------------------
    w("clientes.csv", "id,nombre,ciudad,plan\n" + "".join(f"{i},Cliente{i},Bogota,oro\n" for i in range(1, 21)))
    w("config_backup.ini", "[backup]\nfrecuencia=diaria\nretencion=30\ndestino=/srv/vault\ncifrado=aes256\n")
    w("politica_recuperacion.txt", "Politica: validar integridad antes de restaurar.\nRPO=24h RTO=4h.\n" * 3)
    w("inventario.csv", "activo,tipo,critico\n" + "".join(f"srv-{i},servidor,{'si' if i%3 else 'no'}\n" for i in range(1, 16)))
    w("manual.pdf", PDF + b"contenido de manual\n")
    w("logo.png", PNG)
    w("respaldo_ok.zip", ZIP)
    for i in range(1, 6):
        w(f"notas/nota_{i}.txt", f"Nota operativa {i}: revisar el job de backup nocturno.\n" * (i + 2))

    # ---- 2) MAGIC FALSO (extension != contenido) --------------------
    w("factura_2024.pdf", PNG)                       # dice PDF, es PNG
    w("reporte_ventas.xlsx", "solo texto plano, no es un excel real\n")   # dice XLSX, es texto
    w("foto_evento.jpg", ZIP)                        # dice JPG, es ZIP
    w("informe.docx", PDF + b"tampoco es un word\n") # dice DOCX, es PDF

    # ---- 3) CIFRADOS COMPLETOS (entropia ~8) ------------------------
    w("nomina.xlsx.locked3d", lcg(180000, 111))
    w("contratos.pdf.locked3d", lcg(160000, 222))
    w("base_datos.sql.crypt", lcg(220000, 333))

    # ---- 4) PARCIALMENTE cifrados (mitad legit + mitad random) -------
    #    ~mitad texto valido y ~mitad aleatorio: entropia POR BLOQUES mixta
    #    (bloques bajos al inicio, ~8 al final -> chunk_ent_std alto)
    csv_limpio = ("id,nombre,ciudad,plan\n" + "".join(f"{i},Cliente{i},Bogota,oro\n" for i in range(1, 3000))).encode()
    w("clientes_parcial.csv", csv_limpio[:70000] + lcg(70000, 444))
    texto_limpio = ("Manual de recuperacion. Validar integridad antes de restaurar.\n" * 2000).encode()
    w("manual_parcial.pdf", PDF + texto_limpio[:70000] + lcg(70000, 555))

    # ---- 5) VARIANTES casi duplicadas (hashing difuso) --------------
    base_txt = factura(1001)
    w("facturas/factura_v1.txt", base_txt)
    w("facturas/factura_v2.txt", base_txt.replace("servicios de nube", "servicios cloud"))       # cambio menor
    w("facturas/factura_v3.txt", base_txt + "Observacion: pago a 30 dias\n")                       # adicion menor
    w("facturas/factura_v4.txt", base_txt.replace("Empresa 1001", "Empresa 1001 S.A.S"))          # cambio menor
    #   variante TROYANIZADA: misma factura + payload basura al final (debe destacar)
    w("facturas/factura_v5_sospechosa.txt", base_txt.encode() + b"\n<<PAYLOAD>>" + lcg(40000, 666))

    # ---- 6) nota de rescate (contexto) ------------------------------
    w("LEEME_RESCATE.txt", "Tus archivos .locked3d y .crypt fueron cifrados. Contacto: pay@lock.onion\n")

    # ---- resumen ----------------------------------------------------
    total = 0
    for root, _, files in os.walk(BASE):
        total += len(files)
    print(f"Dataset creado en: {os.path.normpath(BASE)}  ({total} archivos)")

if __name__ == "__main__":
    main()
