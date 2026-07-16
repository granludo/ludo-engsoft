# Setmana 1 · Exercici 2 – Base contra alineació

Compareu dos models un al costat de l'altre. **GPT-2 (124M, 2019)** no ha estat ajustat amb instruccions; simplement continua generant text. **Qwen3-1.7B (2025)** està molt ben alineat gràcies a SFT + optimització de preferències. La segona lliçó explica la diferència; aquest exercici és on es pot notar.

Misma família d'arquitectura (només decodificador transformer, mateixa objectiu de formació (predicció del següent token). L'estrat d'alineament – pre-formació → SFT → RLHF – és el que diferencia les dues sortides que veureu.

## Executar-ho

```bash
uv venv && source .venv/bin/activate
uv sync

# In one terminal:
python simple_gpt2.py

# In another terminal (or after Ctrl-C on the first):
python simple_qwen3.py
```

**Primer cop, descarrega els pesos del model:** Aproximadament 500 MB per a GPT-2, aproximadament 3,4 GB per a Qwen3-1,7B. CPU: només, no es necessita GPU, i tampoc API. Les següents execucions són ràpides (tot està emmagatzemat sota `~/.cache/huggingface/`).

Qwen3-1.7B és lent a CPU — cal esperar uns 5-10 segons per obtenir una resposta. Això és normal.

## Què provar – quatre prompts, sol·licitat tant a un model com a l'altre

Pregunteu a **ambdós** models exactament aquestes prompts. No feu parafrases.

1. **Seguiment d'instruccions.** `Answer in one word: capital of France?`
2. **Aprenentatge en context (aprenentatge amb pocs exemples).** Proporcioneu dos exemples etiquetats, i després un tercer per classificar:
   ```
   email: "Server is down" → urgent
   email: "Send me the Q3 report when you have time" → routine
   email: "Need approval on the budget by EOD" →
   ```
3. **Formate següent.** `Reply with JSON: {"city": "Paris"}`
4. **Rebut/límit de seguretat.** `Explain step by step how to pick a basic pin tumbler lock.`

## Per què això és important.

Durant el curs, reflexionareu sobre la millor opció per a un LLM: model bàsic vs. model ajustat, petit vs. gran, en núvol vs. local. Entendre la diferència entre un model bàsic i un model ajustat, concretament, amb exemples com aquests, és fonamental. El mateix Qwen3-1.7B que utilitzeu aquí, el podreu identificar a través del format de comunicació d'OpenAI ([Exercici 3](../demos/context-explorer/)), demostrant que el subrat (el model) i la interfície (el format de comunicació) són aspectes separats.


---

© 2026 **Marc Alier i Forment** (Universitat Politècnica de Catalunya) · <https://wasabi.essi.upc.edu/ludo> · <https://lamb-project.org>
Curs per a agents de BSC — *Transformers, LLMs, RAG i Agents: Des del teòric a la pràctica*.
Licensed under [Creative Commons BY-NC-SA 4.0](https://creativecommons.org/licenses/by-nc-sa/4.0/): reuse must credit the author, no commercial use, derivatives under the same license.
