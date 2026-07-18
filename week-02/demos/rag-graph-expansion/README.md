# Expansió de graf + RRF — recuperar per connexió i, després, fusionar

El quart esglaó de la setmana 2. `rag-context-aware` va arreglar la *consulta*; això arregla un
problema que una consulta perfecta no pot tocar: la pregunta **multi-salt**, on la resposta
és una cadena que travessa diversos documents i el chunk pont no comparteix cap paraula amb la pregunta.

Exemple treballat: *«Què és de ràpid el robot fabricat per l'empresa que va adquirir Acme
Robotics?»* La resposta necessita tres enllaços —Acme → Northwind → Pallet Pup → 2,1 m/s—
i la frase pont (*«Northwind fabrica el Pallet Pup»*) no esmenta ni
«Acme» ni «ràpid». El cosinus la classifica avall, així que el RAG vectorial no la veu mai.

La canonada, en unes 90 línies honestes:

1. **Recuperador vectorial** (Chroma) —la línia de base, ordenada per similitud. No arriba
   al pont.
2. **Recuperador de graf** —extreu les entitats de la pregunta, **recorre el graf**
   un o dos salts sobre relacions tipades (`acquired_by`, `builds`, `has_spec`) i
   recull els chunks on aterres. Això arriba al pont per *connexió*.
3. **Reciprocal Rank Fusion** —`score(id) = Σ weight / (k + rank)` sobre totes dues
   llistes, tornades a ordenar. Cinc línies. `RRF_K=20` i `GRAPH_WEIGHT=0.85` són els valors
   que l'Adrià va triar d'un escombratge de 98 configuracions. El top-K fusionat recupera el pont **sense**
   desplaçar allò que la cerca vectorial ja havia encertat.

### Per què les relacions surten d'un LLM (i no del NER clàssic)

Aquesta demostració ve amb el graf **ja extret** (`TRIPLES`) perquè sigui determinista. En
producció, les relacions s'extreuen en el moment de la ingesta amb un **LLM** de sortida
estructurada, perquè el NER clàssic (spaCy, TF-IDF) et dona *entitats* i, com a molt,
*coocurrència* —«aquestes dues paraules apareixen a prop l'una de l'altra»—, cosa que és semànticament
buida i impossible de curar per a un humà. **El reconeixement d'entitats no és
extracció de relacions.** El cost de l'extracció es paga un sol cop, en la ingesta, no per consulta.

### Manetes

- `TOP_K` — chunks passats al model.
- `RRF_K` — esmorteïment del rang (l'article de RRF fa servir 60; com més baix, més dominen els rangs superiors).
- `GRAPH_WEIGHT` — quant compta la llista del graf. Posa'l a `0.0` i el pont
  torna a caure fora del top-K —aquesta és la demostració que «la fusió és qui fa la feina».

### Executar-ho

```bash
cd week-02/demos/rag-graph-expansion
uv venv && source .venv/bin/activate && uv sync
python rag_graph_expansion.py
```

Necessita un Ollama local que serveixi un model de xat i `nomic-embed-text`
(`ollama pull nomic-embed-text`). Sense clau API, sense diners. Vegeu `.env.example`.

### La lliçó

El graf **mai no degrada** la línia de base i afegeix cobertura **en proporció al grau
multi-salt del teu corpus** —molt en corpus de cadenes d'entitats, gairebé zero en els
generalistes. El cost és una crida addicional a l'LLM per consulta (extracció d'entitats), no el recorregut
del graf en si. Els nombres mesurats darrere de tot això surten del **TFG de l'Adrià Guilera
Bernabé** (FIB-UPC, 2026), que va construir i avaluar una capa de graf sobre el
`kb-server` de LAMB en tres conjunts de dades públics de QA multi-salt. Diagnostica el teu corpus abans de
recórrer-hi.
