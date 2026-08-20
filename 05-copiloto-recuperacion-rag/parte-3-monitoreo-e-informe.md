# Parte 3 · Monitorea tu bóveda y entrega el informe

**Taller Sesión 5 · Ciber-Recuperación (92-EAN)** · Duración: 25 min
Herramientas: **MinIO** (tu bóveda) + **Wazuh** (monitoreo), por navegador.

> Ya sabes qué pasó (Parte 1) y cuál backup está corrupto (Parte 2). Ahora cierras
> el ciclo del blue team: **custodiar el backup** — que exista una copia intocable
> y que el SIEM **avise** si alguien la ataca. Y entregas el informe.

## 1. Deposita un backup en tu bóveda (5 min)

Entra a la **consola de MinIO** con tu usuario (del CSV que te dio el docente):

```
https://<IP-del-SOC>:9001     usuario: alumnoNN     clave: EanSOC2026-xxxx
```

Verás **solo tu bucket** (`alumnoNN`) — es tu bóveda con Object Lock (WORM). Sube un
archivo cualquiera como "backup" (botón **Upload**). Fíjate: hereda una **retención
de 30 días** — no se puede borrar antes.

## 2. Simula el ataque y compruébalo en el SIEM (10 min)

Ponte en los zapatos del ransomware: **intenta borrar tu backup** desde la consola
(selecciónalo → Delete). Observa dos cosas:

- **La bóveda resiste:** con Object Lock, el objeto no desaparece de verdad (queda
  protegido por WORM). Actívalo con *"Show deleted objects"* y verás que la versión
  sigue ahí. Igual que la Sesión 4.
- **El SIEM te avisa:** vuelve a Wazuh y filtra:

  ```
  rule.id: 100231 and data.api.bucket: alumnoNN
  ```

  Ahí está tu intento de borrado registrado (nivel 12, MITRE **T1490**), con tu
  `data.accessKey`. **Eso es monitorear un backup**: no basta con que sea inmutable;
  el equipo azul tiene que *enterarse* de que alguien lo atacó.

Pregunta para el informe: ¿por qué la **combinación** importa? (inmutabilidad SIN
monitoreo = no sabes que te atacan; monitoreo SIN inmutabilidad = ves el ataque pero
pierdes el dato). Relaciónalo con la regla **3-2-1-1-0** de la Sesión 4.

## 3. Escribe el informe (10 min)

Usa la plantilla [`PLANTILLA-informe-incidente.md`](PLANTILLA-informe-incidente.md).
Debe quedar registrado, estilo forense:

- **Resumen ejecutivo** (3–5 líneas para dirección).
- **Línea de tiempo** del incidente (de la Parte 1, con horas y técnicas MITRE).
- **Hipótesis** que manejaste y cuál confirmaste con evidencia.
- **Hallazgos técnicos**: kill chain, IOCs, y **qué backup está corrupto vs cuál
  restaurar** (con hash + entropía + hit YARA de la Parte 2).
- **Técnicas MITRE ATT&CK** mapeadas (T1204.002, T1059.001, T1490, T1070.001, T1486, T1071).
- **Recomendaciones de recuperación y de monitoreo** de backups.

## 4. Entrega

Dos opciones (tu docente indica cuál):

- **Subir al repositorio** en la carpeta [`informes/`](informes/), con el nombre
  **`nombre-y-dependencia.md`** (o `.pdf`). Ejemplo: `juan-perez-contabilidad.md`.
  Un informe por persona.
- **Entregar directo al docente** (si no usan el repo).

Lee [`informes/README.md`](informes/README.md) para la convención exacta de nombre.

> ✅ **Checkpoint Parte 3 (fin del lab):** monitoreaste tu propia bóveda (viste el
> ataque rebotar por WORM **y** aparecer como alerta en el SIEM) y entregaste un
> informe forense con la kill chain, el backup corrupto identificado y las técnicas
> MITRE. Cerraste el ciclo: **detectar → investigar → custodiar → recuperar**.
