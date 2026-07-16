# © 2026 Marc Alier i Forment (Universitat Politècnica de Catalunya) · https://wasabi.essi.upc.edu/ludo · https://lamb-project.org
# Curs per a agents de BSC — Transformers, LLMs, RAG i Agents: Des del teòric fins a la pràctica
# Amb llicència Creative Commons BY-NC-SA 4.0 – és obligatori citar l'autor, no es pot fer ús comercial, i les obres derivades han de tenir la mateixa llicència.

"""
Setmana 1 · Exercici 2 — GPT-2 (base model, 124M, 2019).

Mai no s'ha entrenat amb instruccions, ni s'ha utilitzat RLHF. Predicció pura del següent token basada en el rastre de la web de 2019. L'objectiu d'aquest script és experimentar com funciona un base model.

Configuració: `uv venv` i després `source .venv/bin/activate` i finalment, executar `uv sync python simple_gpt2.py`

Només amb la versió CPU, aproximadament 500 MB de descàrrega al primer inici, i després es descarregaran les parts necessàries.
"""
from transformers import pipeline

# Cargar GPT-2 a CPU (per defecte)
generator = pipeline("text-generation", model="gpt2")

print("GPT-2 CLI (Prem 'Ctrl+C' per sortir)")

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
        print("Adéu.")
        break
