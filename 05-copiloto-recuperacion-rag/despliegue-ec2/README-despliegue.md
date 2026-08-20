# Despliegue del SOC del curso en AWS EC2 (Sesión 5 · 92-EAN)

> **Documento del docente.** Levanta el entorno que los alumnos investigan por
> navegador: **Wazuh** (SIEM) + **MinIO** (bóveda WORM) en UNA EC2, y
> **Velociraptor** local en la VM de cada alumno. Validado en Wazuh **4.14.7**
> (AMI oficial) sobre Amazon Linux 2023, `t3.xlarge`.

## 0. La arquitectura

```
     EC2 (AMI Wazuh All-In-One, t3.xlarge, amd64)          VM del alumno (16 GB)
   ┌──────────────────────────────────────────┐         ┌────────────────────┐
   │  WAZUH  (SIEM)          MinIO (bóveda WORM)│         │  Velociraptor GUI  │
   │  dashboard :443         API :9000 con :9001│  <────  │  (binario local)   │
   │   ▲ caso Locked3D        │ audit-log       │  hunt   │  hunting del propio│
   │   │ pre-cargado          ▼ (→ Wazuh)        │         │  endpoint          │
   └───┴──────────────────────────────────────┘         └────────────────────┘
       ▲ navegador (read-only)   ▲ navegador (su bucket)
```

Cada alumno recibe (por navegador, sin instalar Wazuh): **cuenta Wazuh** read-only
+ **bucket MinIO** propio con Object Lock. Y en su VM corre **Velociraptor** local
(un binario) para el hunting DFIR.

## 1. Lanza la EC2 (AMI del Marketplace)

- **AMI:** *Wazuh All-In-One Deployment* (Marketplace). **Launch from EC2 Console.**
- **Instancia:** `t3.xlarge` (16 GB). **Disco:** 50 GB gp3. **Elastic IP** (para URL estable).
- **SSH user:** `wazuh-user`. **Clave del dashboard `admin`** = Instance ID con la
  1ª letra en mayúscula (ej. `I-0abc...`). Espera ~5 min tras el lanzamiento.
- **Security Group** (restringe orígenes; nada de `0.0.0.0/0` en producción):
  | Puerto | Servicio | Origen |
  |---|---|---|
  | 443 | Dashboard Wazuh | CIDR alumnos |
  | 9001 / 9000 | MinIO consola / API | CIDR alumnos |
  | 22 | SSH | solo tu IP |

Copia este bundle (`despliegue-ec2/`) a la EC2 (`scp -r` o `git clone`).

## 2. Instala Docker (para MinIO)

```bash
sudo dnf install -y docker
sudo systemctl enable --now docker
sudo mkdir -p /usr/local/lib/docker/cli-plugins
sudo curl -sL "https://github.com/docker/compose/releases/download/v2.29.7/docker-compose-linux-x86_64" \
  -o /usr/local/lib/docker/cli-plugins/docker-compose
sudo chmod +x /usr/local/lib/docker/cli-plugins/docker-compose
```

## 3. Carga el incidente, la bóveda y los alumnos (3 scripts)

Desde `despliegue-ec2/` en la EC2, en orden:

```bash
# 3.1 Reglas Locked3D + inyección del incidente en Wazuh
sudo bash scripts/01-cargar-incidente.sh
#     -> 10 alertas de la kill chain (MITRE) en el dashboard. Filtro: rule.groups: locked3d

# 3.2 MinIO (bóveda WORM) + colector de audit-log conectado a Wazuh
sudo bash scripts/02-minio-boveda.sh
#     -> consola MinIO en :9001. Un borrado en 'boveda' dispara la alerta 100231 en Wazuh

# 3.3 Aprovisionar N alumnos (cuentas Wazuh read-only + buckets MinIO WORM)
export WAZUH_ADMIN_PW='<clave-admin-del-indexer>'    # = Instance ID capitalizado
export EC2_PUBLIC_HOST='<Elastic-IP-o-DNS>'
sudo -E bash scripts/03-crear-alumnos.sh 25
#     -> credenciales_alumnos.csv (una fila por alumno; NO commitear)
```

## 4. Verifica antes de clase

- [ ] Dashboard `https://<IP>` abre; `rule.groups: locked3d` muestra 10 alertas
      (hosts FIN-PC-07 y SRV-DB-01).
- [ ] En MinIO (`:9001`), borrar algo de `boveda` genera la alerta `rule.id: 100231`.
- [ ] Un alumno del CSV entra al dashboard (read-only) y ve el incidente.
- [ ] Un alumno entra a MinIO y ve SOLO su bucket.

## 5. Velociraptor en la VM del alumno (hunting DFIR)

Ver `../velociraptor-alumno/` (script de siembra + arranque). Resumen: descarga el
binario `velociraptor` (arm64/amd64), corre `velociraptor gui`, y hunt sobre su
propio endpoint sembrado con los backups sintéticos (uno cifrado `.locked3d`).

## Seguridad y limpieza

- Cambia la clave por defecto del `admin` (Instance ID) — ver [password management de
  Wazuh](https://documentation.wazuh.com/current/user-manual/user-administration/password-management.html).
- El día de clase, restringe 443/9001 al **CIDR de los alumnos**. Asigna **Elastic IP**.
- `credenciales_alumnos.csv`, `.env` y `data/` están en `.gitignore`.
- Al terminar el curso: `docker compose down -v` en `/opt/soc-minio` y **termina la EC2**.
- Todo es sintético (familia Locked3D del curso). Nada aquí es malware real.

## Qué instala cada script (para auditar)

| Script | Qué hace | Validado |
|---|---|---|
| `01-cargar-incidente.sh` | Copia `local_rules.xml`, añade localfile, reinicia, inyecta 12 eventos → 10 alertas | ✅ |
| `02-minio-boveda.sh` | Levanta MinIO+colector, crea `boveda` WORM, instala `minio_rules.xml`+localfile | ✅ |
| `03-crear-alumnos.sh N` | Rol `alumno_ro`, N usuarios Wazuh read-only, N buckets/usuarios MinIO, CSV | ✅ |
