<!-- =============================================================================================================== -->
<!-- Universitat Politècnica de Catalunya (UPC) -->
<!-- =============================================================================================================== -->

# 🗂️ Explorador de col·leccions

Una base de dades embeddings que pots explorar. Una **col·lecció** és una taula indexada amb
embeddings; aquesta demostració obre un fitxer — **que es guarda permanentment al disc per defecte**, de manera que el teu chunks.
són còn quan tornes – i et permet omplir-lo amb chunks i elements bàsics
metadades, i després cerca-les per significat.

Tot passa per la programació del curs.
[`collections-manager`](../../collections-manager/) funcionalitat (tres funcions:
`create_collection` / `insert` / `query`, a ChromaDB. Aquest és també el propòsit de...
La demostració: **la vostra aplicació interactua amb la capa d'abstracció, no amb el motor.**
sota. Per a projectes de petites a mitjanes dimensions, Chroma és més que suficient – i si...
Si necessites una botiga més robusta, has de canviar les parts internes del programa, no l'aplicació en si.

## Configuració

```bash
cd collections-explorer
uv venv && source .venv/bin/activate && uv sync
```

Còpia `.env.example` a `.env`. L'opció per defecte és la local Ollama – sense clau, sense cost:

```bash
ollama serve
ollama pull nomic-embed-text
```

## Correr

```bash
uv run collections_explorer.py            # persistent collection at ./collections-store
uv run collections_explorer.py --memory   # throwaway in-memory collection
```

| Comanda; ordre | El que fa |
|---|---|
| `/add <text>` | emmagatzemar un chunk (requereix la **font**; el número de **fragment** dins d'aquesta font es assigna automàticament). |
| `/seed` | carregar alguns exemples chunks perquè les consultes es facin immediatament |
| `/list` | tot el contingut de la col·lecció: font · número de fragment · text |
| *(qualsevol altre text)* | **Cerca per significat** – el més proper (chunks), juntament amb la seva similaritat i metadades. |
| (línia buida) | parar; deixar |

## La cosa important a tenir en compte

Afegiu unes quantes chunks, tanqueu-ho i executeu-lo de nou: **són encara allà** – això és el que...
La base de dades és només la meitat de la història. Després, feu una consulta amb paraules que el chunks mai no utilitza ("com ràpid
és un robot de lliurament?"). I observa la superfície correcta (chunk). Aquest és el...
embeddings mig. Insereu el mateix chunk dues vegades i llegiu el missatge "ids són".
`source::chunk_number`, per tant, una col·lecció evita duplicats silenciosos.

## 📖 Llicència

Licensed under [Creative Commons BY-NC-SA 4.0](https://creativecommons.org/licenses/by-nc-sa/4.0/) (`CC BY-NC-SA 4.0`).

## 👤 Autor

[@granludo](https://github.com/granludo) – Marc Alier, Universitat Politècnica de Catalunya (UPC)
