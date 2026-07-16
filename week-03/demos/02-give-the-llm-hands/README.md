# Dóna les LLM mans – una estructura amb eines.

Exemple d'ensenyament per la setmana 3. Li donem al model dues eines: `wget` per obtenir un URL i `execute_sql` per escriure en una base de dades SQLite local — i continuem cridant-lo fins que deixi de sol·licitar eines. Després, li donem una **tasca**, no una pregunta, i observem què passa.

## Requisits previs

Executant un model local d'Ollama amb una petita capacitat de processament:

```bash
ollama serve
ollama pull qwen3:1.7b
```

## Correr

La configuració habitual, igual que en totes les demostracions d'aquest curs:

```bash
cd week-03/demos/02-give-the-llm-hands
uv venv
source .venv/bin/activate
uv sync
python give_the_llm_hands.py
```

O amb els vostres propis prompt:

```bash
python give_the_llm_hands.py "fetch https://api.github.com/users/torvalds and store the login, name and public_repos count"
```

La petició per defecte consulta una API JSON, demana al model que creï una taula, inserteixi les files i reporti quantes ha guardat – una tasca que requereix diversos passos, per tant, observeu el bucle `while` en acció (`── LLM call #N ──`): obtenir dades, crear la taula, inserir, respondre. El programa no rep instruccions sobre l'ordre dels passos. El model decideix; el bucle s'executa.

Quan es demana `wget`, apareixerà un missatge que demanarà: escriu `y` per autoritzar-ho. Això és intencional: s'imprimeix l'ordre exacte, i l'acció perillosa només es realitza amb el teu consentiment. Si es denegada, la informació es retorna al model (es *notifica* que ha estat denegada), i el bucle continua executant-se, sense que hi hagi cap error.

## Configuració

Els valors per defecte són Ollama; no es necessita `.env` per executar-los localment. Copia `.env.example` a `.env` per sobreescriure `OPENAI_BASE_URL`, `OPENAI_API_KEY` i `MODEL` (per exemple, per apuntar a una frontera endpoint).

**Comentari sobre els models:** Els petits models locals operen aquest bucle de manera desigual: poden oblidar-se d'encadenar passos, utilitzar arguments incorrectes per a les eines, o finalitzar prematurament. El bucle és senzill; la intel·ligència que el dirigeix és el model. Si apunteu `.env` a un model més gran, els mateixos sis línies funcionaran molt millor.

---

## La revelació – llegiu-ho després de la conferència

**Acabaveu de crear un agent.** Aquest és el secret principal: un agent és una `while` estructura que continua cridant al model fins que aquest deixa de sol·licitar eines. Sense cap marc ni trucs.

1. **El bucle és el motor principal.** Sis línies de codi (`give_the_llm_hands.py`) realitzen la tasca – estan marcades a la font com les línies `1`–`6` dins del bloc `run_loop()`. Tot el que resta (esquemes d'eines, SQLite, impressió, configuració) és infraestructura.
   - `1` el `while True` bucle
   - `2` cridar al model i proporcionar-li els esquemes de les eines.
   - `3` No s'han retornat crides a la funció → aquesta és la resposta definitiva, parem.
   - `4` Afegir el missatge de crida a la eina del model a l'històric
   - `5` executar cada eina demanada
   - `6` afegeix els resultats i torna al `2`
2. **Les eines donen al model la capacitat de "fer".** Sense eines, un LLM només pot parlar. Amb `wget` i `execute_sql`, pot accedir a internet i escriure en una base de dades – és a dir, *actua*.
3. **La seguretat rau en la estructura, no en el prompt.** No demanes al model que es comporti bé; bloquejes l'acció perillosa amb codi. Aquest és el `y` prompt.
4. **El comportament autònom prové del programa, no de LLM.** El model proposa; el vostre programa executa. Recordeu aquesta frase: tot el curs es basa en ella.
