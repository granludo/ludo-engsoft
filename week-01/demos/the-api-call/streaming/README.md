# Streaming a chat completion

The same chat-completions call, but you receive the answer **token by token as it
is produced** instead of waiting for the whole thing. That is the typewriter
effect in ChatGPT. The total time is about the same; it just *feels* faster, and
for long answers the user sees progress instead of a frozen spinner.

In code the only change is `stream=True`: the response becomes an *iterator of
chunks*, and each chunk carries a little more text in `choices[0].delta.content`.
You print it the moment it arrives (`flush=True`). Pass `stream_options={"include_usage": True}`
to get a final chunk with the token `usage`, which a streamed response otherwise omits.

## Run it

```bash
cp ../.env.example .env        # OPENAI_ENDPOINT / OPENAI_API_KEY / MODEL
uv run --with openai python stream.py
```

Watch the text appear a few tokens at a time, then the `usage` line at the end.

---

© 2026 **Marc Alier i Forment** (Universitat Politècnica de Catalunya) · <https://wasabi.essi.upc.edu/ludo> · <https://lamb-project.org>
BSC Agents Course — *Transformers, LLMs, RAG and Agents: From Theory to Production*.
Licensed under [Creative Commons BY-NC-SA 4.0](https://creativecommons.org/licenses/by-nc-sa/4.0/): reuse must credit the author, no commercial use, derivatives under the same license.
