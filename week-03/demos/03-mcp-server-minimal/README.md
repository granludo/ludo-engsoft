<!-- =============================================================================================================== -->
<!-- Universitat Politècnica de Catalunya (UPC) -->
<!-- =============================================================================================================== -->

# 🔌 Un servidor MCP mínim — i el bucle de l'agent que el crida

MCP (el Model Context Protocol) és una manera estàndard d'endollar funcionalitats a una aplicació basada en un LLM sense haver de cablejar-les una a una a mà. Exposa una funcionalitat **un sol cop**, com a servidor, i qualsevol agent que compleixi l'estàndard la pot descobrir i utilitzar.

- **`server.py`** — un servidor MCP complet en un grapat de línies: una **eina** (`get_robot_spec`) i un **recurs** (`acme://company`), servits per stdio. Un decorador converteix una funció en una eina; la biblioteca s'encarrega del JSON-RPC.
- **`agent_with_mcp.py`** — el bucle d'agent fet a mà de `give-the-llm-hands`, ara apuntat al servidor. **El bucle no canvia; només canvia d'on surten les eines.** En connectar-s'hi, descobreix el **registre** del servidor (nom + descripció + esquema de cada eina) i l'entrega al model; les crides del model s'encaminen per JSON-RPC i els resultats se li retornen.

```bash
uv venv && source .venv/bin/activate && uv pip install openai mcp
MODEL=qwen3.6:27b OPENAI_BASE_URL=http://localhost:11434/v1 \
  uv run agent_with_mcp.py "what is the top speed of the Pallet Pup?"
```

`agent_with_mcp.py` engega ell mateix el `server.py`, així que executa'l des d'aquest directori. Fes servir un model capaç de cridar eines.

> **Nota sobre la cadena de subministrament:** fixa la versió de l'SDK `mcp` a una que ja porti un parell de
> setmanes publicada (la regla del curs: «no l'instal·lis el dia que surt»). Una versió acabada de sortir és exactament
> on apareixeria primer una dependència compromesa.

## 📖 Llicència i autor

Licensed under **CC BY-NC-SA 4.0**. © 2026 **Marc Alier i Forment** (UPC) ·
<https://wasabi.essi.upc.edu/ludo> · <https://lamb-project.org>. Curs per a agents de la BSC.
