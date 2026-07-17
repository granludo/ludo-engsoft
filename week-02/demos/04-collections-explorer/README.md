<!-- =============================================================================================================== -->
<!-- Universitat Politècnica de Catalunya (UPC) -->
<!-- =============================================================================================================== -->

# 🗂️ Explorador de col·leccions

Una base de dades d'embeddings que pots remenar. Una **col·lecció** és una taula indexada amb
embeddings; aquesta demostració n'obre una —**persistent al disc per defecte**, de manera que els teus chunks
segueixen allà quan hi tornes— i et deixa omplir-la de chunks i metadades bàsiques,
per després cercar-hi per significat.

Tot passa per la utilitat
[`collections-manager`](../../collections-manager/) del curs (tres funcions:
`create_collection` / `insert` / `query`, sobre ChromaDB). I aquest és justament el sentit de
la demostració: **la teva aplicació parla amb la capa d'abstracció, no amb el motor
que hi ha a sota.** Per a projectes petits o mitjans, Chroma en té de sobres —i si
algun dia necessites un magatzem més robust, canvies les entranyes de la capa, no la teva aplicació.

## Configuració

```bash
cd collections-explorer
uv venv && source .venv/bin/activate && uv sync
```

Copia `.env.example` a `.env`. Per defecte és Ollama en local —sense clau, sense cost:

```bash
ollama serve
ollama pull nomic-embed-text
```

## Execució

```bash
uv run collections_explorer.py            # persistent collection at ./collections-store
uv run collections_explorer.py --memory   # throwaway in-memory collection
```

| Comanda | Què fa |
|---|---|
| `/add <text>` | desa un chunk (et demana la **source**; el **chunk_number** dins d'aquesta source s'assigna automàticament) |
| `/seed` | carrega uns quants chunks d'exemple perquè les consultes retornin resultats de seguida |
| `/list` | tot el contingut de la col·lecció: source · chunk_number · text |
| *(qualsevol altre text)* | **consulta per significat** —els chunks més propers, amb la seva similitud i metadades |
| *(línia buida)* | surt |

## El detall que cal observar

Afegeix uns quants chunks, surt i torna-la a executar: **encara hi són** —aquesta és la
meitat de la història que aporta la base de dades. Després consulta amb paraules que els chunks no fan servir mai («què és de ràpid
el robot de repartiment?») i observa com el chunk correcte surt igualment a la superfície —aquesta és la
meitat que aporten els embeddings. Insereix el mateix chunk dues vegades i llegeix el missatge d'error: els ids són
`source::chunk_number`, de manera que una col·lecció refusa els duplicats silenciosos.

## 📖 Llicència

Licensed under [Creative Commons BY-NC-SA 4.0](https://creativecommons.org/licenses/by-nc-sa/4.0/) (`CC BY-NC-SA 4.0`).

## 👤 Autor

[@granludo](https://github.com/granludo) – Marc Alier, Universitat Politècnica de Catalunya (UPC)
