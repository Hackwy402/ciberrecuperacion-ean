# Guion del deck de teoría · Sesión 3 (para armar el PPTX)

> Borrador de contenido por lámina, mismo formato de los decks S1/S2.
> Cuando el PPTX/PDF esté listo, reemplaza este archivo por
> `92-EAN_S03_Teoria.pptx/pdf` + `92-EAN_S03_Guia-Lab.pdf`.

1. **Portada** — Sesión 3 · Detección de variantes con IA (YARA/Sigma). 92-EAN.
2. **Recap S2** — Sabemos QUÉ está dañado (scoring del backup). Pregunta de hoy:
   ¿QUIÉN fue y dónde más está? El actor recompiló: la variante v3.1.
3. **El problema de las variantes** — Un hash detecta UN archivo; una familia
   son cientos de builds. Detección por hash = jugar whack-a-mole.
4. **Pirámide del dolor** — qué le duele cambiar al actor: hash (trivial) →
   dominios → strings → mutex/formato → TTPs/comportamiento (lo más caro).
   Hilo conductor de toda la sesión.
5. **CTI → detección** — el ciclo: informe de inteligencia → extracción de IOCs
   → regla → validación → despliegue → feedback. Hoy lo recorren completo.
6. **YARA: anatomía** — meta / strings (texto, hex, regex) / condition.
   Ejemplo en pantalla: la regla Locked3D del lab (sin la solución completa).
7. **Diseñar la condition = diseñar el costo del error** — `any of` (sensible,
   FP) vs `all of` (rígida, FN) vs `N of` + `at 0` (equilibrio). El runbook de
   TI como trampa.
8. **Sigma: el YARA de los logs** — misma idea, fuente distinta: eventos.
   Anatomía: logsource / detection (selecciones + condition) / level.
9. **Una regla, N SIEMs** — sigma-cli convierte a Splunk/Elastic/Sentinel.
   SigmaHQ: miles de reglas comunitarias. No reinventar: adaptar y validar.
10. **Comportamiento que no pueden evitar** — vssadmin delete shadows, bcdedit,
    wevtutil cl: el ransomware DEBE inhibir la recuperación (T1490) — ahí lo cazas.
    Contexto legítimo (backups) → filtros.
11. **El LLM como redactor de reglas** — velocidad y recall del estándar;
    riesgos: alucinación de IOCs, condiciones flojas. Regla del curso: borrador
    IA + banco de pruebas + criterio humano. El validador manda.
12. **Datos → backend** — informes CTI de la víctima = potencialmente sensibles
    → modelo local (Ollama). Recap de la matriz del curso.
13. **Lab de hoy** — 3 partes: YARA a mano (30') → Sigma (25') → copiloto +
    auditoría (25'). Caso Locked3D v3/v3.1, 100% sintético.
14. **Puente a S4** — detectar no basta: cuando la regla dispara, ¿desde dónde
    restauras con confianza? → bóveda inmutable (WORM) la próxima semana.
