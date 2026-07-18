#!/usr/bin/env python3
# © 2026 Marc Alier i Forment (Universitat Politècnica de Catalunya) · https://wasabi.essi.upc.edu/ludo · https://lamb-project.org
# Curs d'agents del BSC — Transformers, LLMs, RAG i Agents: de la teoria a la producció
# Amb llicència Creative Commons BY-NC-SA 4.0 – és obligatori citar l'autor, no es pot fer ús comercial, i les obres derivades han de tenir la mateixa llicència.

"""
Setmana 1 · Exercici 1 — Hugging Face tokenizers, en local.

Script de referència de l'exercici. Tu l'EXECUTES; no en toquis el codi (pots
substituir els dos paràgrafs de PARAGRAPH_EN / PARAGRAPH_MINE pel teu propi
text: és l'única modificació que et cal). També pots canviar els dos
identificadors de tokenizer (TOKENIZER_A / TOKENIZER_B) per comparar famílies
diferents.

Fa tres coses i les imprimeix amb claredat:
  1. carrega un tokenizer amb AutoTokenizer.from_pretrained(...) i en mostra el
     recompte de tokens (la pregunta bàsica: «quants tokens són?»);
  2. divideix en tokens el mateix paràgraf en anglès i en una altra llengua, i
     calcula la penalització multilingüe;
  3. compara DOS tokenizers (famílies de models diferents) amb quatre tipus
     d'entrada semblant a codi, i imprimeix una petita taula.

Configuració:
    uv venv
    source .venv/bin/activate
    uv sync
    python ex_01_tokenise.py

Només es descarreguen els tokenizers (uns quants centenars de KB cadascun): res
de pesos del model, ni GPU, ni clau d'API, ni cap connexió a la xarxa més enllà
de la primera descàrrega de Hugging Face.

Bones parelles de contrast «antic vs. més recent», totes sense accés restringit:
  - "gpt2"               (2019, BPE a nivell de bytes)
  - "bert-base-uncased"  (2018, WordPiece)
  - "bert-base-multilingual-cased" (WordPiece multilingüe)
"""
from __future__ import annotations

# ---- els dos tokenizers a comparar -----------------------------------------
TOKENIZER_A = "gpt2"                 # el «més antic»
TOKENIZER_B = "bert-base-uncased"    # el «més recent» (d'una altra família)

# ---- els dos paràgrafs (pots substituir-los pels teus) --------------------
PARAGRAPH_EN = (
    "A large language model reads text as tokens, not words. The number of "
    "tokens — not the number of words — is what you are billed for and what "
    "must fit in the context window."
)
# El mateix paràgraf, en el teu idioma. Per defecte és en espanyol; substitueix-lo
# pel TEU idioma per a l'exercici.
PARAGRAPH_MINE = (
    "Un gran modelo de lenguaje lee el texto como tokens, no como palabras. "
    "El número de tokens — no el de palabras — es lo que se te factura y lo "
    "que tiene que caber en la ventana de contexto."
)

# ---- quatre entrades semblants a codi per a la comparació de tokenizers ---------------------
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
    print(f"  carregant tokenizer: {name} …")
    return AutoTokenizer.from_pretrained(name)


def n_tokens(tok, text: str) -> int:
    """Recompte de tokens, sense comptar els tokens especials: el que pagues."""
    return len(tok.encode(text, add_special_tokens=False))


def main() -> None:
    # Les consoles de Windows fan servir CP1252 per defecte i s'ennueguen amb els símbols — · → ± de la nostra sortida.
    try:
        import sys
        sys.stdout.reconfigure(encoding="utf-8")
    except Exception:
        pass
    print("=" * 70)
    print("Setmana 1 · Exercici 1 — tokenizers, en local")
    print("=" * 70)

    print("[1] Carregar un tokenizer i comptar tokens")
    tok_a = _load(TOKENIZER_A)
    demo = "The model never sees the letters in strawberry."
    print(f'  text : "{demo}"')
    print(f"  tokens amb {TOKENIZER_A}: {n_tokens(tok_a, demo)}")

    print("[2] La penalització multilingüe (mateix paràgraf, dues llengües)")
    en = n_tokens(tok_a, PARAGRAPH_EN)
    mine = n_tokens(tok_a, PARAGRAPH_MINE)
    penalty = (mine - en) / en if en else 0.0
    print(f"  Anglès           : {en} tokens")
    print(f"  el teu idioma    : {mine} tokens")
    print(f"  penalització multilingüe = (mine - en) / en = {penalty:+.1%}")
    print("  → apunta aquest número al teu informe.")

    print("[3] Dos tokenizers contra quatre tipus de codi")
    tok_b = _load(TOKENIZER_B)
    width = max(len(k) for k in CODE_SAMPLES) + 2
    print(f"\n  {'entrada':<{width}}{TOKENIZER_A:>14}{TOKENIZER_B:>20}")
    print("  " + "-" * (width + 34))
    for label, sample in CODE_SAMPLES.items():
        a, b = n_tokens(tok_a, sample), n_tokens(tok_b, sample)
        print(f"  {label:<{width}}{a:>14}{b:>20}")
    print("\n  → per a cada fila, escriu UNA frase: on divergeixen més")
    print("    tots dos, i per què deu ser així? (inclou-ho al teu informe)")

    print("\n" + "=" * 70)
    print("Fet. Ara escriu l'informe i puja'l al repositori del curs.")
    print("=" * 70)


if __name__ == "__main__":
    try:
        main()
    except ModuleNotFoundError:
        raise SystemExit(
            "transformers no està instal·lat. Executa:\n"
            "    uv venv && source .venv/bin/activate && uv sync"
        )
