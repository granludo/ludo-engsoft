<!-- =============================================================================================================== -->
<!-- Universitat Politècnica de Catalunya (UPC) -->
<!-- =============================================================================================================== -->

# 📚 Explorador d'embeddings i RAG

**La demostració del RAG dinàmic.** Un sol programa ensenya tot el bucle. En arrencar, **ingereix**
`knowledge.txt` —el parteix en chunks amb una finestra lliscant i insereix cada chunk en una
col·lecció mitjançant el [`collections-manager`](../../collections-manager/) del curs
(el gestor n'incrusta i n'indexa cadascun). Després, a cada torn, veus com passa el RAG
dinàmic, panell rere panell:

1. **Què envia la interfície de xat** —els torns pelats, res més.
2. **Recuperació** —el teu missatge esdevé la consulta; la col·lecció retorna els chunks
   més propers amb la seva similitud, i veus quins superen el llindar (**→ injectat**)
   i quins es descarten (**✗ per sota del llindar**).
3. **Què enviem realment a l'LLM** —system + historial + plantilla(missatge, chunks).
4. **La resposta —i què perdura**— la resposta, la factura de tokens, i el fet que
   els chunks ja han desaparegut.

Tot parla amb les tres crides del gestor —`create_collection` / `insert` / `query`—,
la mateixa interfície que l'explorador de col·leccions, l'eina proporcionada
[`simple-dynamic-rag`](../../simple-dynamic-rag/) i el teu projecte final. Aquest és
el sentit d'una capa d'abstracció: aquí ningú parla directament amb el motor de la base de dades.

## Configuració

```bash
cd 05-embeddings-rag-explorer
uv venv && source .venv/bin/activate && uv sync
```

Copia `.env.example` a `.env`. Per defecte és Ollama en local —sense clau, sense cost:

```bash
ollama serve
ollama pull qwen3:1.7b
ollama pull nomic-embed-text
```

## Execució

```bash
uv run embeddings_rag_explorer.py
```

La col·lecció viu **en memòria** i es reconstrueix des de `knowledge.txt` a cada execució,
de manera que cada passada de la demostració comença igual. Configura `PERSIST_PATH` a `.env` si prefereixes conservar-la.

El panell d'introducció **suggereix preguntes per apuntar-hi** —una escala pensada per a la demostració que va
de la «recuperació per significat» (paraules que el text no fa servir mai) a la lliçó del llindar
per a preguntes fora de tema, passant per la procedència entre dominis— i, després de cada resposta, apunta la següent, de manera que
sempre saps què vol mostrar la pregunta següent.

| Comanda | Què fa |
|---|---|
| `/topk N` | quants chunks vols recuperar |
| `/threshold X` | la comporta de similitud —observa com els chunks basculen entre injectat i descartat |
| *(qualsevol text)* | un torn complet, els quatre panells |
| *(línia buida)* | surt |

## El detall que cal observar

Pregunta **«què és de ràpid el robot de repartiment?»** —paraules que el document no fa servir mai— i el
chunk correcte encapçala la taula igualment: la recuperació és per significat. Després pregunta alguna cosa que el
document no cobreix i mira la columna de similitud. Les preguntes sense relació encara puntuen
al voltant de 0,40–0,50 en aquest model d'embeddings, mentre que les respostes reals se situen al voltant de 0,50–0,70 —
la banda és estreta. Juga amb `/threshold`: troba el punt on les preguntes fora de tema no injecten
res mentre les autèntiques encara mengen; puja'l més amunt i observa com les preguntes legítimes també es queden a l'estacada.
La comporta és una decisió de disseny que cal calibrar contra el teu model i el teu corpus
—i el system prompt ancorat és la segona línia de defensa quan alguna cosa s'escola.

## 📖 Llicència

Licensed under [Creative Commons BY-NC-SA 4.0](https://creativecommons.org/licenses/by-nc-sa/4.0/) (`CC BY-NC-SA 4.0`).

## 👤 Autor

[@granludo](https://github.com/granludo) – Marc Alier, Universitat Politècnica de Catalunya (UPC)
