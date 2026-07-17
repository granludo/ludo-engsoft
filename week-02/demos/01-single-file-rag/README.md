# RAG d'un sol fitxer — fer trampes al solitari

El més senzill que encara es pot anomenar RAG: llegeix tot el fitxer de coneixement, enganxa'l
al prompt i xerra-hi. Sense chunking, sense embeddings, sense magatzem vectorial. El model respon
perquè la resposta és allà mateix, dins del seu context window. És un bucle de xat minúscul —una
trentena de línies que pots llegir de dalt a baix.

Això funciona, i per a un corpus prou petit és exactament el que has de fer. La lliçó és on es
trenca: **el fitxer sencer es torna a enviar a cada torn**, de manera que els `prompt_tokens`
creixen amb la mida de la teva base de coneixement, no amb la de la pregunta. Fes unes quantes
preguntes i mira com la línia de `prompt_tokens` va pujant mentre les teves preguntes segueixen sent
curtes. Després fes-ne una que quedi fora del corpus (per exemple, «Qui és el CEO de Tesla?») i mira
com la resposta fonamentada falla amb honestedat: la prova que el model llegeix el context, i no pas
les seves dades d'entrenament.

## Configuració

```bash
cd single-file-rag
uv venv && source .venv/bin/activate && uv sync
```

Copia `.env.example` a `.env`. Els valors per defecte pressuposen un Ollama local (sense clau API,
sense diners, sense internet):

```bash
OPENAI_API_KEY=ollama
MODEL=qwen3:1.7b
OPENAI_ENDPOINT=http://localhost:11434/v1
```

Apunta `OPENAI_ENDPOINT` a qualsevol API compatible amb OpenAI per fer servir un altre proveïdor (i
escriu `MODEL` tal com l'escriu aquell proveïdor).

## Execució

```bash
uv run single_file_rag.py
```

Xerra amb el document; cada torn imprimeix la resposta i el recompte de `prompt_tokens`. El fitxer
sencer va a parar als `prompt_tokens` —a cada torn—, així que el número puja a mesura que avances,
fins i tot quan les teves preguntes són minúscules. Aquest és el preu que paga aquest enfocament, i
la raó per la qual existeix el graó següent (embeddings + recuperació). Línia en blanc per sortir.
