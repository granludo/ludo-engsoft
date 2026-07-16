# © 2026 Marc Alier i Forment (Universitat Politècnica de Catalunya) · https://wasabi.essi.upc.edu/ludo · https://lamb-project.org
# Curs per a agents de BSC — Transformers, LLMs, RAG i Agents: Des del teòric fins a la pràctica
# Amb llicència Creative Commons BY-NC-SA 4.0 – és obligatori citar l'autor, no es pot fer ús comercial, i les obres derivades han de tenir la mateixa llicència.

"""
Setmana 1 · Exercici 2 — Qwen3-1.7B (aligned model, 1.7B, 2025).

Ha estat entrenat intensament amb supervisió i afinació detallada, així com optimització de preferències. Té la mateixa arquitectura que GPT-2 (únic decodificador transformer, predicció del següent token) — la diferència és l'estrat d'alineació de la Lliçó 2.

Configuració: `uv venv` i després `source .venv/bin/activate` i finalment, executar `uv sync python simple_qwen3.py`

Només necessita CPU, aproximadament 3,4 GB de descàrrega al primer inici, i després es guarda en memòria RAM.
"""
from transformers import AutoTokenizer, AutoModelForCausalLM
import torch

MODEL_ID = "Qwen/Qwen3-1.7B"

tokenizer = AutoTokenizer.from_pretrained(MODEL_ID)
model = AutoModelForCausalLM.from_pretrained(MODEL_ID, torch_dtype=torch.float32)
model.eval()

print("Qwen3 1.7B CLI (Prem \"Ctrl+C\" per sortir)")

while True:
    try:
        user = input("\n> ").strip()
        if not user:
            continue

        messages = [{"role": "user", "content": user}]
        prompt = tokenizer.apply_chat_template(
            messages,
            tokenize=False,
            add_generation_prompt=True,
            enable_thinking=False,
        )

        inputs = tokenizer(prompt, return_tensors="pt")

        with torch.no_grad():
            output = model.generate(
                **inputs,
                max_new_tokens=200,
                do_sample=True,
                temperature=0.7,
                top_p=0.9,
                pad_token_id=tokenizer.eos_token_id,
            )

        print("\n" + tokenizer.decode(output[0], skip_special_tokens=True))

    except KeyboardInterrupt:
        print("Adéu.")
        break
