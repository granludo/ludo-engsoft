# Enviar una imatge a l'API

Un model multimodal llegeix imatges igual que text, però la crida és la **mateixa
petició de chat completions** que ja coneixes. L'única diferència és la forma del
`content` d'un missatge: en lloc d'una cadena simple, es converteix en una **llista de
parts**, i una d'aquestes parts és una imatge. La imatge es proporciona o bé com una
**URL** que el servidor descarrega, o bé incrustada com una **URI `data:` en base64**
(útil per a fitxers locals o privats). L'endpoint, l'SDK i el registre `usage` no
canvien.

Necessites un **model amb capacitat de visió** (p. ex. `gpt-4.1-mini`, `gpt-4o`). Un
model local petit normalment no pot veure imatges.

## Executar-ho

```bash
cp ../.env.example .env        # set a vision MODEL + your key
uv run --with openai --with python-dotenv python send_image.py                  # the bundled image
uv run --with openai --with python-dotenv python send_image.py path/to/photo.jpg
uv run --with openai --with python-dotenv python send_image.py https://example.com/photo.jpg
```

Sense cap argument, envia la imatge inclosa **`great-atuin.png`** — el Gran A'Tuin
carregant els elefants i el Disc (tortugues fins al fons) — i pregunta al model què
sosté el món. Una bona primera prova que la visió funciona, i ben escaient per a
aquest curs. Imprimeix la resposta del model més el `usage` de tokens.

---

© 2026 **Marc Alier i Forment** (Universitat Politècnica de Catalunya) · <https://wasabi.essi.upc.edu/ludo> · <https://lamb-project.org>
BSC Agents Course — *Transformers, LLMs, RAG and Agents: From Theory to Production*.
Licensed under [Creative Commons BY-NC-SA 4.0](https://creativecommons.org/licenses/by-nc-sa/4.0/): reuse must credit the author, no commercial use, derivatives under the same license.
