# Dóna mans a l'LLM — un bucle amb eines

Exemple didàctic de la setmana 3. Li donem al model dues eines —`wget` per obtenir un URL i `execute_sql` per escriure en una base de dades SQLite local— i el cridem un cop i un altre fins que deixa de demanar eines. Després li donem una **tasca**, no una pregunta, i observem què passa.

## Requisits previs

Un Ollama local en marxa amb un model petit capaç d'usar eines:

```bash
ollama serve
ollama pull qwen3:1.7b
```

## Executar

El muntatge de sempre, igual que a totes les demos d'aquest curs:

```bash
cd week-03/demos/02-give-the-llm-hands
uv venv
source .venv/bin/activate
uv sync
python give_the_llm_hands.py
```

O amb el teu propi prompt:

```bash
python give_the_llm_hands.py "fetch https://api.github.com/users/torvalds and store the login, name and public_repos count"
```

El prompt per defecte obté dades d'una API JSON, demana al model que creï una taula, insereixi les files i informi de quantes n'ha guardat: una tasca que necessita diversos passos, així que veus com gira el bucle `while` (`── LLM call #N ──`): obtenir, crear la taula, inserir, respondre. Ningú no li diu al programa en quin ordre van els passos. El model decideix; el bucle executa.

Quan es demana `wget`, se't demanarà confirmació: escriu `y` per autoritzar-ho. És deliberat: s'imprimeix l'ordre exacta i l'acció perillosa només s'executa amb el teu vistiplau. Si la deneguies, se n'informa el model (se li *diu* que l'has denegat) i el bucle continua sense que res peti.

## Configuració

Els valors per defecte prioritzen Ollama; no cal cap `.env` per executar-ho localment. Copia `.env.example` a `.env` per sobreescriure `OPENAI_BASE_URL`, `OPENAI_API_KEY` i `MODEL` (per exemple, per apuntar a un endpoint de frontera).

**Nota sobre els models:** els models locals petits condueixen aquest bucle de manera irregular: obliden encadenar passos, passen arguments mal formats a les eines o s'aturen abans d'hora. El bucle és trivial; la intel·ligència que el guia és el model. Apunta el `.env` a un model més gran i les mateixes sis línies es comporten molt millor.

---

## La revelació — llegeix-ho després de la classe

**Acabes de construir un agent.** Aquest és tot el secret: un agent és un bucle `while` que continua cridant el model fins que el model deixa de demanar eines. Sense cap framework, sense màgia.

1. **El bucle és tot el motor.** Sis línies de `give_the_llm_hands.py` fan la feina: estan marcades al codi font com les línies `1`–`6` dins de `run_loop()`. Tota la resta (esquemes d'eines, SQLite, impressió, configuració) són canonades.
   - `1` el bucle `while True`
   - `2` crida el model i passa-li els esquemes de les eines
   - `3` no s'ha retornat cap crida a eina → aquesta és la resposta final, atura't
   - `4` afegeix a l'històric el missatge de crida a eina del model
   - `5` executa cada eina sol·licitada
   - `6` afegeix els resultats i torna al pas `2`
2. **Les eines donen mans al model.** Sense eines, un LLM només pot parlar. Amb `wget` i `execute_sql` pot arribar al web i escriure en una base de dades: *actua*.
3. **La seguretat viu a l'estructura, no al prompt.** No demanes amablement al model que es porti bé; bloqueges l'acció perillosa amb codi. Aquest és el prompt de la `y`.
4. **El comportament agèntic surt del programari, no de l'LLM.** El model proposa; el teu programa disposa. Queda't amb aquesta frase: tota la resta del curs s'hi aguanta.
