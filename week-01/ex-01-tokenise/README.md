# Setmana 1 · Exercici 1 — Tokenize, local

Carrega un tokenizer amb la biblioteca Hugging Face `transformers` i comptar manualment les tokens. Veure què realment veu el model. Mesurar la penalització per a múltiples idiomes. Comparar dues tokenizer famílies amb entrades relacionades amb codi.

## Executar-ho

```bash
uv venv && source .venv/bin/activate
uv sync
python ex_01_tokenise.py
```

La primera execució descarrega dues petites tokenizers de Hugging Face (unes centenars de KB cadascuna). No hi ha pesos del model, tampoc GPU ni la clau API.

## Què podeu modificar

- `PARAGRAPH_EN` / `PARAGRAPH_MINE` a la part superior de `ex_01_tokenise.py` — substitueix `PARAGRAPH_MINE` per la teva pròpia llengua per calcular la penalització multilingüe *per a tu*.
- `TOKENIZER_A` / `TOKENIZER_B` — qualsevol ID de Hugging Face tokenizer funciona (`gpt2`, `bert-base-uncased`, `bert-base-multilingual-cased`, ...).



---

© 2026 **Marc Alier i Forment** (Universitat Politècnica de Catalunya) · <https://wasabi.essi.upc.edu/ludo> · <https://lamb-project.org>
Curs per a agents de BSC — *Transformers, LLMs, RAG i Agents: Des del teòric a la pràctica*.
Licensed under [Creative Commons BY-NC-SA 4.0](https://creativecommons.org/licenses/by-nc-sa/4.0/): reuse must credit the author, no commercial use, derivatives under the same license.
