# © 2026 Marc Alier i Forment (Universitat Politècnica de Catalunya) · https://wasabi.essi.upc.edu/ludo · https://lamb-project.org
# Curs per a agents de BSC — Transformers, LLMs, RAG i Agents: Des del teòric fins a la pràctica
# Amb llicència Creative Commons BY-NC-SA 4.0 – és obligatori citar l'autor, no es pot fer ús comercial, i les obres derivades han de tenir la mateixa llicència.

# =============================================================================================================== #
# Universitat Politècnica de Catalunya (UPC)                                                                      #
# =============================================================================================================== #

"""
🔌 Un servidor MCP mínim: una eina, un únic recurs.

El protocol MCP (Model Context Protocol) és una manera estàndard d'integrar funcionalitats en una aplicació impulsada per un model de llenguatge, sense haver de programar-les manualment. Un servidor anuncia les seves funcionalitats a través de JSON-RPC; un client (el teu agent) les descobreix i les utilitza. Les tres primitives:

  - eines: accions que el model pot executar (aquí: get_robot_spec)
  - recursos: dades que el model pot llegir (aquí: acme://company)
  - prompts : plantilles reutilitzables prompt (omès – mantenir-ho senzill)

Quan un client es connecta, el servidor li proporciona un registre: el nom, la descripció i l'esquema de cada eina (JSON). Aquest registre s'introdueix en el context del model al principi de la sessió – és important saber-ho, ja que defineix la estructura exacta que utilitzarà el model de costos en un capítol posterior.

Executar-lo directament per servir a través de l'API estàndard (stdio): `uv run server.py`
"""
from mcp.server.fastmcp import FastMCP

mcp = FastMCP("acme-robotics")

# dades emmagatzemades — fora de línia, per tant, la demostració no necessita una xarxa.
_SPECS = {
    "pallet pup": "Pallet Pup: top speed 2.4 m/s, 9 h battery, carries up to 600 kg, runs PupOS.",
    "shelf cat":  "Shelf Cat: top speed 0.9 m/s, reaches 8 m racking, shares the PupOS platform.",
}


@mcp.tool()
def get_robot_spec(model: str) -> str:
    """Torneu el full de especificacions del model d'Acme Robotics (per exemple, 'Pallet Pup', 'Shelf Cat')."""
    return _SPECS.get(model.strip().lower(), f"No spec on file for {model!r}.")


@mcp.resource("acme://company")
def company() -> str:
    """Informació de fons sobre Acme Robotics que el model pot llegir."""
    return ("Acme Robotics, founded 2019 in Girona, builds small autonomous warehouse "
            "robots. CEO Berta Comas. Motto: 'small robots, heavy lifting.'")


if __name__ == "__main__":
    mcp.run()  # Transport de dades mitjançant stdio (JSON-RPC a través de stdin/stdout)
