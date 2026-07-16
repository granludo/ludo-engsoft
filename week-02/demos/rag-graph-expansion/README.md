# Expansió de la grafa + RRF – recuperar per connexió, i després fusionar

El quart pas de la setmana 2. `rag-context-aware` ha solucionat la *consulta*; això soluciona un...
un problema que una consulta perfecta no pot abordar: la pregunta de "múltiples salts", on la resposta
és una cadena que connecta diversos documents, i el pont chunk no té cap relació amb la pregunta.

Exemple pràctic: "Quina velocitat té el robot que ha construït l'empresa que va adquirir Acme?"
"Robòtica?" La resposta necessita tres enllaços: Acme → Northwind → Pallet Pup → 2,1 m/s
— i la frase clau ("Northwind construeix el Pallet Pup") no es refereix a cap de les dues coses.
Ni "Acme" ni "ràpid". La funció cosí el classifica com a baix, per tant, el vector RAG mai no el veu.

La canonada, en aproximadament 90 línies sinceres:

1. **Recuperador de vectors** (Chroma) – és la base, classificada per similitud. Però no cobreix tot.
l'aducte.
2. **Recollidor de grafs** – extraure les entitats de la pregunta, **analitzar el grafe**
una o dues "saltades" a les relacions tipografiades (`acquired_by`, `builds`, `has_spec`) i,
Recolliu les chunks que trobeu. Això es transporta fins al pont mitjançant una *connexió*.
3. **Fusión de rangs recíprocs** — `score(id) = Σ weight / (k + rank)` tant en un com en l'altre
llistes, reordenades. Cinc línies. `RRF_K=20` i `GRAPH_WEIGHT=0.85` són els valors.
Adrià va triar un dels resultats d'una anàlisi amb una configuració de 98. El mètode de recuperació del millor conjunt (top-K) permet obtenir el pont **sense** necessitat de...
eliminant all aquelles funcionalitats que la cerca vectorial ja havia aconseguit.

### Per què les relacions proven d'un LLM (no d'un tipus de reconeixement de noms propers clàssic)?

Aquesta demostració inclou el graf **ja extret** (`TRIPLES`), de manera que és determinista.
La producció: les relacions es extreuen al moment de la ingesta per un **LLM** amb estructura.
resultat, ja que els sistemes de NER clàssics (com spaCy o TF-IDF) et donen les *entitats*, i en el millor dels casos...
*coïncidència* – "aquestes dues paraules apareixen juntes" – cosa que és semànticament
vació i impossible per a un humà gestionar. El reconeixement d'entitats propies no és
extracció de relacions. El cost d'extracció es paga una sola vegada, al moment de la incorporació, no per consulta.

### Manetes

- `TOP_K` — chunks s'han passat al model.
- `RRF_K` – Reducció de la influència del rang (el paper RRF utilitza un valor de 60; valors més baixos signifiquen que els rangs superiors tenen una influència major).
- `GRAPH_WEIGHT` – indica quant elements inclou la llista del graf. Canviar-lo a `0.0` i activar el pont.
tornen a la posició inicial — això és una demostració de com funciona la "fusión".

### Executar-ho

```bash
cd week-02/demos/rag-graph-expansion
uv venv && source .venv/bin/activate && uv sync
python rag_graph_expansion.py
```

Necessita un servei local Ollama que ofereixi un model de xat i `nomic-embed-text`.
(`ollama pull nomic-embed-text`). Sense clau API, sense diners. Veure `.env.example`.

### La lliçó

El gràfic **mai deteriora** la base i afegeix la precisió **en proporció a com**.
el vostre corpus és de tipus "multi-hop" — destaca en la gestió de corpes amb relacions complexes, però és dèbil en la comprensió general.
una vegada. El cost és una crida addicional de LLM per a cada consulta (extracció d'entitats), no el graf.
el mateix procés de travessar. Els valors mesurats que donen suport a tot això proven d'**Adrià Guilera**.
El TFG de Bernabé** (FIB-UPC, 2026), que va construir i avaluar una capa de graf sobre
LAMB `kb-server` sobre tres conjunts de dades públiques per a preguntes i respostes (QA) amb múltiples salts. Diagnostiqueu el vostre corpus abans de...
intentant-ho.
