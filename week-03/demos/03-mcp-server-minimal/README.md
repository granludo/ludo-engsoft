<!-- =============================================================================================================== -->
<!-- Universitat Politècnica de Catalunya (UPC) -->
<!-- =============================================================================================================== -->

# 🔌 Un servidor MCP mínim – i el bucle de l'agent que el crida

MCP (el protocol·le de context del model) és una manera estàndard d'integrar funcionalitats en un sistema basat en LLM.
aplicació sense necessitat de cablejar-les manualment. Oferir una funcionalitat **una sola vegada**, com a servidor, i qualsevol altre.
Un agent conforme pot descobrir-lo i utilitzar-lo.

- **`server.py`** – un servidor MCP complet en només unes poques línies de codi: una eina única
(`get_robot_spec`) i un **recurs,** (`acme://company`), servit a través de `stdio`. Un decorador.
Transforma una funció en una eina; la biblioteca gestiona la comunicació JSON.
- **`agent_with_mcp.py`** – el bucle d'agent manual creat a partir de `give-the-llm-hands`, ara apuntat
al servidor. **El bucle no canvia – només la font de les eines es modifica.** Quan s'estableix la connexió
Descobreix el registre del servidor (nom + descripció + esquema per a cada eina) i l'entrega.
a la màquina; les sol·licituds de la màquina es gestionen a través de JSON-RPC i els resultats es tornen a enviar.

```bash
uv venv && source .venv/bin/activate && uv pip install openai mcp
MODEL=qwen3.6:27b OPENAI_BASE_URL=http://localhost:11434/v1 \
  uv run agent_with_mcp.py "what is the top speed of the Pallet Pup?"
```

`agent_with_mcp.py` crea `server.py`, per tant, executa'l des d'aquest directori. Utilitza un
Model de comunicació per sol·licitar eines.

> **Nota sobre la cadena de subministrament:** enganxeu les referències `mcp` i SDK a una publicació que ja ha estat disponible durant uns quants dies.
> setmanes (en virtut de la regla del curs: "no instal·leu-lo el dia que l'envieu"). Una nova versió és exactament
> on es manifestaria primer la dependència comprometida.

## 📖 Llicència i autor

Licensed under **CC BY-NC-SA 4.0**. © 2026 **Marc Alier i Forment** (UPC) ·
<https://wasabi.essi.upc.edu/ludo> · <https://lamb-project.org>. Curs per a agents de la BSC.
