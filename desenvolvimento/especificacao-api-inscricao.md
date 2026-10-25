# Especificação da tarefa — API de inscrição

> Escrita **antes** da geração de código. Dados fictícios.
> Regras cobertas: RF02, RF03, RF06, RF08, RF09, RF14, RN01, RN03, RN05,
> RN06 (por meio de `avaliar_inscricao`, já implementada).

## Objetivo

Expor a avaliação de inscrição como uma API REST que integra três
componentes:

1. **Regra de negócio** — `eventus.inscricao.avaliar_inscricao` (já
   existe; não altere).
2. **Repositório** — guarda eventos e inscrições. Nesta tarefa, em memória.
3. **Notificador** — envia o comprovante de inscrição (RF03). O canal não
   está definido (lacuna 5), então é uma interface; nesta tarefa, uma
   implementação falsa que só registra os envios.

## Onde gravar

- Código: `desenvolvimento/src/eventus/` (ex.: `api.py`, `repositorio.py`,
  `notificacao.py`).
- Testes: `desenvolvimento/tests/` (os testes de integração desta API ficam
  em `desenvolvimento/tests/integracao/`).

## Dependências aprovadas para esta tarefa

- `fastapi` (produção) e `httpx` (desenvolvimento, para o `TestClient`).

## Contrato

### `POST /eventos/{evento_id}/inscricoes`

Corpo (JSON):

```json
{ "participante_id": "p1" }
```

- `participante_id`: texto obrigatório, não vazio.

Respostas:

| Situação | Status HTTP | Corpo |
|----------|-------------|-------|
| Inscrição aceita (`CONFIRMADA`, `PENDENTE_PAGAMENTO` ou `LISTA_ESPERA`) | `201` | `{"evento_id", "participante_id", "status", "comprovante_enviado"}` |
| Evento não existe | `404` | `{"detail": "<mensagem>"}` |
| Conflito de horário (`RECUSADA_CONFLITO_HORARIO`) | `409` | `{"detail": "<mensagem>"}` |
| Participante já inscrito no evento | `409` | `{"detail": "<mensagem>"}` |
| Corpo inválido (`participante_id` ausente, vazio ou não texto) | `422` | erro de validação |

- `status` no `201`: `"confirmada"`, `"pendente_pagamento"` ou
  `"lista_espera"` (valores de `ResultadoInscricao`).
- As mensagens de `detail` devem dizer o motivo (ex.: conflito de horário,
  já inscrito).

### Efeitos

- **201:** a inscrição é gravada no repositório com o status retornado, e
  o notificador recebe **um** pedido de envio de comprovante para ela.
- **404, 409 e 422:** nada é gravado e nenhum comprovante é enviado.
- **Falha do notificador** (o envio lança exceção): a inscrição **continua
  gravada** e a API responde `201` com `"comprovante_enviado": false`.
  *Decisão de 2026-10-25: falha na notificação não tira a vaga de quem se
  inscreveu. O reenvio do comprovante está fora desta tarefa.*

### Injeção de dependências

O repositório e o notificador devem poder ser trocados nos testes (ex.:
`app.dependency_overrides` do FastAPI ou uma função que cria a aplicação
recebendo os dois). Os testes precisam conseguir:

- cadastrar eventos e inscrições existentes antes da chamada;
- consultar as inscrições gravadas depois da chamada;
- consultar os comprovantes enviados e simular falha no envio.

## Fora do escopo

Criação de eventos pela API, autenticação, cancelamento, pagamento,
persistência real, concorrência (RNF02 não foi levantado) e reenvio de
comprovante.

## Exemplos

Base: os eventos `W1`, `W2` e `W3` de `especificacao-tarefa.md`
cadastrados no repositório.

| ID | Situação | Esperado |
|----|----------|----------|
| A1 | `p1` em `W1`, sem inscrições | `201`, `status: "confirmada"`, `comprovante_enviado: true`; 1 inscrição gravada; 1 comprovante |
| A2 | `p1` em `W2` (pago) | `201`, `status: "pendente_pagamento"` |
| A3 | `p1` em `W1` lotado (3 `CONFIRMADA` de outros) | `201`, `status: "lista_espera"` |
| A4 | `p1` em `W3`, tendo `CONFIRMADA` em `W1` | `409`; nada gravado; nenhum comprovante |
| A5 | `p1` em `W1`, já inscrito em `W1` | `409`; nada gravado; nenhum comprovante |
| A6 | evento `XX` inexistente | `404`; nada gravado; nenhum comprovante |
| A7 | corpo `{}` | `422`; nada gravado; nenhum comprovante |
| A8 | corpo `{"participante_id": ""}` | `422`; nada gravado; nenhum comprovante |
| A9 | `p1` em `W1`, notificador falha | `201`, `status: "confirmada"`, `comprovante_enviado: false`; 1 inscrição gravada |
