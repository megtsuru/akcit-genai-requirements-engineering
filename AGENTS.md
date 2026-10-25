# AGENTS.md — Eventus

> Contexto do projeto para agentes de IA (formato aberto
> [AGENTS.md](https://agents.md)). Complementa o agente genérico
> `.claude/agents/desenvolvedor.md`.

## Projeto

O **Eventus** é um sistema fictício de gestão de eventos com quatro papéis:
Participante, Organizador, Equipe Financeira e Palestrante. Este
repositório é usado em um curso: todos os dados são fictícios.

## Documentação (fonte da verdade)

- `analise/requisitos-funcionais.md` — RF01–RF16
- `analise/regras-de-negocio.md` — RN01–RN07
- `analise/duvidas-e-lacunas.md` — pontos **ainda não decididos**
- `analise/requisitos-nao-funcionais.md` — só candidatos, a validar
- `especificacao/casos-de-uso.md` e `especificacao/criterios-de-aceitacao.md`
- `arquitetura/descricao-sistema.md` — as regras de negócio ficam na
  camada de API de Aplicação

## Stack

- **Python**, conforme o guia [`guias/stack-python.md`](guias/stack-python.md).
- Raiz do código Python: `desenvolvimento/` (pacote em
  `desenvolvimento/src/eventus/`, testes em `desenvolvimento/tests/`).
- Comandos, a partir de `desenvolvimento/`: `uv run pytest`,
  `uv run ruff check src tests`, `uv run ruff format src tests`, `uv run mypy src`.
- A elicitação não definiu stack; Python é uma escolha deste curso.

## Convenções do projeto

- Identificadores e mensagens em **português**, sem acentos nos nomes
  (`avaliar_inscricao`, `Evento`, `StatusInscricao`).
- Regras de negócio são **funções puras**: nada de banco, rede, relógio do
  sistema (`datetime.now()`) ou estado global. Tudo que a função precisa
  entra por parâmetro.
- Cite a regra na docstring ou em comentário quando o código a implementa
  (ex.: `# RN06`). Nos testes, cite a regra e o ID do exemplo.
- Especificações de tarefa ficam em `desenvolvimento/` (ex.:
  `desenvolvimento/especificacao-tarefa.md`).

## Restrições

- Os requisitos não funcionais **não foram levantados** com os
  stakeholders. Não implemente controle de concorrência, cache, segurança
  ou desempenho sem que a tarefa peça.
- Há regras em aberto que afetam inscrição e cancelamento: prazo de
  cancelamento, critérios de reembolso, funcionamento da lista de espera e
  se a vaga fica reservada durante o pagamento pendente (itens 1, 2, 3 e 6
  de `analise/duvidas-e-lacunas.md`). Se a tarefa depender de alguma delas,
  trate como regra incompleta: pare e pergunte.
- Pagamento e reembolso (RN03, RN04) envolvem dinheiro: qualquer decisão
  sobre eles exige aprovação humana.
