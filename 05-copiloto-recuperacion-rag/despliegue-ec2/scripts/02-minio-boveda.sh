#!/usr/bin/env bash
# =====================================================================
#  02-minio-boveda.sh — Despliega MinIO (bóveda WORM) + colector de
#  audit-log y lo conecta a Wazuh (Sesión 5 · 92-EAN). Idempotente.
#
#  Ejecutar EN la EC2, desde despliegue-ec2/:
#      sudo bash scripts/02-minio-boveda.sh
#
#  Requiere Docker + compose, y wazuh-custom/minio_rules.xml en el bundle.
#  Credenciales de MinIO desde variables (cámbialas):
#      MINIO_USER (def. labadmin)  MINIO_PASS (def. Boveda-92EAN-2026)
# =====================================================================
set -euo pipefail
BUNDLE="$(cd "$(dirname "$0")/.." && pwd)"
OSSEC=/var/ossec
MINIO_USER="${MINIO_USER:-labadmin}"
MINIO_PASS="${MINIO_PASS:-Boveda-92EAN-2026}"
AUDIT=/var/log/minio-audit
STACK=/opt/soc-minio

echo "==> Preparando el destino del audit-log ($AUDIT)"
mkdir -p "$AUDIT"; touch "$AUDIT/minio-audit.json"; chmod 644 "$AUDIT/minio-audit.json"

echo "==> Generando el stack de MinIO en $STACK"
mkdir -p "$STACK"
cat > "$STACK/collector.py" <<'PY'
import http.server, socketserver
f = open('/salida/minio-audit.json', 'a', buffering=1)
class H(http.server.BaseHTTPRequestHandler):
    def do_POST(self):
        n = int(self.headers.get('Content-Length', 0))
        body = self.rfile.read(n).decode('utf-8', 'replace').strip()
        if body: f.write(body + '\n')
        self.send_response(200); self.end_headers()
    def do_GET(self):
        self.send_response(200); self.end_headers()
    def log_message(self, *a): pass
socketserver.TCPServer(('', 8080), H).serve_forever()
PY
cat > "$STACK/docker-compose.yml" <<YML
services:
  minio:
    image: minio/minio:latest
    container_name: cr-minio
    command: server /data --console-address ":9001"
    environment:
      MINIO_ROOT_USER: "${MINIO_USER}"
      MINIO_ROOT_PASSWORD: "${MINIO_PASS}"
      MINIO_AUDIT_WEBHOOK_ENABLE_wazuh: "on"
      MINIO_AUDIT_WEBHOOK_ENDPOINT_wazuh: "http://audit-collector:8080/audit"
    ports: ["9000:9000", "9001:9001"]
    volumes: ["./data/minio:/data"]
    depends_on: [audit-collector]
    restart: unless-stopped
  audit-collector:
    image: python:3.11-slim
    container_name: cr-audit-collector
    command: ["python3", "/app/collector.py"]
    volumes: ["./collector.py:/app/collector.py:ro", "${AUDIT}:/salida"]
    restart: unless-stopped
YML

echo "==> Levantando MinIO + colector"
( cd "$STACK" && docker compose up -d )
sleep 8

echo "==> Creando la bóveda WORM (bucket 'boveda' con Object Lock COMPLIANCE)"
docker exec cr-minio sh -c "
  mc alias set local http://localhost:9000 '$MINIO_USER' '$MINIO_PASS' >/dev/null 2>&1
  mc mb --with-lock local/boveda 2>/dev/null || true
  mc retention set --default COMPLIANCE 30d local/boveda 2>/dev/null || true
  echo 'backup-nocturno-2026-08-19' | mc pipe local/boveda/produccion_2026-08-19.bak 2>/dev/null || true
  mc ls local/boveda
"

echo "==> Instalando reglas MinIO en Wazuh + localfile del audit-log"
cp "$BUNDLE/wazuh-custom/minio_rules.xml" "$OSSEC/etc/rules/minio_rules.xml"
chown wazuh:wazuh "$OSSEC/etc/rules/minio_rules.xml"
if ! grep -q "minio-audit.json" "$OSSEC/etc/ossec.conf"; then
  python3 - "$OSSEC/etc/ossec.conf" <<'PY'
import sys
p=sys.argv[1]; s=open(p).read()
block="""
  <localfile>
    <log_format>json</log_format>
    <location>/var/log/minio-audit/minio-audit.json</location>
  </localfile>
"""
open(p,"w").write(s.replace("</ossec_config>", block+"</ossec_config>",1))
print("   localfile minio insertado")
PY
else echo "   localfile minio ya existía"; fi

systemctl restart wazuh-manager
sleep 40
echo "==> Listo. MinIO consola: https://<IP>:9001  (usuario $MINIO_USER)"
echo "    Prueba: borra algo en 'boveda' y busca en el dashboard rule.id: 100231"
