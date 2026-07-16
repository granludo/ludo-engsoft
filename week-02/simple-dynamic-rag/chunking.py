# © 2026 Marc Alier i Forment (Universitat Politècnica de Catalunya) · https://wasabi.essi.upc.edu/ludo · https://lamb-project.org
# Curs per a agents de BSC — Transformers, LLMs, RAG i Agents: Des del teòric fins a la pràctica
# Amb llicència Creative Commons BY-NC-SA 4.0 – és obligatori citar l'autor, no es pot fer ús comercial, i les obres derivades han de tenir la mateixa llicència.

"""Dos estratègies de fragmentació senzilles. Sense estructura – la fragmentació és un bucle, no una biblioteca.

Un CHUNK és la unitat de recerca: una part d'un document suficientment petita per ser integrada com un punt i introduïda en un prompt, però alhora suficientment significativa per tenir sentit per si mateixa. La manera com secció el document determina què pot trobar el teu sistema de cerca.

  chunk_by_chars(text, size, overlap) — una finestra que es desplassa: `size` caràcters per chunk, avançant d'una quantitat igual a "size - overlap". L'"overlap" és un marge compartit, de manera que un fragment que es divideix en un límit encara persisteix complet en un dels chunks. Funciona amb **qualsevol** text i ignora la estructura pròpia del document.

  chunk_by_sections(markdown, level) — divide un document Markdown en seccions basades en els seus títols (level=2 talla a "##", level=4 a "####"). Cada chunk representa una secció, incloent el títol, per tant, porta el seu propi títol com a context. Respecta la estructura de l'autor; les dimensions de chunk varien segons el document.
"""

import re


def chunk_by_chars(text: str, size: int = 800, overlap: int = 100) -> list[str]:
    """Finestra de desplaçament de `size` caràcters, avançant per intervals de superposició."""
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
    """Dividir un document en Markdown per als títols `level` (2 = ##, 4 = ####).

    Tot el que precedeix al primer títol (títol, introducció) es considera chunk 0 si no està buit. Cada chunk posterior correspon a una secció, incloent-hi el seu títol.
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
