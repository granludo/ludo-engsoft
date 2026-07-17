<!-- =============================================================================================================== -->
<!-- Universitat Politècnica de Catalunya (UPC) -->
<!-- =============================================================================================================== -->

# 🔁 RAG dinàmic senzill

La trampa del fitxer únic, però amb una base de dades al darrere. La mateixa plantilla de prompt que
`single-file-rag` —`{context}` i `{user_input}`—, però el context ja no és un
fitxer sencer enganxat: són **els K chunks més rellevants recuperats per significat d'una col·lecció**,
frescos a cada torn. El coneixement ara pot ser de cinquanta documents o de mil; cada
pregunta continua enviant només un grapat de chunks rellevants.

Dos programes, que es corresponen amb les dues meitats del flux de treball:

## 1 · Ingesta — `ingest.py`

La ingesta és com un document entra en una col·lecció, en quatre passos:

1. **Convertir a Markdown** — [markitdown](https://github.com/microsoft/markitdown)
   gestiona pdf, docx, pptx, html, txt... Per a documents *escanejats* faries servir un
   model d'OCR: mistral-ocr al núvol, o deepseek-ocr en local
   (mlx en Apple Silicon, CUDA en NVIDIA).
2. **Desar l'original i la seva destil·lació en Markdown** en algun lloc enllaçable —aquí,
   `static/`, la mateixa idea que `/static` en una aplicació FastAPI—, de manera que cada chunk pugui apuntar
   de tornada al seu document per URL.
3. **Trossejar** el Markdown en chunks (`chunking.py`, sense framework —el chunking és un bucle for):
   - `chars` —una finestra lliscant: `--size` caràcters amb un marge compartit d'`--overlap`,
     de manera que un fet partit en un límit sobreviu sencer dins d'un chunk. Funciona amb qualsevol text.
   - `sections` —parteix pels títols del mateix document (`--level 2` talla als `##`).
     Cada chunk porta el seu propi títol; les mides varien segons el document.
4. **Inserir** cada chunk amb les seves metadades: `doc_url`, `md_url`, `title`,
   `chunk_number`, `chunking_strategy`, `ingested_at`.

```bash
uv run ingest.py docs/acme-handbook.md --strategy sections
uv run ingest.py somepaper.pdf --strategy chars --size 800 --overlap 100
```

## 2 · Consulta — `simple_dynamic_rag.py`

Augmentació dinàmica senzilla: agafa el `{user_input}` i fes-lo servir **com a consulta**;
consulta la col·lecció; queda't amb els K chunks que superen **el llindar de similitud**; dona'ls format
(Markdown, amb la procedència inclosa); insereix-los a la plantilla de prompt; respon.

```bash
uv run simple_dynamic_rag.py
```

## Configuració

```bash
cd simple-dynamic-rag
uv venv && source .venv/bin/activate && uv sync
```

Copia `.env.example` a `.env`. Per defecte és Ollama en local —sense clau, sense cost:

```bash
ollama serve
ollama pull qwen3:1.7b
ollama pull nomic-embed-text
```

Construït sobre la utilitat [`collections-manager`](../collections-manager/) del curs —
l'aplicació parla amb la capa d'abstracció, no amb el motor que hi ha a sota.

## El detall que cal observar

Ingereix el manual i, després, pregunta: **«què és de ràpid el robot de repartiment?»** —les paraules
no apareixen en cap chunk, i la secció correcta surt igualment. Fixa't en la línia de
`prompt_tokens`: només els chunks recuperats viatgen amb la pregunta, per molt que creixi
la col·lecció.

Després demana una recepta de fideus i mira les similituds. Sorpresa: preguntes totalment
sense relació encara puntuen al voltant de 0,40–0,50 en aquest model d'embeddings, mentre que les
respostes reals se situen al voltant de 0,50–0,70 —la banda és estreta, de manera que un llindar cal
calibrar-lo contra el *teu* model i el *teu* corpus, i no ho atraparà tot.
Per això el system prompt ancorat («respon només a partir del context») és la
segona línia de defensa: fins i tot quan un chunk amb prou feines relacionat s'escola per la comporta,
el model encara es nega a inventar-se una recepta a partir d'ell. Puja el `THRESHOLD` i observa com es tanca
la comporta —i fixa't en quan comença a deixar sense resposta també les preguntes legítimes.

## 📖 Llicència

Licensed under [Creative Commons BY-NC-SA 4.0](https://creativecommons.org/licenses/by-nc-sa/4.0/) (`CC BY-NC-SA 4.0`).

## 👤 Autor

[@granludo](https://github.com/granludo) – Marc Alier, Universitat Politècnica de Catalunya (UPC)
