# Exercise 4 — Call the LLM from code

You have a model running on your own machine (Exercise 3). Now you call it from
code — the same way you would call a frontier model in the cloud. The point:
**it is the same call.** A chat-completion request is JSON over HTTP, and one
wire format reaches OpenAI, OpenRouter, Groq, and your laptop's Ollama alike.

## What's here

```
call.py              Chat Completions via the openai SDK   (runs on Ollama)
call.sh              the same call, raw curl — no SDK       (runs on Ollama)
responses_openai.py  the Responses API — OpenAI ONLY (will not run on Ollama)
.env.example         config; copy to .env
```

## Setup

1. Have Ollama running with a model you can fit (from Exercise 3):

   ```bash
   ollama serve            # if it isn't already running
   ollama pull ministral-3:8b
   ```

2. Configure and install the client:

   ```bash
   cp .env.example .env    # the defaults point at your local Ollama
   pip install openai
   ```

   Edit `MODEL` in `.env` to whatever fits your machine — `ministral-3:8b`
   (~6 GB), `qwen3:1.7b` (~1.5 GB), or anything you ran in Exercise 3.

## Run it

```bash
# load your .env into the shell, then:
python call.py
bash   call.sh
```

You should get a one-sentence reply, plus the token `usage` and the
`finish_reason`. That `usage` block is your bill on a paid API — read it.

## Try this

- Change the `temperature` (0.0 vs 1.5) and run a few times. What changes?
- Change the model in `.env`. Same code, different brain.
- If you have an OpenAI key: set the cloud values in `.env` and run `call.py`
  again — **unchanged**. Then run `responses_openai.py`. It works on OpenAI and
  fails on Ollama. Why? Because `/v1/responses` is OpenAI-specific;
  `/v1/chat/completions` is the format everyone speaks.



---

© 2026 **Marc Alier i Forment** (Universitat Politècnica de Catalunya) · <https://wasabi.essi.upc.edu/ludo> · <https://lamb-project.org>
BSC Agents Course — *Transformers, LLMs, RAG and Agents: From Theory to Production*.
Licensed under [Creative Commons BY-NC-SA 4.0](https://creativecommons.org/licenses/by-nc-sa/4.0/): reuse must credit the author, no commercial use, derivatives under the same license.
