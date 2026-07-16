# Enviar una imatge a la API

Un model multimodial pot llegir imatges i text, però la funció és la mateixa.
**sol·licitud de completar la conversa**, que ja coneixeu. La única diferència és la forma en què...
un missatge `content`: en lloc d'una simple cadena de caràcters, es converteix en una **llista de fragments**.
I una part és una imatge. La imatge es proporciona ja sigui com a **URL**, directament des del servidor.
recopilades, o incloses com una **URI Base64 `data:`** (útil per a utilitzar-les localment o en entorns privats)
els fitxers). Endpoint, SDK, i el registre `usage` no han canviat.

Necessiteu un model amb capacitat de visió (per exemple, `gpt-4.1-mini`, `gpt-4o`). Un petit dispositiu local
Normalment, els models no poden veure imatges.

## Executar-ho

```bash
cp ../.env.example .env        # set a vision MODEL + your key
uv run --with openai --with python-dotenv python send_image.py                  # the bundled image
uv run --with openai --with python-dotenv python send_image.py path/to/photo.jpg
uv run --with openai --with python-dotenv python send_image.py https://example.com/photo.jpg
```

Sense cap dubte, envia el paquet **`great-atuin.png`**, que és el Gran A'Tuin.
transportant els elefants i el Disc (tot inclòs les tortugues), i pregunta a...
Mostra què està impedint el progrés del món. Un bon primer test per comprovar si la visió és efectiva.
i és adequat per a aquest curs. Imprimeix la resposta del model, juntament amb el token.
`usage`.

---

© 2026 **Marc Alier i Forment** (Universitat Politècnica de Catalunya) · <https://wasabi.essi.upc.edu/ludo> · <https://lamb-project.org>
Curs per a agents de BSC — *Transformers, LLMs, RAG i Agents: Des del teòric a la pràctica*.
Licensed under [Creative Commons BY-NC-SA 4.0](https://creativecommons.org/licenses/by-nc-sa/4.0/): reuse must credit the author, no commercial use, derivatives under the same license.
