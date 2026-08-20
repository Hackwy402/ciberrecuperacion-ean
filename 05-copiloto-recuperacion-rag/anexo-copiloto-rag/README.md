# Anexo opcional · Copiloto de recuperación (RAG local)

> **Material complementario, no evaluado.** El núcleo de la Sesión 5 es la
> **investigación del incidente** (Wazuh + Velociraptor) y el **informe** (ver la
> carpeta principal del módulo). Este anexo muestra cómo un **copiloto RAG local**
> puede ayudar a redactar el informe o consultar runbooks — sin sacar datos de la
> sala. Es una herramienta de apoyo, nunca el centro.

- `parte-1-construir-rag.md` — retriever + grounded vs alucinación.
- `parte-2-crisis-rto-rpo.md` — el copiloto en crisis + métricas RTO/RPO.
- `parte-3-owasp-prompt-injection.md` — seguridad del copiloto (OWASP LLM Top 10).

Los scripts viven en `../scripts/` (`rag_copiloto.py`, `generar_corpus.py`,
`metricas_rto_rpo.py`) y no tienen dependencias más allá de la stdlib + el
`../../core` del curso.
