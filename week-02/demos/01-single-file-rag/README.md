# Joc individual RAG — fer trampa al joc de les cartes

La cosa més senzilla que es pugui considerar RAG: llegir tot el coneixement.
fitxer, copia'l al camp de text i xata amb ell. Sense dividir en fragments, sense vectors d'embedding, sense...
base de dades vectorial. El model respon perquè la resposta està continguda en el seu context.
la finestra. És un petit bucle de conversa – aproximadament trenta línies que es poden llegir d'un sol cop.

Això funciona, i per a un conjunt de dades suficientment petit, simplement hauríeu de fer-ho. La lliçó és:
on es trenca: l'**arxiu complet s'envia de nou en cada ocasió**, per tant `prompt_tokens`
Escala en funció de la mida de la vostra base de coneixement, no de la pregunta. Feu una...
unes preguntes i observa com la línia `prompt_tokens` puja mentre les teves preguntes queden en el mateix punt.
Primer, feu una pregunta sobre un tema conegut ("Qui és el director executiu de Tesla?"). Després, feu una pregunta sobre un tema desconegut i observeu com respon.
resposta concreta que no és honesta — prova que el model està llegint el context, i no les seves pròpies limitacions.
dades per a l'entrenament.

## Configuració

```bash
cd single-file-rag
uv venv && source .venv/bin/activate && uv sync
```

Còpia `.env.example` a `.env`. Els valors per defecte prenen una configuració local Ollama (sense clau API, sense
diners, sense connexió a Internet):

```bash
OPENAI_API_KEY=ollama
MODEL=qwen3:1.7b
OPENAI_ENDPOINT=http://localhost:11434/v1
```

Seleccionar el punt `OPENAI_ENDPOINT` en qualsevol OpenAI compatible amb API per utilitzar un proveïdor diferent.
(i escriu el número `MODEL` tal com ho escriuen els proveïdors).

## Correr

```bash
uv run single_file_rag.py
```

Interactua amb el document; cada resposta s'imprimeix juntament amb el comptador `prompt_tokens`.
Tot el fitxer es guarda a `prompt_tokens` — en cada pas — per tant, el nombre augmenta amb
fins i tot quan les vostres preguntes són petites. Aquest enfocament té el seu preu, i
La raó per la qual existeix l'esgrafa següent (embeddings + recuperació). Línia en blanc per sortir.
