#!/usr/bin/env bash
# =====================================================================
#  03-crear-alumnos.sh — Aprovisiona N alumnos (Sesión 5 · 92-EAN):
#    - usuario Wazuh read-only (rol custom 'alumno_ro') para el dashboard
#    - usuario + bucket MinIO con Object Lock (su bóveda propia)
#  Genera credenciales_alumnos.csv (NO commitear).
#
#  Ejecutar EN la EC2, desde despliegue-ec2/:
#      export WAZUH_ADMIN_PW='<clave-admin-del-indexer>'
#      export EC2_PUBLIC_HOST='<Elastic-IP-o-DNS>'
#      sudo -E bash scripts/03-crear-alumnos.sh 25
#
#  Reglas del entorno: la clave NO puede parecerse al usuario (política del
#  indexer) → se genera 'EanSOC2026-<hex>'. MinIO secret-key >= 8 chars.
# =====================================================================
set -euo pipefail
N="${1:?uso: 03-crear-alumnos.sh <N>}"
ADMIN_PW="${WAZUH_ADMIN_PW:?exporta WAZUH_ADMIN_PW (clave admin del indexer)}"
MINIO_USER="${MINIO_USER:-labadmin}"
MINIO_PASS="${MINIO_PASS:-Boveda-92EAN-2026}"
HOST="${EC2_PUBLIC_HOST:-<IP-EC2>}"
B="https://localhost:9200/_plugins/_security/api"
CSV="credenciales_alumnos.csv"

echo "==> Creando/actualizando el rol read-only 'alumno_ro'"
curl -s -k -u "admin:$ADMIN_PW" -XPUT "$B/roles/alumno_ro" -H "Content-Type: application/json" -d '{
  "cluster_permissions":["cluster_composite_ops_ro","cluster:monitor/main","cluster:monitor/health"],
  "index_permissions":[
    {"index_patterns":["wazuh-alerts-*","wazuh-archives-*","wazuh-monitoring-*","wazuh-statistics-*","wazuh-states-*"],
     "allowed_actions":["read","indices:admin/mappings/get","indices:admin/get","indices:monitor/*"]},
    {"index_patterns":[".kibana*",".opensearch-dashboards*"],
     "allowed_actions":["read","indices:admin/mappings/get","indices:data/read/*","indices:admin/get"]}
  ],
  "tenant_permissions":[{"tenant_patterns":["global_tenant"],"allowed_actions":["kibana_all_read"]}]
}' >/dev/null

echo "alumno,clave,wazuh_dashboard,minio_consola,minio_bucket,minio_usuario" > "$CSV"
USERS=""
for i in $(seq -w 1 "$N"); do
  U="alumno$i"
  PW="EanSOC2026-$(openssl rand -hex 2)"

  # --- Wazuh: usuario read-only ---
  curl -s -k -u "admin:$ADMIN_PW" -XPUT "$B/internalusers/$U" \
    -H "Content-Type: application/json" -d "{\"password\":\"$PW\"}" >/dev/null
  USERS="$USERS\"$U\","

  # --- MinIO: bucket WORM + usuario + policy solo-su-bucket ---
  docker exec cr-minio sh -c "
    mc alias set local http://localhost:9000 '$MINIO_USER' '$MINIO_PASS' >/dev/null 2>&1
    mc mb --with-lock local/$U >/dev/null 2>&1 || true
    mc retention set --default COMPLIANCE 30d local/$U >/dev/null 2>&1 || true
    mc admin user add local $U '$PW' >/dev/null 2>&1
    printf '%s' '{\"Version\":\"2012-10-17\",\"Statement\":[{\"Effect\":\"Allow\",\"Action\":[\"s3:*\"],\"Resource\":[\"arn:aws:s3:::$U\",\"arn:aws:s3:::$U/*\"]}]}' > /tmp/pol-$U.json
    mc admin policy create local pol-$U /tmp/pol-$U.json >/dev/null 2>&1 || true
    mc admin policy attach local pol-$U --user $U >/dev/null 2>&1 || true
  "

  echo "$U,$PW,https://$HOST,http://$HOST:9001,$U,$U" >> "$CSV"
  echo "   + $U"
done

# --- mapear TODOS los alumnos al rol de una vez ---
USERS="[${USERS%,}]"
curl -s -k -u "admin:$ADMIN_PW" -XPUT "$B/rolesmapping/alumno_ro" \
  -H "Content-Type: application/json" -d "{\"users\":$USERS}" >/dev/null

echo "==> Listo. $N alumnos creados. Credenciales en: $CSV"
echo "    Cada alumno: dashboard Wazuh (read-only) + su bucket WORM en MinIO."
echo "    Reparte una fila del CSV a cada uno. NO subas el CSV al repo."
