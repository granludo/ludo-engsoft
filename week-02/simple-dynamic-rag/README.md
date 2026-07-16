<!-- =============================================================================================================== -->
<!-- Universitat Politècnica de Catalunya (UPC) -->
<!-- =============================================================================================================== -->

# 🔁 Dinàmica senzilla RAG

La solució "trampot", amb una base de dades al darrere. El mateix prompt que...
`single-file-rag` – `{context}` i `{user_input}` – però el context ja no és el mateix.
arxiu complet: és **el K més rellevant chunks recuperat per ordre de significació d'una col·lecció**,
fresc en cada gir. El coneixement pot ser ara de cinquanta documents o d'un miler; cada
Tot i així, la plataforma continua enviant només una quantitat limitada de resultats rellevants chunks.

Dos programes, que corresponen a les dues parts del procés de treball:

## 1. Ingestió — `ingest.py`

La incorporació és el procés pel qual un document entra en una col·lecció, i consta de quatre etapes:

1. **Convertir a Markdown** — [markitdown](https://github.com/microsoft/markitdown)
Gestiona fitxers PDF, .docx, .pptx, .html, .txt… Per a documents escanejats, hauríeu d'utilitzar un…
Model d'OCR en lloc d'això: mistral-ocr a la nuvem, o DeepSeek-ocr que funciona localment.
(MLX a la plataforma Apple Silicon, CUDA a les targetes NVIDIA).
2. **Guarda la versió original i la seva versió resumida (en format Markdown)** en un lloc accessible per a enllaços – aquí
`static/`, la mateixa idea que `/static` en una aplicació FastAPI — per tant, cada chunk pot apuntar.
tornar al seu document a través de URL.
3. **Chunk** El codi Markdown (`chunking.py`, sense estructura específica — chunking és un bucle de repetició):
   - `chars` – una finestra desplaçable: `--size` caràcters amb un margí compartit de `--overlap`.
Per tant, un fragment de text que es divideix en un límit, persisteix intact en una chunk. Funciona amb qualsevol tipus de text.
   - `sections` – Dividir el document segons els seus títols principals (`--level 2` divideix en `##`).
Cada chunk té el seu propi títol; les dimensions varien segons el document.
4. **Insereu** cada chunk juntament amb les seves metadades: `doc_url`, `md_url`, `title`.
   `chunk_number`, `chunking_strategy`, `ingested_at`.

```bash
uv run ingest.py docs/acme-handbook.md --strategy sections
uv run ingest.py somepaper.pdf --strategy chars --size 800 --overlap 100
```

## 2. Consulta — `simple_dynamic_rag.py`

Augmentació dinàmica senzilla: agafar el `{user_input}` i utilitzar-lo **com a consulta**.
consultar la col·lecció; mantenir les K millors chunks en funció de la similitud; format
els (incloent la marca Markdown i l'origen); inserir al model prompt; respondre.

```bash
uv run simple_dynamic_rag.py
```

## Configuració

```bash
cd simple-dynamic-rag
uv venv && source .venv/bin/activate && uv sync
```

Còpia `.env.example` a `.env`. El valor predeterminat és local Ollama – sense clau, sense cost:

```bash
ollama serve
ollama pull qwen3:1.7b
ollama pull nomic-embed-text
```

Construït sobre la funcionalitat [`collections-manager`](../collections-manager/) del curs —
L'aplicació interactua amb la capa d'abstracció, no amb el motor que hi ha sota.

## La cosa important a tenir en compte

Llegeix el manual, i després pregunta: "**Quina és la velocitat de l'robot de entrega?**" – les paraules.
no apareixen a cap chunk, i la part dreta s'afegeix automàticament. Feu-ho amb atenció.
`prompt_tokens` línia: només el vehicle recuperat chunks, encara que sigui gran.
La col·lecció augmenta.

Després, demaneu una recepta de noodles i compareu les similituds. Sorpresa: totalment.
Preguntes no relacionades continuen obtenint una puntuació d'al voltant de 0,40-0,50 en aquest embeddings model, mentre que...
Respones reals que oscilen entre 0,50 i 0,70 — l'interval és relativament estreit, per tant, cal establir un límit.
Es cal calibrar-lo en comparació amb el vostre model i la vostra base de dades, i no capturarà tot.
És per això que la resposta basada únicament en el context (system prompt) és la
segona línia de defensa: fins i tot quan un element relacionat superficialment (chunk) aconsegueix passar,
El programa encara es nega a crear una recepta a partir d'aquestes dades. Augmenteu el valor `THRESHOLD` i observeu què passa.
la porta es tanca – i observeu quan comença a ignorar preguntes legítimes.

## 📖 Llicència

Licensed under [Creative Commons BY-NC-SA 4.0](https://creativecommons.org/licenses/by-nc-sa/4.0/) (`CC BY-NC-SA 4.0`).

## 👤 Autor

[@granludo](https://github.com/granludo) – Marc Alier, Universitat Politècnica de Catalunya (UPC)
