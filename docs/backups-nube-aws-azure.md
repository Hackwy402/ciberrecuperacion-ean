# Backups en la nube · AWS y Azure (herramientas nativas)

Cómo llevar el respaldo del curso a la nube con **inmutabilidad (WORM)**, en las dos
nubes que usamos: **AWS** (cuenta del docente) y **Azure** (crédito de los estudiantes).
El análisis de integridad (entropía / scoring) es el mismo tras descargar; solo cambia
el almacenamiento.

## Mapa de equivalencias

| Capacidad | AWS (nativo) | Azure (nativo) |
|---|---|---|
| Almacenar el backup | **Amazon S3** | **Blob Storage** |
| Inmutabilidad WORM | **S3 Object Lock** (Governance / Compliance) | **Blob immutability policy** (time-based / legal hold) |
| Bóveda de backup inmutable | **AWS Backup + Vault Lock** | **Azure Backup + immutable vault** |
| Versionado | **S3 Versioning** | **Blob versioning** |
| Recuperación ante borrado | Versioning + **MFA Delete** | **Soft delete** de blobs/contenedor |
| Subir / bajar por CLI | `aws s3 cp` / `aws s3api` | `az storage blob upload` / `az storage blob download` |
| Medir integridad | *(no hay servicio nativo)* → descargar y correr `extraer_features.py` + `score.py` | *(igual)* |

> No existe un "servicio de entropía" gestionado en ninguna nube: la detección se hace
> con nuestros scripts tras descargar, o en una VM. La nube aporta el **almacenamiento
> inmutable**; el criterio forense lo pones tú.

## AWS — para el docente

```bash
# 1) bucket con Object Lock (requiere versioning; se activa al crear)
aws s3api create-bucket --bucket ean-backup-demo --region us-east-1 \
  --object-lock-enabled-for-bucket

# 2) subir el backup
aws s3 cp 02-analisis-de-integridad-datos/datasets/backup_caso2/ \
  s3://ean-backup-demo/backup_caso2/ --recursive

# 3) proteger una copia como INMUTABLE (WORM) hasta una fecha
aws s3api put-object --bucket ean-backup-demo --key backup_caso2/clientes.csv \
  --body 02-analisis-de-integridad-datos/datasets/backup_caso2/clientes.csv \
  --object-lock-mode COMPLIANCE --object-lock-retain-until-date 2026-08-15T00:00:00Z

# 4) intentar sobrescribir/borrar la copia inmutable -> DENEGADO por Object Lock
aws s3api delete-object --bucket ean-backup-demo --key backup_caso2/clientes.csv
#   => AccessDenied: Object Lock (COMPLIANCE) impide el borrado. Esa es la demo.

# 5) descargar para analizar
aws s3 cp s3://ean-backup-demo/backup_caso2/ ./descarga_aws/ --recursive
```

> **Compliance vs Governance:** en modo *Compliance* ni el root puede borrar antes del
> vencimiento (ideal para la demo anti-ransomware). *Governance* permite excepción con
> permisos especiales.

## Azure — para los estudiantes

```bash
# variables
ACC=eanbackupdemo; RG=ean-rg; CONT=backup-demo

# 1) grupo, cuenta y contenedor (con versioning y soft delete recomendados)
az group create -n $RG -l eastus
az storage account create -n $ACC -g $RG -l eastus --sku Standard_LRS
KEY=$(az storage account keys list -n $ACC -g $RG --query "[0].value" -o tsv)
az storage container create -n $CONT --account-name $ACC --account-key $KEY

# 2) subir el backup
az storage blob upload-batch -d $CONT \
  -s 02-analisis-de-integridad-datos/datasets/backup_caso2 \
  --account-name $ACC --account-key $KEY

# 3) política de inmutabilidad (WORM) time-based sobre el contenedor
az storage container immutability-policy create \
  --account-name $ACC --container-name $CONT \
  --period 7 --account-key $KEY
# (para bloquear definitivamente: az storage container immutability-policy lock ...)

# 4) intentar sobrescribir/borrar dentro del periodo -> DENEGADO por la policy
az storage blob delete -c $CONT -n clientes.csv --account-name $ACC --account-key $KEY
#   => error de inmutabilidad. Esa es la demo.

# 5) descargar para analizar
az storage blob download-batch -s $CONT -d ./descarga_azure \
  --account-name $ACC --account-key $KEY
```

> En Azure algunos pasos de inmutabilidad se ven mejor en el **portal** (Storage
> account → Data protection). El CLI de arriba es la ruta equivalente; confírmalo en
> la consola si tu versión de `az` difiere.

## Cómo correr el taller con dos nubes en paralelo

- **El código es el mismo** en ambas: generar el backup, cifrar una copia con
  `openssl` (corrupción), y analizar con `extraer_features.py` + `score.py`. Eso NO
  depende de la nube.
- **Solo cambia el bloque de almacenamiento inmutable:** el docente lo demuestra en
  **AWS (S3 Object Lock)** y los estudiantes lo replican en **Azure (Blob
  immutability)**. Proyecta ambos lado a lado para que vean que el concepto (WORM)
  es idéntico y el proveedor es intercambiable.
- **La demo clave** en las dos: intentar borrar/sobrescribir la copia inmutable →
  la nube lo **rechaza**. Ahí queda claro por qué la inmutabilidad derrota al ransomware.

## Control de costo (importante)

- Usa una sola región, objetos pequeños (el `backup_caso2` pesa < 1 MB) y **borra todo
  al terminar** (fuera del periodo de inmutabilidad):
  - AWS: `aws s3 rb s3://ean-backup-demo --force` (tras vencer el lock).
  - Azure: `az group delete -n ean-rg --yes`.
- Con objetos tan pequeños, el costo es de **centavos**; el crédito de $100 de Azure
  y la cuenta del docente en AWS lo cubren de sobra.

> Nota: nombres y flags de CLI pueden cambiar; verifica en la documentación oficial de
> AWS/Azure si algún comando difiere en tu versión.
