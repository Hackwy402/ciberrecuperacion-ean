#!/usr/bin/env bash
# =====================================================================
#  01-cargar-incidente.sh — Carga las reglas Locked3D e inyecta el
#  incidente en Wazuh (Sesión 5 · 92-EAN). Idempotente.
#
#  Ejecutar EN la EC2 (AMI Wazuh All-In-One), desde despliegue-ec2/:
#      sudo bash scripts/01-cargar-incidente.sh
#
#  Requiere: wazuh-custom/local_rules.xml y dataset/eventos_locked3d.json
#  (en el mismo bundle). Probado en Wazuh 4.14.7 / Amazon Linux 2023.
# =====================================================================
set -euo pipefail
BUNDLE="$(cd "$(dirname "$0")/.." && pwd)"
OSSEC=/var/ossec
LOGDIR="$OSSEC/logs/incidente"

echo "==> Instalando reglas Locked3D"
cp "$BUNDLE/wazuh-custom/local_rules.xml" "$OSSEC/etc/rules/local_rules.xml"
chown wazuh:wazuh "$OSSEC/etc/rules/local_rules.xml"

echo "==> Preparando el log del incidente ($LOGDIR/locked3d.json)"
mkdir -p "$LOGDIR"
: > "$LOGDIR/locked3d.json"          # limpio (evita duplicados en re-ejecución)
chown -R wazuh:wazuh "$LOGDIR"

echo "==> Registrando el localfile en ossec.conf (si falta)"
if ! grep -q "incidente/locked3d.json" "$OSSEC/etc/ossec.conf"; then
  cp "$OSSEC/etc/ossec.conf" "$OSSEC/etc/ossec.conf.bak.$(date +%s 2>/dev/null || echo bak)"
  python3 - "$OSSEC/etc/ossec.conf" <<'PY'
import sys
p=sys.argv[1]; s=open(p).read()
block="""
  <localfile>
    <log_format>json</log_format>
    <location>/var/ossec/logs/incidente/locked3d.json</location>
  </localfile>
"""
open(p,"w").write(s.replace("</ossec_config>", block+"</ossec_config>",1))
print("   localfile insertado")
PY
else
  echo "   localfile ya existía"
fi

echo "==> Reiniciando wazuh-manager"
systemctl restart wazuh-manager
sleep 40

echo "==> Inyectando los eventos del incidente"
cat "$BUNDLE/dataset/eventos_locked3d.json" >> "$LOGDIR/locked3d.json"
sleep 12

N=$(grep -c "Locked3D" "$OSSEC/logs/alerts/alerts.json" 2>/dev/null || echo 0)
echo "==> Listo. Alertas Locked3D en alerts.json: $N"
echo "    Verifícalo en el dashboard: rule.groups: locked3d"
