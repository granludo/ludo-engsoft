# © 2026 Marc Alier i Forment (Universitat Politècnica de Catalunya) · https://wasabi.essi.upc.edu/ludo · https://lamb-project.org
# Curs d'agents de BSC — Transformers, LLMs, RAG i Agents: de la teoria a la producció
# Amb llicència Creative Commons BY-NC-SA 4.0 – és obligatori citar l'autor, no es pot fer ús comercial, i les obres derivades han de tenir la mateixa llicència.

# =============================================================================================================== #
# Universitat Politècnica de Catalunya (UPC)                                                                      #
# =============================================================================================================== #

"""
🔌 Un servidor MCP mínim: una eina, un recurs.

MCP (el Model Context Protocol) és una manera estàndard d'afegir capacitats a una aplicació impulsada per un LLM sense haver de cablejar-les una a una. Un servidor anuncia les seves capacitats per JSON-RPC; un client (el teu agent) les descobreix i les crida. Les tres primitives:

  - eines      : accions que el model pot invocar     (aquí: get_robot_spec)
  - recursos   : dades que el model pot llegir         (aquí: acme://company)
  - prompts    : plantilles de prompt reutilitzables   (omès — simplifiquem)

Quan un client es connecta, el servidor li lliura un REGISTRE: el nom, la descripció i l'esquema JSON de cada eina. Aquest registre es carrega en el context del model al començament de la sessió —cert i útil de saber—, i és l'estructura exacta que desmuntarà el model de costos d'un capítol posterior.

Executa'l directament per servir sobre stdio:  uv run server.py
"""
from mcp.server.fastmcp import FastMCP

mcp = FastMCP("acme-robotics")

# dades predefinides — fora de línia, així la demo no necessita xarxa
_SPECS = {
    "pallet pup": "Pallet Pup: top speed 2.4 m/s, 9 h battery, carries up to 600 kg, runs PupOS.",
    "shelf cat":  "Shelf Cat: top speed 0.9 m/s, reaches 8 m racking, shares the PupOS platform.",
}


@mcp.tool()
def get_robot_spec(model: str) -> str:
    """Retorna el full d'especificacions d'un model d'Acme Robotics (p. ex. 'Pallet Pup', 'Shelf Cat')."""
    return _SPECS.get(model.strip().lower(), f"No spec on file for {model!r}.")


@mcp.resource("acme://company")
def company() -> str:
    """Informació de context sobre Acme Robotics que el model pot llegir."""
    return ("Acme Robotics, founded 2019 in Girona, builds small autonomous warehouse "
            "robots. CEO Berta Comas. Motto: 'small robots, heavy lifting.'")


if __name__ == "__main__":
    mcp.run()  # transport stdio (JSON-RPC sobre stdin/stdout)
