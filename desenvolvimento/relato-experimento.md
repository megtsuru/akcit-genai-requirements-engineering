# Relato do experimento — agente `desenvolvedor`

**Tarefa:** `avaliar_inscricao` (`especificacao-tarefa.md`), definida antes
da geração com entradas, saídas e exemplos normais, de limite e de erro. A
lacuna 6 (inscrição pendente de pagamento ocupa vaga?) ficou em aberto de
propósito.

**Execução:** sessão nova do Claude Code com o agente
`.claude/agents/desenvolvedor.md` (`claude -p --agent desenvolvedor`), sem
histórico de conversa.

**Rodada 1:** o agente implementou os 12 exemplos e **parou na lacuna 6**:
propôs 3 opções (reservar a vaga, não reservar, configurável por evento),
recomendou reservar e deixou o caso bloqueado com `NotImplementedError` em
vez de decidir sozinho. Também:

- decidiu sozinho, mas declarou, que `LISTA_ESPERA` não ocupa vaga;
- percebeu que o comando `ruff format .` do guia reformatava um `.md`,
  desfez a mudança e só sugeriu a correção, por estar fora do escopo.

**Correções minhas:** escolhi a opção A (pendente reserva a vaga),
registrei a decisão na especificação com dois exemplos novos (L6, L7),
confirmei a regra da lista de espera e corrigi o comando do Ruff no guia
(`src tests`).

**Rodada 2:** o agente ajustou código e testes à decisão.

**Verificações (refeitas por mim, fora do agente):**

- `uv run pytest`: 14/14 exemplos da especificação com teste e passando;
- `uv run ruff check src tests` e `uv run mypy src` (strict): sem erros;
- testes revisados: usam os valores literais da especificação, citam o ID
  do exemplo e a regra, e não recalculam o esperado com a lógica do código;
- só arquivos de `src/` e `tests/` alterados; nenhuma dependência nova.

**Decisão:** código aceito.
