# © 2026 Marc Alier i Forment (Universitat Politècnica de Catalunya) · https://wasabi.essi.upc.edu/ludo · https://lamb-project.org
# Curs d'agents del BSC — Transformers, LLMs, RAG i Agents: de la teoria a la producció
# Amb llicència Creative Commons BY-NC-SA 4.0 – és obligatori citar l'autor, no es pot fer ús comercial, i les obres derivades han de tenir la mateixa llicència.

"""
Setmana 1 · Exercici 2 — GPT-2 (base model, 124M, 2019).

Mai no s'ha ajustat amb instruccions ni se li ha aplicat RLHF. Pura predicció
del següent token a partir del seu rastreig web de 2019. L'objectiu d'aquest
script és que copsis què és un base model.

Configuració:
    uv venv && source .venv/bin/activate && uv sync
    python simple_gpt2.py

Només CPU, ~500 MB de descàrrega a la primera execució; després queda a la memòria cau.
"""
from transformers import pipeline

# Carrega GPT-2 a la CPU (per defecte)
generator = pipeline("text-generation", model="gpt2")

print("GPT-2 CLI (prem Ctrl+C per sortir)")

while True:
    try:
        prompt = input("\n> ")
        if not prompt.strip():
            continue

        output = generator(
            prompt,
            max_new_tokens=50,
            do_sample=True,
            temperature=0.8,
        )

        print("\n" + output[0]["generated_text"])

    except KeyboardInterrupt:
        print("\nAdéu.")
        break
