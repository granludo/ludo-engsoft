#!/usr/bin/env python3
# © 2026 Marc Alier i Forment (Universitat Politècnica de Catalunya) · https://wasabi.essi.upc.edu/ludo · https://lamb-project.org
# Curs per a agents de BSC — Transformers, LLMs, RAG i Agents: Des del teòric fins a la pràctica
# Amb llicència Creative Commons BY-NC-SA 4.0 – és obligatori citar l'autor, no es pot fer ús comercial, i les obres derivades han de tenir la mateixa llicència.

"""
Setmana 1 · Exercici 1 – Hugging Face tokenizers, a l'entorn local.

Script de referència per a l'exercici. **VOUS** executeu aquest script; no modifiqueu el codi (podeu canviar els dos paràgrafs en PARAGRAPH_EN / PARAGRAPH_MINE pel vostre propi text – aquesta és la única modificació que necessiteu). També podeu canviar les dues identificadores tokenizer (TOKENIZER_A / TOKENIZER_B) per comparar diferents famílies.

Fa tres coses i les imprimeix de forma clara:
  1. Carrega un tokenizer amb AutoTokenizer.from_pretrained(...), i mostra'l.
     token comptar (la pregunta bàsica: "quant tokens hi ha?").
  2. Analitza el mateix paràgraf en anglès i en un altre idioma, i
     calcula la penalització per l'ús de múltiples idiomes;
  3. compareu DOS tokenizers (famílies de models diferents) en quatre tipus de
     entrada de tipus "codi", i imprimeix una petita taula.

Configuració: activar l'entorn virtual amb `uv venv source .venv/bin/activate` i executar el script `python ex_01_tokenise.py`.

Només es descarreguen els tokenitzadors (unes centenars de KB cadascun) – no s'utilitzen pesos del model, ni es necessita una GPU, ni una clau d'API, ni cap xarxa més enllà de la primera descàrrega de Hugging Face.

Bones parelles de comparació entre "vint i nou", totes sense restriccions:
  - "gpt2" (2019, codificació BPE a nivell de bytes)
  - "bert-base-uncased" (2018, WordPiece)
  - "bert-base-multilingual-cased" (WordPiece multilingüe amb majúscules)
"""
from __future__ import annotations

# ---- els dos tokenizers per comparar -----------------------------------------
TOKENIZER_A = "gpt2"                 # el més antic
TOKENIZER_B = "bert-base-uncased"    # el més recent (d'una família diferent)

# ---- Els dos paràgrafs (podeu substituir-los pels vostres) --------------------
PARAGRAPH_EN = (
    "A large language model reads text as tokens, not words. The number of "
    "tokens — not the number of words — is what you are billed for and what "
    "must fit in the context window."
)
# Més tard, en el teu idioma. Per defecte, és l'espanyol; canvia-ho a:
# El llenguatge que utilitzareu per a l'exercici.
PARAGRAPH_MINE = (
    "Un gran modelo de lenguaje lee el texto como tokens, no como palabras. "
    "El número de tokens — no el de palabras — es lo que se te factura y lo "
    "que tiene que caber en la ventana de contexto."
)

# ---- Quatre entrades relacionades amb codi per a la comparació tokenizer ---------------------
CODE_SAMPLES = {
    "python function": (
        "def add(a, b):\n"
        "    \"\"\"Return the sum.\"\"\"\n"
        "    return a + b\n"
    ),
    "JSON blob": (
        '{"model": "gpt-4", "messages": [{"role": "user", '
        '"content": "hello"}], "max_tokens": 256}'
    ),
    "regex-heavy line": r"re.compile(r'^\s*([A-Za-z_]\w*)\s*=\s*(.+?)\s*;?$')",
    "whitespace-heavy": "x = 1\n\n\n\t\t\treturn          x\n\n",
}


def _load(name):
    from transformers import AutoTokenizer
    print(f"  loading tokenizer: {name} …")
    return AutoTokenizer.from_pretrained(name)


def n_tokens(tok, text: str) -> int:
    """Token, sense comptar les excepcions tokens — el que pagues."""
    return len(tok.encode(text, add_special_tokens=False))


def main() -> None:
    # Les consoles de Windows per defecte utilitzen la codificació CP1252 i tenen problemes amb els símbols «·» «→» i «±» a la nostra sortida.
    try:
        import sys
        sys.stdout.reconfigure(encoding="utf-8")
    except Exception:
        pass
    print("=" * 70)
    print("Week 1 · Exercise 1 — tokenizers, locally")
    print("=" * 70)

    print("[1] Carregar un tokenizer i comptar tokens")
    tok_a = _load(TOKENIZER_A)
    demo = "The model never sees the letters in strawberry."
    print(f'  text : "{demo}"')
    print(f"  tokens with {TOKENIZER_A}: {n_tokens(tok_a, demo)}")

    print("[2] La sanció multilingüe (mateixa paraula, dos llengües)")
    en = n_tokens(tok_a, PARAGRAPH_EN)
    mine = n_tokens(tok_a, PARAGRAPH_MINE)
    penalty = (mine - en) / en if en else 0.0
    print(f"  English          : {en} tokens")
    print(f"  your language    : {mine} tokens")
    print(f"  multilingual penalty = (mine - en) / en = {penalty:+.1%}")
    print("  → record this number in your report.")

    print("[3] Dos tokenitzadors contra quatre tipus de codi")
    tok_b = _load(TOKENIZER_B)
    width = max(len(k) for k in CODE_SAMPLES) + 2
    print(f"\n  {'input':<{width}}{TOKENIZER_A:>14}{TOKENIZER_B:>20}")
    print("  " + "-" * (width + 34))
    for label, sample in CODE_SAMPLES.items():
        a, b = n_tokens(tok_a, sample), n_tokens(tok_b, sample)
        print(f"  {label:<{width}}{a:>14}{b:>20}")
    print("\n  → for each row, write ONE sentence: where do the two disagree")
    print("El més important, i per què podria ser així? (incloeu-ho al vostre informe).")

    print("\n" + "=" * 70)
    print("Fet. Ara escriu el informe i envia'l al repositori del curs.")
    print("=" * 70)


if __name__ == "__main__":
    try:
        main()
    except ModuleNotFoundError:
        raise SystemExit(
            "transformers is not installed. Run:\n"
            "    uv venv && source .venv/bin/activate && uv sync"
        )
