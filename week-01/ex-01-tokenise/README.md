# Setmana 1 · Exercici 1 — Tokenize, en local

Carrega un tokenizer amb la biblioteca `transformers` de Hugging Face i compta els tokens a mà. Mira què veu realment el model. Mesura la penalització multilingüe. Compara dues famílies de tokenizers amb entrades de tipus codi.

## Executar-ho

```bash
uv venv && source .venv/bin/activate
uv sync
python ex_01_tokenise.py
```

La primera execució descarrega dos tokenizers petits de Hugging Face (uns quants centenars de KB cadascun). Sense pesos de model, sense GPU, sense clau d'API.

## Què pots modificar

- `PARAGRAPH_EN` / `PARAGRAPH_MINE` al principi de `ex_01_tokenise.py` — substitueix `PARAGRAPH_MINE` per la teva llengua per calcular la *teva* penalització multilingüe.
- `TOKENIZER_A` / `TOKENIZER_B` — funciona qualsevol id de tokenizer de Hugging Face (`gpt2`, `bert-base-uncased`, `bert-base-multilingual-cased`, …).



---

© 2026 **Marc Alier i Forment** (Universitat Politècnica de Catalunya) · <https://wasabi.essi.upc.edu/ludo> · <https://lamb-project.org>
Curs per a agents de BSC — *Transformers, LLMs, RAG i Agents: Des del teòric a la pràctica*.
Licensed under [Creative Commons BY-NC-SA 4.0](https://creativecommons.org/licenses/by-nc-sa/4.0/): reuse must credit the author, no commercial use, derivatives under the same license.
