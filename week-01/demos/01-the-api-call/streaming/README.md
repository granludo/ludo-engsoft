# Streaming un cop completat el diàleg

La mateixa petició de "completar la conversa", però rebeu la resposta **token per part de token tal com és.
és produït **en lloc de esperar que s'acabi tot**. Aquest és el mecanotex
efecte a ChatGPT. El temps total és gairebé el mateix; simplement *sembla* més ràpid, i
Per a respostes llargues, l'usuari veu un indicador de progrés en comptes d'un "spinner" congelat.

En el codi, l'única modificació és `stream=True`: la resposta es converteix en un *iterador de*.
chunks*, i cada chunk conté una mica més de text al `choices[0].delta.content`.
Ho imprimeu tan aviat com arribi (`flush=True`). Passeu `stream_options={"include_usage": True}`.
per obtenir la resposta final chunk amb el token `usage`, que una resposta en directe normalment no inclou.

## Executar-ho

```bash
cp ../.env.example .env        # OPENAI_ENDPOINT / OPENAI_API_KEY / MODEL
uv run --with openai --with python-dotenv python stream.py
```

Observeu com el text apareix de forma gradual, unes quantes línies tokens alhora, i després la línia final `usage`.

O, vegeu-ho des d'una perspectiva de HTTP sense processar – mateixa petició amb `"stream": true`, però sense resposta.
SDK. `curl -N` imprimeix cada `data: {...}` chunk tan aviat com arriba:

```bash
bash curl.sh
```

Obteniu els esdeveniments del servidor que SDK amaga de vosaltres: una seqüència de `data:` línies.
Cadascun amb una mica més de text al `choices[0].delta.content`, i finalitzant al `data: [DONE]`.

---

© 2026 **Marc Alier i Forment** (Universitat Politècnica de Catalunya) · <https://wasabi.essi.upc.edu/ludo> · <https://lamb-project.org>
Curs per a agents de BSC — *Transformers, LLMs, RAG i Agents: Des del teòric a la pràctica*.
Licensed under [Creative Commons BY-NC-SA 4.0](https://creativecommons.org/licenses/by-nc-sa/4.0/): reuse must credit the author, no commercial use, derivatives under the same license.
