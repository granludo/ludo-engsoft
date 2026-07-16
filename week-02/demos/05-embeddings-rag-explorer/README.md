<!-- =============================================================================================================== -->
<!-- Universitat Politècnica de Catalunya (UPC) -->
<!-- =============================================================================================================== -->

# 📚 Embeddings-RAG Explorador

**La demostració del mètode dinàmic-RAG.** Un programa mostra tot el bucle. Al començament, **processa**
`knowledge.txt` — chunks utilitzant una finestra corredora i inserint cada chunk en un...
recolectar-ho a través del curs [`collections-manager`](../../collections-manager/)
(el gestor afegeix i indexa cada un d'ells). Després, en cada tornada, observeu el comportament dinàmic.
RAG succeix, pas a pas:

1. **El que envia la interfície de xat:** només les seqüències bàsiques, res més.
2. **Recuperació** – el vostre missatge es converteix en la consulta; la col·lecció retorna el més proper.
chunks gràcies a la seva similitud, i veieu quins superen el límit (**→ injectat**).
i que es descarten (**✗ per sota del límit**).
3. **El que realment enviem al sistema LLM + historial + plantilla (missatge, chunks)**.
4. **La resposta – i el que perdura** – la resposta, la factura token, i el fet que...
Les chunks ja han desaparegut.

Tot indica les tres crides del responsable: `create_collection` / `insert` / `query`.
la mateixa interfície que la de "collections-explorer", la que s'ha proporcionat.
[`simple-dynamic-rag`](../../simple-dynamic-rag/) e l'eina, i el vostre projecte final. Això és
El propòsit d'una capa d'abstracció: aquí ningú interactua directament amb el motor de la base de dades.

## Configuració

```bash
cd 05-embeddings-rag-explorer
uv venv && source .venv/bin/activate && uv sync
```

Còpia `.env.example` a `.env`. El valor predeterminat és local Ollama – sense clau, sense cost:

```bash
ollama serve
ollama pull qwen3:1.7b
ollama pull nomic-embed-text
```

## Correr

```bash
uv run embeddings_rag_explorer.py
```

La col·lecció existeix **en la memòria**, i es reconstruïx des del principi (`knowledge.txt`) cada vegada que s'executa.
Per tant, cada inici de prova comença de la mateixa manera. Per mantenir-ho així, configureu `PERSIST_PATH` a `.env`.

La primera pantalla **sugereix preguntes per començar**, una guia gradual pensada per a la demostració.
"recuperació per significat" (paraules que el text no utilitza) a través d'una font transdissa
– fins a l'extrem de la temàtica – i després de cada resposta, suggereix la següent, així
Sempre saps què intenta mostrar la pregunta següent.

| Comanda; ordre | El que fa |
|---|---|
| `/topk N` | Quant chunks vols recuperar? |
| `/threshold X` | el mecanisme de similaritat – observeu chunks canviar entre la injecció i la eliminació |
| *(qualsevol text)* | una rotació completa, totes les quatre parts. |
| (línia buida) | parar; deixar |

## La cosa important a tenir en compte

Pregunte "Quina és la velocitat de l'robot de entrega?". – Aquestes paraules no apareixen al document – i així
tot i així, chunk és el primer de la llista: la recuperació es fa per significat. Després, pregunta alguna cosa...
Aquest document no cobreix i no analitza la columna de similaritat. Les preguntes que no estan relacionades continuen tenint una puntuació.
al voltant de 0,40-0,50 en aquest embeddings model, mentre que les respostes reals oscil·len al voltant de 0,50-0,70 —
La banda és estreta. Jugueu amb `/threshold`: trobeu els punts on les preguntes fora de tema interfereixen.
res mentre els autèntics continuen alimentant-se; augmenta-ho i observa com les preguntes reals es veuen privades de recursos.
També. La porta és una decisió de disseny que cal avaluar en funció del vostre model i les vostres necessitats.
conjunt de dades — i la instrucció del sistema fonamental és la segona línia de defensa quan es produeix alguna cosa
escapa sense.

## 📖 Llicència

Licensed under [Creative Commons BY-NC-SA 4.0](https://creativecommons.org/licenses/by-nc-sa/4.0/) (`CC BY-NC-SA 4.0`).

## 👤 Autor

[@granludo](https://github.com/granludo) – Marc Alier, Universitat Politècnica de Catalunya (UPC)
