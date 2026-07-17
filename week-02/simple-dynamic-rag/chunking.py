# © 2026 Marc Alier i Forment (Universitat Politècnica de Catalunya) · https://wasabi.essi.upc.edu/ludo · https://lamb-project.org
# Curs d'agents de BSC — Transformers, LLMs, RAG i Agents: De la teoria a la producció
# Amb llicència Creative Commons BY-NC-SA 4.0 – és obligatori citar l'autor, no es pot fer ús comercial, i les obres derivades han de tenir la mateixa llicència.

"""Dues estratègies de chunking senzilles. Sense cap framework: el chunking és un bucle for, no una biblioteca.

Un CHUNK és la unitat de recuperació: un fragment d'un document prou petit per representar-lo com un sol punt d'embedding i injectar-lo en un prompt, però prou gran per tenir sentit per si mateix. La manera com talles el document determina què podrà trobar el teu recuperador.

  chunk_by_chars(text, size, overlap)   — una finestra lliscant: `size` caràcters per chunk, avançant en passos de size-overlap. L'overlap és un marge compartit, de manera que un fet partit en un límit sobreviu sencer en un dels chunks. Funciona amb QUALSEVOL text; ignora l'estructura pròpia del document.

  chunk_by_sections(markdown, level)    — divideix un document markdown pels seus propis encapçalaments (level=2 talla als ##, level=4 als ####). Cada chunk és una secció, amb l'encapçalament inclòs, de manera que porta el seu propi títol com a context. Respecta l'estructura de l'autor; la mida dels chunks varia segons el document.
"""

import re


def chunk_by_chars(text: str, size: int = 800, overlap: int = 100) -> list[str]:
    """Finestra lliscant de `size` caràcters, avançant en passos de size-overlap."""
    step = max(1, size - overlap)
    chunks = []
    i = 0
    while i < len(text):
        piece = text[i:i + size].strip()
        if piece:
            chunks.append(piece)
        i += step
    return chunks


def chunk_by_sections(markdown: str, level: int = 2) -> list[str]:
    """Divideix un document markdown pels encapçalaments de `level` (2 = ##, 4 = ####).

    Tot el que hi ha abans del primer encapçalament (títol, introducció) esdevé el chunk 0 si no és buit. Cada chunk següent és una secció, amb el seu encapçalament inclòs.
    """
    heading = re.compile(rf"^#{{{level}}}\s", flags=re.MULTILINE)
    starts = [m.start() for m in heading.finditer(markdown)]
    if not starts:
        return [markdown.strip()] if markdown.strip() else []
    cuts = [0] + starts + [len(markdown)]
    chunks = []
    for a, b in zip(cuts, cuts[1:]):
        piece = markdown[a:b].strip()
        if piece:
            chunks.append(piece)
    return chunks
