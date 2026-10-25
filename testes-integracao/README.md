# Prompts para testes de integração — API de inscrição

Experimento da Unidade III: como diferentes tipos de prompt influenciam os
casos de teste de integração gerados por uma LLM.

## Cenário de integração

`POST /eventos/{evento_id}/inscricoes` de um sistema fictício de gestão de
eventos. A API integra três componentes:

```
cliente ──HTTP──▶ API (FastAPI) ──▶ regra de negócio (avaliar_inscricao)
                       │
                       ├──▶ repositório (eventos e inscrições, em memória)
                       └──▶ notificador (envio do comprovante, falso)
```

- Contrato: [`../desenvolvimento/especificacao-api-inscricao.md`](../desenvolvimento/especificacao-api-inscricao.md)
- Implementação: [`../desenvolvimento/src/eventus/api.py`](../desenvolvimento/src/eventus/api.py)

## Tipos de prompt

| Prompt | Tipo | Arquivo |
|--------|------|---------|
| 1 | Simples (*zero-shot*), sem contexto — linha de base | [`prompts/1-simples.md`](prompts/1-simples.md) |
| 2 | Papel + contrato da API + regras de negócio + formato de saída + "não invente regras" | v1: [`prompts/2-contrato.md`](prompts/2-contrato.md) · v2: [`prompts/2-contrato-v2.md`](prompts/2-contrato-v2.md) |
| 3 | Papel + contrato + foco em erros e falhas **entre componentes**, agrupados por tipo de falha | v1: [`prompts/3-erros-e-falhas.md`](prompts/3-erros-e-falhas.md) · v2: [`prompts/3-erros-e-falhas-v2.md`](prompts/3-erros-e-falhas-v2.md) |

**Como foi executado:** cada prompt rodou numa sessão isolada do Claude
(Claude Code em modo não interativo, sem ferramentas e sem acesso ao
repositório), para que o resultado dependesse só do texto do prompt. As
respostas estão em [`resultados/`](resultados/).

## Resultados

| Prompt | Casos | Dúvidas levantadas | Aderência ao contrato |
|--------|-------|--------------------|-----------------------|
| 1 — simples | 37 | 0 | **Baixa.** Inventou o contrato (autenticação, campos `nome`/`email`, "evento lotado → 409", período de inscrição). Poucos casos se aplicam, e mesmo esses com campos e códigos diferentes |
| 2 — contrato (v1) | 39 | 16 | **Alta**, com 1 caso incompatível: CT09 espera `lista_espera` num evento com 0 vagas, que o sistema trata como dado inválido |
| 3 — erros (v1) | 35 | 16 | **Média.** Casos de falha que os outros não cobrem, mas supôs comportamento para concorrência e para um notificador que "retorna falha" sem exceção; marcou como dúvida os valores de `status` e a regra de conflito, que eu não tinha incluído no prompt |
| 2 — contrato (v2) | 54 | 14 | **Total** — todos os casos executáveis passam contra a API |
| 3 — erros (v2) | 53 | 14 | **Total** — todos os casos executáveis passam contra a API |

Os casos das versões 2 viraram **82 testes pytest** (sem duplicatas entre
os dois arquivos), em
[`../desenvolvimento/tests/integracao/test_casos_gerados_llm.py`](../desenvolvimento/tests/integracao/test_casos_gerados_llm.py).
Resultado da suíte completa: **108 testes passando** (82 gerados a partir
dos prompts + 26 já existentes), Ruff e mypy sem erros.

## Como cada tipo de prompt influenciou os casos

- **Simples:** gera volume e variedade aparente, mas sobre um sistema
  imaginário. Sem contrato, a LLM preenche as lacunas com padrões
  genéricos de mercado (autenticação, `409` para lotado), e alguns
  contradizem as regras reais. Serve para *brainstorming* de categorias
  (concorrência, autenticação, Content-Type), não como suíte.
- **Baseado no contrato:** os casos ficam verificáveis (estado inicial,
  requisição, status, corpo e efeitos no repositório e no notificador) e
  cobrem bem limites das regras (sobreposição de 1 minuto, eventos que se
  encostam, ordem entre as regras). A instrução "não invente regras" fez
  a LLM separar o que não sabia numa lista de dúvidas, em vez de chutar.
- **Focado em erros e falhas:** trouxe o que os outros não trazem —
  corpo que não é objeto, tipos errados, falha do notificador com
  exceções genéricas, efeitos colaterais em sequência (`422` → `404` →
  `409` sem acumular envios) e contraprovas (o `comprovante_enviado` não
  pode ser sempre `false`). É o prompt que mais exercita a **comunicação
  entre componentes**, que é o foco do teste de integração.

## Ajustes de prompt necessários

| De → para | O que mudou | Por quê (o que a v1 mostrou) |
|-----------|-------------|------------------------------|
| Prompt 2 v1 → v2 | Regra de "já inscrito" em qualquer status e sua posição na ordem; eventos do repositório sempre válidos; concorrência fora do escopo | A v1 perguntou quem conta como "já inscrito" e em que ordem, e gerou um caso com evento de 0 vagas |
| Prompt 3 v1 → v2 | Valores de `status`, regras de negócio, "o notificador falha lançando exceção", concorrência e timeouts fora do escopo | A v1 marcou como dúvida o que eu tinha esquecido de informar e supôs comportamentos para concorrência e para falhas sem exceção |

Lição: as **dúvidas** que a LLM devolve são o melhor guia para ajustar o
prompt — cada dúvida é uma informação que faltou ou uma decisão que ainda
não foi tomada.

## Achados no sistema

- O caso CT09 da v1 (evento com 0 vagas) mostrou que a API responde `409`
  com a mensagem "deve ter ao menos 1 vaga" quando um evento inválido está
  no repositório. Um dado inválido no servidor deveria ser um erro do
  servidor (`500`), não um conflito do cliente. O agente desenvolvedor já
  tinha apontado essa ambiguidade ao implementar a API; fica registrada
  como melhoria futura (exige um erro próprio para "já inscrito" em
  `avaliar_inscricao`).
- As dúvidas que se repetem nas versões 2 (espaços em `participante_id`,
  campos extras, precedência entre `404` e `422`, texto de `detail`,
  falha do repositório) são lacunas reais do contrato.
